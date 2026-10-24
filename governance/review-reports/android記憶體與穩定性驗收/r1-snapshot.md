---
type: project
status: doing
created: 2026-10-24
updated: 2026-10-24
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/macrobenchmark-adapter
related:
  - "[[Projects/Android逐層診斷_計劃]]"
  - "[[Projects/Macrobenchmark驗收門檻_計劃]]"
  - "[[Projects/Android介面寫法分流_計劃]]"
  - "[[Projects/Android診斷證據接入_調研]]"
---
# Android記憶體與穩定性驗收_計劃

白話:Android 效能驗收補上記憶體與穩定性。主要防的是「第三方 SDK 有提供釋放的方法(release、close、destroy),App 卻忘了呼叫」造成的洩漏,不論 SDK 的物件在 Java 那一側還是第三方 .so 的原生記憶體。做法是量測、收集、判定三段分開:Macrobenchmark 在實機上跑「開畫面 → 用一下 → 關畫面」重複 N 輪,每輪錄 Perfetto 追蹤檔;收集腳本用一支查詢範本從追蹤檔算出每輪的記憶體數字、凍結幀與主執行緒阻塞,再從系統結束紀錄與 StrictMode 日誌留下測試期間的事件,寫成一份結果檔;`lumos macrobench` 照門檻檔判。記憶體那幾項沒過就直接接 [[Projects/Android逐層診斷_計劃]] 的 L3(記憶體層)往下查是誰留住記憶體。這是 Maestro 整合成 Android E2E 驗收(子案二)之前的子案一;量測只靠追蹤檔,子案二換驅動工具時收集與判定不用重做。實驗室指工具鏈作者本機的測試專案 macrobench-lab(`/Users/enzo/orca/workspaces/macrobench-lab`,本機 git、沒有遠端)。Enzo 2026-10-24 裁:「先補足記憶體與穩定性那一塊,再來整合mestro」「我是想防堵第三方有支援release,卻疏漏沒有呼叫,造成記憶體洩漏這類的問題」。

用到的詞:Java 堆積是 ART(Android 的執行環境)管的 Java/Kotlin 物件所佔的記憶體,ART 每次回收記憶體後記一次大小;匿名常駐記憶體是行程自己配置、系統沒辦法丟掉再讀回來的那部分(Java 堆積與原生配置都算在裡面),Android vitals 量的是它加 swap;原生記憶體在這裡指匿名常駐記憶體扣掉 Java 堆積,第三方 .so 用 C/C++ 配置的記憶體落在這裡;支配樹是記憶體快照裡「拿掉某個物件,底下哪些物件會跟著被回收」的結構,沿著它往上找得到是哪個欄位把一整串物件留住。

