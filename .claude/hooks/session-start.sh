#!/bin/bash
# 雲端工作階段開場:補齊全套測試要的工具,讓推送前的全套測試在雲端也跑得綠。
# 只在 Claude Code 雲端工作階段跑;本機不動。冪等,可重複執行。
# 家:Systems/雲端工作階段開場設定;為什麼這樣做見 Projects/雲端環境跑綠全套測試_計劃。
set -euo pipefail

[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

# 1. rsync:沙箱推送測試要用它複製 repo。
if ! command -v rsync >/dev/null 2>&1; then
  apt-get install -y -q rsync >/dev/null 2>&1 \
    || { apt-get update -q >/dev/null 2>&1 && apt-get install -y -q rsync >/dev/null 2>&1; }
fi

# 2. Python 3.14:測試總檔要求的版本,用 uv 裝。
command -v uv >/dev/null 2>&1 || python3 -m pip install -q uv
uv python install 3.14 >/dev/null 2>&1
real="$(readlink -f "$(uv python find 3.14)")"

# uv 放在 ~/.local/bin 的 python3.14 是跨目錄捷徑;從捷徑建的虛擬環境找不到標準庫
# (encodings 載入失敗),測試裡建 venv 的那幾支就假紅。改放一支轉呼叫真實路徑的小殼,
# 讓 sys.executable 是真實路徑;只放 python3.14 這一個名字,不改動系統的 python3。
shim_dir="$HOME/.local/lumos-python"
mkdir -p "$shim_dir"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$real" > "$shim_dir/python3.14"
chmod +x "$shim_dir/python3.14"

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PATH=\"$shim_dir:\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi
