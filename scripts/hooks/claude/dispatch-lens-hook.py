#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
# MIT licensed. Full text: scripts/lumos header, or LICENSE at
# https://github.com/EnzoHsieh-Android/Lumos
"""dispatch-lens-hook — Claude Code PreToolUse(matcher Agent)薄殼(Projects/派工鏡頭注入_計劃,2026-09-03);
Codex 側掛 SubagentStart(Projects/Codex完全支援_計劃 d3,2026-09-04):叫 `lumos dispatch-lens --claim` 領一席 → additionalContext。

Claude 路徑只做三件事:①派工詞裡逐行找 `LUMOS-IMPACT: <base>..<head>` ②subprocess 叫 `lumos dispatch-lens`
③把回傳文字接在派工詞尾端,經 updatedInput 送給子代理(additionalContext 實測到不了子代理)。
其餘判斷(範圍文法、base 主線可達、消毒、快取)全在 lumos 端。
永不 deny、永不改 permissionDecision;失敗一律放行。★2026-09-05 起超時不再靜默★:附一行固定超時句進派工詞(Codex 走 additionalContext);其他失敗仍靜默(LUMOS_HOOK_DEBUG=1 才印 stderr)。
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

def _find_lumos_script() -> str | None:
    """★2026-09-07 外家審查席抓到:這支是第四支,前一批漏了★
    原本 which 找不到就退回「這支 hook 檔往上四層」的 scripts/lumos——這支 hook 會被複製進
    消費專案,那時往上四層正好是**消費專案自己的根**,等於又回到「執行手邊資料夾的碼」。
    前一批只改了三支、測試也只掃那三支,所以沒抓到。現在改用共用的可信來源解析。"""
    return _trusted_lumos()


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
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": _frame_injected(TIMEOUT_NOTE.format(what="(Codex 席:--claim)", cmd="--arm <base>..<head> --seats N 重新武裝(--status 只看剩幾席、不重算)", n=10))}}, ensure_ascii=False))
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
    # 這段 text 是 lumos dispatch-lens 產的,框已經加在那邊(單源:框跟內容同一個地方組)。
    # 這裡不重複框——重複會變成框中框,反而讓邊界更難讀。
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart",
                                             "additionalContext": text}},   # framed-upstream
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
