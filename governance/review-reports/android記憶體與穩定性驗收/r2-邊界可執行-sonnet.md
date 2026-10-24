severity: major

總覽:已逐節讀完。第 3 節(結果檔欄位)、第 5 節(診斷)、StrictMode 以外的 WHY(WHY 2、3、5)、PRIOR-ART、RETIRE-IF 與回退節已讀,無 finding。碰到的風險類逐類答在最後。實機只做了唯讀查詢:SM-X710、Android 16、MemTotal 7386728 kB(約 7213 MB)。

1. exits 的判定寫了兩套互相矛盾的條件
severity: major
blocking: 是——照表格字面實作,正常測試也會被判不過,會做錯決定。
引句:「多出任何一筆,或 pid 變了」
- 表格與 S5 說只要多一筆就不過,S6 卻只分崩潰、原生崩潰、ANR、MemoryLimiter 四種。
- 實機上同一份 exit-info 的 reason 有 10 USER REQUESTED、13 OTHER KILLS BY SYSTEM、21 FORCE STOP、24 KILL BACKGROUND、14 FREEZER、15 STATE CHANGE 等,都不是崩潰。
- 場景:收集腳本在「讀前」之後為了乾淨啟動做 `am force-stop`,或量測輪關畫面進背景被系統回收。這時 exits 一定多出 reason=21、13 或 24 的紀錄,正常版被判紅。
- 要明定只有哪幾個 reason 算不過,其餘只回報。
- 佐證:`scripts/lumos:39675`(判定走單一分支,沒有依 reason 過濾的既有做法)、`adb shell dumpsys activity exit-info` 實測輸出。

2. 沒有結束紀錄的套件會被判成 failed,而不是空
severity: major
blocking: 是——全新安裝或乾淨裝置第一次跑,exits 恆為跳過,不符合守衛的目的。
引句:「標頭格式不同或解析不到時那個來源的 status 是 failed」
- 實機對不存在或沒有紀錄的套件執行 `dumpsys activity exit-info com.nonexistent.pkg.zzz`,只印兩行全域標頭:「ACTIVITY MANAGER PROCESS EXIT INFO」和「Last Timestamp of Persistence…」。沒有 `package:` 區段。
- 這是合法的「零筆歷史」。spec 沒區分「零筆」與「格式變了」。
- 照字面,前讀看不到套件區段就是解析失敗。更糟的是:前讀零筆、後讀有一筆崩潰,也可能被判成 failed 而跳過,真崩潰變成沒判。
- 要定義:全域標頭在、套件區段不在是空集合;全域標頭也沒有才是 failed。
- 順帶:同一份輸出最多 16 筆(實機 `ApplicationExitInfo #15` 為上限)。紀錄環滿了後用 pid+timestamp 比對仍成立,但 spec 沒寫。

3. 驅動指令失敗或逾時沒有地方記錄,會假綠
severity: major
blocking: 是——UI 找不到元件時,量測輪實際上沒跑完,卻是全綠。
引句:「收集腳本在主機端呼叫驅動兩次」
- 結果檔的來源清單(unreachable、heap、native_heap_kb、cycle_trace、exits、strictmode)沒有「驅動」這一項。S11 只管來源 status。
- 場景:`am instrument` 因元件找不到而回非零(或逾時),或只跑了 1 輪就失敗,但 App 沒崩潰。pid 沒變、exits 空、unreachable 為 0、heap 增量為 0。全部通過,但實際沒有量到 N 輪。
- `am instrument -w` 在測試失敗時照樣可能以 exit 0 結束,只在輸出印 FAILURES。spec 沒說判斷方式。
- 要加 `driver` 來源:warmup 和 cycles 的結束狀態與實跑輪數,不是 ok 就整份跳過。
- 補充 ⚠:`am instrument` 結束時,系統可能會強停被測目標套件(`finished inst`)。該行為我沒在實機驗證。若 instrumentation 的 targetPackage 是 App 本體而非測試套件,pid 會在兩次驅動之間改變,pid_changed 恆為真。
- 實驗室找不到 instrumentation 設定,spec 的例子也沒寫目標套件。

4. frozen 在沒有任何幀時判通過
severity: major
blocking: 是——錄不到幀就是沒量到,卻判通過。
引句:「當結果檔的凍結幀數大於 0 時,lumos macrobench 應把 frozen 那條列成沒過」
- S9 的欄位有 frames。S8 和 S11 只在值是 -1 時才跳過。
- 場景:App 在背景、被殺、或畫面沒更新、追蹤檔沒抓到 Choreographer 區段,frozen_frames=0 且 frames=0。照字面是通過。
- 要定義 frames==0 時 frozen 跳過。
- 補充:`doFrame` 區段的名稱帶幀號(`Choreographer#doFrame 12345`),要用前綴比對。它只量主執行緒那一段,不等於 vitals 說的整幀 700ms。這會讓沒有幀時間線的退路偏鬆(minor)。
- 佐證:官方 vitals/render 的 700ms 定義是整幀。

5. StrictMode 靠日誌緩衝,可能被擠掉或讀到別人的行
severity: major
blocking: 是——會產生「一筆就不過」的反向假綠。
引句:「收集腳本開跑前清日誌緩衝、跑完讀出 StrictMode 那幾行,一筆就不過」
- 場景 1:N 輪加暖機時間很長,SM-X710 這類 Samsung 裝置的 logcat 緩衝(預設約 256KB 量級)被系統與其他 App 的訊息輪替掉,早期的 StrictMode 行消失。status 仍是 ok,判成通過。
- 場景 2:logcat 的 tag 是 StrictMode,但沒有過濾 pid 或 uid。別的行程的違規會被算進來,正常版判紅。
- 要加 `--pid` 或 uid 過濾,並在輪前後確認緩衝沒溢出(例如放大緩衝、或從日誌第一行時間判斷有沒有被擠掉),讀不出來時標 failed。