WHY:記憶體快照只在測試資料下錄(實驗室 App,或消費專案用測試帳號與假資料跑),快照原始檔只放專案 `.lumos/artifacts/android/<run-id>/`、不進版控、不上傳,本機保留 7 天後刪;進版控的只有查詢結果(類別名、實例數、大小、欄位名),不含物件內容。追蹤檔不是快照,不受 7 天限制,照舊留在產物目錄給收據重跑 [出處:2026-10-24 Enzo 選「只在測試資料下錄,本機留 7 天」] [因:記憶體快照可能含個資,原本 skill 寫「沒有人裁的保存規則,不錄 L3」,所以 L3 一直鎖著;只留結構不留內容,診斷要的「誰留住、哪個欄位」照樣拿得到;追蹤檔只有區段名、時間與計數,收據重跑要讀它] [不選:每次錄前問人(無人看顧時診斷會停在這一步);先不做診斷(洩漏只知道有、不知道是誰)]
WHY:洩漏情境固定寫成「開畫面 → 用一下 → 關畫面」重複 N 輪,不用同一個畫面裡滑動 [出處:2026-10-24 設計討論] [因:忘記 release 的洩漏只在「該釋放的時候沒釋放」才發生;只滑動時 SDK 物件只建一次,永遠漏不出來] [不選:沿用現有滑動基準當洩漏情境]
WHY:洩漏看兩條線:Java 堆積與原生記憶體,各自判趨勢,任一條持續上漲就不過;報告標明是哪一條 [出處:2026-10-24 Enzo 問「如果是第三方的 so 檔,看得出來嗎」] [因:第三方 .so 的配置不算在 Java 堆積裡,只看 Java 堆積時原生洩漏會判過] [不選:只看 Java 堆積]
WHY:洩漏用趨勢判:N 輪結束時的值一路往上(每一輪都不低於前一輪),而且最後一輪比第一輪多出超過容差,兩個條件同時成立;容差照 [[Systems/macrobenchmark-adapter]] 既有的規則取「第一輪值乘百分比」與「絕對值」兩者較大的 [出處:2026-10-24 設計討論] [因:回收記憶體的時間點不固定,單輪抖動大;要求連續上漲加總漲幅可擋掉抖動,換裝置也不太受影響;第一輪值接近 0 時只靠百分比會被正常抖動誤報] [代價:漏得很慢、N 輪內漲幅不到容差的洩漏抓不到;這種情況靠宣告類別的實例數那一項]
WHY:門檻檔可以宣告 SDK 類別的實例上限;只在洩漏情境、而且門檻檔宣告了類別時,N 輪全部量完之後錄一份 Java 堆積快照數實例,每次執行只錄這一份 [出處:2026-10-24 Enzo 選「照調和做:N 輪後錄一次」] [因:趨勢要漏夠多才看得出來,實例數一翻兩瞪眼(開關 5 次後應是 0 或 1 個);快照的支配樹同時指出是誰留住,也就是該在哪裡 release。[[Projects/Android逐層診斷_計劃]] 否決過「每次都錄 Trace、CPU 取樣與記憶體」(慢、改變被量對象、留下敏感檔),那條照留;這裡是例外:N 輪量完才錄所以不改變量到的數字,只錄一份所以慢的代價只有一次快照,敏感檔照保存規則] [代價:SDK 物件全在原生那一側時看不到,只剩原生趨勢那條線]
WHY:記憶體峰值分兩層:底線用 Android vitals 依裝置記憶體分級的前景上限(4 GB 裝置 2.00 GB、6 與 8 GB 2.25 GB、12 GB 3.25 GB、16 GB 4.25 GB,量的是匿名常駐記憶體加 swap),抓退步用 App 自己的基準加容差(容差規則同洩漏) [出處:2026-10-24 Enzo 問「峰值門檻該怎麼定義?有 google 的建議值嗎」;developer.android.com/google/play/vitals 2026-10-24 讀到的表] [因:官方數字有出處、不用人拍,但它是不被商店降級的天花板,一般 App 離它很遠,只抓得到災難級;真正抓「這次改動多吃記憶體」的是基準那層] [不選:只用官方數字;只用人拍的絕對值]
WHY:主執行緒只用 700ms(凍結幀)當硬門檻,單次阻塞的門檻由人在門檻檔自訂、不訂就只回報 [出處:2026-10-24 查 developer.android.com/google/play/vitals/render] [因:官方寫明「No frames in your app should ever take longer than 700ms」;比這更細的數字官方沒給,不拍一個] [不選:預設 200ms(沒有出處)]
WHY:崩潰、原生崩潰、ANR、被記憶體上限殺掉(Android 17 起,結束原因 REASON_OTHER 且描述含 MemoryLimiter:AnonSwap)只要測試期間有一筆就不過;用測試開始的時間點過濾系統結束紀錄 [出處:2026-10-24 Enzo 選「崩潰與 ANR 歸零」;android-developers.googleblog.com 2026/08 app-broader-memory-limits] [因:Android vitals 的 1.09% 與 0.47% 是線上使用者比例,不適合單次測試;系統結束紀錄會留著之前的舊紀錄,不過濾的話上週的崩潰會害這次不過]
WHY:StrictMode 的 VM 規則(可關閉物件沒 close、註冊沒取消、Activity 被留住)在測試建置打開,違規寫進日誌,收集腳本讀出來,一筆就不過 [出處:2026-10-24 設計討論] [因:平台內建、零依賴,抓得到平台機制寫的資源] [代價:第三方 SDK 自己管的資源多半看不到,所以只當補充]
WHY:代碼審的「成對方法」靜態提醒(專案宣告取得與釋放、改動有取得沒釋放就出題)不在這個子案做,移到後續另案 [出處:2026-10-24 Enzo 選「移到後續另案」] [因:前掃讀程式發現現在的代碼審題目是寫死在 lumos 的一張表,沒有「讀專案設定出題」這條路,等於新建一套機制;它也是這份計劃動到守衛面的唯一來源;先讓實機那幾層跑過、知道常見漏法再設計] [不選:留在子案一一起做;改成只印不要表態(容易被忽略)]
WHY:量測、收集、判定三段分開;收集腳本放工具鏈範本目錄、照抄進消費專案,判定加在 `lumos macrobench` 與既有門檻檔 [出處:2026-10-24 Enzo 同意「從 Perfetto 追蹤檔算」的做法] [因:量測只靠追蹤檔,子案二 Maestro 跑時一樣錄追蹤檔,收集與判定不用重做;診斷也從同一份追蹤檔往下查;Lumos 不跑第三方工具,trace_processor 與 adb 只在範本腳本與 skill 裡用] [不選:直接讀 Macrobenchmark 結果檔的記憶體指標(數字綁死在 Macrobenchmark,Maestro 要再接一次);lumos 在測試外面用 adb 前後各查一次(太粗,抓不到峰值與漲勢)]
WHY:門檻檔的每一條加一個選填的 `kind` 欄位(leak、instances、peak、exits、strictmode、frozen);沒寫 `kind` 的照舊是 Macrobenchmark 結果檔的單值門檻,寫了的讀收集結果檔;每種有自己的必填欄位,`scenario`、`contract`、`decided_by`、`decided_at` 照舊必填 [出處:2026-10-24 前掃讀 `lumos macrobench` 的門檻檢查,現行每條只收一個有限的上限或下限] [因:趨勢、實例數、官方底線都不是單一上下限,硬塞進 max 會讓「用官方底線」寫成假數字;既有門檻檔不用改] [不選:另開一個門檻檔(兩個檔要同步合約與裝置);另開一個指令(多一種做法)]
WHY:這個子案的判定照舊只提醒、不擋推送 [出處:2026-10-23 Enzo 裁「效能門檻沒達只提醒、不擋」;2026-10-24 Enzo 為 E2E 驗收選「擋合併,人可留痕放行」與「本機實機跑,CI 驗收據」] [因:擋合併要的是本機跑出綁版本的收據、CI 驗收據那一整套,這套在子案二才建;子案一先擋會讓現有推送突然被擋] [applies:子案二上線前]
PRIOR-ART: Jetpack Macrobenchmark 的 MemoryUsageMetric(Mode.Last 取每輪結束值、Mode.Max 取最大值;子指標 HeapSize、RssAnon、RssFile、Gpu、RssShmem,developer.android.com reference 2026-10-24 讀到);Perfetto 的 linux.process_stats 資料來源(proc_stats_poll_ms 至少 100ms,產生 mem.rss.anon、mem.swap 等行程計數);Perfetto heapprofd(原生堆積呼叫鏈)與 Java 堆積快照(支配樹),工具名與用法以 lumos-android-evidence skill 的 L3 段為準;Android 的 ApplicationExitInfo 與 StrictMode VM 規則;Android vitals 的記憶體與凍結幀門檻。LeakCanary 是業界抓 Java 洩漏的標準函式庫,能讓測試遇到洩漏就失敗並指出誰留住,但它要改消費專案的 App 依賴,列成消費專案自選、不當驗收必要條件。借用:Macrobenchmark 與 Perfetto 的量測,自建只有查詢範本、收集腳本與判定。
RETIRE-IF: Android Studio 或 Macrobenchmark 內建「重複進出畫面判洩漏」的指標並輸出可比對的結果,就撤掉趨勢判定改讀官方;或連續兩個真實專案跑滿三個月,六種記憶體與穩定性檢查都零觸發而且沒有後來才發現的洩漏,就把這一層從驗收拿掉、只留診斷。
REVISIT:2026-11-21 洩漏的輪數(預設 5)與容差、Java 堆積計數在追蹤檔裡的實際名稱與取樣頻率、「每輪結束值」是不是回收後的值(沒有強制回收時),實驗室真的跑過之後校準,把代擬值換成量到的數字
REVISIT:2027-02-28 Google 說記憶體門檻 2027 年 2 月起影響商店曝光,到時重讀 developer.android.com/google/play/vitals 的表,數字變了就改門檻判定裡的對照表
REVISIT:2027-01-31 子案一在實驗室與一個真實專案跑過之後,重新設計代碼審的「成對方法」靜態提醒(取得沒釋放就出題),決定題目從哪裡來、會不會擋推送

