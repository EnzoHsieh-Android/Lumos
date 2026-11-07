#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
# MIT licensed. Full text: scripts/lumos header, or LICENSE at
# https://github.com/EnzoHsieh-Android/Lumos
"""全域 Stop hook: 提醒「程式碼改了但圖譜沒同步」。

只在當前專案有 docs/*-knowledge/ 或 docs/knowledge/ 時作用,否則完全闭嘴。
兩家一致(2026-09-05):改了程式碼、筆記沒動 → 回 decision:block ★一次★讓模型續做補筆記或一句話說明;
  stop_hook_active / session 標記檔雙護欄,LUMOS_STOP_BLOCK_OFF=1 關閉。擋過一次之後才退回 stderr 提醒(那條只進除錯日誌——
  Claude Code 官方文件:exit 0 的 stderr 模型看不到;Codex 亦然)。--harness codex 只影響逐字稿怎麼讀。
  沿革:Codex 先做(Projects/Codex行為精修_計劃),同日 README 審視發現 Claude 側「軟提醒」其實沒人看得到,套成一致(Projects/README審視五修_計劃 d2)。

四層閘門:
  0  圖譜不存在                      → exit 0
  1  這 turn 什麼都沒做              → exit 0(讀逐字稿,只判有沒有動作)
  2  工作樹上沒有未提交的程式碼檔    → exit 0(問版本控制,不看用了哪個工具)
  3  工作樹上有未提交的圖譜筆記      → 改印「動了筆記但這幾篇沒動」
  否則                                → 印提醒(擋停一次,之後走 stderr)

★清單為什麼改成問版本控制★(2026-09-18,單源 Projects/收工點名問版本控制_計劃):
原本閘門 2 與閘門 3 都靠列舉工具名算清單(三個編輯工具 + rm/mv/cp 那幾個命令),
用 `echo >`、`sed -i`、heredoc 改的檔一支都不算——實測一輪改三支只報一支,
而最近 12 份逐字稿裡改 code 的動作 286 次走 shell、31 次走編輯工具。列舉法原理上補不完。
代價:清單是「工作樹上未提交的」,★不再宣稱切得出這一輪★,訊息措辭已跟著改口;
為了不變成每輪唸同一批檔,跟「上次印過什麼」比對,一樣就不印
(那份紀錄在體驗路徑不在正確性路徑——壞掉只會多印一次,不會少報)。
"""
from __future__ import annotations
import json
import os
import posixpath
import re
import shlex
import subprocess
import sys
from pathlib import Path, PurePosixPath

# ── 鉤子共用程式(家目錄底下的標記目錄、標記檔名消毒與 O_EXCL 佔名額、檔名消毒、git 防護)在 _hookshared.py ──────────
# 單源在那支檔([[Projects/Android寫法回合結束檢查與改檔前推列_計劃]] 範圍 2:收工寫法檢查那支也要用,
# 這支檔吃過「邏輯抄一份、一邊改另一邊沒跟上」的虧,所以不抄第二份)。照名字匯入回來,外部看到的名字不變;
# 匯入失敗(共用模組沒裝過去)時 main 靜默放行,不讓收工卡住。
# ★可信來源解析與逾時預算不在共用模組★:那兩段跟安全邊界綁在一起,照 [[Systems/hook信任邊界]] 留在這支檔當逐字複本(下面)。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # 不用 resolve():匯入這支檔不碰檔案系統中繼資料(t_handoff_hook_import_is_pure)
try:
    from _hookshared import (_cache_dir_under_home, _mkdir_under_home, _stop_dir_ok, _safe_path,  # noqa: F401
                             _harden_git_env, _GIT_UNSAFE_CONFIG, _mark_name, _claim_mark)
    _SHARED_OK = True
except Exception:          # 共用模組不在或壞掉:整支靜默結束(rc0)
    _SHARED_OK = False

# === 觸發提醒的原始碼副檔名 ===
CODE_EXTS = {
    ".cs",                                                    # C# / .NET
    ".vue", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".php",             # 前端
    ".sql",                                                   # DB migration
    ".py",                                                    # Python
    ".kt", ".kts",                                            # Kotlin / Compose
    ".java",                                                  # Java
    ".swift",                                                 # Swift
    ".go",                                                    # Go
    ".rs",                                                    # Rust
    ".c", ".cc", ".cpp", ".h", ".hpp",                        # C/C++
    ".sh", ".ps1",                                            # shell(2026-08-21 體檢 #7 補;各份清單由 t_code_exts_lists_agree 釘)
}

# === 即使副檔名對也要排除的路徑/檔名 ===
EXCLUDE_PATH_CONTAINS = (
    "/docs/",            # 圖譜本身 + 一般文件 (.md 全排除靠這個 + 副檔名清單)
    "/node_modules/",
    "/bin/", "/obj/",
    "/.git/",
    "/dist/", "/build/",
    "/__pycache__/",
)
EXCLUDE_FILENAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
}

EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}

# === #2 收緊 ===
# obsidian CLI 子命令裡「真的會 mutate 圖譜」的清單。
# Read-only 子命令 (search/backlinks/files/orphans/...) 不算「動過圖譜」,
# 避免 `obsidian --help` / `cat ...lumos-project-notes...` 之類純查詢誤判靜音。
OBSIDIAN_WRITE_SUBCMDS = {
    "create", "append", "prepend", "delete",
    "move", "rename",
    "property:set", "property:remove",
    "daily:append", "daily:prepend",
    "base:create",
    "template:insert",
}

# === #6 補抓 Bash 檔案異動 ===
# 由 rm/mv/cp/git mv/git rm 製造的檔案變動。
# 不處理 find -delete、brace expansion、xargs rm 之類 corner case,只覆蓋常見手寫情境。
BASH_FILE_OPS_PATH_BEARING = {"rm", "mv", "cp", "git rm", "git mv"}


def find_graph_root(project_root: Path) -> Path | None:
    """找到此專案的圖譜目錄,沒有就回 None (代表沒用這套系統)。"""
    docs = project_root / "docs"
    if not docs.is_dir():
        return None
    # 新慣例: docs/{slug}-knowledge/
    for child in docs.iterdir():
        if child.is_dir() and child.name.endswith("-knowledge"):
            return child
    # 舊慣例: docs/knowledge/
    legacy = docs / "knowledge"
    return legacy if legacy.is_dir() else None


def _is_real_user_input(obj: dict) -> bool:
    """區分「真實 user 輸入」vs「tool_result(也被標 type=user)」。

    Claude Code transcript 把 tool 回應記成 type=user + content[0].type=tool_result,
    若 turn 切點誤切在 tool_result,會漏報這 turn 前面的改動(風險四)。
    """
    if obj.get("type") != "user":
        return False
    msg = obj.get("message", {})
    if not isinstance(msg, dict):
        return False
    content = msg.get("content", "")
    if isinstance(content, str):
        return True  # 純文字 user 輸入
    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict):
            return first.get("type") != "tool_result"
    return False


# ── Codex 逐字稿(Projects/Codex完全支援_計劃 S1)──────────────────────────────────────────
# 官方明說逐字稿格式不是 hooks 的穩定介面;只認 fixture 過的版本,認不得就印一行、本 session 略過判定(r1 外家 F13)。
CODEX_TRANSCRIPT_VERSIONS = {"0.144.1", "0.153.2"}   # 0.153.2:2026-09-05 真實稿驗過同形(多 event_msg/item_completed、token_usage_record 兩型,reader 不讀)
# key 有引號 {"cmd":"…"} 與沒引號 {cmd:"…"}(含換行縮排)兩種都出現(2026-09-04 當日逐字稿 31:30;code-codex-s1 r1 外家 #2)
_CODEX_EXEC_CMD_RE = re.compile(r'(?<![\w$])["\']?cmd["\']?\s*:\s*"((?:[^"\\]|\\.)*)"')
# patch 可能直接傳字串 tools.apply_patch("…"),也可能先存變數 const patch = "…" 再呼叫(S1 驗收實看):
# 一律掃所有含 *** Begin Patch 的 JS 字串字面值
_CODEX_APPLY_PATCH_RE = re.compile(r'"((?:[^"\\]|\\.)*\*\*\* Begin Patch(?:[^"\\]|\\.)*)"')
_CODEX_PATCH_HDR_RE = re.compile(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+?)\s*$")


