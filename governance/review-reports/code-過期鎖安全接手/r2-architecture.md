severity: minor

## Finding A1

severity: minor  
blocking: no  
file: `scripts/lumos:33883`  
引句:「def _lens_lock_timeout(lock, diff_range, as_json):」

名稱與同層慣例不一致：`_lens_lock_timeout` 會判斷鎖狀態、輸出 JSON／人話並回傳 CLI 狀態碼 5（`scripts/lumos:33886-33903`），但同檔既有 `_disp_git_timeout` 是單純回傳逾時秒數的 getter（`scripts/lumos:35464-35470`）；有輸出副作用的 helper 則明示為 `_lens_render_listed`（`scripts/lumos:33794`）或 `*_print_*`。建議改成 `_lens_report_lock_timeout` 或 `_lens_emit_lock_timeout`，讓呼叫端可從名稱看出輸出副作用與狀態碼責任。

## 三問

1. 分層依賴：無 major。hook 仍維持薄殼，只透過子程序呼叫 `lumos`（`scripts/hooks/claude/dispatch-lens-hook.py:321-344`）。新增留帳呼叫的是同目錄共用 helper `_hookevent.mark`（`scripts/hooks/claude/dispatch-lens-hook.py:368-374`、`scripts/hooks/claude/_hookevent.py:111-124`），不是跨層直呼。`scripts/lumos` 新 helper 也只由同一派工鏡頭區段呼叫（`scripts/lumos:33927-33980`）。

2. 命名／錯誤／事件留帳：命名有 A1。錯誤處理未另起慣例：背景程序啟動失敗仍只清理由本次取得的鎖並 fail-open（`scripts/lumos:33918-33924`），建鎖錯誤仍由上層轉成 rc 2 與既有 JSON schema（`scripts/lumos:33950-33958`）。事件留帳使用既有 `mark("error", …)`，並由共用 `guard` 消費標記（`scripts/hooks/claude/_hookevent.py:127-160`）；也與同檔既有 timeout 留帳路徑一致（`scripts/hooks/claude/dispatch-lens-hook.py:387-397`）。

3. 第二種機制：沒有。鎖仍只有 `_excl_lock_try`（`scripts/lumos:33839-33880`），暖機仍只有 `_lens_spawn_warmer`（`scripts/lumos:33906-33924`），事件仍寫入共用 `_hookevent`；本 delta 是抽 helper 與補既有事件帳標記，未新增平行鎖協議、背景工作通道或第二套帳本。

最重等級：minor