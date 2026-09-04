#!/usr/bin/env bash
# install.sh — 薄殼:安裝邏輯已收進 python 單一源(scripts/lumos)。保留檔名供舊文檔/離線使用(cmd_bootstrap 已改探測 scripts/lumos,2026-07-25 F3)。
# 等價於 `lumos install --force`:裝全域 lumos + user-scope skills(symlink → ~/.claude/skills/* 與 Codex 讀的 ~/.agents/skills/*)
# + 兩家 hook 註冊(~/.claude/settings.json、~/.codex/hooks.json;Codex 的 hook 要你開一次互動 codex 審過才會跑)。
exec python3 "$(cd "$(dirname "$0")" && pwd)/scripts/lumos" install --force
