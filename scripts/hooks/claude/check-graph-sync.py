#!/usr/bin/env python3
"""全域 Stop hook: 提醒「程式碼改了但圖譜沒同步」。

只在當前專案有 docs/*-knowledge/ 或 docs/knowledge/ 時作用,否則完全闭嘴。
軟提醒 (stderr surface 給 Claude),不 block turn 結束。

四層閘門:
  0  圖譜不存在               → exit 0
  1  這 turn 沒改任何檔        → exit 0
  2  改的都是非原始碼/在 docs/ → exit 0
  3  這 turn 已動過圖譜        → exit 0
  否則                         → 印 stderr 提醒
"""
from __future__ import annotations
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

# === 觸發提醒的原始碼副檔名 ===
CODE_EXTS = {
    ".cs",                                                    # C# / .NET
    ".vue", ".js", ".ts", ".tsx", ".jsx", ".mjs",             # 前端
    ".sql",                                                   # DB migration
    ".py",                                                    # Python
    ".kt", ".kts",                                            # Kotlin / Compose
    ".java",                                                  # Java
    ".swift",                                                 # Swift
    ".go",                                                    # Go
    ".rs",                                                    # Rust
    ".c", ".cc", ".cpp", ".h", ".hpp",                        # C/C++
    ".sh", ".ps1",                                            # shell(2026-08-21 體檢 #7 補;四份清單由 t_code_exts_four_lists_agree 釘)
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
CODEX_TRANSCRIPT_VERSIONS = {"0.144.1"}
_CODEX_EXEC_CMD_RE = re.compile(r'"cmd"\s*:\s*"((?:[^"\\]|\\.)*)"')
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
        if obj.get("type") == "event_msg" and p.get("type") == "user_message":
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


def is_code_file(path: str, project_root: Path) -> bool:
    p = Path(path)
    if p.suffix.lower() not in CODE_EXTS:
        return False
    # 必須在 project_root 之下;避免改 ~/.claude/、/tmp 等外部檔案被誤判
    try:
        p.resolve().relative_to(project_root.resolve())
    except (ValueError, OSError):
        return False
    norm = str(p).replace("\\", "/")
    if any(seg in norm for seg in EXCLUDE_PATH_CONTAINS):
        return False
    if p.name in EXCLUDE_FILENAMES:
        return False
    return True


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


def _segment_command(cmd: str) -> list[str]:
    """切 shell chain (`&&` / `||` / `;` / `|`)。Quote-aware 不嚴格,但對常見 case 夠用。"""
    return [s.strip() for s in re.split(r'\s*(?:&&|\|\||;|\|)\s*', cmd) if s.strip()]


def _tokens_of(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        return []


def touched_graph_via_cli(bash_commands: list[str]) -> bool:
    """這 turn 是否真的「寫」過圖譜 (#2 收緊):
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
                capture_output=True, text=True, timeout=2,
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


def _impact_missing(src_files, all_paths, project_root, graph_root, cap=8):
    """跟 pre-commit/pre-push 同一條路:lumos impact --diff HEAD --sync-check --json(工作樹 vs HEAD),
    取「固定席未動」的前 cap 篇。lumos 尋路同 impact-hook._find_lumos_script 的順序(PATH 先、repo 後);
    rc 協定同它:rc≠0 視為沒資料,fail-open 回 []。"""
    import json as _json, shutil as _shutil
    lumos = _shutil.which("lumos") or (str(project_root / "scripts" / "lumos") if (project_root / "scripts" / "lumos").exists() else None)
    if lumos is None:
        return []
    try:
        r = subprocess.run([sys.executable, lumos, "impact", "--diff", "HEAD", "--sync-check", "--json", "--repo", str(project_root)],
                           capture_output=True, text=True, timeout=25)
        if r.returncode != 0 or not r.stdout.strip():
            return []
        d = _json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return []
    miss = [m for m in (d.get("sync") or {}).get("missing", []) if m.get("pinned")]
    miss.sort(key=lambda m: -m.get("score", 0))
    return [m["node"] for m in miss[:cap]]

def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return 0  # 寧可漏報

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

    # 閘門 2
    src_files = [f for f in file_paths if is_code_file(f, project_root)]
    if not src_files:
        return 0

    # 閘門 3
    graph_touched_via_edit = any(is_graph_file(f, graph_root) for f in file_paths)
    if graph_touched_via_edit or touched_graph_via_cli(bash_commands):
        # 2026-08-22(圖譜同步覆蓋):動過圖譜不等於動對篇——拿 impact 算「跟你改的碼直接相關、
        # 帶合約或出過事故、這輪卻沒動」的筆記點名。只提醒,不擋。
        missing = _impact_missing(src_files, file_paths, project_root, graph_root)
        if missing:
            print("\n".join([
                f"提醒:這一輪動了筆記,但 impact 說下面這些筆記跟你改的程式碼直接相關(合約 / 事故 / 直接相依),還沒動:",
                *[f"   • {m}" for m in missing],
                "確定不受影響就略過;受影響的現在補,別等到 pre-push。"]), file=sys.stderr)
        return 0

    # ── 印提醒 ──
    project_root_resolved = project_root.resolve()
    rel: list[str] = []
    seen: set[str] = set()
    for f in src_files:
        try:
            r = str(Path(f).resolve().relative_to(project_root_resolved))
        except (ValueError, OSError):
            r = f
        if r not in seen:
            seen.add(r)
            rel.append(r)

    try:
        graph_rel = graph_root.resolve().relative_to(project_root_resolved)
    except (ValueError, OSError):
        graph_rel = graph_root

    msg = [
        f"提醒:這一輪改了 {len(rel)} 個程式碼檔,但知識筆記沒有跟著動:",
        *[f"   • {r}" for r in rel],
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
    print("\n".join(msg), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