6. W=0、N=0 或每輪門檻為 0 時 java_growth 的語意沒定義
severity: minor
blocking: 否——只在設定錯誤時發作,但失敗樣子是全部類別都紅。
引句:「某個類別的實例數增加量達到 N × 每輪門檻時」
- 場景:cycles=0 或每輪門檻 0,任何類別的增加量 0 都「達到」0。幾萬個類別全部列為增長。
- W=0 時第一份快照在首次載入前,首次載入的類別數全算成增長,必然紅。
- 要驗證 cycles≥1、每輪門檻>0,warmup 為 0 時至少警告。
- 佐證:`scripts/lumos:39632` 的欄位驗證只收 max/min,現行沒有這類欄位檢查可沿用。

7. native_unreachable 預設 0 沒有基準
severity: minor
⚠
blocking: 否——判不準,實驗室的乾淨 SDK 是 0。
引句:「大於門檻(預設 0)」
- 只量 N 輪後的絕對值,不是暖機後與 N 輪後的差。
- 場景:某些 GPU 或廠商驅動(Mali、Adreno)的 libmemunreachable 掃描常有非零的基線,這類 App 恆紅。⚠ 我沒在實機驗證這類基線。
- 建議暖機後也掃一次取差,或明定預設會因裝置而異。
- 另外,0 筆時 `--unreachable` 的輸出文字沒驗證,spec 要寫出沒有找到時的解析結果,不能解析不到就當 failed。
- 實機只確認 `dumpsys meminfo --help` 有 `--unreachable` 選項,沒真的對 App 掃(避免影響行程)。

8. 收據的重跑腳本對快照查詢有兩個限制
severity: minor
blocking: 否——重跑時才發現,可以寫在範本註解處理。
引句:「查詢第一欄是字串鍵(追蹤檔那支輸出一列、鍵是 cycle;快照那支每個類別一列、鍵是類別名)」
- 重跑腳本一條查詢只對一個 `trace=`(`scripts/templates/android-receipt-rerun.sh:58`)。兩份快照要寫成兩條 Q,差值只能由 lumos 算。
- 它用 `split(',')` 加首列相符的第一筆(`android-receipt-rerun.sh:65`、`:67`)。同名類別出現在不同 classloader 時只取第一筆,重跑會比出假差異。
- 類別數上萬時結果檔也會有數萬列。建議只存有增減的類別與宣告類別。

9. 峰值對照表只對一般 App,遊戲的上限不同
severity: minor
blocking: 否——只影響遊戲類專案,且是偏嚴。
引句:「超過裝置分級的官方前景上限」
- 我讀官方 vitals 頁,分級區間與 spec 一致(含下界、不含上界,低於 3200 與高於 18432 沒有數字),`MemoryInfo.totalMem` 等同 MemTotal 換成 MB,吻合。
- 但官方表另有遊戲欄:4 GB 為 2.25、6 GB 為 2.75、8 GB 為 3.50、12 GB 為 4.00、16 GB 為 5.00。spec 只用一般 App 欄。
- 遊戲專案會被用較低的上限誤判。要在門檻檔加 app 或 game 類型。

10. 追蹤檔錄製的結束沒定義
severity: minor
blocking: 否。
引句:「開始錄追蹤檔(範本錄製設定:行程記憶體計數、幀時間線、App 的區段),跑量測輪指令,停止錄製」
- 沒寫 duration_ms、緩衝大小,也沒寫怎麼停止與拉檔(perfetto 背景模式的 pid 或 `--stop`)。
- 場景:N 輪比設定的時長長,錄製自己結束,後半段沒有資料。峰值被低估,卻判通過。
- `linux.process_stats` 的 `proc_stats_poll_ms` 最短約 100 ms,短於此的尖峰會漏。這是設計限制。

極端輸入逐類答覆
- App 暖機或量測中途被殺:exits 與 pid_changed 能抓到,但見 #1(誤報)與 #2(零筆格式)。快照對死 pid 會失敗,依 #3 補驅動狀態後可正確跳過。
- 驅動失敗或逾時:見 #3。
- 快照錄到一半:有 status 機制可跳過,已讀,無 finding。
- 快照超大、類別數上萬:見 #8。
- unreachable 在別的廠牌或版本:見 #7 與 REVISIT 的綁定,spec 已有跳過路徑。
- exit-info 前後重疊、順序不同、pid 重用:用 pid+timestamp 集合比對,不受順序影響,pid 重用不會撞(timestamp 不同),已讀,無 finding。紀錄環最多 16 筆,見 #2 的補充。
- 日誌緩衝被擠掉:見 #5。
- 追蹤檔沒有幀時間線:見 #4。
- 裝置記憶體剛好在分級邊界:區間符合官方,已讀,無 finding。
- N=0 或 W=0:見 #6。
- test_data 宣告與實際不符:純人寫宣告,spec 已明說這是設計取捨;java_hprof 不含字串內容,已讀,無 finding。
- 可執行性:`heap_graph_object.reachable` 和 `process_stats` 計數 `mem.rss.anon`、`mem.swap` 可行。`am dumpheap` 不行的結論與 spec 一致,未再驗證。

總結:最高嚴重度 major,blocking 共 5 條
