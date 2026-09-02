#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionStart hook — 開場一行:提醒「第一步敲 lumos」和指令索引在哪(Projects/指令索引與情境測試_計劃)。

為什麼要有它:規則寫在 CLAUDE.md 和 skill 裡,但 Claude 會在任務中途忘記「我該去翻索引」;
SessionStart 注入是唯一不靠它自己想起來的機械提醒。只印三行,沒有圖譜的專案完全靜默。
全程 fail-open:任何異常靜默退出 0。
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def _repo_root(cwd):
    try:
        r = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=10)
    except Exception:
        return None
    return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def _discipline_lag(root):
    """CLAUDE.md 紀律區塊跟來源範本不一樣 → 一行提醒(工具鏈補強十件 #8)。
    比內容不比版本號——版本號手動 bump,範本改了常沒 bump。來源不在、沒 sentinel 都靜默。"""
    try:
        cm = (root / "CLAUDE.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError:
        return None
    start = cm.find("<!-- LUMOS:GRAPH-DISCIPLINE:START")
    end = cm.find("<!-- LUMOS:GRAPH-DISCIPLINE:END -->")
    if start < 0 or end < 0:
        return None
    norm = lambda t: "\n".join(l.rstrip() for l in t.replace("\r\n", "\n").split("\n")).strip("\n")
    body = norm(cm[cm.find("\n", start) + 1:end])
    src = Path(os.environ.get("LUMOS_HOME") or (Path.home() / "harness" / "lumos-toolchain"))
    tpl = src / "scripts" / "templates" / "graph-discipline.md"
    if not tpl.exists():
        return None
    kgs = sorted((root / "docs").glob("*-knowledge"))
    if not kgs:
        return None
    slug = kgs[0].name[:-len("-knowledge")]
    try:
        expected = norm(tpl.read_text(encoding="utf-8").replace("{{KG}}", f"docs/{slug}-knowledge/"))
    except OSError:
        return None
    if body == expected:
        return None
    return ("提醒:這個專案 CLAUDE.md 裡的 lumos 紀律區塊跟來源的最新版不一樣(規則可能已經更新),"
            "有空跑一次:\n    lumos update")


def _enforcement_alert(rows):
    """回一行「防護有幾層沒生效」提醒,或 None(全 active、或只剩 unknown)。
    ★讓 lumos enforcement 不靠人記得敲——每 session 開頭自動查,只在有層掉了才吭聲★。
    unknown 不 nag(本機修不動,如遠端 GitHub 設定);只點名 inactive/degraded。"""
    down = [r for r in rows if r.get("status") in ("inactive", "degraded")]
    if not down:
        return None
    names = ", ".join(f"{r['layer']}({r['status']})" for r in down)
    return (f"⚠ 防護有 {len(down)} 層沒生效:{names}\n"
            f"    細節與修法:lumos enforcement(多半是在專案根跑 lumos install --force)")


def _enforcement_line(root):
    """跑 vendored 的 lumos enforcement --json,回提醒行或 None。任何異常靜默(fail-open)。"""
    try:
        cli = root / "scripts" / "lumos"
        if not cli.exists():
            return None                            # 沒 vendored CLI → 跳過,不猜
        # ★timeout 必須遠小於外層 hook 天花板★:這支 SessionStart hook 被 Claude Code 掛 10s
        # (merge-claude-settings.py 寫死);內部若 ≥10s、enforcement 一卡住,外層會 SIGKILL 整支 hook,
        # 連核心「先查圖譜」提醒都被吃掉(SIGKILL 繞過 try/except)。設 3s:正常 0.2s 的 15 倍餘裕,
        # 卡住就快速放棄回 None、核心訊息照印(code-enf-autohook r1 審)。
        r = subprocess.run([sys.executable, str(cli), "enforcement", "--json"],
                           capture_output=True, text=True, timeout=3, cwd=str(root))
        if r.returncode != 0 or not r.stdout.strip():
            return None
        rows = json.loads(r.stdout).get("rows", [])
        return _enforcement_alert(rows)
    except Exception:
        return None


def main():
    if os.environ.get("LUMOS_ENTRY_HOOK_OFF") == "1":
        # 修法 A ablation 的「不帶」組(Projects/修法A_lumos先行ablation_計劃):探針沙盒砍了 CLAUDE.md 那一節,
        # 同一句提醒不能從這裡再進來。平時沒人設這個變數,行為不變。
        return 0
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        payload = {}
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    root = _repo_root(cwd)
    if root is None or not list((root / "docs").glob("*-knowledge")):
        return 0
    idx = Path.home() / ".claude" / "skills" / "lumos-project-notes" / "commands" / "INDEX.md"
    if not idx.exists():   # 全域 skills 沒裝(或正在重裝)→ 退用來源 repo 的那份
        src = Path(os.environ.get("LUMOS_HOME") or (Path.home() / "harness" / "lumos-toolchain"))
        idx = src / "skills" / "lumos-project-notes" / "commands" / "INDEX.md"
        if not idx.exists():
            return 0
    lag = _discipline_lag(root)
    msg = ("本專案用 lumos 知識圖譜。動既有系統的第一個工具呼叫是 lumos search / context,不是 grep / Read;"
           "被催「直接改」也一樣,改 code 前至少 lumos impact --file <檔> 一行。\n"
           f"不確定該敲哪個指令 → 讀索引(4k 字元,按情境分九類,只開需要的子檔):\n    {idx}")
    if lag:
        msg += "\n" + lag
    enf = _enforcement_line(root)      # 自動查各層防護,有掉才追一行(全綠靜默)
    if enf:
        msg += "\n" + enf
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": msg}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
