#!/usr/bin/env python3
"""Merge graph hook entries into ~/.claude/settings.json — idempotent.

跟 scripts/install-hooks.sh 配合用。已存在的 hook entry 不重複加。
不會清掉使用者既有的其他 settings (mcpServers/permissions/...)。
"""
from __future__ import annotations
import json
import re
import shutil
import sys
from pathlib import Path

SETTINGS = Path.home() / ".claude" / "settings.json"
HOOKS_DIR = Path.home() / ".claude" / "hooks"

_PY = shutil.which("python3") or shutil.which("python") or "python3"
# W3:${HOME} 只有 POSIX shell 展開;native Windows(Claude Code 經 cmd/PowerShell 跑 hook)
# 不展開 → hook 路徑變字面 ${HOME} → L1/L3 靜默不觸發。Windows 用解析後的絕對 home。
_HOME = str(Path.home()).replace("\\", "/")


def _hook_cmd(rel_path):  # rel_path = "verification-rot-check.py"
    # W6:Claude Code 在 Windows 用 Git Bash 跑 hook command → 反斜線會被 shell 吃掉
    # (C:\Users → C:Users → python 找不到 → hook 靜默失敗)。故 Windows 下 python 路徑與
    # home 都用正斜線 + 引號。Unix 保留 ${HOME}(可攜、Mac 已驗)。
    if sys.platform == "win32":
        py = _PY.replace("\\", "/")
        return f'"{py}" "{_HOME}/.claude/hooks/{rel_path}"'
    return f'{_PY} "${{HOME}}/.claude/hooks/{rel_path}"'


HOOK_ENTRIES = {
    "PreToolUse": [
        {
            # 主動影響幅度偵測:Edit/Write/MultiEdit 動手前注入 additionalContext。
            # 比照現有 claude/ hooks 現況:不進 ANCHOR_FILES(見設計 §5)。
            # 生產實測:用 `claude --debug` 驗 PreToolUse additionalContext 注入時機;
            # 若版本行為有變可退回 stderr 備援(check-graph-sync.py 已證此路可行)。
            # (設計 §3 r5-F2)
            "matcher": "Edit|Write|MultiEdit",
            "hooks": [
                {
                    "type": "command",
                    "command": _hook_cmd("impact-hook.py"),
                    "timeout": 30,
                }
            ],
        }
    ],
    "PostToolUse": [
        {
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": _hook_cmd("verification-rot-check.py"),
                    "timeout": 60,
                }
            ],
        }
    ],
    "Stop": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": _hook_cmd("check-graph-sync.py"),
                    "timeout": 10,
                }
            ]
        },
        # NOTE(2026-07-06):code-loop-guard Stop nag 已移除——每回合注入太擾民。
        # code-loop 把關改由 pre-push git hook(scripts/hooks/pre-push)在 push 時單點強制,
        # 不再每回合 nag。(2026-07-07 起懸空註冊由 _prune_dangling 自動清,不再需手動。)
    ],
}


def _prune_dangling(settings: dict) -> list:
    """剪掉指向 ~/.claude/hooks/ 下「不存在檔案」的 hook 註冊(懸空只會每回合報錯)。
    起因 2026-07-07 現場事故:code-loop-guard.py 被工具鏈更新刪除、settings 註冊沒清 →
    每回合「檔案不存在」。只動 command 含 `.claude/hooks/` 的項;使用者自訂
    (指向他處)的 command 一律不碰。回傳被剪的 (event, script) 列表。"""
    pruned = []
    for event, entries in list(settings.get("hooks", {}).items()):
        kept_entries = []
        for entry in entries:
            kept_hooks = []
            for h in entry.get("hooks", []):
                cmd = h.get("command", "")
                if ".claude/hooks/" in cmd.replace("\\", "/"):
                    script = _hook_script(cmd)
                    if script.endswith(".py") and not (HOOKS_DIR / script).exists():
                        pruned.append((event, script))
                        continue
                kept_hooks.append(h)
            if kept_hooks or not entry.get("hooks"):
                entry = dict(entry)
                if "hooks" in entry:
                    entry["hooks"] = kept_hooks
                kept_entries.append(entry)
            # else:整組 hooks 都懸空 → entry 一併剪
        settings["hooks"][event] = kept_entries
    return pruned


def _hook_script(cmd: str):
    m = re.search(r"([\w.-]+\.py)", cmd or "")
    return m.group(1) if m else cmd


def _equivalent(a: dict, b: dict) -> bool:
    """同一個 hook entry 認定為已存在 (避免重複註冊)。
    比對:matcher (PostToolUse 需要) + 內層 hook 腳本檔名
    (認出舊裸路徑 == 新 `python …/xxx.py` 為同一 hook)。"""
    if a.get("matcher") != b.get("matcher"):
        return False
    a_s = sorted(_hook_script(h.get("command", "")) for h in a.get("hooks", []))
    b_s = sorted(_hook_script(h.get("command", "")) for h in b.get("hooks", []))
    return a_s == b_s


def main() -> int:
    if SETTINGS.exists():
        try:
            settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"ERROR: {SETTINGS} JSON 損毀: {e}", file=sys.stderr)
            return 1
    else:
        settings = {}

    settings.setdefault("hooks", {})
    changed = False

    # 先清懸空(腳本已被刪、註冊還在 → 每回合報錯),再 merge
    for event, script in _prune_dangling(settings):
        print(f"  [prune] {event} hook → {script}(檔案不存在,懸空註冊已清)")
        changed = True

    # --prune-only:只剪懸空、★不 re-add★(teardown 用——刪掉我方 hook .py 後跑此模式,
    # 剪掉變懸空的我方註冊而不把它加回去;預設 merge 模式會 re-add,反而抵銷 teardown)。
    prune_only = "--prune-only" in sys.argv

    for event, entries_to_add in ({} if prune_only else HOOK_ENTRIES).items():
        existing = settings["hooks"].setdefault(event, [])
        for new_entry in entries_to_add:
            match_idx = next((i for i, e in enumerate(existing) if _equivalent(new_entry, e)), None)
            if match_idx is not None:
                if existing[match_idx] != new_entry:
                    existing[match_idx] = new_entry  # 遷移:取代成 resolved-python 格式
                    print(f"  [migrate] {event} hook → resolved-python")
                    changed = True
                else:
                    print(f"  [skip] {event} hook already current")
                continue
            existing.append(new_entry)
            print(f"  [add ] {event} hook")
            changed = True

    if not changed:
        print("settings.json 已經是最新狀態,無需修改")
        return 0

    # Backup before write
    if SETTINGS.exists():
        backup = SETTINGS.with_suffix(".json.bak")
        backup.write_text(SETTINGS.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  備份到: {backup}")

    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"已更新: {SETTINGS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
