severity: minor

## F1 partial=True 會把別人剛建、還沒寫完的鎖當成自己的而刪掉
severity: minor
blocking: 否
引句:「return got == data or (partial and data.startswith(got))」
file: `/home/user/Lumos/scripts/lumos:42514`
失敗場景:`_excl_lock_try` 寫入丟 OSError,進 except 先 `os.close(fd)`,inode 此刻釋放;若別人在這個瞬間刪掉我的檔並重建同名鎖(Linux 重用同一 inode),而我讀到的內容是空檔,或剛好是 `PID\n` 這種我內容的前綴,`data.startswith(got)` 為真,第 42514 行 partial=True 通過,接著 unlink 刪掉別人的新鎖。實跑:在 os.close 之後換入空檔 -> 對方鎖被刪(survives False);換入 `{pid}\n` -> 被刪;換入不相干內容 -> 保留。空內容恆為任何字串的前綴,所以 partial=True 對「別人剛 O_EXCL 建好、還沒 write」的鎖完全無防護。
與修法前比較:修法前只比 inode,同樣會刪,所以不是退步;但修法宣稱要補的洞在這條路徑上沒補完。要補的話,partial 路徑的空檔只在「自己確實一個位元組都沒寫成」時才該算數(例如記住已寫入位元組數 n,只接受 got == data[:n])。
另:lstat 與 read_bytes 之間再被換掉的檢查後使用時間差,在 partial=True 下同樣能被空檔/前綴穿過(實跑 is_mine 回 True);非 partial 時因隨機尾碼不會誤判。

## F2 spawn 失敗路徑下,自己的鎖「讀不了」會被當成「已不是我的」而靜默留下
severity: minor
blocking: 否
引句:「return True, False  # 本次鎖已被移除或換成別人的,不碰後來取得同名路徑的持有者。」
file: `/home/user/Lumos/scripts/lumos:42561`
失敗場景:Popen 失敗後,`_excl_lock_is_mine` 內 `lock.read_bytes()` 丟 OSError(EIO、權限被改等)就回 False,第 42561 行直接回 (True, False),也就是「無清理錯誤」。實跑(mock read_bytes 丟 PermissionError、鎖確為自己的):回 (True, False) 且鎖檔仍在,不會印「本次鎖清理失敗」提示,而這把鎖永遠擋後續派工(只能等人工清)。修法前 lstat 丟非 ENOENT 的 OSError 會走 `except OSError: return True, True` 回報清理失敗;現在把「讀不到」與「被換掉」混成同一個靜默分支,可診斷性變差。docstring 的「寧可留鎖」是刻意取捨,但至少該回 cleanup_error=True 與 FileNotFoundError 區分。⚠ 只能用 mock 重現,實際發生機率低。

## F3 測試守不住 partial 路徑與寫入失敗清理;t_excl_lock_stale_takeover_is_single_owner 與本修法無關
severity: minor
blocking: 否
引句:「if identity is not None and _excl_lock_is_mine(lock, identity, partial=True):」
file: `/home/user/Lumos/scripts/test_lumos.py:67853`
實測:把 `_excl_lock_is_mine` 的比對改成恆回 True(拿掉內容比對),在隔離副本跑 `-k excl_lock` 11 支全綠(含 stale_takeover);`-k lens_spawn_failure` 則 t_lens_spawn_failure_preserves_replacement_lock 翻紅(6 passed, 1 failed),所以 spawn 失敗那條有被守住。但 `_excl_lock_try` 的寫入失敗清理(partial=True)沒有任何測試:拿掉 partial 判斷、或像 F1 那樣放寬,都不會紅。stale_takeover 測的是既有鎖不被偷,不碰身份內容。
建議補測:注入 os.write 失敗,驗(a)自己的殘鎖(含短寫 1 位元組後失敗)被清掉、(b)close 後換入空檔/他人內容時不被刪(F1 修好後)。

## 已走過沒問題的範圍
引句:「data = full」
- 短寫:os.write 每次只回 1 位元組,成功時檔案內容 == identity 內第三欄(實跑 E3 為真);寫到一半失敗時,自己的殘鎖(內容為 data 的前綴)會被清掉(實跑為真)。
- close 報錯但內容已寫全:closed=True 不重試,except 內 partial 比對 got==data,自己的鎖被清掉(實跑為真)。
- 同名重建拿到同一 inode:實跑確認 inode 被重用,非 partial 的 is_mine 因隨機識別碼回 False,別人的新鎖保留(即 t_lens_spawn_failure_preserves_replacement_lock 的情境)。
- 符號連結:lstat 看到的是連結本身的 inode,與 fstat 的不同,回 False,不刪;保守方向。
- 第三行對其他讀者的影響:`_vault_write_lock` 解鎖只取 `split("\n", 1)[0]` 比 PID(file: `/home/user/Lumos/scripts/lumos:17935`);`_lens_release_owned_lock` 只取第一行 strip(file: `/home/user/Lumos/scripts/lumos:42688`);`_lens_report_lock_timeout` 只看 mtime。repo 內沒有別處寫入或解析 .warming 內容,owned_identity 只在 `_lens_wait_or_warm` 取 [0] 傳入,三元組不會被二元解包。
- 鎖檔內容只在建立時寫一次,沒有後續改寫,所以內容比對不會把自己的鎖誤判成別人的。

總結:核心修法對 inode 重用的 spawn 失敗情境正確且有測試守住,僅 partial=True 對空檔與前綴留有舊洞(非退步)、讀失敗的分類與寫入失敗路徑的測試各有小缺口。
