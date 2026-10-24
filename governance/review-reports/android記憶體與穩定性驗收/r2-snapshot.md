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

白話:Android 效能驗收補上記憶體與穩定性。主要防的是「第三方 SDK 有提供釋放的方法(release、close、destroy),App 卻忘了呼叫」造成的洩漏,不論 SDK 的物件在 Java 那一側還是第三方 .so 的原生記憶體。做法分三段:驅動工具(現在是 UI Automator 測試,子案二換成 Maestro)只負責在同一個行程裡「開畫面 → 用一下 → 關畫面」;工具鏈範本裡的收集腳本在主機端排順序——開始前讀一次系統結束紀錄、跑暖機、錄第一份 Java 快照、邊錄追蹤檔邊跑 N 輪、錄第二份 Java 快照並查「沒人指著的原生記憶體」、最後再讀一次結束紀錄——寫成一份結果檔;`lumos macrobench --stability` 照門檻檔判。沒過就接 [[Projects/Android逐層診斷_計劃]] 的 L3(記憶體層)查是誰。這是 Maestro 整合成 Android E2E 驗收(子案二)之前的子案一;子案二只要換驅動指令,收集與判定不動。實驗室指工具鏈作者本機的測試專案 macrobench-lab(`/Users/enzo/orca/workspaces/macrobench-lab`,本機 git、沒有遠端)。Enzo 2026-10-24 裁:「先補足記憶體與穩定性那一塊,再來整合mestro」「我是想防堵第三方有支援release,卻疏漏沒有呼叫,造成記憶體洩漏這類的問題」「也可以上網搜業界做法,不用土法煉鋼」。

用到的詞:Java 快照指 Perfetto 的 java_hprof 資料來源錄下的 Java 堆積參照圖(哪個物件指著哪個,不含字串與位元組內容),查詢時只算「還有人指著」(reachable)的物件,等於回收之後的樣子;沒人指著的原生記憶體指 Android 內建 libmemunreachable(`dumpsys meminfo --unreachable <pid>`)掃出來、程式裡已經沒有任何指標指著的 malloc 區塊,第三方 SDK 的 Java 物件被丟掉卻沒呼叫 release 時,它配的原生記憶體就落在這裡;Native Heap 指 `dumpsys meminfo <套件>` 裡獨立的那一列;支配樹是快照裡「拿掉某個物件,底下哪些物件會跟著被回收」的結構,沿著它往上找得到是哪個欄位把一整串物件留住。

