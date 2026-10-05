severity: major

severity: major
blocking: yes
引句:「把身份核對收成同層 helper，以 `try…finally` 包住快取路徑已算出後的鏡頭主體」
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:22`
file: `scripts/lumos:33909`
file: `scripts/lumos:33917`
file: `scripts/lumos:34053`
finding: F1 — 父程序先用 SHA 算出舊快取與鎖路徑，卻把原始 `diff_range` ref 字串交給背景程序；ref 在兩者之間移動或消失時，背景程序會算出另一個 `cpath`，或在 `cpath` 算出前由 commit/mainline/ancestor 錯誤出口返回。設計把 `finally` 起點放在背景程序自己的 `cpath` 之後，既清不到父程序建立的舊鎖，也無法覆蓋 ref 消失造成的前置錯誤，違反「所有出口一起包住」的核心宣稱。
重現證據: 直接 mock `subprocess.Popen` 呼叫 `_lens_spawn_warmer(lock, "main~1..moving-branch", repo)`，輸出 `spawn argv range = main~1..moving-branch`、`expected immutable range = FULL_BASE_SHA..FULL_HEAD_SHA`、`RED = True`。最小翻紅測試應要求背景 argv 使用父程序已解析的完整 SHA，並在啟動前後移動／刪除 symbolic ref，最後斷言父程序原 `cpath.warming` 消失。

severity: major
blocking: yes
引句:「保留既有鎖格式與鎖內 PID 比對；在原本只有 PID 比對的清理判斷外，加一道 `_LENS_WARM_ENV` 條件」
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:22`
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:27`
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:33`
file: `scripts/lumos:34201`
file: `scripts/lumos:34203`
finding: F2 — PID 不是一次 acquisition 的身份。設計已明知「相同 PID 換入新鎖」會失效，卻只把它寫成日後 `RETIRE-IF`，S2 也只測 PID 不符與沒有暖機標記；同 PID 的新鎖會通過 `_owner` 比對並被舊背景工作刪除。暖機環境標記只能證明呼叫來源，不能區分兩次 acquisition。
重現證據: 以 `LUMOS_LENS_WARMING=1`、`LUMOS_LENS_LOCK_OWNER=111` 執行正常完成出口，在清理前把 `cache.json.warming` 換成另一筆內容同為 `111\n...` 的新鎖；現碼 `read_text` 比對成功後執行 `unlink`，新鎖消失。最小翻紅測試應保存取鎖時的 `(st_dev, st_ino)` 或唯一 token，換入同 PID、不同 inode 的鎖後斷言它仍存在。

severity: major
blocking: yes
引句:「非背景呼叫及身份不符都不刪。這只延伸現行同版身份界線」
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:22`
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:40`
file: `scripts/lumos:33855`
file: `scripts/lumos:33875`
file: `scripts/lumos:34202`
file: `scripts/lumos:34203`
finding: F3 — 設計只說把 PID 核對收成 helper，未要求「核對的檔」與「刪除的檔」身份相同。現行 `read_text()` 後再依路徑 `unlink()` 有 TOCTOU 窗口；競爭者在兩步之間換入不同 PID 的新鎖，舊背景程序仍會刪掉它。相鄰 `_excl_lock_try` 的失敗清理已用 `(st_dev, st_ino)` 避免同類問題，這份設計卻沒有沿用。
重現證據: 在現行 `_dispatch_lens_graph` 正常完成路徑，以 mock 令 `Path.read_text(lock)` 讀到舊 owner `111` 後立刻用 `os.replace` 換入 owner `222`，實跑輸出 `rc = 0`、`replacement swapped in = True`、`new owner lock survives = False`、`RED = True`。這會直接讓「身份不符都不刪」翻紅。

引句:「等待端仍只讀快取，不得按「曾取得」推論現在持有而刪鎖」
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:20`
file: `scripts/lumos:33967`
file: `scripts/lumos:33973`
file: `scripts/test_lumos.py:54631`
檢查: 等待端快取命中路徑只輸出結果，不執行清鎖；既有測試也覆蓋啟動失敗後新持有者換入。已讀，無 finding。

引句:「遇到 impact 錯誤而提前返回時，`_dispatch_lens_graph` 應清理身份相符的鎖，且保留原返回碼」
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:29`
file: `scripts/lumos:34113`
file: `scripts/lumos:34129`
檢查: 對 `cpath` 已確定後的 impact 非零、JSON 解析失敗、base 樹讀取失敗與未預期例外，外層 `try…finally` 是足以統一經過清理且維持原返回／拋例外語意的結構；前置 ref 錯誤缺口已列 F1。已讀，無 finding。

引句:「當背景程序算完新快取時，`_dispatch_lens_graph` 應清自己的鎖，且等待端命中快取應保留其他持有者的鎖」
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:28`
file: `scripts/lumos:34194`
file: `scripts/test_lumos.py:16367`
檢查: 正常算完、快取寫入與等待端不清鎖的既有流程皆有對應測試；目前測試子集 `t_lens_stale_lock_reports_uncertainty` 為 9 passed、0 failed。身份與換檔問題已分列 F2/F3。已讀，無 finding。

總結：最嚴重 severity: major；blocking: 3。
