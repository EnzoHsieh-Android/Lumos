#!/usr/bin/env bash
# get.sh — 遠端一鍵裝「機器層」:clone Lumos + user-scope skills + 全域 lumos。
# 用法:  curl -fsSL https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/main/get.sh | bash
#   傳 --pull:  curl -fsSL <url> | bash -s -- --pull
#   環境變數:LUMOS_HOME(預設 ~/harness/lumos-toolchain)、LUMOS_URL(預設 GitHub)
set -euo pipefail
LUMOS_HOME="${LUMOS_HOME:-$HOME/harness/lumos-toolchain}"
LUMOS_URL="${LUMOS_URL:-https://github.com/EnzoHsieh-Android/Lumos}"
PULL=0; [[ "${1:-}" == "--pull" ]] && PULL=1

if [[ -f "$LUMOS_HOME/scripts/lumos" ]]; then
  echo "[1/2] Lumos 源已在: $LUMOS_HOME"
  [[ "$PULL" == 1 ]] && { git -C "$LUMOS_HOME" pull --ff-only || echo "WARN: git pull 失敗,沿用現有 clone" >&2; }
else
  echo "[1/2] clone Lumos → $LUMOS_HOME …"
  mkdir -p "$(dirname "$LUMOS_HOME")"
  git clone "$LUMOS_URL" "$LUMOS_HOME"
fi

echo "[2/2] 全域 lumos(symlink → scripts/lumos)+ user-scope skills…"
python3 "$LUMOS_HOME/scripts/lumos" install --force

echo
echo "✓ 機器層裝好。下一步:"
echo "  1. **重啟 Claude Code session**(L1/L3 hooks 在 session start 載入)"
echo "  2. 進你的專案:cd <專案> && lumos init   # slug 預設取資料夾名;自訂用 --name <slug>"