WHY:原生洩漏的主判定用「沒人指著的原生記憶體」大於 0 就不過,Native Heap 的趨勢只回報不判 [出處:2026-10-24 實驗室實測 spike/native-leak 分支(做完已刪)] [因:同一個行程開關畫面 5 輪,關畫面沒呼叫 release 時 Native Heap 7036→16104 KB、沒人指著的原生記憶體 10485760 位元組 5 塊(正好 5 輪 × 2 MB);有呼叫 release 時 0 位元組,但 Native Heap 4660、7088、7248、9448、7488 KB 有升有降,只看趨勢正常版也會誤判;非除錯版(profileable)照樣跑得動] [不選:匿名常駐記憶體扣掉 Java 堆積(會把 Java 已回收沒還的頁算成原生);只看 Native Heap 趨勢] [代價:SDK 在原生那側自己另留一份清單、還指著那塊記憶體時不算「沒人指著」,抓不到;這種只剩 Native Heap 趨勢當線索,診斷靠 L3 的原生堆積分析]
WHY:Java 洩漏借 LeakCanary 3.0 堆積增長偵測的思路:暖機 W 輪後錄第一份 Java 快照、再跑 N 輪後錄第二份,比對每個類別還有人指著的實例數,增加量達到「N × 每輪至少多幾個」(預設 1)的類別判不過並列出;快照用 Perfetto 的 java_hprof,不用 `am dumpheap` [出處:2026-10-24 調研(square.github.io/leakcanary/changelog、blog.p-y.wtf/cutting-some-slack-for-leaks-and-giggles)與實驗室實測] [因:LeakCanary 的架構跟這裡一樣(另一個行程重複跑情境、對目標 App 錄快照、比物件增長),不看堆積總量,所以不受回收時間點影響(實驗室沒有洩漏的情境五輪結束時的堆積 15584、13084、28292、21400、12368 KB,忽高忽低兩倍);`am dumpheap -g` 在 SM-X710 Android 16 上對 profileable 的基準建置回 SecurityException: Process not debuggable,官方文件說 profileable 就可以,實機不行;Perfetto java_hprof 對同一個 App 錄得到 15 MB 快照,用 trace_processor 數得出每個類別的實例數] [不選:LeakCanary 本身(它靠 am dumpheap,非除錯版用不了;分析用 Shark 是 Kotlin 函式庫,不能放進零依賴的判定);每輪結束值判趨勢(上面那組數字)]
WHY:門檻檔可以宣告 SDK 類別的實例上限,用第二份 Java 快照數 [出處:2026-10-24 設計討論;2026-10-24 Enzo 選「照調和做:N 輪後錄一次」] [因:增長偵測要漏夠多輪才看得出來,宣告類別一翻兩瞪眼;快照的支配樹同時指出是誰留住,也就是該在哪裡 release。[[Projects/Android逐層診斷_計劃]] 否決過「每次都錄 Trace、CPU 取樣與記憶體」(慢、改變被量對象、留下敏感檔),那條照留;這裡是例外:快照在暖機後與 N 輪後才錄所以不改變 N 輪期間量到的數字,每次只錄兩份,java_hprof 不含字串與位元組內容,敏感檔照保存規則] [代價:SDK 物件全在原生那一側時看不到,只剩原生那項;benchmark 建置開了 R8 時類別名會被混淆,宣告的類別要寫 keep 規則或寫混淆後的名字]
WHY:Java 快照只在專案宣告了測試資料時才錄:`.lumos/macrobench.json` 的 `stability.test_data` 要是 true(人寫的宣告),否則收集腳本不錄快照、Java 那兩項列成跳過並說原因;快照原始檔只放專案 `.lumos/artifacts/android/<run-id>/`、不進版控、不上傳;收集腳本每次開跑先刪掉這個專案產物目錄底下超過 7 天的快照檔(只刪 `heap-*.pftrace`);進版控的只有查詢結果(類別名、實例數、大小、欄位名) [出處:2026-10-24 Enzo 選「只在測試資料下錄,本機留 7 天」;2026-10-24 設計審 r1 指出「確認是測試資料」沒有機械判法、「7 天後刪」沒有執行者] [因:記憶體快照可能含個資,原本 skill 寫「沒有人裁的保存規則,不錄 L3」,所以 L3 一直鎖著;用人寫的宣告取代 AI 自述,無人看顧時照樣有根據;刪除綁在每次執行上,不需要背景程序] [不選:每次錄前問人(無人看顧時診斷會停在這一步);先不做診斷(洩漏只知道有、不知道是誰);skill 自己判斷是不是測試資料(只能是 AI 自述)]
WHY:沒人指著的原生記憶體只留總位元組數與塊數,丟掉它附印的每塊開頭內容 [出處:2026-10-24 調研(libmemunreachable README:輸出含位址、大小與前 32 位元組)] [因:開頭內容可能是使用者資料,判定只要總量]
WHY:驅動工具只負責「開畫面 → 用一下 → 關畫面」的操作,同一個行程裡做完,不殺行程;收集腳本在主機端呼叫驅動兩次(暖機 W 輪、量測 N 輪),中間與前後由收集腳本自己用 adb 量 [出處:2026-10-24 設計審 r1(Macrobenchmark 冷啟動每輪殺行程、在裝置上跑的測試插不進主機端錄快照的時間點、子案二 Maestro 沒有每輪一份追蹤檔)] [因:記憶體要跨輪累積才看得出漏,行程不能被殺;快照與原生掃描都要在 App 還活著時從主機下;驅動指令寫在設定裡,子案二換成 Maestro 指令即可] [不選:用 Macrobenchmark 的 measureRepeated 與 MemoryUsageMetric(冷啟動殺行程;每輪結束值會抖;記憶體指標進結果檔後還會被既有的退步比對用毫秒容差誤報)]
WHY:收集腳本在 N 輪期間錄一份 Perfetto 追蹤檔(錄製設定是工具鏈範本),從它算記憶體峰值、凍結幀與主執行緒最長阻塞 [出處:2026-10-24 Enzo 選「主執行緒卡住」與峰值兩層;設計審 r1 指出錄製設定不能留在 Macrobenchmark 裡] [因:峰值要連續取樣才抓得到,幀與阻塞要追蹤檔;錄製設定放範本,換驅動工具也照用]
WHY:記憶體峰值這個子案只做官方底線:Android vitals 依裝置可用記憶體分級的前景上限(可用記憶體 3200–4800 MB 為 2.00 GB、4800–6800 MB 為 2.25 GB、6800–9216 MB 為 2.25 GB、9216–14336 MB 為 3.25 GB、14336–18432 MB 為 4.25 GB,含下界不含上界;低於 3200 或至少 18432 沒有官方數字),量的是匿名常駐記憶體加 swap;裝置可用記憶體用 `/proc/meminfo` 的 MemTotal 換成 MB。抓退步用自己的基準那層移到 [[Projects/Android效能判定統計化_計劃]] [出處:2026-10-24 Enzo 問「峰值門檻該怎麼定義?有 google 的建議值嗎」;developer.android.com/google/play/vitals 2026-10-24 讀到的表與區間;設計審 r1 指出基準存哪、容差單位都沒定] [因:官方數字有出處、不用人拍;基準那層要存每輪原始值與記憶體單位的容差,跟統計化計劃的第一條是同一件事] [代價:官方底線很寬,只抓得到災難級]
WHY:主執行緒只用 700ms(凍結幀)當硬門檻:Android 12 以上用追蹤檔的幀時間線(actual_frame_timeline_slice),沒有幀時間線時用主執行緒的 Choreographer#doFrame 區段;單次阻塞取主執行緒最上層區段裡最長的那個,只回報、人可在門檻檔另設上限 [出處:2026-10-24 查 developer.android.com/google/play/vitals/render;設計審 r1 指出幀與阻塞的來源沒定] [因:官方寫明「No frames in your app should ever take longer than 700ms」;比這更細的數字官方沒給,不拍一個;暖機輪不錄追蹤檔,首次載入不算] [不選:預設 200ms(沒有出處)]
WHY:崩潰、原生崩潰、ANR、被記憶體上限殺掉(Android 17 起,描述含 MemoryLimiter)用前後比對:開跑前與跑完後各讀一次 `dumpsys activity exit-info <套件>`,多出來的那幾筆(用 pid 加 timestamp 比)就是測試期間的;另外行程 pid 前後不同也算不過 [出處:2026-10-24 實驗室實測(`am crash` 兩秒後就讀得到新的那筆,reason=4 APP CRASH);調研(AppExitInfoTracker 原始碼:套件名精確比對、時間是裝置本地時間不帶時區)] [因:前後比對不用換時區、不受裝置與主機時鐘偏差影響,也不會讀到別的 App;Android vitals 的 1.09% 與 0.47% 是線上使用者比例,不適合單次測試] [不選:用測試開始時間過濾(時區與時鐘偏差)]
WHY:StrictMode 的 VM 規則(可關閉物件沒 close、註冊沒取消、Activity 被留住)要消費專案在測試用的建置自己打開,`.lumos/macrobench.json` 的 `stability.strictmode` 宣告有沒有開;沒宣告就列成跳過;收集腳本開跑前清日誌緩衝、跑完讀出 StrictMode 那幾行,一筆就不過 [出處:2026-10-24 設計討論;設計審 r1 指出沒開時恆為零筆、也要改 App 程式碼] [因:平台內建、零依賴;但要改 App,沒開卻判通過就是假綠] [代價:第三方 SDK 自己管的資源多半看不到;可關閉物件要等被回收才印]
WHY:每一種來源都要留「收得到」的證明:結果檔每個來源帶 `status`(ok、failed、unsupported)與原因;不是 ok 的,對應檢查列成跳過並說原因,不得列成通過 [出處:2026-10-24 設計審 r1(解析不到時空陣列會被當成沒事)] [因:這類守衛最常見的失效是「讀不到所以全綠」]
WHY:代碼審的「成對方法」靜態提醒(專案宣告取得與釋放、改動有取得沒釋放就出題)不在這個子案做,移到後續另案 [出處:2026-10-24 Enzo 選「移到後續另案」] [因:現在的代碼審題目是寫死在 lumos 的一張表,沒有「讀專案設定出題」這條路,等於新建一套機制;它也是這份計劃動到守衛面的唯一來源] [不選:留在子案一一起做;改成只印不要表態(容易被忽略)]
WHY:門檻檔的每一條加一個選填的 `check` 欄位(native_unreachable、java_growth、instances、peak_vitals、exits、strictmode、frozen);沒寫 `check` 的照舊是 Macrobenchmark 結果檔的單值門檻、驗證與判定完全不變;寫了的不需要 metric、stat、max、min,改驗各自的欄位,`scenario`、`contract`、`decided_by`、`decided_at` 照舊必填 [出處:2026-10-24 前掃與設計審 r1(現行每條只收一個有限的上限或下限;`kind` 這個名字在 macrobench 已有兩種意思)] [因:這幾種檢查不是單一上下限,硬塞進 max 會寫出假數字;既有門檻檔不用改] [不選:另開一個門檻檔(兩個檔要同步合約與裝置);另開一個指令(多一種做法);沿用 `kind` 當欄位名]
WHY:判定照舊只提醒、不擋推送 [出處:2026-10-23 Enzo 裁「效能門檻沒達只提醒、不擋」;2026-10-24 Enzo 為 E2E 驗收選「擋合併,人可留痕放行」與「本機實機跑,CI 驗收據」] [因:擋合併要的是本機跑出綁版本的收據、CI 驗收據那一整套,這套在子案二才建] [applies:子案二上線前]
PRIOR-ART: LeakCanary 3.0 的堆積增長偵測(leakcanary-android-uiautomator,另一個行程重複跑情境、比對連續快照的物件增長);Android 內建 libmemunreachable(`dumpsys meminfo --unreachable`);Perfetto java_hprof 與 heapprofd(L3 診斷,用法以 lumos-android-evidence skill 為準);`dumpsys activity exit-info`(ApplicationExitInfo);StrictMode VM 規則;Android vitals 的記憶體分級表與 700ms 凍結幀;Firebase Test Lab 與 Square 用測試結束標記與 RunListener 收崩潰(只參考)。借用:LeakCanary 的偵測思路、平台內建的掃描與紀錄;自建只有收集腳本、兩支查詢範本、錄製設定與判定。騰訊 Matrix、快手 KOOM 要編進 App,不適合外部驗收,不採用。
RETIRE-IF: LeakCanary 或 Android 官方出了不需要除錯版、輸出機器可讀的外部洩漏偵測,就撤掉自己的 Java 增長比對改用它;或連續兩個真實專案跑滿三個月,這幾項檢查都零觸發而且沒有後來才發現的洩漏,就把這一層從驗收拿掉、只留診斷。
REVISIT:2026-11-21 暖機輪數 W(預設 2)、量測輪數 N(預設 5)、Java 增長的每輪門檻(預設 1),在實驗室正常版與注入版各跑三次之後校準;正常版若有類別也照樣增長(快取、字串),決定要不要加排除清單
REVISIT:2027-02-28 Google 說記憶體門檻 2027 年 2 月起影響商店曝光,到時重讀 developer.android.com/google/play/vitals 的表,數字變了就改峰值判定裡的對照表
REVISIT:2027-01-31 子案一在實驗室與一個真實專案跑過之後,重新設計代碼審的「成對方法」靜態提醒(取得沒釋放就出題),決定題目從哪裡來、會不會擋推送
REVISIT:[when-file:scripts/templates/android-stability-collect.sh][by:2027-04-30] 第一個真實專案用收集腳本跑過時,確認 `dumpsys meminfo --unreachable` 在它的 Android 版本與廠牌上跑得動、`am crash` 之外的真實崩潰也讀得到

