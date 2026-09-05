#!/usr/bin/env python3
"""dispatch-lens-hook — Claude Code PreToolUse(matcher Agent)薄殼(Projects/派工鏡頭注入_計劃,2026-09-03);
Codex 側掛 SubagentStart(Projects/Codex完全支援_計劃 d3,2026-09-04):叫 `lumos dispatch-lens --claim` 領一席 → additionalContext。

Claude 路徑只做三件事:①派工詞裡逐行找 `LUMOS-IMPACT: <base>..<head>` ②subprocess 叫 `lumos dispatch-lens`
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
SPEC_RE = re.compile(r"^LUMOS-SPEC:\s*(\S+)\s*$")   # 設計審用:給計劃筆記路徑(2026-09-05 第二輪審視 d2)
TIMEOUT_NOTE = "LUMOS-LENS:鏡頭超時,這次沒附節點({what});編排者:派工前先手跑一次 `lumos dispatch-lens {cmd}` 看它算不算得出來(diff 模式 20 分內有快取;{n} 個 commit 以上約 25 秒起,超過 45 秒就會像這次一樣放空)。"
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


def find_spec_marker(prompt: str) -> str | None:
    for line in prompt.split("\n"):
        m = SPEC_RE.match(line.strip())
        if m:
            return m.group(1)
    return None


def _emit_updated(tool_input: dict, prompt: str, text: str) -> None:
    new_input = dict(tool_input)
    new_input["prompt"] = prompt.rstrip("\n") + "\n\n" + text + "\n"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": new_input}}, ensure_ascii=False))


def _find_lumos_script() -> str | None:
    import shutil
    w = shutil.which("lumos")
    if w:
        return w
    cand = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "lumos"
    return str(cand) if cand.is_file() else None


def _claim_codex_seat(payload: dict) -> int:
    """Codex 側(SubagentStart):派工訊息對 hook 是密文、改不了(實驗 A),改由 `lumos dispatch-lens --claim`
    從派工前武裝的 armed 檔原子領一席,經 additionalContext 給子代理(實驗 5 證到得了)。
    沒武裝/過期/領完 → 什麼都不回(lumos 端判,這裡只轉送)。"""
    repo = payload.get("cwd", "") or os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not repo:
        _debug("Codex SubagentStart 沒有 cwd,放行")
        return 0
    lumos = _find_lumos_script()
    if lumos is None:
        _debug("找不到 lumos,放行")
        return 0
    try:
        r = subprocess.run([sys.executable, lumos, "dispatch-lens", "--claim", "--repo", repo, "--json"],
                           capture_output=True, text=True, timeout=INNER_TIMEOUT)
    except subprocess.TimeoutExpired:
        # 架構 r1 C:與 Claude 分支同語意——超時不再靜默,經 additionalContext 給一行固定說明
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": TIMEOUT_NOTE.format(what="(Codex 席:--claim)", cmd="--status", n=10)}}, ensure_ascii=False))
        _debug("lumos dispatch-lens --claim 超時,已附超時說明")
        return 0
    except OSError as e:
        _debug(f"lumos dispatch-lens --claim 失敗({type(e).__name__}),放行")
        return 0
    if r.returncode != 0:
        _debug(f"lumos dispatch-lens --claim rc={r.returncode}:{r.stderr.strip()[:200]},放行")
        return 0
    try:
        data = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        _debug("--claim 回傳讀不懂,放行")
        return 0
    text = data.get("text") if isinstance(data, dict) else None
    if not text:
        _debug(f"Codex 沒領到席({data.get('reason') if isinstance(data, dict) else '?'})")
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": text}},
                     ensure_ascii=False))
    return 0


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0
    if payload.get("hook_event_name") == "SubagentStart":
        return _claim_codex_seat(payload)
    if payload.get("tool_name") != "Agent":
        return 0
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    prompt = tool_input.get("prompt")
    if not isinstance(prompt, str):
        return 0
    rng = find_marker(prompt)
    spec = find_spec_marker(prompt) if rng is None else None
    if rng is None and spec is None:
        return 0
    repo = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd", "")
    if not repo:
        _debug("沒有 CLAUDE_PROJECT_DIR 也沒有 cwd,放行")
        return 0
    lumos = _find_lumos_script()
    if lumos is None:
        _debug("找不到 lumos,放行")
        return 0
    argv = [sys.executable, lumos, "dispatch-lens"] + ([rng] if rng else ["--spec", spec]) + ["--repo", repo, "--json"]
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=INNER_TIMEOUT)
    except subprocess.TimeoutExpired:
        # 2026-09-05 第二輪審視 d1:超時不再靜默——今天 39 次派工 21 次放空,編排者完全不知道。附一行固定句(零自由文字)。
        what = rng or spec
        _emit_updated(tool_input, prompt, TIMEOUT_NOTE.format(what=what, cmd=(rng if rng else f"--spec {spec}"), n=10))   # 通才 r1 #1:spec 模式要給對指令
        _debug("lumos dispatch-lens 超時,已附超時說明行")
        return 0
    except OSError as e:
        _debug(f"lumos dispatch-lens 失敗({type(e).__name__}),放行")
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
    _emit_updated(tool_input, prompt, text)
    _debug(f"已附 {data.get('shown')} 篇(固定席 {data.get('pinned')},主線 {data.get('mainline', data.get('mode'))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
