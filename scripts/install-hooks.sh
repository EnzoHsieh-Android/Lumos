#!/usr/bin/env bash
# install-hooks.sh — 薄殼:hook 安裝邏輯已收進 python 單一源(scripts/lumos 的 _install_hooks_py)。
# 保留檔名供舊文檔/離線。等價於在當前 repo 跑 `lumos init --force`(會 vendor + 裝 git/Claude hooks)。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/lumos" init --force
