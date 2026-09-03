#!/usr/bin/env python3
"""dispatch-lens-hook — Claude Code PreToolUse(matcher Agent)薄殼(Projects/派工鏡頭注入_計劃,2026-09-03)。

只做三件事:①派工詞裡逐行找 `LUMOS-IMPACT: <base>..<head>` ②subprocess 叫 `lumos dispatch-lens`
③把回傳文字接在派工詞尾端,經 updatedInput 送給子代理(additionalContext 實測到不了子代理)。
其餘判斷(範圍文法、base 主線可達、消毒、快取)全在 lumos 端。
永不 deny、永不改 permissionDecision;任何失敗都原樣放行、預設靜默(LUMOS_HOOK_DEBUG=1 才印 stderr)。
本檔在 ANCHOR_FILES 內:改它要 `lumos anchor approve --note`。
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

MARKER_RE = re.compile(r"^LUMOS-IMPACT:\s*(\S+)\s*$")
INNER_TIMEOUT = 45   # 外層 HOOK_ENTRIES 宣告 60;內層必須明顯小於外層(enforcement儀表板_計劃 事故)


def _debug(msg: str) -> None:
    if os.environ.get("LUMOS_HOOK_DEBUG"):
        print(f"[dispatch-lens-hook] {msg}", file=sys.stderr)


def find_marker(prompt: str) -> str | None:
    for line in prompt.split("\n"):
        m = MARKER_RE.match(line.strip())
        if m:
            return m.group(1)
    return None


def _find_lumos_script() -> str | None:
    import shutil
    w = shutil.which("lumos")
    if w:
        return w
    cand = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "lumos"
    return str(cand) if cand.is_file() else None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") != "Agent":
        return 0
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    prompt = tool_input.get("prompt")
    if not isinstance(prompt, str):
        return 0
    rng = find_marker(prompt)
    if rng is None:
        return 0
    repo = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd", "")
    if not repo:
        _debug("沒有 CLAUDE_PROJECT_DIR 也沒有 cwd,放行")
        return 0
    lumos = _find_lumos_script()
    if lumos is None:
        _debug("找不到 lumos,放行")
        return 0
    try:
        r = subprocess.run([sys.executable, lumos, "dispatch-lens", rng, "--repo", repo, "--json"],
                           capture_output=True, text=True, timeout=INNER_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as e:
        _debug(f"lumos dispatch-lens 失敗或超時({type(e).__name__}),放行")
        return 0
    if r.returncode != 0:
        _debug(f"lumos dispatch-lens rc={r.returncode}:{r.stderr.strip()[:200]},放行")
        return 0
    try:
        data = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        _debug("回傳讀不懂,放行")
        return 0
    text = data.get("text") if isinstance(data, dict) else None
    if not text:
        _debug(f"固定席 0 篇(pinned={data.get('pinned') if isinstance(data, dict) else '?'}),不注入")
        return 0
    new_input = dict(tool_input)
    new_input["prompt"] = prompt.rstrip("\n") + "\n\n" + text + "\n"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": new_input}},
                     ensure_ascii=False))
    _debug(f"已附 {data.get('shown')} 篇(固定席 {data.get('pinned')},主線 {data.get('mainline')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