## 一份驗收看什麼(七種檢查)

| check | 訊號從哪來 | 判不過的條件 |
|---|---|---|
| native_unreachable | N 輪後 `dumpsys meminfo --unreachable` 的總位元組 | 大於門檻(預設 0) |
| java_growth | 暖機後與 N 輪後兩份 Java 快照,每個類別還有人指著的實例數 | 有類別的增加量達到 N × 每輪門檻 |
| instances | N 輪後那份 Java 快照 | 宣告的類別實例數超過上限 |
| peak_vitals | N 輪期間追蹤檔的匿名常駐記憶體加 swap 最大值 | 超過裝置分級的官方前景上限 |
| exits | 前後兩次系統結束紀錄的差異、行程 pid 前後是否相同 | 多出任何一筆,或 pid 變了 |
| strictmode | N 輪期間的日誌 | 有一筆 StrictMode 違規 |
| frozen | N 輪期間的追蹤檔 | 有一幀超過 700ms;阻塞另設上限時,最長阻塞超過上限 |

另外 Native Heap 前後兩個數字只回報,當原生那項的佐證。

## 資料怎麼流

1. 設定:`.lumos/macrobench.json` 加 `stability` 段:`package`、`driver_warmup`(跑暖機的指令)、`driver_cycles`(跑量測輪的指令,收集腳本把輪數用環境變數 `CYCLES` 傳給它)、`warmup`(W)、`cycles`(N)、`test_data`、`strictmode`、`declared_classes`。驅動指令例:UI Automator 測試用 `adb shell am instrument -w -e class <測試類別>#<方法> -e cycles $CYCLES <測試套件>/androidx.test.runner.AndroidJUnitRunner`,子案二換成 `maestro test <flow>`。
2. 收集(工具鏈範本 `scripts/templates/android-stability-collect.sh`,照抄進消費專案;trace_processor 用 `${TP:-trace_processor}` 找,跟收據重跑腳本同一個做法;每個 adb 與 trace_processor 呼叫都有逾時,中途失敗也刪暫存檔):
   1. 刪產物目錄底下超過 7 天的快照檔;清日誌緩衝;讀裝置 MemTotal 與 Android 版本;讀一次結束紀錄(前)。
   2. 啟動 App,跑暖機指令;記下 pid。
   3. test_data 是 true 才錄第一份 Java 快照;讀 Native Heap(前)。
   4. 開始錄追蹤檔(範本錄製設定:行程記憶體計數、幀時間線、App 的區段),跑量測輪指令,停止錄製。
   5. test_data 是 true 才錄第二份 Java 快照;跑 `dumpsys meminfo --unreachable <pid>` 只留總位元組與塊數;讀 Native Heap(後);讀 pid。
   6. 讀一次結束紀錄(後),比出多的那幾筆;讀日誌裡的 StrictMode 行。
   7. 用兩支查詢範本算數字(`android-stability-cycle.sql` 對追蹤檔、`android-heap-classes.sql` 對兩份快照),寫成 `.lumos/artifacts/android/<run-id>/stability.json`。