def _js_unescape(s: str) -> str:
    try:
        return json.loads('"' + s + '"')
    except ValueError:
        return s.replace("\\n", "\n").replace('\\"', '"')


def _is_codex_transcript(first_obj: dict) -> bool:
    return isinstance(first_obj, dict) and first_obj.get("type") == "session_meta"


def collect_codex_turn_actions(lines: list[str]):
    """Codex rollout jsonl → (file_paths, bash_commands)。型別:第一行 session_meta(讀 cli_version);
    真實 user 輸入=event_msg/user_message;工具呼叫=response_item/custom_tool_call name=exec,input 是一段 JS:
    `tools.exec_command({"cmd":"…"})` 取 cmd、`tools.apply_patch("…patch…")` 解 patch 標頭取檔。
    版本不在 CODEX_TRANSCRIPT_VERSIONS → stderr 一行、回 ([], [])(略過,不猜)。"""
    objs = []
    for line in lines:
        if not line.strip():
            continue
        try:
            objs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not objs:
        return [], []
    ver = str(((objs[0].get("payload") or {}).get("cli_version")) or "")
    # patch 標頭的路徑是相對 session cwd 的;is_code_file 要「在 project_root 之下」的絕對路徑(Claude 逐字稿本來就是絕對路徑)
    sess_cwd = str(((objs[0].get("payload") or {}).get("cwd")) or "")
    if ver not in CODEX_TRANSCRIPT_VERSIONS:
        print(f"[check-graph-sync] Codex 逐字稿格式未知(cli_version={ver or '?'};認得的:{','.join(sorted(CODEX_TRANSCRIPT_VERSIONS))}),"
              "收工同步這一輪略過——不猜格式;要接新版先補 fixture", file=sys.stderr)
        return [], []
    turn = []
    for obj in reversed(objs):
        p = obj.get("payload") or {}
        # 輪次邊界兩種型別都認(r1 外家 #1):event_msg/user_message(exec 模式會有)與 response_item/message role=user
        # (真使用者輸入也會以這型出現,且系統注入的 <recommended_plugins> 也是這型——所以只認最後一個,不管內容)
        if obj.get("type") == "event_msg" and p.get("type") == "user_message":
            break
        if obj.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "user":
            break
        turn.append(obj)
    turn.reverse()
    file_paths: list[str] = []
    bash_commands: list[str] = []
    for obj in turn:
        p = obj.get("payload") or {}
        if obj.get("type") != "response_item" or p.get("type") != "custom_tool_call":
            continue
        inp = p.get("input")
        if not isinstance(inp, str):
            continue
        for m in _CODEX_EXEC_CMD_RE.finditer(inp):
            cmd = _js_unescape(m.group(1))
            if cmd:
                bash_commands.append(cmd)
        for m in _CODEX_APPLY_PATCH_RE.finditer(inp):
            patch = _js_unescape(m.group(1))
            for ln in patch.split("\n"):
                h = _CODEX_PATCH_HDR_RE.match(ln.strip())
                if h:
                    fp = h.group(1).strip()
                    if sess_cwd and not Path(fp).is_absolute():
                        fp = str(Path(sess_cwd) / fp)
                    if fp not in file_paths:
                        file_paths.append(fp)
    return file_paths, bash_commands


def collect_turn_actions(transcript_path: Path):
    """從 transcript 尾部反向掃,到最近一個「真實 user 輸入」為止
    (排除 tool_result 之類也被標 type=user 的雜訊)。
    回傳 (file_paths, bash_commands)。Codex 逐字稿(第一行 session_meta)走 collect_codex_turn_actions。
    """
    if not transcript_path.is_file():
        return [], []
    lines = transcript_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    first = next((l for l in lines if l.strip()), "")
    try:
        first_obj = json.loads(first) if first else None
    except json.JSONDecodeError:
        first_obj = None
    if _is_codex_transcript(first_obj):
        return collect_codex_turn_actions(lines)
    turn_lines = []
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if _is_real_user_input(obj):
            break
        turn_lines.append(obj)
    turn_lines.reverse()

    file_paths: list[str] = []
    bash_commands: list[str] = []
    for obj in turn_lines:
        if obj.get("type") != "assistant":
            continue
        for item in obj.get("message", {}).get("content", []) or []:
            if not isinstance(item, dict) or item.get("type") != "tool_use":
                continue
            name = item.get("name", "")
            inp = item.get("input", {}) or {}
            if name in EDIT_TOOLS:
                fp = inp.get("file_path", "")
                if fp:
                    file_paths.append(fp)
            elif name == "Bash":
                cmd = inp.get("command", "")
                if cmd:
                    bash_commands.append(cmd)
    return file_paths, bash_commands


def _shebang_script(p: Path) -> bool:
    """沒有副檔名的檔,首行是 #! 就當程式碼(2026-09-05 f02 後測實證:本 repo 主程式 `scripts/lumos`
    無副檔名,兩家改它都過不了閘門 2,Stop 提醒/擋停從沒對它生效過)。讀不到、不是 #!、二進位 → False。"""
    if p.suffix:
        return False
    try:
        if not p.is_file():      # 目錄 / FIFO / socket / 不存在:不開(整合席 r1:開 FIFO 會卡死)
            return False
        with open(p, "rb") as fh:
            head = fh.readline(200)
    except OSError:
        return False
    return head.startswith(b"#!")   # 任何 shebang 都算(r1 外家:列直譯器會漏 dash;四處同一條規則)


def is_code_file(path: str, project_root: Path) -> bool:
    p = Path(path)
    # 必須在 project_root 之下;避免改 ~/.claude/、/tmp 等外部檔案被誤判(★先判位置再開檔:整合席 r1 blocker——
    # shebang 檢查會 open(),repo 外的路徑一律不碰,FIFO 之類會卡住 10 秒 timeout)
    try:
        p.resolve().relative_to(project_root.resolve())
    except (ValueError, OSError):
        return False
    norm = str(p).replace("\\", "/")
    if any(seg in norm for seg in EXCLUDE_PATH_CONTAINS):
        return False
    if p.name in EXCLUDE_FILENAMES:
        return False
    if p.suffix.lower() in CODE_EXTS:
        return True
    return _shebang_script(p)


def is_graph_file(path: str, graph_root: Path) -> bool:
    """檔案是否在圖譜資料夾底下 (任何 .md)。"""
    p = Path(path)
    if p.suffix.lower() != ".md":
        return False
    try:
        p.resolve().relative_to(graph_root.resolve())
        return True
    except (ValueError, OSError):
        return False


# ── 工作樹查詢(Projects/收工點名問版本控制_計劃)────────────────────────────
# 出身:清單原本靠列舉工具名算(三個編輯工具 + rm/mv/cp/git rm/git mv),
# 用 `echo >`、`sed -i`、heredoc 改的檔一支都不算——實測一輪改三支只報一支,
# 而最近 12 份逐字稿裡改 code 的動作 286 次走 shell、31 次走編輯工具。
# 列舉法原理上補不完(tee/patch/一行 python/包一層 shell/產生器),量結果不量過程才免疫。

