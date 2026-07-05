#!/usr/bin/env python3
"""Stop hook: code-loop 必用守衛 nag 注入 (Task 3)

Claude Code Stop 事件末呼叫。
判定式:tier=high(pitfalls --diff) AND 無有效 code-loop 收斂 AND 無 skip-marker
  → blocked=True → 注入 nag(additionalContext,不擋回合)。
  → blocked=False → 無輸出,靜默退出 0。

fail-open:lumos 缺席/非 git/非圖譜/subprocess 例外 → 靜默 exit 0 不注入。
絕不輸出 block decision;Stop event 分不出做完/中途,擋會每回合卡死。

設計 §1:Stop hook 只注入不擋。
C1 教訓:lumos 用 shutil.which("lumos") 找,hook 複製到 ~/.claude/hooks 後 repo-relative 失效。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _find_lumos_script() -> str | None:
    """找到 lumos CLI 腳本絕對路徑。

    優先用 shutil.which("lumos"):安裝後 hook 複製到 ~/.claude/hooks/,repo-relative 失效。
    fallback 到 repo-relative(開發/未安裝時兜底)。
    """
    import shutil
    which_result = shutil.which("lumos")
    if which_result is not None:
        return which_result
    # fallback: repo-relative(hook 仍在 repo 樹內時)
    hook_dir = Path(__file__).resolve().parent
    repo_root = hook_dir.parent.parent.parent
    candidate = repo_root / "scripts" / "lumos"
    if candidate.is_file():
        return str(candidate)
    return None


def _run_lumos_check(lumos: str, repo: str) -> str:
    """執行 lumos code-loop check --json --repo <repo>,回傳 stdout 字串。

    拋出例外時讓呼叫者 fail-open 處理。
    """
    result = subprocess.run(
        [sys.executable, lumos, "code-loop", "check", "--json", "--repo", repo],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout


def should_inject(verdict: dict) -> bool:
    """判定是否需要注入 nag。

    verdict["blocked"] == True → True;
    其他(False / 缺欄位) → False(fail-open)。
    """
    return verdict.get("blocked") is True


def build_nag(verdict: dict) -> str:
    """把 verdict 轉成 nag 文字。

    格式:⚠ 本分支有 tier=high 代碼未過 code-loop;push 前必須跑
          lumos-code-loop 或 lumos code-loop skip --note "<理由>"。
          <reason>(若有)
    """
    lines = [
        "⚠ 本分支有 tier=high 代碼未過 code-loop;",
        "push 前必須跑 lumos-code-loop 或 lumos code-loop skip --note \"<理由>\"。",
    ]
    reason = verdict.get("reason")
    if reason:
        lines.append(f"({reason})")
    return "\n".join(lines)


def main() -> int:
    # 讀 stdin payload
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # fail-open

    # repo root: 優先 $CLAUDE_PROJECT_DIR,fallback payload cwd
    repo = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd", "")
    if not repo:
        return 0  # fail-open:沒有路徑

    # 找 lumos
    lumos = _find_lumos_script()
    if lumos is None:
        return 0  # fail-open:lumos 缺席

    # 呼叫 lumos code-loop check --json
    try:
        stdout_str = _run_lumos_check(lumos, repo)
    except Exception:
        return 0  # fail-open:subprocess 例外

    # 解析 verdict JSON
    try:
        verdict = json.loads(stdout_str)
    except (json.JSONDecodeError, ValueError):
        return 0  # fail-open:非預期輸出

    # 判定是否注入
    if not should_inject(verdict):
        return 0  # 不 blocked → 靜默

    # blocked → 注入 nag(additionalContext)
    nag = build_nag(verdict)
    output = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": nag,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0  # 永不 block 回合


if __name__ == "__main__":
    sys.exit(main())
