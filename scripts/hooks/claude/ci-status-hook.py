#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionStart hook — CI 紅燈後備網（CI回流閉環_計劃 [S2b]）。

主路徑是「push 後同輪跑 lumos ci-wait 當場修」；本 hook 只在**主路徑沒跑完**
（session 中斷／機器關機）時兜底：開場把「上次 push 的 CI 是紅的」推到眼前。

紀律（血換來的，勿簡化）：
- **總開關**：專案未在 .lumos/config.json 宣告 ci 區塊 → 完全靜默（零侵入的唯一定義）。
- **判法是「當前 HEAD sha 的全部筆」不是「檔尾最後一筆」**：多 workflow 分筆時，
  最後一筆可能是綠的那支，紅的會被蓋掉（續審 r1 實錘）。
- **輸出契約宣告 SessionStart**（不可照抄 PreToolUse hook 的硬編事件名，否則注入被丟棄）。
- 全程 fail-open：任何異常都靜默退出 0，絕不擋 session 開場。
"""
import json
import os
import subprocess
import sys
from pathlib import Path

CI_LOG_NAME = ".ci-log.jsonl"
RED = ("failure", "timed_out", "startup_failure")


def _repo_root(cwd):
    r = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, timeout=10)
    return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def _ci_enabled(root):
    try:
        data = json.loads((root / ".lumos" / "config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and isinstance(data.get("ci"), dict)


def _find_log(root):
    for d in sorted((root / "docs").glob("*-knowledge")):
        p = d.parent / CI_LOG_NAME
        if p.exists():
            return p
    return None


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        payload = {}
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    root = _repo_root(cwd)
    if root is None or not _ci_enabled(root):
        return 0                                   # 總開關：未宣告即靜默
    log = _find_log(root)
    if log is None:
        return 0
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True, timeout=10)
    if head.returncode != 0:
        return 0
    sha = head.stdout.strip()

    rows = []
    try:
        with open(log, encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue                        # 壞行跳過（半寫入容錯）
                if isinstance(d, dict) and d.get("sha") == sha:
                    rows.append(d)
    except OSError:
        return 0
    reds = [r for r in rows if (r.get("conclusion") or "") in RED]
    if not reds:
        return 0                                    # 綠或無資料：零噪音

    first = reds[0]
    detail = f"（{first.get('workflow') or 'CI'}"
    if first.get("failed_step"):
        detail += f" / {first['failed_step']}"
    detail += "）"
    msg = (f"⚠ 上次 push 的 CI 是紅的{detail} sha={sha[:7]} → {first.get('url', '')}"
           f"\n本輪開工前先處理或明確跳過；細節：lumos ci-status")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": msg}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)                                 # fail-open：絕不擋開場