## 一份驗收看什麼(六種檢查)

| 檢查 | 訊號從哪來 | 判不過的條件 |
|---|---|---|
| 洩漏(Java 與原生兩條線) | 「開畫面 → 用一下 → 關畫面」N 輪,每輪結束時的 Java 堆積與原生記憶體 | 任一條 N 個數字一路往上、而且最後一輪比第一輪多出超過容差 |
| 宣告類別的實例數 | N 輪量完後錄的一份 Java 堆積快照 | 門檻檔宣告的類別實例數超過上限 |
| 記憶體峰值 | 每輪匿名常駐記憶體加 swap 的最大值 | 超過 Android vitals 依裝置記憶體分級的前景上限,或超過自己的基準加容差 |
| 崩潰、ANR、被系統殺掉 | 系統結束紀錄,只留測試期間 | 有一筆就不過 |
| StrictMode 違規 | 測試期間的日誌 | 有一筆就不過 |
| 凍結幀與主執行緒阻塞 | 追蹤檔 | 有一幀超過 700ms 就不過;單次阻塞的門檻人訂,不訂只回報 |

## 資料怎麼流

1. 量測(消費專案、實機):Macrobenchmark 的洩漏情境掛 MemoryUsageMetric,讓每輪追蹤檔都錄到記憶體計數;N 輪量完,門檻檔宣告了類別才錄一份 Java 堆積快照;最後用 adb 存系統結束紀錄、日誌與裝置總記憶體。
2. 收集(工具鏈範本 `scripts/templates/` 底下的收集腳本與查詢範本,照抄進消費專案):讀每輪追蹤檔、快照、結束紀錄、日誌與裝置總記憶體;用查詢範本算每輪一列數字;結束紀錄與 StrictMode 只留測試開始之後的;寫成結果檔 `.lumos/artifacts/android/<run-id>/stability.json`,欄位:
   - `scenario`、`device_model`、`total_mem_mb`、`started_utc`
   - `rounds`:每輪一筆,`round`(字串,例 r1)、`java_heap_end_kb`、`native_end_kb`、`rss_anon_swap_peak_kb`、`frozen_frames`、`max_main_block_ms`;量不到的欄位寫 null,不寫 0
   - `instances`:類別名對實例數(沒錄快照時整欄不出現)
   - `exits`:每筆 `kind`(crash、native_crash、anr、memory_limiter)、`ts`、`desc`
   - `strictmode`:每筆 `kind`