def _git(project_root: Path, *args, text=True, data=None):
    """對被檢查的那個資料夾跑一個版本控制指令。兩個旗標都是安全用的,不是裝飾:

    ★關掉檔名轉義★(代碼審 r1 外家備援+邊界+正確性 三席獨立報,編排者實測):
    不帶它,非 ASCII 檔名會被跳脫成 `"scripts/\\346\\224\\266..."` 這種八進位形式,
    只 strip 掉引號還原不了,解析出來的路徑指向一個不存在的檔——
    ★而這個專案的檔名大量是中文★,等於天天踩。

    ★關掉那個會被當成指令執行的設定項★(代碼審 r1 資安席,編排者實測重現):
    這支 hook 是開啟資料夾就自動跑的,而這個呼叫會吃★被打開那個資料夾自己的★版本控制設定;
    其中有一項的值會被當成 shell 指令執行——實測在惡意設定的倉庫上查一次狀態,
    攻擊者指定的指令就跑了。★觸發面是本批改動擴大的★:改動前這條路完全不呼叫版本控制。

    ★誠實邊界,不得宣稱更多★:只關掉已知會執行指令的那一項;版本控制的設定面很大,
    **不宣稱「所有設定都擋得住」**。純 clone 不會把該設定帶過來(實測),
    真正的交付路徑是「直接拿到別人的整個目錄」。
    這支檔其他地方的版本控制呼叫沒有走這條路,是否要一併收攏另案處理。"""
    # ★防護讀同一份清單,不要寫死★:寫死的話清單加一項這裡不會跟,
    # 就會出現「清單上有、某個呼叫點沒有」的不一致——而那正是這條問題前三輪的死法。
    # 環境變數那層已經涵蓋所有子行程,這裡是雙保險:測試會直接呼叫這個函式、不經進入點。
    unsafe = [x for k in _GIT_UNSAFE_CONFIG for x in ("-c", k + "=")]
    return subprocess.run(
        ["git", "-C", str(project_root), "-c", "core.quotePath=false", *unsafe, *args],
        input=data, capture_output=True, text=text, timeout=_inner_budget(default=20))


# ★下面這支是主程式 scripts/lumos 同名函式的逐字複本★(回合結束檢查代碼審 r3 甲組,資安席 F2):找工作樹改動不跑 git status
# (status 會經被打開目錄自帶的內容過濾器,等於執行對方指定的指令)。這是安全邏輯,照 [[Systems/hook信任邊界]] 走「逐字複本+守衛」、
# 不走共用模組;守衛 t_lwt_r3_nofilter_verbatim 盯著兩份一字不差。
def _wt_changed_nofilter(repo_root, run, paths=()):
    """工作樹上還沒提交的改動,★不跑 git status、不經任何內容過濾器★ → [(X, Y, 路徑, 舊路徑或 None)] 或 None(任何一個 git 指令失敗)。
    狀態碼同 git status --porcelain=v1:X 是 HEAD 對索引、Y 是索引對工作樹;?? 未追蹤、UU 衝突;HEAD 與索引同一物件、只換了路徑的算 R。
    為什麼:git status 遇到大小不變、內容改過的檔會跑 .gitattributes 指到的 clean/process 過濾器,過濾器的名字與指令由被打開的目錄決定,
    列名字再逐個關掉的做法被打穿三次。這裡只用不執行內容過濾器的指令:ls-tree -r -z(HEAD)、ls-files -s -z(索引的模式與物件編號)、
    ls-files -s --debug -z(索引記下的時間與大小,只拿來省雜湊、格式認不得就全部算)、ls-files -o --exclude-standard -z(未追蹤)、
    hash-object --no-filters --stdin-paths(工作樹內容照原樣算,https://git-scm.com/docs/git-hash-object )。
    只看一般檔(100644、100755),符號連結與子模組(120000、160000)跳過。時間與大小跟索引記的一樣、而且比索引檔早寫的才不算雜湊(同 git 的 racy 判法)。
    用了真過濾器的專案(LFS、autocrlf)會多報幾支(工作樹原樣跟索引裡轉過的不同),方向是多查不漏查。
    ★索引旗標照 git status★(代碼審 r5 正確性席 F1):ls-files -v 標 S(skip-worktree,sparse-checkout 圈外的檔也是這個)或小寫
    (assume-unchanged)的條目不比工作樹(Y 一律空白、不 lstat 不算雜湊),HEAD 對索引照比——git status 對這類檔也只報索引那一欄
    (https://git-scm.com/docs/git-ls-files 的 -t、-v)。
    run(*參數, data=位元組或 None) → 有 returncode 與 stdout(位元組)的結果或 None;-C 與 -c 參數由呼叫端決定。paths 給了就只看這幾支(字面路徑)。
    ★路徑基準一律是 repo 根★(代碼審 r4 正確性席 F1、邊界席 F1、通才席 F1):repo_root 可以是 repo 的子目錄(monorepo);先用
    rev-parse --show-toplevel 取根、之後每個 git 指令都帶 -C <根>(ls-tree --full-tree 從根算、hash-object --stdin-paths 也從根開檔,
    跟 ls-files 不統一時乾淨的樹會被報成一堆刪除與改名、改過的檔整次回 None),ls-files 加 --full-name;lstat 用根接路徑;
    paths 是相對 repo_root 的,前面補 --show-prefix。回傳的路徑從 repo 根算起(同 git status --porcelain)。"""
    import os as _os
    import stat as _st

    def ok(*a, data=None, here=False):    # here=True 在呼叫端給的目錄跑(只有取根那兩次),其餘一律在 repo 根跑
        r = (run if here else in_top)(*a, data=data)
        return r.stdout if r is not None and r.returncode == 0 else None
    t, pfx = ok("rev-parse", "--show-toplevel", here=True), ok("rev-parse", "--show-prefix", here=True)
    if not t or pfx is None:
        return None
    top = _os.fsdecode(t[:-1] if t.endswith(b"\n") else t)
    pfx = _os.fsdecode(pfx[:-1] if pfx.endswith(b"\n") else pfx)
    lit = ("--", *(pfx + p for p in paths)) if paths else ()

    def in_top(*a, data=None):            # 呼叫端給的 run(-C 是 repo_root)前面再補 -C <根>;不重綁 run 這個名字(代碼審 r5 架構對齊席 F2)
        return run("-C", top, *a, data=data)

    def entries(raw, n=3):
        for ent in (raw or b"").split(b"\0"):
            meta, tab, p = ent.partition(b"\t")
            f = meta.split(b" ")
            if tab and len(f) == n:
                yield f, p
    reg = (b"100644", b"100755")
    h = in_top("rev-parse", "--verify", "-q", "HEAD")
    if h is None or h.returncode not in (0, 1):
        return None
    raw = ok("ls-tree", "-r", "-z", "--full-tree", "HEAD", *lit) if h.returncode == 0 else b""
    idx = ok("ls-files", "-s", "-v", "-z", "--full-name", *lit)
    unt = ok("ls-files", "-o", "--exclude-standard", "-z", "--full-name", *lit)
    if raw is None or idx is None or unt is None:
        return None
    head, index, conflict, skip, hold = {}, {}, set(), set(), set()
    for f, p in entries(raw):
        if f[0] in reg:
            head[p] = f[2]
        else:
            skip.add(p)
    for g, p in entries(idx, 4):          # -v 多一欄旗標:S 是 skip-worktree、小寫是 assume-unchanged
        tag, f = g[0], g[1:]
        if f[2] != b"0":
            conflict.add(p)
        elif f[0] in reg:
            index[p] = f[1]
            if tag == b"S" or tag.islower():
                hold.add(p)
        else:
            skip.add(p)
    stamp = {}
    dbg = ok("ls-files", "-s", "--debug", "-z", "--full-name", *lit) or b""
    prev = None
    for chunk in dbg.split(b"\0"):
        lines = chunk.split(b"\n")
        info = {}
        while lines and lines[0].startswith(b"  "):
            for kv in lines.pop(0).strip().split(b"\t"):
                k, _c, v = kv.partition(b": ")
                info[k.strip()] = v.strip()
        try:
            if prev is not None and info:
                sec, _c, ns = info[b"mtime"].partition(b":")
                stamp[prev] = (int(sec) * 1000000000 + int(ns), int(info[b"size"]))
        except (KeyError, ValueError):
            pass
        rest = b"\n".join(lines)
        prev = rest.partition(b"\t")[2] if b"\t" in rest else None
    gp = ok("rev-parse", "--git-path", "index")
    try:
        idx_ns = _os.stat(_os.path.join(top, _os.fsdecode(gp.rstrip(b"\n")))).st_mtime_ns if gp else None
    except OSError:
        idx_ns = None
    wt, ask = {}, []
    for p, oid in index.items():
        if p in hold:
            continue                      # git status 不比這類檔的工作樹,Y 留空白
        try:
            s = _os.lstat(_os.path.join(top, _os.fsdecode(p)))
        except (FileNotFoundError, NotADirectoryError):
            wt[p] = "D"
            continue
        except OSError:
            wt[p] = "M"
            continue
        if not _st.S_ISREG(s.st_mode):
            wt[p] = "T"
        elif idx_ns is not None and s.st_mtime_ns < idx_ns and stamp.get(p) == (s.st_mtime_ns, s.st_size & 0xFFFFFFFF):
            wt[p] = " "
        elif b"\n" in p or p[:1] == b'"' or p.endswith(b"\r"):
            wt[p] = "M"                   # 一行一個路徑的輸入表達不了(結尾的 CR 會被當行尾吃掉,代碼審 r4 正確性席 F2),當改過(多查)
        else:
            ask.append(p)
    if ask:
        got = ok("hash-object", "--no-filters", "--stdin-paths", data=b"\n".join(ask) + b"\n")
        sums = (got or b"").split()
        if got is None or len(sums) != len(ask):
            return None
        for p, sha in zip(ask, sums):
            wt[p] = " " if sha == index[p] else "M"
    res = {}
    for p in set(head) | set(index) | conflict:
        if p in skip:
            continue
        if p in conflict:
            res[p] = ["U", "U", None]
            continue
        x = " " if head.get(p) == index.get(p) else ("A" if p not in head else ("D" if p not in index else "M"))
        y = wt.get(p, " ") if p in index else " "
        if x + y != "  ":
            res[p] = [x, y, None]
    gone = {}
    for p, v in res.items():
        if v[0] == "D":
            gone.setdefault(head[p], []).append(p)
    for p, v in res.items():
        old = gone.get(index.get(p)) if v and v[0] == "A" else None
        if old and len(old) == 1 and (res.get(old[0]) or [None])[0] == "D":
            v[0], v[2] = "R", old[0]
            res[old[0]] = None
    out = [(v[0], v[1], _os.fsdecode(p), _os.fsdecode(v[2]) if v[2] is not None else None) for p, v in res.items() if v]
    out += [("?", "?", _os.fsdecode(p), None) for p in (unt or b"").split(b"\0") if p]
    return sorted(out, key=lambda e: e[2])


