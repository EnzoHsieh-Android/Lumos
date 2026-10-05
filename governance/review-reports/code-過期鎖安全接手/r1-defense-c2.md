# C2 辯方核對

C2 的 major 不成立，建議降為 minor。

同版 `_excl_lock_try` 遇既有鎖直接回 `False`，不會移除或換入：`scripts/lumos` 的 `_excl_lock_try`。Vault 在取得成功前不登記持有，其他同版 vault 程序也不會清除半成品：`scripts/lumos` 的 `_vault_write_lock`。

現有測試是在假的 `os.write` 裡直接 `unlink` 再建檔，換入發生於 cleanup 的 `lstat` 之前；它沒有重現 C2 所稱的 `lstat`→`unlink` 窗口：`scripts/test_lumos.py` 的 `t_excl_lock_creation_failure_cleans_own_file`。人工操作與舊版程序可以製造 ABA，但 spec 已明示混版不保證安全。

剩餘同版風險只存在於極端 lens 時序：失敗程序停在 `lstat` 後，另一等待者因快取出現而無條件刪鎖；再等快取 20 分鐘過期、第三者建立新鎖，失敗程序才恢復並誤刪。這需要寫鎖失敗加超過 TTL 的停頓，影響是重複暖機與快取最後寫入者覆蓋，無法造成 vault 雙寫，因此最多是 minor 殘餘風險。

編排者處置：已將 lens 等待者在快取命中時刪鎖限制為本次取得者，`t_lens_stale_lock_reports_uncertainty` 先紅後綠；混版／人工換檔仍列於 S6 進場條件，不宣稱跨版本保證。