3. 判定(`lumos macrobench --stability <結果檔>`):門檻檔裡寫了 `kind` 的條目對結果檔判,六種各自判;每條照舊指回一條合約;輸出沿用 threshold_failures、threshold_passed、threshold_skipped 與原因,只提醒、回 0。
4. 診斷(skill 的 L3):洩漏、實例數或峰值沒過,直接進 L3,不先走 L1、L2(那兩層看 CPU 時間,記憶體問題在那裡看不到);Java 那側查支配樹找到留住的欄位,原生那側用原生堆積分析找到呼叫鏈;第三方 .so 沒有符號時停在「哪支 .so、哪個位移、App 哪一行呼叫的」,標成第三方沒有符號。凍結幀或阻塞沒過照原本 L1 走;結束紀錄與 StrictMode 沒過看紀錄裡的現場。
5. 收據:查詢範本可整份貼進收據,用現有的重跑腳本從追蹤檔重算出同樣的數字;查詢輸出第一欄是字串鍵(輪次 r1、r2…),因為重跑腳本拿第一欄的字串比對;快照 7 天後刪,收據裡的實例數只留結果,不重算。

## 這次要改到的地方

- 工具鏈:`lumos macrobench` 加 `--stability` 與門檻的 `kind`;`scripts/templates/` 新增收集腳本與查詢範本,登記工具組複製清單、帶 SPDX 檔頭;家節點 [[Systems/macrobenchmark-adapter]] 的負責範圍改成「讀 Macrobenchmark 結果檔與收集結果檔」。
- skill:lumos-android-evidence 的 L3 段與「沒有人裁的保存規則不錄 L3」那兩處,改成照本計劃的保存規則;加上「記憶體檢查沒過直接進 L3」與「第三方 .so 沒符號停在哪」。
- 圖譜:[[Projects/Android逐層診斷_計劃]] 的 S6(沒有保存裁定時停在 L2)記成被本計劃的保存規則取代。
- 實驗室:洩漏情境、假 SDK、沒符號的 .so、StrictMode 設定。

