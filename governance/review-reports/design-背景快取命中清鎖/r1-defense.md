# 同名換鎖兩條 finding 的唯讀辯方

F2 — evidence（重大降級）：本案只承諾同版、無人工換鎖。相同鎖名稱由快取 key 決定；`_excl_lock_try` 對既存鎖以 `O_EXCL` 拒絕，不再過期接手。等待端命中快取不刪鎖；`Popen` 失敗雖刪自己的鎖，但當時沒有成功啟動的舊背景。故舊背景仍活著時，同版流程無合法的同名新持有者。人工移鎖、舊版接手或同 UID 外部修改才可造出報告中的前提。證據：`scripts/lumos` 的 `_lens_cache_path`、`_excl_lock_try`、`_lens_wait_or_warm`、`_lens_spawn_warmer`。

F3 — evidence（重大降級，競爭現象屬實）：現行 `read_text` 後按路徑 `unlink` 確有空窗，但同版新持有者無法在舊鎖仍存在時換入。`os.unlink(path, dir_fd=...)` 仍按名稱刪除，不能原子地「核對身份才刪」；多核對一次 PID 或 inode 也只縮短空窗。要擴大到外部換鎖保證，須另設取得與釋放協議，不是本次小修。依據：[Python `os.unlink`](https://docs.python.org/3/library/os.html#os.unlink)、[Linux `unlinkat(2)`](https://www.man7.org/linux/man-pages/man2/unlinkat.2.html)。

實作硬前提：新 `finally` 必須**取代**既有 `_dispatch_lens_graph` 尾端清鎖，不得形成兩次清理。若第一次刪鎖後另一同版程序合法取得同名鎖，舊背景第二次清理就可能誤刪。這條用新 S8 回歸測試釘住；F2/F3 的降級僅在單一清理出口成立。