3. 結果檔欄位:`scenario`、`device_model`、`android_sdk`、`total_mem_mb`、`warmup`、`cycles`;每個來源一段,各帶 `status` 與 `reason`:`unreachable`(bytes、allocations)、`heap`(before、after:類別名對實例數;沒錄時 status 是 unsupported)、`native_heap_kb`(before、after)、`cycle_trace`(peak_anon_swap_kb、frozen_frames、max_main_block_ms、frames)、`exits`(新增的每筆 kind、pid、timestamp、desc;pid_changed)、`strictmode`(每筆違規種類)。
4. 判定(`lumos macrobench --stability <結果檔>`):只判門檻檔裡寫了 `check` 的條目;沒給 `--stability` 時這些條目列成跳過、原因寫「沒給結果檔」;專案沒有 `.lumos/macrobench.json` 也照判;結果檔讀不了或格式不對回 2 並印「擋下:」;輸出沿用 threshold_failures、threshold_passed、threshold_skipped,每筆帶 `check` 與那一種的明細(java_growth 列出增長的類別與增加量,native_unreachable 印位元組與塊數);只提醒、回 0。
5. 診斷(skill):native_unreachable 或 java_growth、instances 沒過,直接進 L3,不先走 L1、L2(那兩層看 CPU 時間,記憶體問題在那裡看不到):Java 那側在第二份快照上查支配樹找到留住的欄位;原生那側用 heapprofd 重跑一次 N 輪,看沒釋放的配置是誰呼叫的;第三方 .so 沒有符號時停在「哪支 .so、哪個位移、App 哪一行呼叫的」,標成第三方沒有符號。frozen 沒過照原本 L1;exits 與 strictmode 沒過看紀錄裡的現場。
6. 收據:兩支查詢範本可整份貼進收據,用現有的重跑腳本從追蹤檔與快照重算;查詢第一欄是字串鍵(追蹤檔那支輸出一列、鍵是 cycle;快照那支每個類別一列、鍵是類別名);空值用 COALESCE 換成 -1,重跑比對才寫得出 expect;快照 7 天後刪,刪了之後收據裡跟快照有關的數字標成不能重跑。

