severity: major

## F1 測試抓不住「改用最外層 stability 判斷」的改壞
severity: major
blocking: 是
file: `scripts/templates/android-e2e-run.sh:254`(新檢查的門條件),測試在 `scripts/test_lumos.py` 的 `t_android_e2e_preflight_stability_tools`。
失敗場景:有人把門條件從 `e2e.get("stability")` 改成 `cfg.get("stability")`,也就是讀最外層那段。設定檔裡只有最外層 stability(給單獨的 `lumos macrobench --stability` 用),`e2e.stability` 沒開時,新檢查會擋下一個本來不需要記憶體工具的專案。這是誤擋。
測試的「沒開穩定性」案例把 `e2e` 和 `top` 都設成 None,兩處都沒有 stability,所以改壞前後結果一樣。
我在 /tmp 的副本做了這個改動(已刪),跑 `python3.14 scripts/test_lumos.py -k android_e2e_preflight_stability_tools`,結果 `11 passed, 0 failed`,測試照綠。
被保護的行為是「e2e 沒開 stability 就不擋」。測試應該補一個案例:最外層有 stability、`e2e.stability` 沒開、兩支工具都缺,預期回 0。
引句:「+    if e2e.get("stability"):   # 收集腳本自己也查,但要等建置、安裝、UI、截圖都跑完才輪到它,缺工具就白跑一趟」

## F2 測試的 want=0 案例,完整跑只確認沒崩,沒檢查回傳碼
severity: minor
blocking: 否
file: `scripts/test_lumos.py` 的 `t_android_e2e_preflight_stability_tools`。
場景:「兩支都在」和「沒宣告測試資料」兩個案例,`--preflight` 和完整跑都會執行。但只有 `--preflight` 那趟檢查回傳碼(`elif extra:`),完整跑的結果被丟掉。
所以「完整跑漏做新檢查」不會被這條測試抓到。不過 `--preflight` 和完整跑走同一個 `preflight()`,這個風險很低。想表達的意思大致是完整跑也要被擋,但 want=2 的案例已經涵蓋這點。
引句:「+                elif extra:」

## manifest 逐條判定
- F401 `os` imported but unused:真的有過,diff 裡新測試已不含 `import os`,只剩 `import tempfile`,已修掉,不是現存隱患。
- C901 `t_android_e2e_run_script` 複雜度 15 > 10:位置落在既有函式 `t_android_e2e_run_script`,不是本次新增的程式。diff 只在它前面插入新函式,沒改它的內容。判誤報,或是既有舊帳。新增的 `t_android_e2e_preflight_stability_tools` 是單層迴圈加單一分支,沒有被點名。

## 正確性逐項走查(沒另列 finding 的部分)
- 設定欄位缺或型別怪:`load_config` 先跑 `--check-config`,通過才會到 `preflight`。`(cfg.get("stability") or {}).get("test_data") or {}` 對缺欄位也不會丟例外。stability 若是非物件,check-config 會先擋(`scripts/lumos:39471` 一帶),新檢查碰不到。
- 資源:`die()` 發生在 `take_lock` 之前,此時沒拿鎖,沒有遺漏釋放。
- 新舊互讀:舊設定沒有 `e2e.stability` 時整段略過,行為不變。
- 重跑冪等:檢查只做 `which`,不寫檔。

## 本案特定鏡頭:與收集腳本是否一致
一致。
- 環境變數:範本讀 `TP`、`JAVA_HEAP_DUMP`,預設值與收集腳本一樣(`scripts/templates/android-stability-collect.sh:20`)。傳給收集腳本的 env 是 `dict(os.environ, ...)`,所以環境變數會原樣透傳。
- 判斷條件:兩邊都是 `bool((st.get("test_data") or {}).get("value"))`。範本讀 `cfg["stability"]`,收集腳本讀 `cfg.get("stability")`,同一個物件。
- 工具順序:收集腳本先查 ADB 和 TP,再查 JHD,與範本一致。範本還多查 MAESTRO,這是既有行為。
- 沒有「開跑前放行、收集腳本卻擋」或反過來的差異。

## 圖譜鏡頭
- `測試假綠形態` 的 ★INVARIANT★(還原翻紅釘要配前置斷言證明現場成立):新測試對 want=2 的案例有檢查「沒碰 App」,現場成立有證據。F1 說的是另一個缺口:缺案例,不是現場走不到。這條合約沒有被破壞。
- `arch-alignment-lens`、`test-quality-handbook`:只是牽連檔相同,diff 不影響它們的行為。
- `bound-tests-gate`、`canary-audit`、`guard-kill`、`lumos-cli-lifecycle`、`slim-get-一行安裝`:合約的綁定測試各自獨立,這份 diff 沒改那些測試,也沒動 lumos 本體,不影響。
- 文件對照:README 中英文、驗證紀錄、`android-e2e-acceptance.md` 新增的 WHY 行,與程式一致。WHY 行寫的「開了記憶體與穩定性先查 trace_processor、宣告了測試資料再查 java_heap_dump」符合 `android-e2e-run.sh:254`。README 的回傳碼表(0、1、2)也符合 judge 與 `die` 的行為。`anchor-baseline.json` 的 test_lumos.py 雜湊更新是配合改測試檔,沒看出問題。

本次新檢查的邏輯與收集腳本一致、沒看出誤擋或漏擋,只有一個測試缺口(F1)要補一個「最外層有 stability、e2e 沒開」的案例。