## 實務隱患

- 已排除:金流:不碰任何交易或點數,只讀測試裝置上的量測資料。
- 已排除:對外送出:量測、收集與判定都在本機跑,原始檔不上傳;記憶體快照只在測試資料下錄,進版控的只有結構不含內容。
- 已排除:不可逆:判定唯讀;快照放產物目錄、7 天後刪,刪的是可重錄的量測檔。
- 已排除:守衛面:判定照舊只提醒、回 0,不新增擋推送或擋提交的檢查;代碼審的成對方法題移到後續另案。
- 系統結束紀錄的文字格式會隨 Android 版本改:收集腳本只讀原因、時間與描述三個欄位,測試用不同版本的樣本各一份。
- 回收記憶體的時間點不固定:趨勢判定要求連續上漲加總漲幅兩個條件,輪數與容差先用代擬值,見 REVISIT。
- 沒有符號的 .so 診斷只到位移:報告照實標出停在哪一層,不假裝查到函式。
- 快照可能含個資:只准在測試資料下錄,不在使用者裝置或正式資料上錄。

## 條款

- [S1] 當 N 輪結束時的 Java 堆積一路往上、而且最後一輪比第一輪多出超過容差時,lumos macrobench 應把那條洩漏檢查列成沒過,並標明是 Java 那條線 [test:t_android_memstab_leak_java_trend]
- [S2] 當 Java 堆積是平的、原生記憶體一路往上超過容差時,lumos macrobench 應把洩漏檢查列成沒過,並標明是原生那條線 [test:t_android_memstab_leak_native_trend]
- [S3] 當 N 輪的數字有升有降、或一路往上但總漲幅不到容差、或第一輪值接近 0 而漲幅只超過百分比沒超過絕對值時,lumos macrobench 應把洩漏檢查列成通過 [test:t_android_memstab_leak_jitter_passes]
- [S4] 當門檻檔宣告某個類別的實例上限、收集結果裡那個類別的實例數超過上限時,lumos macrobench 應列成沒過並印出類別名與實例數;結果檔沒有 instances 欄時列成跳過 [test:t_android_memstab_instance_limit]
- [S5] 當峰值檢查寫「用官方底線」時,lumos macrobench 應依收集結果裡的裝置總記憶體查 Android vitals 的前景上限表判定;4 GB 以下或 16 GB 以上沒有官方數字時列成跳過並說原因 [test:t_android_memstab_peak_vitals_floor]
- [S6] 當峰值檢查寫基準加容差、這次峰值超過時,lumos macrobench 應列成沒過 [test:t_android_memstab_peak_baseline]
- [S7] 當系統結束紀錄裡有崩潰、原生崩潰、ANR 或描述含 MemoryLimiter 的紀錄時,收集腳本應只留下測試開始之後的那幾筆、標出是哪一種,lumos macrobench 有一筆就列成沒過 [test:t_android_memstab_exit_info_window]
- [S8] 當測試期間的日誌有 StrictMode 的 VM 違規時,收集腳本應留下違規種類,lumos macrobench 有一筆就列成沒過 [test:t_android_memstab_strictmode]
- [S9] 當追蹤檔裡有一幀超過 700ms 時,查詢範本應算出凍結幀數,lumos macrobench 列成沒過;單次阻塞沒設門檻時只回報最長那次 [test:t_android_memstab_frozen_frame]
- [S10] 當查詢範本拿到一份追蹤檔的記憶體計數與幀資料時,應輸出一列,第一欄是輪次字串,其後是 Java 堆積結束值、原生記憶體結束值、峰值、凍結幀數、最長阻塞;計數是空的欄位輸出空值而不是 0 [test:t_android_memstab_query_rows]
- [S11] 當收集結果缺了門檻要用的欄位、或欄位值是 null 時,lumos macrobench 應把那條列成跳過並說缺哪一欄,不得列成通過 [test:t_android_memstab_missing_field_skipped]
- [S12] 當查詢範本與收集腳本加進工具鏈時,應帶 SPDX 檔頭、登記在工具組複製清單、跟其他範本一起進消費專案 [test:t_android_memstab_vendored]
- [S13] 當門檻檔的條目沒寫 kind 時,lumos macrobench 應照舊對 Macrobenchmark 結果檔判單值門檻,既有門檻檔的判定結果不變;寫了不認得的 kind 或缺了那種的必填欄位時應擋下並說原因 [test:t_android_memstab_kind_compat]
- [S14] 當實驗室 App 有一個「開畫面 → 用一下 → 關畫面」的洩漏情境、正常版跑五輪時,六種檢查應全過 [manual:macrobench-lab 實機跑一次,lumos macrobench 的判定與收據存進 macrobench-lab,寫進驗證紀錄]
- [S15] 當實驗室分別埋入「假 SDK 在 Java 留物件、關畫面時不呼叫 release」與「沒有符號的 .so 漏原生記憶體、關畫面時不呼叫 release」時,每種都應被對應的檢查擋下,診斷分別指到該在哪裡 release,以及哪支 .so、App 哪一行呼叫的 [manual:兩種各跑一次 skill,收據 L3 那筆寫明留住的欄位或 .so 位移與呼叫行;寫進驗證紀錄]
- [S16] 當 skill 要錄記憶體快照時,應先確認跑的是測試資料、快照原始檔只放產物目錄,並提示 7 天後刪 [manual:讀 skill 的 L3 段,實驗室錄一次確認檔案位置與 .gitignore]

## 回退

- 判定只提醒不擋,出錯時把門檻檔裡寫了 kind 的條目拿掉就回到現狀;查詢範本與收集腳本是新檔,撤掉不影響既有的效能門檻與收據;skill 的 L3 改動回退成「沒有保存規則不錄」即可。