## 這次要改到的地方

- 工具鏈 `scripts/lumos`:`lumos macrobench` 加 `--stability` 與門檻的 `check` 欄位與七種判定;門檻驗證只對沒寫 `check` 的條目套原規則;判定輸出與印字照 `check` 分支。
- 工具鏈範本 `scripts/templates/`:新增收集腳本、兩支查詢範本、錄製設定,帶 SPDX 檔頭、登記工具組複製清單。
- 家節點 [[Systems/macrobenchmark-adapter]]:`about_code` 加新的四支範本;負責範圍改成「Lumos 本體讀 Macrobenchmark 結果檔與收集結果檔、不接裝置;範本腳本(收集、重跑)才接裝置」。
- skill lumos-android-evidence:L3 段與「沒有人裁的保存規則不錄 L3」兩處改成照本計劃的保存規則;L0 的往下條件加 `--stability` 的判定結果;記憶體檢查沒過直接進 L3;第三方 .so 沒符號停在哪;reference.md 加結果檔與 `check` 的寫法。
- skill lumos-project-notes:reference.md 與 commands/04-自檢與健康.md 的 macrobench 指令說明加 `--stability`。
- 圖譜:[[Projects/Android逐層診斷_計劃]] 的 S6(沒有保存裁定時停在 L2)與「L3 預設關閉」記成被本計劃的保存規則取代;[[Projects/Macrobenchmark驗收門檻_計劃]] 的 S5(缺必填欄位回 2)補一句「只對沒寫 check 的條目」。
- 實驗室:一個 UI Automator 的開關畫面情境、假 SDK(Java 留物件)、沒有符號的 .so(漏原生記憶體)、StrictMode 設定、`.lumos/macrobench.json` 的 stability 段。