def _git_status_entries(project_root: Path, top: Path | None = None):
    """工作樹上有哪些檔還沒提交。回 [(狀態碼, repo 相對路徑)];狀態碼 '??' = 從未被追蹤。top 是 repo 根(沒給就自己問)。

    ★只回專案底下的條目★(代碼審 r6 正確性、邊界、通才、合約四席 F1):找改動回的是整個 repo,專案根是 repo 子目錄時
    兄弟目錄的改動原本混進來,活檔靠 is_code_file 擋掉、被刪的檔沒那道,於是被點名、還進擋停清單。子目錄專案這族
    連三輪在不同下游各補一處(r4 路徑基準、r5 接路徑、r6 刪除分支),改在這個唯一出口整批濾,下游任何分支只看得到專案內的檔;
    改名的兩端任一端在專案內就留。路徑照舊從 repo 根算起(同 prek 的 monorepo 做法:專案根不一定是 git 根,
    掛鉤只看自己專案的檔 https://prek.j178.dev/monorepos/ )。

    ★不跑 git status★(回合結束檢查代碼審 r3 甲組,資安席 F2 實測):status 遇到大小不變、內容改過的檔
    會執行被打開目錄自帶的內容過濾器;改走 _wt_changed_nofilter(只用不經過濾器的 git 指令)。
    未追蹤的檔逐支列(ls-files -o,不會把新目錄摺成一行);改名那列給新路徑。
    ★為什麼不沿用閘門 3 那條現成的查詢★:那條底層是拿工作樹跟上次提交比,
    **看不到從未被追蹤的新檔**——而 `echo > 新檔.py` 正是最常見的 shell 寫法。

    任何失敗(不是倉庫、索引被鎖、逾時)一律回 None=算不出來,呼叫端 fail-open。
    """
    def run(*a, data=None):
        return _git(project_root, *a, text=False, data=data)
    try:
        ents = _wt_changed_nofilter(project_root, run)
    except Exception:
        return None
    if ents is None:
        return None
    if top is None:
        top = _repo_top(project_root)
    return [(x + y, p) for x, y, p, o in ents
            if p and (_rel_in_project(p, project_root, top) or (o and _rel_in_project(o, project_root, top)))]


def _head_shebang(project_root: Path, relpath: str) -> bool:
    """這支檔在上一次提交裡,首行是不是 `#!`。

    ★給已經被刪掉的檔用★:`_shebang_script` 第一步就問「這個檔存在嗎」,
    檔案刪掉之後永遠回 False——而本 repo 主程式正是沒有副檔名、只能靠首行認出來的檔
    (設計審三席獨立報同一條)。所以刪除的檔改讀它在上次提交裡的內容。"""
    try:
        r = _git(project_root, "show", "HEAD:" + relpath, text=False)
        return r.returncode == 0 and r.stdout[:2] == b"#!"
    except Exception:
        return False


def _entry_is_deleted(code: str) -> bool:
    return "D" in code


def _repo_top(project_root: Path) -> Path:
    """被檢查目錄所在 git repo 的根;git 問不出來就照回 project_root(不崩)。找改動回的路徑從 repo 根算起(同 git status --porcelain),
    ★要接在這個根上,不能接在專案根上★(代碼審 r5 邊界席 F1、通才席 F1:專案根是 repo 子目錄時原本接成 sub/sub/…,
    沒副檔名的腳本認不出、筆記動過也認不出)。圖譜位置與「在不在專案底下」照舊用 project_root 判。
    ★為什麼跟 _wt_changed_nofilter 各問一次根★(代碼審 r6 通才席 F2):那支是主程式的逐字複本(守衛 t_lwt_r3_nofilter_verbatim),
    改它的回傳形狀要兩份連動,所以這裡多開一次 git,換複本不動。名字叫 _repo_top 不叫同目錄別支鉤子的 _repo_root(代碼審 r6 架構對齊席 F2):
    那幾支失敗時各有各的退法,這支失敗照回 project_root;只是命名沒對齊,不改名(改名要動既有測試與筆記的指名,換不到行為差別)。"""
    try:
        r = _git(project_root, "rev-parse", "--show-toplevel")
        t = r.stdout.rstrip("\n") if r.returncode == 0 else ""
    except Exception:
        t = ""
    return Path(t) if t else project_root


def _rel_in_project(relpath: str, project_root: Path, top: Path | None) -> bool:
    """repo 根相對路徑 relpath 落不落在 project_root 底下;★不要求這支檔存在★(被刪的檔、改名前的舊路徑都要判)。
    只解析兩個一定存在的目錄(repo 根、專案根)算出專案在 repo 裡的前綴,relpath 本身照字面逐段比:
    macOS 的暫存目錄經 /var → /private/var,git 回的根是解析後的寫法,直接拿兩個字串比前綴會把專案裡的檔也判成在外面。"""
    try:
        pfx = project_root.resolve().relative_to((top or project_root).resolve()).parts
    except (ValueError, OSError):
        return False
    parts = PurePosixPath(posixpath.normpath(relpath.replace("\\", "/"))).parts
    if not parts or parts[0] in ("/", ".."):
        return False
    return parts[:len(pfx)] == pfx


