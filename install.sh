#!/usr/bin/env bash
# install.sh — 薄殼:安裝邏輯已收進 python 單一源(scripts/lumos)。保留檔名供舊文檔/離線使用(cmd_bootstrap 已改探測 scripts/lumos,2026-07-25 F3)。
# 等價於 `lumos install --force`:裝全域 lumos + user-scope skills(symlink → ~/.claude/skills/lumos-*)。
exec python3 "$(cd "$(dirname "$0")" && pwd)/scripts/lumos" install --force