## 實務隱患

- 已排除:金流:不碰任何交易或點數,只讀測試裝置上的量測資料。
- 已排除:對外送出:量測、收集與判定都在本機跑,原始檔不上傳;快照只在宣告了測試資料時錄,進版控的只有結構不含內容。
- 已排除:不可逆:判定唯讀;收集腳本只刪自己產物目錄底下超過 7 天的 `heap-*.pftrace`,刪的是可重錄的量測檔。
- 已排除:守衛面:判定照舊只提醒、回 0,不新增擋推送或擋提交的檢查;代碼審的成對方法題移到後續另案。
- 系統結束紀錄的文字格式會隨 Android 版本改:收集腳本只讀 pid、timestamp、reason、description,標頭用行首比對且不分大小寫;解析不到時那個來源的 status 是 failed,判定列成跳過。
- `dumpsys meminfo --unreachable` 的前提官方文件沒寫:實驗室 SM-X710 Android 16 的 profileable 建置實測可以;跑不動時那項列成跳過,REVISIT 綁第一個真實專案。
- Java 增長偵測會被正常的快取與字串增長干擾:暖機先把快取填滿;輪數與門檻是代擬值,正常版仍有類別增長時加排除清單(見 REVISIT)。
- 沒有符號的 .so 診斷只到位移:報告照實標出停在哪一層,不假裝查到函式。
- 快照可能含個資:java_hprof 不含字串與位元組內容;只准在宣告了測試資料的專案錄。

## 條款