def _entry_is_code(code: str, relpath: str, project_root: Path, top: Path | None = None) -> bool:
    """狀態表的一列,是不是我們在意的程式碼檔。relpath 從 repo 根算起,top 是 repo 根(沒給就當 project_root 就是根)。"""
    norm = relpath.replace("\\", "/")
    # ★比對前要補前導斜線★(代碼審 r1 邊界席):排除清單寫的是前後帶斜線的形式(例如 /dist/),
    # 而狀態查詢給的是不帶前導斜線的相對路徑(dist/bundle.js)——頂層目錄永遠對不上。
    # 沒被刪的檔後面還有 is_code_file 用絕對路徑再擋一次,★被刪的檔沒有那道★,
    # 於是刪掉建置產物裡的檔會被誤報成「該寫筆記的程式碼檔」。
    if any(seg in "/" + norm.lstrip("/") for seg in EXCLUDE_PATH_CONTAINS):
        return False
    if Path(relpath).name in EXCLUDE_FILENAMES:
        return False
    if _entry_is_deleted(code):                       # 檔已經不在,開不了
        if Path(relpath).suffix.lower() in CODE_EXTS:
            return True
        return _head_shebang(project_root, relpath)
    return is_code_file(str((top or project_root) / relpath), project_root)


# ── 抑制重複(同一批檔不要每輪重講)────────────────────────────────────
# 清單改成「工作樹上未提交的」之後就不限這一輪,不抑制會變成每輪唸同一批檔
# =重現 2026-07-06 撤掉的刷屏(設計審兩席各報 blocker)。
# ★這份紀錄在體驗路徑,不在正確性路徑★:讀不到就當沒印過照印,壞掉只會多印一次、不會少報。
# 對照:前一版被否決的方案把狀態放在正確性路徑(算差集),壞掉會少報,才需要原子寫入/版號/鍵值/清理全套。

def _printed_mark_path(session_id: str):
    name = _mark_name(session_id)           # 標記檔名消毒只有共用模組一份(擋停標記與去重紀錄同一套)
    if name is None:
        return None
    return _printed_dir() / name


def _load_printed(session_id: str):
    """上次印過哪些;讀不到一律回 None=當作沒印過。"""
    mp = _printed_mark_path(session_id)
    if mp is None:
        return None
    try:
        return set(json.loads(mp.read_text(encoding="utf-8")))
    except Exception:
        return None


def _save_printed(session_id: str, keys) -> None:
    """記下這次印了什麼。寫失敗就算了——下一輪會重印一次,那是可接受的代價。"""
    mp = _printed_mark_path(session_id)
    if mp is None or not _stop_dir_ok(mp.parent):
        return
    try:
        mp.write_text(json.dumps(sorted(keys), ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _segment_command(cmd: str) -> list[str]:
    """切 shell chain (`&&` / `||` / `;` / `|`)。Quote-aware 不嚴格,但對常見 case 夠用。"""
    return [s.strip() for s in re.split(r'\s*(?:&&|\|\||;|\|)\s*', cmd) if s.strip()]


def _tokens_of(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        return []


def touched_graph_via_cli(bash_commands: list[str]) -> bool:
    """★2026-09-18 起沒有呼叫點★(代碼審 r1 合約一致席 + 架構對齊席):
    閘門 3 的判準改成問版本控制之後,這個函式不再被 main() 使用。
    暫時留著不刪——它是「認名字」那套的最後一段,刪掉會讓 diff 更難讀;
    下一次動這支檔時一併移除。留著的代價只有讀者困惑,沒有行為影響。

    這 turn 是否真的「寫」過圖譜 (#2 收緊):
       只有 obsidian CLI 用了 mutate 子命令 (create/append/property:set 等) 才算。
       Read-only 子命令 / `obsidian --help` / 路徑裡含 obsidian 字串的非 obsidian command 都不算。
    """
    for cmd in bash_commands:
        for seg in _segment_command(cmd):
            tokens = _tokens_of(seg)
            if not tokens:
                continue
            # 跳過 leading env vars (`FOO=bar obsidian ...`)
            idx = 0
            while idx < len(tokens) and "=" in tokens[idx] and not tokens[idx].startswith("-"):
                idx += 1
            if idx >= len(tokens) or tokens[idx] != "obsidian":
                continue
            # 從 obsidian 後找第一個非 key=value 的 token,即為子命令
            for t in tokens[idx + 1:]:
                if t.startswith("-"):
                    continue
                if "=" in t and not t.startswith("="):
                    continue
                if t in OBSIDIAN_WRITE_SUBCMDS:
                    return True
                break  # 遇到第一個 positional 但非 write subcmd → 結束此 segment
    return False


def extract_bash_file_paths(bash_commands: list[str], project_root: Path) -> list[str]:
    """#6: 從 rm/mv/cp/git rm/git mv 命令裡撈被影響的檔案路徑。

    回傳「絕對路徑字串」list,讓後續 is_code_file 統一處理。
    相對路徑視為相對 project_root (Bash tool 的 cwd 通常就是 project_root)。
    """
    out: list[str] = []
    for cmd in bash_commands:
        for seg in _segment_command(cmd):
            tokens = _tokens_of(seg)
            if not tokens:
                continue
            # 跳過 leading env vars
            i = 0
            while i < len(tokens) and "=" in tokens[i] and not tokens[i].startswith("-"):
                i += 1
            if i >= len(tokens):
                continue
            head = tokens[i]
            args = tokens[i + 1:]
            # 處理 "git rm" / "git mv"
            if head == "git" and args:
                sub = args[0]
                if sub in ("rm", "mv"):
                    head = f"git {sub}"
                    args = args[1:]
                else:
                    continue
            if head not in BASH_FILE_OPS_PATH_BEARING:
                continue
            # 過濾掉 flag,剩下都是路徑候選
            paths = [a for a in args if not a.startswith("-")]
            if not paths:
                continue
            if head == "cp":
                # cp [opts] SRC... DST → DST 是新檔
                if len(paths) >= 2:
                    paths = [paths[-1]]
                else:
                    continue
            # 標準化成絕對路徑
            for p in paths:
                pp = Path(p)
                if not pp.is_absolute():
                    pp = project_root / pp
                out.append(str(pp))
    return out


def find_notes_mentioning(rel_paths: list[str], graph_root: Path) -> dict[str, list[str]]:
    """#5: 用 obsidian CLI search 反查每個改的檔案在哪幾篇圖譜筆記出現。

    搜尋以「檔名 stem」為 query (PointService.cs → 'PointService'),
    既捕捉檔名直接引用,也捕捉透過 class/symbol name 的提及。

    若 obsidian CLI 不可用 (app 沒開 / CLI 未安裝),回 {} 讓警告維持基本版。
    """
    vault_name = graph_root.name
    stems: list[str] = []
    seen: set[str] = set()
    for fp in rel_paths:
        stem = Path(fp).stem
        # 短 stem (<=2 字元) 跳過,搜出來會全是噪音
        if not stem or len(stem) <= 2 or stem in seen:
            continue
        seen.add(stem)
        stems.append(stem)
    stems = stems[:5]  # 控成本

    if not stems:
        return {}

    result: dict[str, list[str]] = {}
    for stem in stems:
        try:
            proc = subprocess.run(
                ["obsidian", f"vault={vault_name}", "search", f"query={stem}", "limit=5"],
                # ★這裡刻意寫死 2 秒,不走預算★(2026-09-07 代碼審 r1 通才席):
                # 這是逐個候選跑的小查詢,最多 5 次;包成 min(2.0, 預算) 只是好看——
                # 預算算出來一定 ≥2,取小值恆等於 2,等於沒接上單一來源卻宣稱接了。
                capture_output=True, text=True, timeout=2.0,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return {}  # obsidian 全面不可用,放棄 enrichment
        if proc.returncode != 0:
            continue
        notes = [
            ln.strip() for ln in proc.stdout.splitlines()
            if ln.strip() and ln.strip().endswith(".md")
        ]
        if notes:
            result[stem] = notes[:3]
    return result


def emit_queue_patrol(project_root: Path) -> None:
    """B (2026-05-25): Stop hook 巡邏 .rot-queue.jsonl,
    堆積到一定量就 stderr 提醒 — 避免 L3 寫入後沒人消化變黑洞。

    機械式不靠記得;用 Stop hook 既有機制不引入 launchd 新失效面。

    閾值:>= 3 個 finding 才提醒 (避免 single 噪音)
    """
    queue_path = project_root / "docs" / ".rot-queue.jsonl"
    if not queue_path.is_file():
        return
    try:
        entries = []
        with queue_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except OSError:
        return
    if len(entries) < 3:
        return
    verifs = {e.get("verification", "") for e in entries if isinstance(e, dict)}
    ts_values = [e.get("ts", "") for e in entries if isinstance(e, dict)]
    oldest = min((t for t in ts_values if t), default="?")
    print(
        f"📋 rot-queue 累積 {len(entries)} 筆 finding 涵蓋 {len(verifs)} 篇 Verification "
        f"(oldest: {oldest[:10]})。"
        f"\n   跑 `lumos gov` 看 L3 rot 事件(rot-queue-digest.sh 從未存在,2026-08-21 更正)。",
        file=sys.stderr,
    )


# ── ★只執行「可信來源」的 lumos,絕不執行被打開那個資料夾裡的碼★ ──────────────
# 單源說明在 Systems/hook信任邊界;這段在幾支 hook 裡是逐字相同的複本,
# 有守衛測試盯著不准漂(hook 是獨立檔、複製到 ~/.claude/hooks 後彼此 import 不到,
# 所以用「複製 + 守衛」而不是抽共用模組)。
#
# 出身(2026-09-06 實地重現):這支 hook 原本執行的是 `<被打開的資料夾>/scripts/lumos`,
# 唯一判準是那個資料夾有 docs/*-knowledge。**clone 一個陌生 repo、開一下 Claude,
# 對方的 python 就在你機器上跑了**——而且因為是拿 python 去執行它,
# 那個檔連執行權限都不需要。
#
# 解析順序:系統裝好的 → $LUMOS_HOME 指的 → 預設來源位置 → 都沒有就回 None。
# 回 None 時呼叫端要靜默跳過那段功能(這套本來就是 fail-open:寧可少一層提醒,
# 不可執行不該信任的碼)。
#
# ★2026-09-07 外家審查席補的一刀★:光是「從 PATH 或 $LUMOS_HOME 找到」不算可信——
# 那兩個都是繼承來的環境值,workspace-local 的 bin(direnv / node_modules/.bin 之類)
# 一進專案就可能改掉 PATH。所以找到之後還要驗那個檔本身:不是 symlink 指到別處、
# 是自己的、group/other 不可寫。
# ★誠實邊界★:完全控制你 PATH 的人本來就能在你帳號下跑任何東西,這條擋不住那種;
# 它擋的是「專案順手塞一個 bin 進 PATH」與「別人可寫的目錄裡放一支同名的」。
def _trusted_lumos():
    import shutil as _sh, os as _os, stat as _st
    from pathlib import Path as _P

    def _ok(cand):
        try:
            p = _P(cand)
            if not p.is_absolute():
                return None          # 相對路徑(PATH 有空項或 .)會從目前目錄、也就是被打開的資料夾解出來(代碼審 r4 資安席 F1)
            if not p.is_file():
                return None
            st = p.stat()
            if hasattr(_os, "getuid") and st.st_uid != _os.getuid():
                return None          # 不是自己的檔
            if st.st_mode & (_st.S_IWGRP | _st.S_IWOTH):
                return None          # 別人可寫 = 別人可換內容
            par = p.parent.stat()
            if hasattr(_os, "getuid") and par.st_uid != _os.getuid():
                return None          # 放在別人的目錄裡
            if par.st_mode & (_st.S_IWGRP | _st.S_IWOTH):
                return None          # 目錄別人可寫 = 可被換掉
            return str(p)
        except OSError:
            return None

    found = _sh.which("lumos")
    if found:
        good = _ok(found)
        if good:
            return good
    for base in (_os.environ.get("LUMOS_HOME"), str(_P.home() / "harness" / "lumos-toolchain")):
        if not base:
            continue
        good = _ok(_P(base) / "scripts" / "lumos")
        if good:
            return good
    return None
# ── ★可信來源解析結束★ ────────────────────────────────────────────────

# ── ★內層逾時一律從外層天花板算出來,不寫死★ ──────────────────────────────
# 單源說明在 Systems/hook逾時預算;這段在幾支 hook 裡是逐字相同的複本,有守衛盯著不准漂
# (hook 是獨立檔、複製到全域後彼此 import 不到)。
#
# 出身(2026-09-07 全 repo 審視 #14 量出來的):外層天花板寫在註冊表、內層逾時寫在各 hook,
# 兩邊各自演化。五支裡三支違反自家「外要明顯大於內」的規則,其中一支內層是外層的 2.5 倍。
#
# ★內層 ≥ 外層代表什麼★:內層那條「逾時就 fail-open」的分支**結構上永遠跑不到**——
# 外面會先把整支 hook 砍掉(SIGKILL,繞過 try/except)。影響鏡頭那支的 fail-open 分支裡
# 有「把冷卻窗記號清掉」,跑不到就表示超時之後那個檔被鎖住 20 分鐘完全不注入,而沒人知道。
# **一個為了 fail-open 而寫的分支,自己被 fail-closed 掉了。**
#
# 現在:天花板由註冊表一處生成,用 --budget 傳進來;內層一律取「天花板 × 0.7 減掉已耗」,
# 留 30% 給 hook 自己的啟動、收尾與寫輸出。拿不到 --budget(舊註冊還沒更新)就用保守預設。
_BUDGET_RATIO = 0.7
_BUDGET_FLOOR = 1.0          # 再怎麼扣也留 1 秒,不要算出 0 或負數
_BUDGET_START = None         # 這支 hook 開始跑的時刻(第一次用到時記)


def _outer_budget(default=10.0):
    """從 argv 讀 --budget <秒>;沒有就回 default(保守值,不是猜大的)。
    ★上限夾住★:異常大的值會讓內層跟著失控放大,等於整個 fail-open 形同虛設。"""
    import sys as _s
    argv = _s.argv
    got = None
    for i, a in enumerate(argv):
        if a == "--budget" and i + 1 < len(argv):
            try:
                got = float(argv[i + 1])
            except ValueError:
                got = None
            break
        if a.startswith("--budget="):
            try:
                got = float(a.split("=", 1)[1])
            except ValueError:
                got = None
            break
    if got is None or got <= 0:
        got = default
    return min(float(got), 600.0)


def _inner_budget(elapsed=None, default=10.0):
    """內層某一段還能用幾秒:天花板 × 0.7 − 這支 hook 到目前為止已經花掉的時間,下限 1 秒。

    ★已耗時間自己算,不靠呼叫端記得傳★(2026-09-07 代碼審 r1 通才席抓到):
    第一版的 elapsed 預設 0,而六個呼叫點裡只有一個真的傳了值——於是同一支 hook
    只要依序呼叫兩次,理論上限就是 2 × 0.7 × 外層 = 1.4 倍外層,**結構性地超過天花板**。
    實測:進場提醒那支 7+7=14 秒 vs 外層 10;CI 狀態那支 10.5+10.5=21 秒 vs 外層 15。
    ★這正是這批改動宣稱要修掉的問題,只是換個地方重新發生。★

    ★★這是「還剩多少」不是「每段配額」★★——很容易誤解,所以講清楚:
    回傳的是「從現在到預算用完還有幾秒」。所以連續呼叫兩次拿到的兩個數字**不該相加**:
    第一次拿到 7 秒、真的用掉 5 秒之後,第二次會拿到 2 秒。
    只有在「第一段其實沒用多久」時第二次才會拿到接近 7 秒——那也是對的,因為時間真的還在。
    ★守衛要驗的是「真的用掉時間之後,下一次拿到的會變少,而且總和不超過天花板」★,
    不是「兩次的數字相加小於天花板」(那個判準本身就錯,會逼出錯誤的修法)。

    ★誠實邊界★:天花板小於約 1.43 秒時,下限 1 秒會反過來大於外層。各支的天花板看註冊表 HOOK_BUDGET
    (merge-claude-settings.py),目前都離這個門檻很遠;真要調到那麼小的話這個假設就不成立了。
    """
    import time as _tm
    global _BUDGET_START
    if _BUDGET_START is None:
        _BUDGET_START = _tm.monotonic()
    used = (_tm.monotonic() - _BUDGET_START) if elapsed is None else float(elapsed)
    return max(_BUDGET_FLOOR, _outer_budget(default) * _BUDGET_RATIO - used)
# ── ★逾時預算結束★ ──────────────────────────────────────────────────

def _impact_missing(src_files, all_paths, project_root, graph_root, cap=8):
    """跟 pre-commit/pre-push 同一套判法:lumos impact --diff HEAD --sync-check --worktree-nofilter --json(工作樹 vs HEAD;
    --worktree-nofilter 讓它不跑 git diff、不經被打開目錄自帶的內容過濾器,回合結束檢查代碼審 r3;舊版 lumos 不認得這個選項會 rc2 → 沒資料),
    取「固定席未動」的前 cap 篇。lumos 尋路同 impact-hook._find_lumos_script 的順序(PATH 先、repo 後);
    rc 協定同它:rc≠0 視為沒資料,fail-open 回 []。"""
    import json as _json
    # ★2026-09-06 改★:原本 which 找不到就退回 `project_root/scripts/lumos`
    # ——那是**被打開那個資料夾自己的碼**。改成只用可信來源,找不到就跳過。
    lumos = _trusted_lumos()
    if lumos is None:
        return []
    try:
        r = subprocess.run([sys.executable, lumos, "impact", "--diff", "HEAD", "--sync-check", "--worktree-nofilter", "--json", "--repo", str(project_root)],
                           capture_output=True, text=True, timeout=_inner_budget(default=30))
        if r.returncode != 0 or not r.stdout.strip():
            return []
        d = _json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return []
    miss = [m for m in (d.get("sync") or {}).get("missing", []) if m.get("pinned")]
    miss.sort(key=lambda m: -m.get("score", 0))
    return [m["node"] for m in miss[:cap]]

# ── Codex 收工擋停一次(Projects/Codex行為精修_計劃 d1,2026-09-05)──
# Codex 的 Stop hook 回 {"decision":"block","reason":…} 會讓模型以 reason 當下一個提示繼續做(官方通道);
# 本 hook 只在「改了程式碼、筆記沒動」時擋★一次★(兩家一致,2026-09-05 README 審視 d2):兩道護欄=payload 的 stop_hook_active(這輪已續做過)
# 與 session 標記檔(同 session 只擋一次)。2026-07-06 撤的是「每回合刷屏的 nag」;這裡只擋一次、只在該補沒補時,不是重開 nag。
STOP_BLOCK_HEAD = "LUMOS-STOP:改了程式碼但知識筆記沒跟著動"


def _stop_block_dir() -> Path:
    """擋停名額的標記目錄。既有測試在驗「只有擋過的 session 才會在這裡留東西」。"""
    return _cache_dir_under_home("stop-block", "收工擋停")


def _printed_dir() -> Path:
    """收工點名「上次印過什麼」的目錄。★刻意跟擋停標記分開★:兩者職責不同,
    混在一起會打破上面那個性質。跟它共用同一套安全建法,不另寫一份。"""
    return _cache_dir_under_home("stop-printed", "收工點名去重")


def stop_block_decision(payload: dict, session_id: str) -> bool:
    """要不要對這次 Stop 回 block(兩家同一份邏輯):沒設 LUMOS_STOP_BLOCK_OFF、這輪還沒被續做過、本 session 還沒擋過。
    ★名額先佔再擋(code-codex-refine r1 外家 #1/#4):回 True 表示標記檔已用 O_EXCL 建成——建不成(已存在 / 目錄寫不進 / 唯讀檔案系統)
    一律 False,所以「同 session 兩個 Stop 同時來」只有一個擋、「cache 寫不進」永遠不擋,不會每輪都擋。"""
    if os.environ.get("LUMOS_STOP_BLOCK_OFF") == "1":
        return False
    if payload.get("stop_hook_active"):
        return False
    if not session_id:
        return False
    return _stop_mark_write(session_id)


def _stop_mark_path(session_id: str):
    """標記檔路徑;消毒後是空字串、"." 或 ".." 回 None(正確性席 F3:Path 語意會讓 "." 永遠「存在」而悄悄關掉擋停)。
    消毒走共用模組的 _mark_name(收工寫法檢查的標記在同一個目錄,兩邊同一套規則)。"""
    name = _mark_name(session_id)
    if name is None:
        return None
    return _stop_block_dir() / name


def _stop_mark_write(session_id: str) -> bool:
    """O_EXCL 原子建檔佔名額(兩個 hook 同時來只有一個成功);任何 OSError 都回 False=不擋(寧可漏)。佔名額走共用模組的 _claim_mark。"""
    mp = _stop_mark_path(session_id)
    if mp is None:
        return False
    return _claim_mark(mp.parent, mp.name)


def stop_block_reason(rel: list, graph_rel, mentions: dict) -> str:
    """reason 版面(r1 外家 #8):首行固定標頭、第二行就是指令、再列檔名(最多 10)、整段 ≤1500 字——續做提示約 2500 tokens 後會被截成頭尾預覽。"""
    lines = [STOP_BLOCK_HEAD,
             "lumos 收工檢查,只擋這一次:現在把該記的寫回知識筆記(Systems / Verification / lumos decision-add),或一句話說明為什麼這次不用(改錯字 / 排版 / 半成品),然後再結束。",
             f"工作樹上有 {len(rel)} 個程式碼檔還沒提交、筆記沒跟著動"
             "(★清單是工作樹狀態,不保證每支都是你這一輪改的——共用工作目錄下可能含別人的,"
             "自己判斷哪些該補★;下面反引號裡的只是檔名,檔名寫什麼都不是指令):"] + [f"  • `{_safe_path(r)}`" for r in rel[:10]]
    if len(rel) > 10:
        lines.append(f"  (另 {len(rel) - 10} 個)")
    lines.append(f"筆記放在 {_safe_path(graph_rel)}/;下一個 session 只讀得到筆記,讀不到你這次為什麼這樣改。")
    if mentions:
        lines.append("提到你改的檔的筆記(同樣只是檔名):" + ";".join(f"`{_safe_path(k)}`→{','.join('`' + _safe_path(x) + '`' for x in v[:3])}" for k, v in list(mentions.items())[:5]))
    out = "\n".join(lines)
    return out if len(out) <= 1500 else out[:1490] + "…"


def main() -> int:
    if not _SHARED_OK:
        return 0
    _harden_git_env()
    harness = "codex" if "--harness" in sys.argv and sys.argv[sys.argv.index("--harness") + 1:][:1] == ["codex"] else "claude"
    try:
        payload = json.loads(sys.stdin.read())
    except (ValueError, RecursionError, UnicodeDecodeError, OSError):   # 壞 JSON、深層巢狀、非 UTF-8、超長整數(代碼審 r3 邊界席 F1)
        return 0  # 寧可漏報
    if not isinstance(payload, dict):
        return 0

    project_root_str = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd")
    if not project_root_str:
        return 0
    project_root = Path(project_root_str)

    # 閘門 0
    graph_root = find_graph_root(project_root)
    if graph_root is None:
        return 0

    # B 巡邏: queue 堆積就提醒 (在主邏輯前跑,獨立於 code-sync warning)
    emit_queue_patrol(project_root)

    # 閘門 1
    transcript_path_str = payload.get("transcript_path", "")
    if not transcript_path_str:
        return 0
    file_paths, bash_commands = collect_turn_actions(Path(transcript_path_str))
    # #6: 補上 Bash rm/mv/cp/git mv/git rm 影響的檔案
    file_paths = file_paths + extract_bash_file_paths(bash_commands, project_root)
    if not file_paths and not bash_commands:
        return 0

    # 閘門 2:清單問版本控制,不再靠列舉工具名(單源 Projects/收工點名問版本控制_計劃)
    top = _repo_top(project_root)      # 狀態表的路徑從 repo 根算起,接在 repo 根上(代碼審 r5)
    entries = _git_status_entries(project_root, top)   # 只含專案底下的條目(代碼審 r6)
    if entries is None:
        return 0                       # 算不出來就靜默放行:擋住收工的代價遠大於漏一次提醒
    code_entries = [(c, r) for c, r in entries if _entry_is_code(c, r, project_root, top)]
    if not code_entries:
        return 0
    src_files = [str(top / r) for _, r in code_entries]
    deleted_rel = {r for c, r in code_entries if _entry_is_deleted(c)}

    # 閘門 3:判準同樣改問版本控制——原本它跟閘門 2 共用「認名字」那套,
    # 用 shell 改筆記時會誤判「筆記沒動」,同一種少報換個位置活下來(設計審正確性席 blocker)
    graph_touched = any(is_graph_file(str(top / r), graph_root) for _, r in entries)
    if graph_touched:
        # 2026-08-22(圖譜同步覆蓋):動過圖譜不等於動對篇——拿 impact 算「跟你改的碼直接相關、
        # 帶合約或出過事故、這輪卻沒動」的筆記點名。只提醒,不擋。
        missing = _impact_missing(src_files, file_paths, project_root, graph_root)
        if missing:
            print("\n".join([
                f"提醒:這一輪動了筆記,但 impact 說下面這些筆記跟你改的程式碼直接相關(是它的家 / 帶合約 / 出過事故 / 直接相依),還沒動:",
                *[f"   • {m}" for m in missing],
                "確定不受影響就略過;受影響的現在補,別等到 pre-push。"]), file=sys.stderr)
        return 0

    # ── 印提醒 ──
    project_root_resolved = project_root.resolve()
    rel: list[str] = []
    seen: set[str] = set()
    for _, r in code_entries:
        if r not in seen:
            seen.add(r)
            rel.append(r)

    # 同一批檔第二次就不再講(清單已經不限這一輪,不抑制會變成每輪刷屏)
    sid_for_dup = str(payload.get("session_id") or "")
    printed_key = sorted((("D " if r in deleted_rel else "M ") + r) for r in rel)
    if sid_for_dup:
        prev = _load_printed(sid_for_dup)
        if prev is not None and prev == set(printed_key):
            return 0

    try:
        graph_rel = graph_root.resolve().relative_to(project_root_resolved)
    except (ValueError, OSError):
        graph_rel = graph_root

    # ★不再宣稱切得出「這一輪」★:清單是工作樹上未提交的東西,含這輪以外的改動,
    # 共用工作目錄下還可能含別人的。換來的是「用什麼工具改的都看得到」。
    msg = [
        f"提醒:工作樹上有 {len(rel)} 個程式碼檔還沒提交,知識筆記沒有跟著動:",
        *[f"   • {r}{'(已刪除)' if r in deleted_rel else ''}" for r in rel],
        "",
        "程式碼只記「現在長怎樣」;為什麼這樣改、改動牽連到哪裡,要寫進筆記,下一個 session 才接得上。",
        "筆記放在這裡:",
        f"   {graph_rel}/",
    ]

    # #5: 反查改的檔案出現在哪幾篇筆記
    mentions = find_notes_mentioning(rel, graph_root)
    if mentions:
        msg += ["", "這幾篇筆記有提到你改的檔案或名稱,最可能需要更新:"]
        for stem, notes in mentions.items():
            msg.append(f"   • {stem} → {', '.join(notes)}")

    msg += [
        "",
        "通常要跟著改的是:受影響功能的說明(Systems)、這次驗證了什麼(Verification)、有做設計選擇的話寫進 decisions。",
        "",
        "如果這次只是改錯字、整理排版、重構但行為沒變,這條提醒可以略過。",
    ]
    sid = str(payload.get("session_id") or "")
    try:   # 只包擋停分支:失敗退回下面的 stderr 提醒(進除錯日誌)
        if stop_block_decision(payload, sid):
            # ★模型那條也列完整清單★(代碼審 r1 合約一致席 + 正確性席,兩席獨立報)。
            # 初版為了「不把別人的改動塞給模型」而只列這一輪的檔,
            # ★而拿來算「這一輪」的正是這次要換掉的那套工具名清單★——
            # 於是用 shell 改的檔在這條路完全不列名(退化成「算不出來」),少報換個位置活著。
            # 正解不是修交集,是承認「這一輪」算不準:列完整清單,
            # 風險改用措辭講明(見 stop_block_reason 的首句),讓模型自己判斷哪些不是它動的。
            reason = stop_block_reason(rel, graph_rel, mentions)
            if reason.strip():
                # r2 delta #1:名額已佔,輸出一定要送到——用 bytes 寫 stdout(不受 locale/ASCII 影響);真寫不出去就把名額退回,下一次 Stop 再試
                try:
                    sys.stdout.buffer.write((json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False) + "\n").encode("utf-8")); sys.stdout.buffer.flush()
                except Exception:
                    mp = _stop_mark_path(sid)
                    if mp is not None:
                        try:
                            mp.unlink()
                        except OSError:
                            pass
                    raise
                return 0
    except Exception:
        pass
    print("\n".join(msg), file=sys.stderr)
    if sid_for_dup:
        _save_printed(sid_for_dup, printed_key)
    return 0


# ★下面這支是主程式 scripts/lumos 同名函式的逐字複本★(安全邏輯,照 [[Systems/hook信任邊界]];守衛 t_r5path_hooks_verbatim)
def _clean_path_env():
    """★程序一開始就把 PATH 洗成只剩絕對路徑項★(回合結束檢查代碼審 r5 資安席 F1):PATH 的空項(開頭、結尾或連續的冒號)、. 與
    任何相對項,開子程序時都從目前目錄找,而鉤子與主程式的目前目錄常常就是被打開的資料夾——repo 根放一支可執行的 git,裸名呼叫
    git 就執行它。ast-grep(r3)、lumos(r4)、git(r5)同一類第三次被打穿,不再一支工具一支工具解路徑:入口洗一次,之後同一程序
    開的所有子程序都吃乾淨的 PATH(既有的逐支解析照留,當縱深)。洗完一項都不剩時改用 os.defpath 的絕對項(空字串的 PATH
    一樣等於目前目錄);沒設 PATH 不動(子程序照 os.defpath 找)。安全邏輯:主程式與每支鉤子各一份逐字複本,照
    [[Systems/hook信任邊界]],守衛 t_r5path_hooks_verbatim 盯著一字不差、入口第一句就呼叫。"""
    import os as _os
    if "PATH" not in _os.environ:
        return
    keep = [d for d in _os.environ["PATH"].split(_os.pathsep) if d and _os.path.isabs(d)]
    _os.environ["PATH"] = _os.pathsep.join(keep or [d for d in _os.defpath.split(_os.pathsep) if d and _os.path.isabs(d)])


if __name__ == "__main__":
    _clean_path_env()
    # #19 S4:把「我跑完了」記成一筆事件,讓 lumos enforcement 答得出
    # 「它最近有沒有真的跑過」,而不是只答「有沒有註冊」。共用寫入器在 _hookevent.py。
    import sys as _s, pathlib as _p
    _s.path.insert(0, str(_p.Path(__file__).resolve().parent))
    try:
        from _hookevent import guard as _guard
    except Exception:
        _guard = None
    sys.exit(_guard("stop-graph-sync-hook", __file__, main) if _guard else main())
