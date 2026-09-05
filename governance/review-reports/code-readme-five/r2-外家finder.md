1.
severity: minor
blocking: 否
引句:「local first; first="$(git show ":$path" 2>/dev/null | head -c 200 | head -n 1)" || return 1」
file: `scripts/hooks/pre-commit:125`
場景: staged 無副檔名檔若檔名含換行或雙引號，`git diff --name-only` 會輸出 C-style quoted 名稱；迴圈把引號與反斜線當成實際路徑交給 `git show`，讀取失敗，帶 `#!` 的程式碼便不會觸發同步閘。post-commit 的 `CHANGED` 管線及 `HEAD:$path` 同樣受影響（`scripts/hooks/post-commit:42,50`）。

max severity: minor
