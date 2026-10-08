severity: major

R2-01 初次取得鎖被誤當成持續持有權
severity: major
blocking: yes
file: `scripts/lumos:33970`
引句:「已存在的鎖可能屬於別人；快取命中不代表我能替持有者刪鎖。」
症狀：`already=False` 只代表本程序最初取得過鎖，不能證明目前路徑仍是那把鎖。若背景程序啟動失敗，`_lens_spawn_warmer` 會刪除原鎖並吞下 `OSError`；另一程序之後可建立新鎖。首程序看到快取時仍會因舊的 `already=False` 執行 `lock.unlink()`，刪掉第二程序的鎖，重新開出多背景工作並行窗口。

最短重現（已對現碼執行）：

1. 無鎖進入 `_lens_wait_or_warm(..., deadline=.2)`，令首次 `_excl_lock_try` 成功。
2. 令 `subprocess.Popen` 拋出 `OSError`；helper 刪除首次鎖。
3. 在第一次 `_lens_cache_read` 前，以第二持有者重建同一路徑鎖，並讓讀快取回 `{"text": "ready"}`。
4. 函式回 `0`，但第二持有者的鎖已不存在。

實際觀察值為：
`{'rc': 0, 'replacement_owner_after_return': None, 'stdout': '{"text": "ready", "cache_hit": true}'}`

新增測試只從「鎖一開始就已存在」進場，因此 `already=True`，完全不會走有問題的刪鎖分支；這是可重現的假綠。

修法：等待端命中快取時不要刪鎖；成功啟動後應由背景持有者依不可重用的身份或 inode 清理。若仍需等待端清理，取得鎖時必須保存 inode/token，刪除前以 `lstat` 核對身份。另補上述「首次取得 → 啟動失敗 → 第二持有者換入 → 快取命中」回歸測試。

審查範圍：完整逐 hunk 檢查 397 行凍結 patch，並核對 hook 錯誤事件、S1 斷言、鏡頭 helper 分拆、非持有者快取路徑、背景鎖清理及圖譜更新。