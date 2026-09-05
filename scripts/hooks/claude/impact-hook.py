#!/usr/bin/env python3
"""PreToolUse hook: 主動影響幅度偵測 (Task 10 — TTL 冷卻窗)

攔截 Edit/Write/MultiEdit → 過濾(只 code 副檔名) → TTL 冷卻窗判定 →
subprocess 呼叫 `lumos impact --file <path> --repo <repo> --json` → 依 rc 協定處理。

rc 協定:
  rc 0   = 成功 (影響集有/無皆算,json 照出)
  rc 3   = vault 找不到 → 印一行 debug,不注入,放行
  其他非 0 = 內部錯 → fail-open 純靜默放行

additionalContext 注入 → Task 11 實作。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# === 觸發的原始碼副檔名 ===
# 同源:check-graph-sync.py(20 副檔名版)
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
# 同源:check-graph-sync.py EXCLUDE_PATH_CONTAINS / EXCLUDE_FILENAMES
EXCLUDE_PATH_CONTAINS = (
    "/docs/",            # 圖譜本身 + 一般文件
    "/node_modules/",
    "/bin/", "/obj/",
    "/.git/",
    "/dist/", "/build/",
    "/__pycache__/",
)
EXCLUDE_FILENAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
}

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "apply_patch"}   # apply_patch=Codex 改檔工具(Edit/Write 只是它的 matcher 別名)
# Codex 多檔 patch:最多算前 N 檔、總時間預算(hook 外層 30 秒);既有碼沒有「處理檔數」上限(cap_* 限的是查詢字串長度)
# ——Projects/Codex完全支援_計劃 S1(r2 通才 F2)
APPLY_PATCH_MAX_FILES = 5
APPLY_PATCH_BUDGET_SEC = 20.0
_PATCH_HDR_RE = re.compile(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+?)\s*$")


def extract_patch_paths(command: str) -> list[str]:
    """從 Codex apply_patch 的 patch 全文抽檔案路徑:`*** Add File:` / `*** Update File:` / `*** Delete File:` /
    `*** Move to:`(改名的新路徑,r1 邊界 F7)。去重、保序。不是 patch 文字 → []。"""
    if not isinstance(command, str) or "*** Begin Patch" not in command:
        return []
    out: list[str] = []
    for line in command.split("\n"):
        m = _PATCH_HDR_RE.match(line.strip())
        if m:
            fp = m.group(1).strip()
            if fp and fp not in out:
                out.append(fp)
    return out


def extract_paths(payload: dict) -> list[str]:
    """payload → 這次改動碰到的檔案清單。Claude(Edit/Write/MultiEdit):tool_input.file_path 一個;
    Codex(apply_patch):tool_input.command 是 patch 全文、沒有 file_path,解標頭(可多檔)。"""
    ti = payload.get("tool_input") or {}
    if payload.get("tool_name") == "apply_patch":
        return extract_patch_paths(ti.get("command", ""))
    fp = ti.get("file_path")
    return [fp] if fp else []


def extract_path(payload: dict) -> str | None:
    """從 hook payload 取「第一個」路徑(相容既有呼叫/測試;多檔用 extract_paths)。

    r8-F9 / r9-F8 說明:file_path 在 tool_input 巢狀 dict 內,非頂層。
    MultiEdit 亦同。
    """
    ps = extract_paths(payload)
    return ps[0] if ps else None


def _is_excluded_path(file_path: str) -> bool:
    """判斷路徑是否在排除清單(EXCLUDE_PATH_CONTAINS + EXCLUDE_FILENAMES)。"""
    norm = file_path.replace("\\", "/")
    # 確保路徑段比對加 leading slash 一致性
    if not norm.startswith("/"):
        norm_check = "/" + norm
    else:
        norm_check = norm
    for seg in EXCLUDE_PATH_CONTAINS:
        if seg in norm_check:
            return True
    p = Path(file_path)
    if p.name in EXCLUDE_FILENAMES:
        return True
    return False


def _shebang_is_code(abs_path: Path) -> bool:
    """無副檔名檔靠首行 shebang 入樣(主session鏡頭利用率_計劃 前置修正①:scripts/lumos、git hooks 原本永不入樣)。
    只讀前 128 bytes、包 try/except:二進位/不存在/讀不到 → False,現役 fail-open hook 不得因此炸。"""
    try:
        if not abs_path.is_file():
            return False
        with open(abs_path, "rb") as fh:
            head = fh.read(128)
    except OSError:
        return False
    return head.startswith(b"#!")   # 任何 shebang 都算(2026-09-05 四處同一條規則;之前這裡的清單跟另兩處都不一樣)


def hook_decide(payload: dict, repo: str | None = None) -> str | None:
    """過濾邏輯:決定是否對此 payload 觸發 lumos impact。

    回傳:
      None   → 放行(非 code / 排除路徑)
      str    → 要送給 lumos impact 的 file_path(非空字串)

    此函式設計為可獨立 import 測試(不依賴 stdin/subprocess)。
    repo 給了才做無副檔名 shebang 判定(相對路徑相對 repo 解;沒 repo 維持只看副檔名)。
    """
    file_path = extract_path(payload)
    return _decide_one(file_path, repo)


def _decide_one(file_path: str | None, repo: str | None = None) -> str | None:
    """單一路徑的過濾(hook_decide 的本體;多檔逐一套用)。"""
    if not file_path:
        return None
    p = Path(file_path)
    if p.suffix.lower() not in CODE_EXTS:
        if not (p.suffix == "" and repo):
            return None
        abs_path = p if p.is_absolute() else Path(repo) / p
        if not _shebang_is_code(abs_path):
            return None
    if _is_excluded_path(file_path):
        return None
    return file_path


def hook_decide_paths(payload: dict, repo: str | None = None) -> tuple[list[str], list[str]]:
    """多檔版:回 (要跑 impact 的路徑[最多 APPLY_PATCH_MAX_FILES], 超出只列名的路徑)。"""
    kept = [fp for fp in extract_paths(payload) if _decide_one(fp, repo)]
    return kept[:APPLY_PATCH_MAX_FILES], kept[APPLY_PATCH_MAX_FILES:]


def _ttl_marker_path(session_id: str, file_abs: str) -> Path:
    """標記檔路徑: <tmpdir>/lumos-impact-<session_id>/<sha1[:16]>。"""
    h = hashlib.sha1(file_abs.encode()).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"lumos-impact-{session_id}" / h


def _ttl_lazy_cleanup() -> None:
    """惰性清理: 刪 lumos-impact-* 下 mtime > 24h 的 session 目錄 (best-effort)。"""
    import shutil  # m-1: 提到函式頂,避免每次迭代 import
    try:
        tmp = Path(tempfile.gettempdir())
        cutoff = time.time() - 24 * 3600
        for d in tmp.iterdir():
            if d.name.startswith("lumos-impact-") and d.is_dir():
                try:
                    if d.stat().st_mtime < cutoff:
                        shutil.rmtree(str(d), ignore_errors=True)
                except OSError:
                    pass
    except OSError:
        pass


def _ttl_unmark(session_id: str, file_abs: str, token: str | None = None) -> None:
    """撤冷卻標記:判定當下已先寫(窗口不變寬,code-loop r1),最後沒注入就撤——零注入的 Edit 不開冷卻窗(前置修正②)。
    ★只撤自己寫的★:標記內容為「<ts> <token>」,token 不符就不動(code-loop r2 併發席:無條件 unlink 會抹掉另一次判定剛建立的合法冷卻窗)。"""
    if token is None:
        return   # 自己沒寫成標記(mark 失敗)就沒有東西可撤;不得退回無條件刪(r3 併發席)
    marker = _ttl_marker_path(session_id, file_abs)
    try:
        parts = marker.read_text(encoding="utf-8").split()
        if len(parts) < 2 or parts[1] != token:
            return
        marker.unlink()
    except (OSError, IndexError):
        pass


def _ttl_mark(session_id: str, file_abs: str) -> str | None:
    """寫冷卻標記,回擁有權 token(pid+隨機);內容「<ts> <token>」,舊讀取端只取第一欄。失敗回 None(best-effort)。"""
    import os as _os
    _ttl_lazy_cleanup()
    marker = _ttl_marker_path(session_id, file_abs)
    token = f"{_os.getpid()}-{_os.urandom(3).hex()}"
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(f"{time.time()} {token}", encoding="utf-8")
        return token
    except OSError:
        return None


def _ttl_should_inject(session_id: str, file_abs: str, ttl_sec: float, mark: bool = True) -> bool:
    """判定是否在 TTL 冷卻窗內。

    首次或距上次注入 >= ttl_sec → True(應注入);mark=True 時順手寫標記(舊語意),
    main 走 mark=False 再自己 _ttl_mark 取 token、沒注入用 token 撤(2026-09-04)。
    距上次注入 < ttl_sec → False(冷卻中,壓掉)。

    標記檔內容 = 「<time.time()> <token>」(舊格式只有數字,讀取端相容)。
    不用 mtime(避免 touch/rsync 誤動)。

    Args:
        session_id: hook payload 的 session_id(UUID)。
        file_abs: 被編輯的檔案絕對路徑。
        ttl_sec: 冷卻秒數。

    Returns:
        True = 應注入;False = 冷卻窗內壓掉。

    Race note (I-1): exists→read→write 非原子;並行呼叫最多多注入一次,
    不會造成資料損壞。此為 best-effort TTL,非嚴格 once 語意。
    """
    marker = _ttl_marker_path(session_id, file_abs)
    now = time.time()

    # 讀現有標記
    if marker.exists():
        try:
            content = marker.read_text(encoding="utf-8").strip()
            last_ts = float(content.split()[0])   # 內容「<ts> <token>」(r2 併發席);舊格式只有 ts 也相容
            if now - last_ts < ttl_sec:
                return False  # 冷卻窗內,壓掉
        except (ValueError, OSError, IndexError):   # 空檔/半途寫壞 → 視為過期(r3 邊界/通才席:IndexError 沒接會讓現役 hook 當掉,違反 fail-open)
            pass  # 壞標記 → 視為過期,重新注入

    # 首次或窗外。mark=True 維持舊語意(判定+寫一體,既有測試);main 走 mark=False,真的注入後才 _ttl_mark。
    if mark:
        _ttl_mark(session_id, file_abs)
    return True


def _backdate_marker(session_id: str, file_abs: str, seconds_ago: float) -> None:
    """測試輔助:把標記檔時間戳倒推 seconds_ago 秒。"""
    marker = _ttl_marker_path(session_id, file_abs)
    backdated = time.time() - seconds_ago
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(str(backdated), encoding="utf-8")
    except OSError:
        pass


def _find_lumos_script() -> str | None:
    """找到 lumos CLI 腳本的絕對路徑。

    優先用 shutil.which("lumos"):設計 §3 本就假設 PATH 呼叫,hook 複製到
    ~/.claude/hooks/ 後 repo-relative 猜測失效,which 是唯一可靠方式。
    which 找不到再 fallback 到 repo-relative(開發中 / 未安裝時兜底)。
    """
    import shutil
    # 1. 優先 PATH:安裝後 lumos 在 ~/.local/bin/lumos(或系統 PATH)
    which_result = shutil.which("lumos")
    if which_result is not None:
        return which_result
    # 2. Fallback:repo-relative(hook 仍在 repo 樹內時有效,如開發測試)
    hook_dir = Path(__file__).resolve().parent
    repo_root = hook_dir.parent.parent.parent
    candidate = repo_root / "scripts" / "lumos"
    if candidate.is_file():
        return str(candidate)
    return None


def extract_delta_query(payload: dict, cap_tokens: int = 512, cap_chars: int = 8000) -> str:
    """v1.1:從 tool_input 抽「這次改動的內容」當查詢詞(spec §3)。

    Edit = old_string+new_string(刪與增都算「碰到」);MultiEdit = 各 edit 串接;
    Write = content 全文。cap:512 distinct 空白分詞(CJK 連串視為一詞,罕觸頂)+ 字元上限兜底。
    prospective 整檔重建刻意省略:content trigger 已 delta-scoped(比對本查詢詞),
    新增/刪除的危險內容都在 delta 內,不需為觸發語意重建整檔。"""
    ti = payload.get("tool_input") or {}
    tool = payload.get("tool_name", "")
    parts: list[str] = []
    if tool == "Edit":
        parts = [str(ti.get("old_string") or ""), str(ti.get("new_string") or "")]
    elif tool == "MultiEdit":
        for e in (ti.get("edits") or []):
            if isinstance(e, dict):
                parts += [str(e.get("old_string") or ""), str(e.get("new_string") or "")]
    elif tool == "Write":
        parts = [str(ti.get("content") or "")]
    # 每段獨立配額(codex r1+r2 折入):先串接再整體截斷會讓「超長 old_string」吃掉整段 new;
    # 地板配額×多段再尾切又會吃掉後段 edit(r2 抓到的同類假陰性)——
    # 故:每段保底 300 字元、總量不再尾切(查詢只餵斷詞與 regex,尺寸無虞;512 token cap 照舊)。
    nz = [p for p in parts if p]
    per_part = max(300, cap_chars // max(1, len(nz)))
    q = " ".join(p[:per_part] for p in nz)
    toks = q.split()
    if len(set(toks)) > cap_tokens:
        seen: set[str] = set()
        kept: list[str] = []
        for tok in toks:
            if tok not in seen:
                seen.add(tok)
                if len(seen) > cap_tokens:
                    break
            kept.append(tok)
        q = " ".join(kept)
    return q


_INJECT_INSTRUCTION = (
    "動手前看一眼上面這些筆記:這次改動會不會影響到它們講的事?"
    "真的有關的就順手更新,不確定的先在筆記裡記一句,不相關的跳過。"
)


def build_additional_context(impact_data: dict) -> str:
    """把 impact_data 轉成人可讀的影響清單文字,尾加動手前分析指令。

    格式:
      直接關聯:
        ★INVARIANT★ Systems/A  (body-inline-code)
        Systems/B  (body-inline-code)
      間接關聯(hop N):
        Systems/C  via related [backlink]
      <指令文字>

    空 direct + 空 indirect → 不應呼叫此函式(呼叫者先守衛)。
    """
    lines: list[str] = []

    direct = impact_data.get("direct", [])
    indirect = impact_data.get("indirect", [])

    if direct:
        lines.append("直接提到這個檔的筆記:")
        for item in direct:
            node = item.get("node", "?")
            contract = item.get("contract")
            combo = item.get("combo", False)
            hit = item.get("hit", "")
            prefix = ""
            if contract:
                prefix = f"★{contract}★"
            if combo:
                prefix += "★COMBO★"
            if prefix:
                lines.append(f"  {prefix} {node}  ({hit})")
            else:
                lines.append(f"  {node}  ({hit})")

    if indirect:
        lines.append("透過連結間接牽到的筆記:")
        for item in indirect:
            node = item.get("node", "?")
            hop = item.get("hop", "?")
            via = item.get("via", "?")
            direction = item.get("direction", "")
            contract = item.get("contract")
            combo = item.get("combo", False)
            cross = item.get("cross_repo", False)
            prefix = ""
            if contract:
                prefix = f"★{contract}★"
            if combo:
                prefix += "★COMBO★"
            suffix = ""
            if cross:
                suffix = " [跨repo葉,不展開]"
            dir_tag = f" [{direction}]" if direction else ""
            if prefix:
                lines.append(f"  hop{hop} {prefix} {node}  via {via}{dir_tag}{suffix}")
            else:
                lines.append(f"  hop{hop} {node}  via {via}{dir_tag}{suffix}")

    incidents = impact_data.get("incidents", [])
    if incidents:
        lines.append("這個檔過去出過的事故(改之前先看):")
        for item in incidents:
            node = item.get("node", "?")
            matched_by = item.get("matched_by", "?")
            contract = item.get("contract")
            combo = item.get("combo", False)
            prefix = ""
            if contract:
                prefix = f"★{contract}★"
            if combo:
                prefix += "★COMBO★"
            if prefix:
                lines.append(f"  {prefix} {node}  (matched_by: {matched_by})")
            else:
                lines.append(f"  {node}  (matched_by: {matched_by})")

    lines.append("")
    lines.append(_INJECT_INSTRUCTION)
    return "\n".join(lines)


def build_ranked_context(data: dict) -> str:
    """v1.1:把 ranked 輸出({results,meta})轉成降噪清單文字。固定席在前(合約/事故),
    非固定帶分數;截斷數照 meta 標注。尾附棧別效能追問(若 lumos 輸出帶 stack_questions——
    單源在 scripts/lumos 的 _STACK_PERF_QUESTIONS,本 hook 只格式化不持有內容)。"""
    lines: list[str] = []
    res = data.get("results", [])
    meta = data.get("meta", {})
    pins = [x for x in res if x.get("pinned")]
    free = [x for x in res if not x.get("pinned") and not x.get("rescued")]
    rescued = [x for x in res if x.get("rescued")]
    if pins:
        lines.append(f"必看——這 {len(pins)} 篇帶著不能破壞的合約或出過事故:")
        for x in pins:
            mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
            ct = f" ★{x['contract']}★" if x.get("contract") else ""
            mb = f"  (trigger: {x['matched_by']})" if x.get("matched_by") else ""
            # about_code 語意欄位命中(工具清單 #9):讀 about_hit(只在 True 時存在),不碰既有 hit 來源標記
            ab = "★關於★" if x.get("about_hit") else ""
            lines.append(f"  {ab}{mk}{ct} {x.get('node','?')}{mb}")
    if free:
        lines.append(f"可能相關的 {len(free)} 篇(依關聯度排序):")
        for x in free:
            mk = {"direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
            lines.append(f"  {x.get('score',0):.2f} {mk} {x.get('node','?')}")
    if rescued:
        # R1 直連保底(plan:hook必看召回修復):分數不過閾但為僅有的直連節點——信心層級不同於排序席
        lines.append(f"另外 {len(rescued)} 篇分數不高但直接提到這個檔,一併列出:")
        for x in rescued:
            hit = f"/{x['hit']}" if x.get("hit") == "basename-match" else ""
            lines.append(f"  {x.get('score',0):.2f} 直接{hit} {x.get('node','?')}")
    if meta.get("truncated"):
        lines.append(f"  (+{meta['truncated']} 條低分截斷,沒列出來)")
    # pin-denoise-a-v4:參考道(JSON 獨立頂層鍵;.get 條件鍵慣例——knob=0 時鍵不存在)
    lane = data.get("lane", [])
    if lane:
        lines.append(f"守衛面參考——這 {len(lane)} 篇是軟標記樞紐,跟每支檔都近,未被本次改動直接證實相關:")
        for x in lane:
            lines.append(f"  {x.get('score',0):.2f} hop{x.get('hop','?')} {x.get('node','?')}")
        if meta.get("lane_truncated"):
            lines.append(f"  (另有 {meta['lane_truncated']} 條守衛面參考未列出)")
    for stk, qs in (data.get("stack_questions") or {}).items():
        lines.append(f"[{stk} 效能檢核——動手時順答這幾個問題]")
        for q in qs:
            lines.append(f"  - {q}")
    lines.append("")
    # 收尾指令只在真的列了節點時附(單 reviewer 終審 minor:僅檢核問題時
    # 「判上列節點」答非所問,會弱化對提問的聚焦——檢核段標題已自帶指令)
    if res or lane:
        lines.append(_INJECT_INSTRUCTION)
    return "\n".join(lines)


def inject_ranked_context(data: dict) -> bool:
    """ranked 版注入:results/stack_questions/lane 皆空 → 不輸出(lane-only 的題也要注入,v4 Codex f2)。"""
    if not data.get("results") and not data.get("stack_questions") and not data.get("lane"):
        return False
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": build_ranked_context(data),
    }}, ensure_ascii=False))
    return True


def inject_additional_context(impact_data: dict) -> None:
    """非空影響集 → 印 hookSpecificOutput JSON 到 stdout;空集合 → 不輸出。

    永不 block、永不改 permissionDecision。

    注意 (r5-F2):此格式是 Claude Code 官方 PreToolUse additionalContext 能力。
    上線後請用 `claude --debug` 實測注入時機(PreToolUse 的 additionalContext 注在
    tool result 旁);若版本行為有變,可退回 stderr 備援(現有 hook 已證此路可行)。
    """
    direct = impact_data.get("direct", [])
    indirect = impact_data.get("indirect", [])
    incidents = impact_data.get("incidents", [])
    if not direct and not indirect and not incidents:
        return  # 空影響集(direct+indirect+incidents 皆空):不注入

    ctx = build_additional_context(impact_data)
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": ctx,
        }
    }
    print(json.dumps(output, ensure_ascii=False))


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return 0  # fail-open

    # 只處理 Edit/Write/MultiEdit
    tool_name = payload.get("tool_name", "")
    if tool_name not in EDIT_TOOLS:
        return 0

    # repo root: 優先 $CLAUDE_PROJECT_DIR,fallback payload cwd(同 check-graph-sync.py:348-355)
    # ★先算 repo 再 hook_decide★:無副檔名檔的 shebang 判定要用 repo 解相對路徑(前置修正①)
    repo = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd", "")
    paths, overflow = hook_decide_paths(payload, repo=repo or None)
    if not paths:
        return 0  # 放行:非 code 或排除路徑
    if not repo:
        return 0  # fail-open
    lumos = _find_lumos_script()
    if lumos is None:
        return 0  # lumos 不在 PATH/repo → fail-open
    # 多檔(Codex apply_patch):逐檔算、合併輸出;總預算 APPLY_PATCH_BUDGET_SEC,超預算後面的只列名
    session_id = payload.get("session_id", "")
    t0 = time.monotonic()
    chunks: list[str] = []
    skipped: list[str] = list(overflow)
    for i, fp in enumerate(paths):
        left = APPLY_PATCH_BUDGET_SEC - (time.monotonic() - t0)
        if i > 0 and left < 3:
            skipped.extend(paths[i:])
            break
        # 單檔(Claude Edit/Write 或只碰一檔的 patch)維持舊的固定 30 秒(逐字等價;code-codex-s1 r1 單reviewer F1);
        # 多檔才用總預算切每檔的 timeout
        tmo = 30.0 if len(paths) == 1 else min(30.0, max(3.0, left))
        ctx = _impact_for_file(payload, repo, fp, session_id, lumos, timeout=tmo)
        if ctx:
            chunks.append(ctx)
    if skipped:
        chunks.append("(多檔 patch 只算了前 " + str(len(paths) - len([s for s in skipped if s in paths])) + " 檔,其餘只列名:" + ",".join(skipped[:10]) + ")")
    if not chunks or all(c.startswith("(多檔") for c in chunks):
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": "\n\n".join(chunks),
    }}, ensure_ascii=False))
    return 0


def _impact_for_file(payload: dict, repo: str, file_path: str, session_id: str, lumos: str, timeout: float = 30.0) -> str | None:
    """單檔:TTL 冷卻窗 → 叫 lumos impact → 回可注入的文字(None=不注入)。內容與舊 main 逐字等價,只是不直接 print。"""

    # 絕對路徑:若 file_path 是相對路徑,補上 repo
    if not Path(file_path).is_absolute():
        file_path_abs = str(Path(repo) / file_path)
    else:
        file_path_abs = file_path

    # TTL 冷卻窗:讀 .lumos/impact.json 的 ttl_min(預設 20min)
    if session_id:
        ttl_min = 20  # 預設
        try:
            impact_cfg_path = Path(repo) / ".lumos" / "impact.json"
            if impact_cfg_path.is_file():
                cfg = json.loads(impact_cfg_path.read_text(encoding="utf-8"))
                ttl_raw = cfg.get("ttl_min", 20)
                if isinstance(ttl_raw, (int, float)) and not isinstance(ttl_raw, bool):
                    ttl_min = max(1, int(ttl_raw))  # m-4: 截斷兜底,防 0.5 → 0 → TTL 恆觸發
        except (OSError, json.JSONDecodeError, ValueError):
            pass

        in_cooldown = not _ttl_should_inject(session_id, file_path_abs, ttl_sec=ttl_min * 60, mark=False)
        ttl_token = _ttl_mark(session_id, file_path_abs) if not in_cooldown else None   # 判定後立刻寫(窗口同舊版);沒注入再用 token 撤
    else:
        in_cooldown = False
        ttl_token = None

    # v1.1(2026-07-11,goldset §6 全過後轉正):
    # 窗外 → ranked 降噪版(固定席+top-8,delta 當查詢詞);
    # 窗內 → --incidents-only 快速路(只跑事故比對——安全面每次都看,重型 BFS 降頻)。
    delta_q = extract_delta_query(payload)
    stdin_payload = json.dumps({"query": delta_q, "prospective": {}}, ensure_ascii=False)
    cmd = [sys.executable, lumos, "impact", "--file", file_path_abs, "--repo", repo,
           "--ranked", "--stdin-payload", "--json"]
    if in_cooldown:
        cmd.append("--incidents-only")
    try:
        result = subprocess.run(
            cmd,
            input=stdin_payload,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        if session_id and not in_cooldown:
            _ttl_unmark(session_id, file_path_abs, ttl_token)
        return None  # fail-open

    rc = result.returncode

    if rc != 0 and session_id and not in_cooldown:
        _ttl_unmark(session_id, file_path_abs, ttl_token)   # 沒注入不開冷卻窗
    if rc == 3:
        # vault 找不到 → 印一行 debug,不注入,放行
        print(
            f"[impact-hook] vault 未找到 (rc=3)。非圖譜專案或 --repo={repo} 路徑下無 docs/*-knowledge/。",
            file=sys.stderr,
        )
        return None

    if rc != 0:
        # 其他非 0 → fail-open 純靜默
        return None

    # rc == 0: ranked schema {file, results, meta}
    try:
        impact_data = json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, ValueError, IndexError):
        impact_data = None
    if not impact_data:
        if session_id and not in_cooldown:
            _ttl_unmark(session_id, file_path_abs, ttl_token)
        return None
    # 判空與 inject_ranked_context 同一條:results/stack_questions/lane 皆空 → 不注入(lane-only 也注入)
    has = impact_data.get("results") or impact_data.get("stack_questions") or impact_data.get("lane")
    ctx = build_ranked_context(impact_data) if has else ""
    if not ctx.strip():
        if session_id and not in_cooldown:
            _ttl_unmark(session_id, file_path_abs, ttl_token)   # 零注入不開冷卻窗(前置修正②);標記在判定當下已寫,這裡只撤
        return None
    return ctx


if __name__ == "__main__":
    sys.exit(main())
