severity: major

F1
severity: major
blocking: 是
引句:「當啟動失敗清掉原鎖後另一程序取得同名鎖，`_lens_wait_or_warm` 應保留新鎖」
file: `scripts/lumos:33921`
重現/因果: `_lens_spawn_warmer` 在 `Popen` 拋錯後直接按路徑 `lock.unlink()`，未核對 inode。最小故障注入讓 `Popen` 先移除舊鎖、建立內容為 `replacement` 的同名新鎖再拋 `OSError`，實際輸出 `{'replacement_survives': False, 'content': None}`。S4 現有與新增測試只覆蓋「舊鎖清完後，於 `_lens_cache_read` 才取得替代鎖」，即使全綠仍證明不了清理瞬間不會刪掉新持有者。設計需保存取得時的鎖身分並只刪同一 inode，另加這個交錯順序的翻紅測試。

F2
severity: major
blocking: 是
引句:「hook 必須用固定說明告知「背景未啟動」並記 error 事件」
file: `scripts/hooks/claude/dispatch-lens-hook.py:345`
重現/因果: hook 是複製檔、全域 `lumos` 是指向來源的 symlink，程式也明載「兩邊版本錯開是常態」。以提交 `e5695c11` 的舊 hook 接收新版預定的 `rc 2 + {"spawn_error":true,...,"role_text":"ROLE"}`，輸出只含 `ROLE`，沒有背景未啟動提示，也沒有 error 事件；來源更新後尚未重跑 install、或跨版本回退時，S2/S5 仍可在同版測試全綠而實際靜默。需定義並測試舊 hook＋新 lumos、新 hook＋舊 lumos 的安裝邊界，或讓協議在舊 hook 已識別的欄位上相容。

回退與安全停用
severity: minor
blocking: 否
引句:「讓鏡頭改同步計算並停止新背景暖機；確認舊背景工作停止與鎖狀態後」
file: `scripts/test_lumos.py:34816`
重現/因果: S1–S5 沒有條款綁定回退開關；既有測試只驗 hook 最終有注入內容，未斷言 `Popen` 零次、沒有新 `.warming` 鎖，也未驗既有脫離程序如何確認已停止。應補回退驗收，明確驗證開關生效後同步計算、零新背景程序／鎖，並寫出舊暖機的可執行確認方式。

總結最嚴重 severity: major；blocking: 2 條。