- [S1] 當結果檔的沒人指著的原生記憶體大於門檻時,lumos macrobench 應把 native_unreachable 那條列成沒過並印出位元組與塊數;等於門檻時列成通過 [test:t_android_memstab_native_unreachable]
- [S2] 當兩份快照裡某個類別的實例數增加量達到 N × 每輪門檻時,lumos macrobench 應把 java_growth 那條列成沒過並列出那些類別與增加量;增加量少一個時列成通過 [test:t_android_memstab_java_growth]
- [S3] 當門檻檔宣告某個類別的實例上限、第二份快照裡那個類別超過上限時,lumos macrobench 應列成沒過並印出類別名與實例數;快照裡沒有那個類別時算 0 個 [test:t_android_memstab_instance_limit]
- [S4] 當 peak_vitals 判定時,lumos macrobench 應依結果檔的 total_mem_mb 照官方區間查前景上限(含下界不含上界),超過就列成沒過;低於 3200 或至少 18432 時列成跳過並說原因 [test:t_android_memstab_peak_vitals_floor]
- [S5] 當結果檔的 exits 有新增的紀錄、或 pid_changed 是 true 時,lumos macrobench 應列成沒過並印出每筆的種類 [test:t_android_memstab_exits]
- [S6] 當收集腳本拿到前後兩份結束紀錄時,應只留下後一份多出來的那幾筆(用 pid 加 timestamp 比),並把崩潰、原生崩潰、ANR、描述含 MemoryLimiter 分成四種;標頭格式不同或解析不到時那個來源的 status 是 failed [test:t_android_memstab_exit_info_diff]
- [S7] 當結果檔有 StrictMode 違規時,lumos macrobench 應列成沒過;設定沒宣告 strictmode 時應列成跳過並說原因 [test:t_android_memstab_strictmode]
- [S8] 當結果檔的凍結幀數大於 0 時,lumos macrobench 應把 frozen 那條列成沒過;門檻另設了阻塞上限、最長阻塞超過時也列成沒過;沒設時只回報最長阻塞 [test:t_android_memstab_frozen_frame]
- [S9] 當追蹤檔查詢範本拿到一份追蹤檔時,應輸出一列,第一欄是字串 cycle,其後是匿名常駐記憶體加 swap 的最大值(swap 取每個時間點之前最近一次的值)、凍結幀數(有幀時間線用幀時間線,沒有用 doFrame)、主執行緒最長的最上層區段、幀數;量不到的欄位輸出 -1 [test:t_android_memstab_cycle_query]
- [S10] 當快照查詢範本拿到一份 Java 快照時,應每個類別輸出一列、第一欄是類別名,只算還有人指著的物件 [test:t_android_memstab_heap_query]
- [S11] 當結果檔某個來源的 status 不是 ok、或欄位缺、或值是 -1 時,lumos macrobench 應把用到它的那條列成跳過並說原因,不得列成通過 [test:t_android_memstab_source_not_ok_skipped]
- [S12] 當收集腳本、兩支查詢範本與錄製設定加進工具鏈時,應帶 SPDX 檔頭、登記在工具組複製清單、跟其他範本一起進消費專案 [test:t_android_memstab_vendored]
- [S13] 當門檻檔的條目沒寫 check 時,lumos macrobench 應照舊對 Macrobenchmark 結果檔判單值門檻,既有門檻檔的判定結果不變;寫了不認得的 check 或缺了那種的必填欄位時應回 2 並說原因;沒給 --stability 時寫了 check 的條目列成跳過 [test:t_android_memstab_check_compat]
- [S14] 當給了 --stability 而專案沒有 .lumos/macrobench.json 時,lumos macrobench 應照樣判寫了 check 的條目;結果檔讀不了或不是 JSON 時應回 2 並印擋下 [test:t_android_memstab_stability_without_config]
- [S15] 當設定的 test_data 不是 true 時,收集腳本不應錄 Java 快照,結果檔的 heap 來源 status 是 unsupported;是 true 時收集腳本開跑先刪掉產物目錄底下超過 7 天的 heap-*.pftrace、不刪別的檔 [test:t_android_memstab_collect_test_data_gate]
- [S16] 當實驗室 App 的開關畫面情境正常版跑時(暖機 2 輪、量測 5 輪),七種檢查應全過 [manual:macrobench-lab 實機跑一次收集腳本與 lumos macrobench --stability,判定與收據存進 macrobench-lab,寫進驗證紀錄]
- [S17] 當實驗室分別埋入「假 SDK 在 Java 留物件、關畫面時不呼叫 release」與「沒有符號的 .so 漏原生記憶體、關畫面時不呼叫 release」時,前者應被 java_growth 與 instances 擋下、後者應被 native_unreachable 擋下,診斷分別指到留住的欄位,以及哪支 .so、App 哪一行呼叫的 [manual:兩種各跑一次收集腳本與 skill,收據 L3 那筆寫明留住的欄位或 .so 位移與呼叫行;寫進驗證紀錄]
- [S18] 當實驗室用 am crash 讓 App 在量測輪中崩潰時,exits 應列成沒過 [manual:實驗室跑一次,判定存進驗證紀錄]

## 回退

- 判定只提醒不擋,出錯時把門檻檔裡寫了 check 的條目拿掉就回到現狀;收集腳本、查詢範本與錄製設定是新檔,撤掉不影響既有的效能門檻與收據;skill 的 L3 改動回退成「沒有保存規則不錄」即可。
