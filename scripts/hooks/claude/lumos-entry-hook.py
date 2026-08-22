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


def main():
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
           f"不確定該敲哪個指令 → 讀索引(4k 字元,按情境分八類,只開需要的子檔):\n    {idx}")
    if lag:
        msg += "\n" + lag
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": msg}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
