#!/usr/bin/env python3
"""PreToolUse hook: 主動影響幅度偵測 (Task 9 — 過濾 + 呼叫原語 + rc 處理)

攔截 Edit/Write/MultiEdit → 過濾(只 code 副檔名) → subprocess 呼叫
`lumos impact --file <path> --repo <repo> --json` → 依 rc 協定處理。

rc 協定:
  rc 0   = 成功 (影響集有/無皆算,json 照出)
  rc 3   = vault 找不到 → 印一行 debug,不注入,放行
  其他非 0 = 內部錯 → fail-open 純靜默放行

TTL 冷卻窗 / additionalContext 注入 → Task 10/11 實作。
Task 9 只做:過濾 + 呼叫 + 拿到 rc/json。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
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

EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}


def extract_path(payload: dict) -> str | None:
    """從 hook payload 的 tool_input.file_path 巢狀 dict 取路徑。

    r8-F9 / r9-F8 說明:file_path 在 tool_input 巢狀 dict 內,非頂層。
    MultiEdit 亦同。
    """
    return (payload.get("tool_input") or {}).get("file_path")


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


def hook_decide(payload: dict) -> str | None:
    """過濾邏輯:決定是否對此 payload 觸發 lumos impact。

    回傳:
      None   → 放行(非 code / 排除路徑)
      str    → 要送給 lumos impact 的 file_path(非空字串)

    此函式設計為可獨立 import 測試(不依賴 stdin/subprocess)。
    """
    file_path = extract_path(payload)
    if not file_path:
        return None
    p = Path(file_path)
    if p.suffix.lower() not in CODE_EXTS:
        return None
    if _is_excluded_path(file_path):
        return None
    return file_path


def _find_lumos_script() -> str | None:
    """找到 lumos CLI 腳本的絕對路徑(同 repo scripts/lumos)。"""
    # hook 所在目錄是 scripts/hooks/claude/,往上 3 層是 repo root
    hook_dir = Path(__file__).resolve().parent
    repo_root = hook_dir.parent.parent.parent
    candidate = repo_root / "scripts" / "lumos"
    if candidate.is_file():
        return str(candidate)
    return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return 0  # fail-open

    # 只處理 Edit/Write/MultiEdit
    tool_name = payload.get("tool_name", "")
    if tool_name not in EDIT_TOOLS:
        return 0

    file_path = hook_decide(payload)
    if file_path is None:
        return 0  # 放行:非 code 或排除路徑

    # repo root: 優先 $CLAUDE_PROJECT_DIR,fallback payload cwd
    # (同 check-graph-sync.py:348-355)
    repo = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd", "")
    if not repo:
        return 0  # fail-open

    # 絕對路徑:若 file_path 是相對路徑,補上 repo
    if not Path(file_path).is_absolute():
        file_path_abs = str(Path(repo) / file_path)
    else:
        file_path_abs = file_path

    lumos = _find_lumos_script()
    if lumos is None:
        return 0  # lumos 不在 PATH/repo → fail-open

    # 呼叫 lumos impact --file <path> --repo <repo> --json
    try:
        result = subprocess.run(
            [sys.executable, lumos, "impact", "--file", file_path_abs, "--repo", repo, "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return 0  # fail-open

    rc = result.returncode

    if rc == 3:
        # vault 找不到 → 印一行 debug,不注入,放行
        print(
            f"[impact-hook] vault 未找到 (rc=3)。非圖譜專案或 --repo={repo} 路徑下無 docs/*-knowledge/。",
            file=sys.stderr,
        )
        return 0

    if rc != 0:
        # 其他非 0 → fail-open 純靜默
        return 0

    # rc == 0: 取得 json 結果
    # Task 11 在此注入 additionalContext;Task 9 只完成到「拿到 rc/json」
    try:
        impact_data = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        impact_data = None

    # 空影響集不注入(Task 11 處理注入;此處預留結構)
    if not impact_data:
        return 0

    direct = impact_data.get("direct", [])
    indirect = impact_data.get("indirect", [])
    if not direct and not indirect:
        return 0

    # Task 11 將在此完成 additionalContext 注入
    # Task 9 完成:過濾 + 呼叫 + rc 處理(rc0/rc3/其他)
    return 0


if __name__ == "__main__":
    sys.exit(main())
