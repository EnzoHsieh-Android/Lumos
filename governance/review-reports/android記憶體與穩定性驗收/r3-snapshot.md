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
  - Systems/android-stability-collector
related:
  - "[[Projects/Android逐層診斷_計劃]]"
  - "[[Projects/Macrobenchmark驗收門檻_計劃]]"
  - "[[Projects/Android介面寫法分流_計劃]]"
  - "[[Projects/Android診斷證據接入_調研]]"
---
# Android記憶體與穩定性驗收_計劃

白話:Android 效能驗收補上記憶體與穩定性。主要防的是「第三方 SDK 有提供釋放的方法(release、close、destroy),App 卻忘了呼叫」造成的洩漏,不論 SDK 的物件在 Java 那一側還是第三方 .so 的原生記憶體。做法分三段:驅動(現在是 UI Automator 測試,子案二換成 Maestro)只負責在同一個行程裡「開畫面 → 用一下 → 關畫面」;工具鏈範本裡的收集腳本在主機端排順序——讀一次系統結束紀錄、跑暖機、錄第一份 Java 快照並掃一次沒人指著的原生記憶體、邊錄追蹤檔與日誌邊跑 N 輪、再錄第二份快照並再掃一次、最後再讀一次結束紀錄——寫成一份結果檔;`lumos macrobench --stability` 照門檻檔判。沒過就接 [[Projects/Android逐層診斷_計劃]] 的 L3(記憶體層)查是誰。這是 Maestro 整合成 Android E2E 驗收(子案二)之前的子案一。實驗室指工具鏈作者本機的測試專案 macrobench-lab(`/Users/enzo/orca/workspaces/macrobench-lab`,本機 git、沒有遠端)。Enzo 2026-10-24 裁:「先補足記憶體與穩定性那一塊,再來整合mestro」「我是想防堵第三方有支援release,卻疏漏沒有呼叫,造成記憶體洩漏這類的問題」「也可以上網搜業界做法,不用土法煉鋼」。

用到的詞:Java 快照指 Perfetto 的 java_hprof 資料來源錄下的 Java 堆積參照圖(哪個物件指著哪個,不含字串與位元組內容),由 lumos-android-evidence skill 原本就在用的 `java_heap_dump` 腳本錄;查詢時只算「還有人指著」(reachable)的物件,等於回收之後的樣子;沒人指著的原生記憶體指 Android 內建 libmemunreachable(`dumpsys meminfo --unreachable <pid>`)掃出來、程式裡已經沒有任何指標指著的 malloc 區塊,第三方 SDK 的 Java 物件被丟掉卻沒呼叫 release 時,它配的原生記憶體就落在這裡;Native Heap 指 `dumpsys meminfo <套件>` 裡獨立的那一列;支配樹是快照裡「拿掉某個物件,底下哪些物件會跟著被回收」的結構,沿著它往上找得到是哪個欄位把一整串物件留住;自己測自己的 instrumentation 指測試 APK 的 targetPackage 是測試套件本身(Macrobenchmark 模組就是這種),跑測試時不會重啟被測 App。

WHY:原生洩漏用「沒人指著的原生記憶體」在暖機後與 N 輪後各掃一次,差值大於門檻(預設 0 位元組)就不過;Native Heap 前後兩個數字只回報 [出處:2026-10-24 實驗室實測 spike/native-leak 分支(做完已刪);設計審 r2 指出只看 N 輪後的絕對值會被廠商驅動的基線誤判] [因:同一個行程開關畫面 5 輪,關畫面沒呼叫 release 時沒人指著的原生記憶體 10485760 位元組 5 塊(正好 5 輪 × 2 MB)、Native Heap 7036→16104 KB;有呼叫 release 時 0 位元組,Native Heap 4660、7088、7248、9448、7488 KB 有升有降;非除錯版(profileable)照樣跑得動;用差值扣掉 App 本來就有的部分] [不選:匿名常駐記憶體扣掉 Java 堆積(會把 Java 已回收沒還的頁算成原生);只看 Native Heap 趨勢;只看 N 輪後的絕對值] [代價:SDK 在原生那側自己另留一份清單、還指著那塊記憶體時不算「沒人指著」,抓不到;這種只剩 Native Heap 前後數字當線索,診斷靠 L3 的原生堆積分析]
WHY:Java 洩漏借 LeakCanary 3.0 堆積增長偵測的思路:暖機 W 輪後錄第一份 Java 快照、再跑 N 輪後錄第二份,比對每個類別還有人指著的實例數,增加量至少「N × 每輪門檻」(預設 1)的類別判不過並列出;預設不算 java.、javax.、kotlin.、android.、androidx.、dalvik.、libcore.、sun. 開頭的類別與基本型別陣列,門檻檔可以改排除清單 [出處:2026-10-24 調研(square.github.io/leakcanary/changelog、blog.p-y.wtf/cutting-some-slack-for-leaks-and-giggles)與實驗室實測;設計審 r2 指出 String、byte[] 這類平台型別在真實 App 幾乎必增長] [因:LeakCanary 的架構跟這裡一樣(另一個行程重複跑情境、對目標 App 錄快照、比物件增長),不看堆積總量,所以不受回收時間點影響(實驗室沒有洩漏的情境五輪結束時的堆積 15584、13084、28292、21400、12368 KB,忽高忽低兩倍);沒有釋放的 SDK 會留下它自己的類別,平台型別的增長多半是快取與字串,混進來會讓真實專案第一次就全紅] [不選:LeakCanary 本身(它靠 `am dumpheap`,在 SM-X710 Android 16 上對 profileable 的建置回 SecurityException: Process not debuggable;分析用 Shark 是 Kotlin 函式庫,不能放進零依賴的判定);每輪結束值判趨勢(上面那組數字)]
WHY:Java 快照沿用 skill 原本的 `java_heap_dump` 腳本錄(收集腳本用環境變數 `JAVA_HEAP_DUMP` 找它,沒設就找 PATH 上的,跟 trace_processor 用 `TP` 同一個做法),不另寫一份錄製設定 [出處:2026-10-24 設計審 r2 架構對齊席] [因:同一份快照兩種錄法,接手的人要猜哪個對;skill 已釘 Perfetto v57.2 的腳本]
WHY:門檻檔的 instances 條目宣告 SDK 類別的實例上限,用第二份快照數;類別在第二份快照沒有算 0 個,兩份快照都沒有就列成跳過並說「類別不在快照(拼錯或被混淆?)」 [出處:2026-10-24 設計討論;2026-10-24 Enzo 選「照調和做:N 輪後錄一次」;設計審 r2 指出拼錯或混淆時算 0 會假綠] [因:增長偵測要漏夠多輪才看得出來,宣告類別一翻兩瞪眼;快照的支配樹同時指出是誰留住,也就是該在哪裡 release。[[Projects/Android逐層診斷_計劃]] 否決過「每次都錄 Trace、CPU 取樣與記憶體」(慢、改變被量對象、留下敏感檔),那條照留;這裡是例外:快照在暖機後與 N 輪後才錄所以不改變 N 輪期間量到的數字,每次只錄兩份,java_hprof 不含字串與位元組內容,敏感檔照保存規則] [代價:SDK 物件全在原生那一側時看不到,只剩原生那項;release 建置開了 R8 時類別名會被混淆,宣告的類別要寫 keep 規則或寫混淆後的名字]
WHY:Java 快照只在專案宣告了測試資料時才錄:`.lumos/macrobench.json` 的 `stability.test_data` 要寫成 `{"value": true, "decided_by": …, "decided_at": …}`(人寫的宣告),否則收集腳本不錄快照、java_growth 與 instances 列成跳過並說原因;快照原始檔只放專案 `.lumos/artifacts/android/<run-id>/`、檔名 `heap-*.pftrace`、不進版控、不上傳,裝置上的暫存檔錄完就刪;收集腳本每次開跑先刪掉這個專案產物目錄底下超過 7 天的 `heap-*.pftrace`;skill 的 L3 手動錄的快照也用同一個檔名樣式,一起被刪;進版控的只有查詢結果(類別名、實例數、大小、欄位名) [出處:2026-10-24 Enzo 選「只在測試資料下錄,本機留 7 天」;設計審 r1、r2 指出「確認是測試資料」沒有機械判法、7 天後刪沒有執行者、裝置端與 L3 的檔不在範圍] [因:記憶體快照可能含個資,原本 skill 寫「沒有人裁的保存規則,不錄 L3」,所以 L3 一直鎖著;用帶署名與日期的人寫宣告取代 AI 自述,無人看顧時照樣有根據;刪除綁在每次執行上,不需要背景程序] [不選:每次錄前問人(無人看顧時診斷會停在這一步);skill 自己判斷是不是測試資料(只能是 AI 自述)] [代價:專案不再跑收集腳本時舊快照不會被刪;AI 改設定檔就能打開宣告,這屬單人工具鏈的信賴範圍]
WHY:沒人指著的原生記憶體只留總位元組數與塊數,丟掉它附印的每塊開頭內容 [出處:2026-10-24 調研(libmemunreachable README:輸出含位址、大小與前 32 位元組)] [因:開頭內容可能是使用者資料,判定只要總量]
WHY:驅動要在同一個行程裡做完,不殺行程:UI Automator 驅動必須是自己測自己的 instrumentation;Maestro 驅動的 flow 不能用會停 App 的 launchApp(要寫 stopApp: false 或不啟動)、輪數用 `maestro test -e CYCLES=…` 傳、兩次呼叫都從同一個約定的起點畫面開始。收集腳本在主機端呼叫驅動兩次(暖機 W 輪、量測 N 輪),驅動指令裡的 `{cycles}` 換成輪數;暖機前、暖機後、量測後三次讀 pid,不一樣就把 exits 列成不過並說 pid 變了 [出處:2026-10-24 設計審 r1(冷啟動殺行程)、r2(三席都指出:instrumentation 啟動時通常會重啟目標 App,source.android.com/docs/core/tests/development/instrumentation;Maestro 的 launchApp 預設先停 App)] [因:記憶體要跨輪累積才看得出漏,行程不能被殺;快照與原生掃描都要在 App 還活著時從主機下] [不選:用 Macrobenchmark 的 measureRepeated 與 MemoryUsageMetric(冷啟動殺行程;每輪結束值會抖;記憶體指標進結果檔後還會被既有的退步比對用毫秒容差誤報)]
WHY:驅動本身也是一個來源:收集腳本記下兩次驅動的回傳碼與輸出;UI Automator 驅動要看到 `INSTRUMENTATION_CODE: -1` 且沒有 `FAILURES!!!`,Maestro 驅動要回傳碼 0;不是就把 driver 來源記成 failed,整份結果的每一條都列成跳過 [出處:2026-10-24 設計審 r2 邊界席(UI 找不到元件時量測輪沒跑完,其他數字照樣全綠)] [因:`am instrument -w` 測試失敗時回傳碼照樣可能是 0]
WHY:收集腳本在 N 輪期間錄一份 Perfetto 追蹤檔(錄製設定是工具鏈範本:行程記憶體計數每 250ms 取樣一次、幀時間線、App 的區段,錄製上限 `stability.max_record_s` 預設 600 秒),從它算記憶體峰值、凍結幀與主執行緒最長阻塞;N 輪跑完還沒到上限就由收集腳本停止錄製,到了上限 N 輪還沒跑完就把 cycle_trace 記成 failed [出處:2026-10-24 Enzo 選「主執行緒卡住」與峰值兩層;設計審 r1 指出錄製設定不能留在 Macrobenchmark 裡;r2 指出錄製的結束沒定義] [因:峰值要連續取樣才抓得到,幀與阻塞要追蹤檔;錄製設定放範本,換驅動工具也照用] [代價:取樣間隔 250ms,比它短的尖峰會漏]
WHY:記憶體峰值這個子案只做官方底線:Android vitals 依裝置可用記憶體分級的前景上限,量的是匿名常駐記憶體加 swap;區間含下界不含上界:一般 App 3200–4800 MB 為 2.00 GB、4800–6800 MB 為 2.25 GB、6800–9216 MB 為 2.25 GB、9216–14336 MB 為 3.25 GB、14336–18432 MB 為 4.25 GB;遊戲依序為 2.25、2.75、3.50、4.00、5.00 GB,設定 `stability.category` 寫 game 才用;低於 3200 或至少 18432 沒有官方數字;裝置可用記憶體用 `/proc/meminfo` 的 MemTotal 換成 MB(官方要的 ActivityManager.MemoryInfo.totalMem 就是它)。抓退步用自己的基準那層移到 [[Projects/Android效能判定統計化_計劃]] 的第 6 條 [出處:2026-10-24 Enzo 問「峰值門檻該怎麼定義?有 google 的建議值嗎」;developer.android.com/google/play/vitals 2026-10-24 讀到的表與區間(設計審 r2 邊界席另讀一次核對一致)] [因:官方數字有出處、不用人拍;基準那層要存每次的數字與記憶體單位的容差,跟統計化計劃一起做] [代價:官方底線很寬,只抓得到災難級]
WHY:主執行緒只用 700ms(凍結幀)當硬門檻:Android 12 以上用追蹤檔的幀時間線(actual_frame_timeline_slice),沒有幀時間線時用主執行緒名稱以 Choreographer#doFrame 開頭的區段;追蹤檔裡一幀都沒有時 frozen 列成跳過;單次阻塞取主執行緒最上層區段裡最長的那個,只回報、人可在門檻檔另設上限 [出處:2026-10-24 查 developer.android.com/google/play/vitals/render;設計審 r1 指出幀與阻塞的來源沒定;r2 指出沒有幀時會判通過] [因:官方寫明「No frames in your app should ever take longer than 700ms」;比這更細的數字官方沒給,不拍一個;暖機輪不錄追蹤檔,首次載入不算] [代價:沒有幀時間線時 doFrame 只量主執行緒那一段,比官方的整幀寬鬆] [不選:預設 200ms(沒有出處)]
WHY:崩潰類事件用前後比對:開跑前與跑完後各讀一次 `dumpsys activity exit-info <套件>`,後一次多出來的(用 pid 加 timestamp 比)才是測試期間的;其中崩潰(reason 4)、原生崩潰(5)、ANR(6)、低記憶體被殺(3)、記憶體上限(描述含 MemoryLimiter)五種判不過,其他原因(使用者要求、系統回收背景等)只回報;輸出有全域標頭但沒有這個套件的區段時是零筆、status ok,連全域標頭都沒有才是 failed [出處:2026-10-24 實驗室實測(`am crash` 兩秒後就讀得到新的那筆,reason=4 APP CRASH;不存在的套件只印兩行全域標頭);調研(AppExitInfoTracker 原始碼:套件名精確比對、時間是裝置本地時間不帶時區);設計審 r2 指出系統回收與強制停止也會產生紀錄] [因:前後比對不用換時區、不受時鐘偏差影響,也不會讀到別的 App;Android vitals 的 1.09% 與 0.47% 是線上使用者比例,不適合單次測試] [代價:每個套件只留最近十幾筆,測試期間新增超過這個數會漏;單次測試很少到]
WHY:StrictMode 的 VM 規則(可關閉物件沒 close、註冊沒取消、Activity 被留住)要消費專案在測試用的建置自己打開,`.lumos/macrobench.json` 的 `stability.strictmode` 宣告有沒有開;沒宣告就列成跳過;收集腳本在 N 輪期間把這個 pid 的日誌持續串流到主機(`adb logcat --pid`),不清裝置的共用緩衝,串流中斷就把 strictmode 記成 failed;有一筆 StrictMode 違規就不過 [出處:2026-10-24 設計討論;設計審 r1 指出沒開時恆為零筆;r2 指出日誌緩衝會被擠掉、會讀到別的行程、清緩衝影響整台裝置] [因:平台內建、零依賴;但要改 App,沒開卻判通過就是假綠] [代價:宣告了卻沒真的開,零筆照樣判通過,只有實驗室那條人工驗收會發現;第三方 SDK 自己管的資源多半看不到;可關閉物件要等被回收才印]
WHY:每一種來源都要分得出「收到了、是零」和「沒收到」:結果檔每個來源帶 `status`(ok、failed、unsupported)與原因;不是 ok 的,用到它的檢查列成跳過並說原因,不得列成通過;結果檔與門檻裡的數字一律走既有的「只收有限數」檢查,門檻不是有限數回 2,結果不是有限數列成跳過 [出處:2026-10-24 設計審 r1(解析不到時空陣列會被當成沒事)、r2(NaN 讓「大於門檻」恆假,[[Systems/macrobenchmark-adapter]] 記過的 PITFALL)] [因:這類守衛最常見的失效是「讀不到所以全綠」]
WHY:代碼審的「成對方法」靜態提醒(專案宣告取得與釋放、改動有取得沒釋放就出題)不在這個子案做,移到後續另案 [出處:2026-10-24 Enzo 選「移到後續另案」] [因:現在的代碼審題目是寫死在 lumos 的一張表,沒有「讀專案設定出題」這條路,等於新建一套機制;它也是這份計劃動到守衛面的唯一來源] [不選:留在子案一一起做;改成只印不要表態(容易被忽略)]
WHY:門檻檔的每一條加一個選填的 `check` 欄位;沒寫 `check` 的照舊是 Macrobenchmark 結果檔的單值門檻、驗證與判定完全不變;寫了的不需要 metric、stat、max、min,改驗下表各自的欄位,`scenario`、`contract`、`decided_by`、`decided_at` 照舊必填,`device_model` 照舊選填並照舊篩裝置;`scenario` 要等於結果檔的 scenario,不等就列成跳過 [出處:2026-10-24 前掃與設計審 r1、r2(現行每條只收一個有限的上限或下限;`kind` 這個名字在 macrobench 已有兩種意思;各 check 的欄位沒列)] [因:這幾種檢查不是單一上下限,硬塞進 max 會寫出假數字;既有門檻檔不用改] [不選:另開一個門檻檔(兩個檔要同步合約與裝置);另開一個指令(多一種做法);沿用 `kind` 當欄位名]
WHY:`.lumos/macrobench.json` 有 `stability` 段時,`results_dirs` 可以不填(只做穩定性的專案);兩個都沒有才算沒接;`--stability` 吃一份結果檔的路徑,不掃目錄 [出處:2026-10-24 設計審 r2(現行要求非空的 results_dirs,只做穩定性的專案會被回 2)] [因:每次收集各自一個 run-id 目錄,掃目錄會挑到別次的結果;一個情境一份結果檔,多情境就跑多次]
WHY:判定照舊只提醒、不擋推送 [出處:2026-10-23 Enzo 裁「效能門檻沒達只提醒、不擋」;2026-10-24 Enzo 為 E2E 驗收選「擋合併,人可留痕放行」與「本機實機跑,CI 驗收據」] [因:擋合併要的是本機跑出綁版本的收據、CI 驗收據那一整套,這套在子案二才建] [applies:子案二上線前]
PRIOR-ART: LeakCanary 3.0 的堆積增長偵測(leakcanary-android-uiautomator,另一個行程重複跑情境、比對連續快照的物件增長);Android 內建 libmemunreachable(`dumpsys meminfo --unreachable`);Perfetto java_hprof(經 skill 的 java_heap_dump 腳本)與 heapprofd(L3 診斷,用法以 lumos-android-evidence skill 為準);`dumpsys activity exit-info`(ApplicationExitInfo);StrictMode VM 規則;Android vitals 的記憶體分級表與 700ms 凍結幀;Firebase Test Lab 與 Square 用測試結束標記與 RunListener 收崩潰(只參考)。借用:LeakCanary 的偵測思路、平台內建的掃描與紀錄、skill 既有的快照腳本;自建只有收集腳本、兩支查詢範本、錄製設定與判定。騰訊 Matrix、快手 KOOM 要編進 App,不適合外部驗收,不採用。
RETIRE-IF: LeakCanary 或 Android 官方出了不需要除錯版、輸出機器可讀的外部洩漏偵測,就撤掉自己的 Java 增長比對改用它;或連續兩個真實專案跑滿三個月,這幾項檢查都零觸發而且沒有後來才發現的洩漏,就把這一層從驗收拿掉、只留診斷。
REVISIT:2026-11-21 暖機輪數 W(預設 2)、量測輪數 N(預設 5)、Java 增長的每輪門檻(預設 1)與預設排除清單,在實驗室正常版與注入版各跑三次之後校準
REVISIT:2027-02-28 Google 說記憶體門檻 2027 年 2 月起影響商店曝光,到時重讀 developer.android.com/google/play/vitals 的表,數字變了就改峰值判定裡的對照表
REVISIT:2027-01-31 子案一在實驗室與一個真實專案跑過之後,重新設計代碼審的「成對方法」靜態提醒(取得沒釋放就出題),決定題目從哪裡來、會不會擋推送
REVISIT:2027-04-30 第一個真實專案用收集腳本跑過之後,確認 `dumpsys meminfo --unreachable` 在它的 Android 版本與廠牌上跑得動、暖機後的基線多大、預設門檻 0 位元組合不合用,以及真實崩潰讀不讀得到

## 一份驗收看什麼(七種檢查)

| check | 訊號 | 判不過的條件 | 這種條目的欄位(另加 scenario、contract、decided_by、decided_at) |
|---|---|---|---|
| native_unreachable | 暖機後與 N 輪後兩次 `dumpsys meminfo --unreachable` 的總位元組差 | 差值大於門檻 | `max_bytes`(預設 0) |
| java_growth | 暖機後與 N 輪後兩份 Java 快照,每個類別還有人指著的實例數 | 有類別的增加量至少 N × 每輪門檻 | `min_per_cycle`(預設 1)、`exclude_prefixes`(選填,蓋掉預設排除清單) |
| instances | N 輪後那份 Java 快照 | 宣告的類別實例數超過上限 | `class`、`max` |
| peak_vitals | N 輪期間追蹤檔的匿名常駐記憶體加 swap 最大值 | 超過裝置分級的官方前景上限 | 無 |
| exits | 前後兩次系統結束紀錄的差異、三次 pid | 多出崩潰、原生崩潰、ANR、低記憶體被殺、記憶體上限任一筆,或 pid 變了 | 無 |
| strictmode | N 輪期間這個 pid 的日誌 | 有一筆 StrictMode 違規 | 無 |
| frozen | N 輪期間的追蹤檔 | 有一幀超過 700ms;設了阻塞上限時最長阻塞超過上限 | `max_block_ms`(選填) |

另外 Native Heap 前後兩個數字只回報,當原生那項的佐證。

## 資料怎麼流

1. 設定:`.lumos/macrobench.json` 加 `stability` 段:`package`、`scenario`、`driver_warmup`、`driver_cycles`(驅動指令,`{cycles}` 會換成輪數)、`warmup`(W,至少 1)、`cycles`(N,至少 1)、`test_data`(帶署名與日期的宣告)、`strictmode`(true 或 false)、`category`(app 或 game,預設 app)、`max_record_s`(預設 600)、`device`(選填,多台裝置時的 adb 序號)。驅動指令例:UI Automator 用自己測自己的測試 `adb shell am instrument -w -e class <測試類別>#<方法> -e cycles {cycles} <測試套件>/androidx.test.runner.AndroidJUnitRunner`;子案二用 `maestro test -e CYCLES={cycles} <flow>`(flow 照上面那條 WHY 的規範寫)。設定檔裡的驅動指令由收集腳本執行,跟專案自己的建置腳本同一個信賴等級。
2. 收集(工具鏈範本 `scripts/templates/android-stability-collect.sh`,照抄進消費專案;跟收據重跑腳本一樣是 sh 外殼包 python3,不靠第三方套件;trace_processor 用 `TP`、快照腳本用 `JAVA_HEAP_DUMP` 找;每個 adb、驅動、trace_processor 與快照呼叫都用 python 的逾時;中途失敗也刪暫存檔與裝置上的暫存檔;設定讀不了或必要工具找不到時回 2 並印「擋下:」,其餘情況都寫出結果檔並回 0,哪一段沒收到寫在那個來源的 status):
   1. 刪產物目錄底下超過 7 天的 `heap-*.pftrace`(只刪這個樣式);讀裝置 MemTotal、Android 版本與機型;讀一次結束紀錄(前)。
   2. 啟動 App,記 pid;跑暖機驅動;再讀 pid。
   3. test_data 宣告為 true 才錄第一份 Java 快照;掃一次沒人指著的原生記憶體;讀 Native Heap。
   4. 開始錄追蹤檔、開始串流這個 pid 的日誌,跑量測驅動,停止錄製與串流。
   5. 讀 pid;test_data 宣告為 true 才錄第二份 Java 快照;再掃一次沒人指著的原生記憶體;讀 Native Heap。
   6. 讀一次結束紀錄(後),比出多的那幾筆並分類;從日誌串流挑出 StrictMode 行。
   7. 用兩支查詢範本算數字(`android-stability-cycle.sql` 對追蹤檔、`android-heap-classes.sql` 對兩份快照),寫成 `.lumos/artifacts/android/<run-id>/stability.json`。
3. 結果檔欄位:`scenario`、`device_model`、`android_sdk`、`total_mem_mb`、`category`、`warmup`、`cycles`;每個來源一段,各帶 `status` 與 `reason`:`driver`(warmup、cycles 各自的回傳碼與判讀)、`pids`(三次)、`unreachable`(before、after 各自的 bytes、allocations)、`heap`(before、after:只存有增減的類別與門檻檔宣告的類別,類別名對實例數;沒錄時 status 是 unsupported)、`native_heap_kb`(before、after)、`cycle_trace`(peak_anon_swap_kb、frozen_frames、max_main_block_ms、frames)、`exits`(新增的每筆 reason、kind、pid、timestamp、desc)、`strictmode`(每筆違規種類)。
4. 判定(`lumos macrobench --stability <結果檔>`):只判門檻檔裡寫了 `check` 的條目;沒給 `--stability` 時這些條目列成跳過、原因寫「沒給結果檔」;driver 來源不是 ok 時全部列成跳過;結果檔讀不了或格式不對回 2 並印「擋下:」;輸出沿用 threshold_failures、threshold_passed、threshold_skipped,每筆帶 `check` 與那一種的明細(java_growth 列出增長的類別與增加量,native_unreachable 印差值位元組與塊數,exits 印每筆種類);只提醒、回 0。
5. 診斷(skill):native_unreachable 或 java_growth、instances 沒過,直接進 L3,不先走 L1、L2(那兩層看 CPU 時間,記憶體問題在那裡看不到):Java 那側在第二份快照上查支配樹找到留住的欄位;原生那側用 heapprofd 重跑一次 N 輪,看沒釋放的配置是誰呼叫的;第三方 .so 沒有符號時停在「哪支 .so、哪個位移、App 哪一行呼叫的」,標成第三方沒有符號。frozen 沒過照原本 L1;exits 與 strictmode 沒過看紀錄裡的現場。
6. 收據:兩支查詢範本可整份貼進收據,用現有的重跑腳本從追蹤檔與快照重算;查詢第一欄是字串鍵(追蹤檔那支輸出一列、鍵是 cycle;快照那支每個類別一列、鍵是類別名,同名類別出現在不同 classloader 時加總成一列);兩份快照各寫一條查詢,增減由 lumos 算;空值用 COALESCE 換成 -1,重跑比對才寫得出 expect;快照 7 天後刪,刪了之後收據裡跟快照有關的數字標成不能重跑。

## 這次要改到的地方

- 工具鏈 `scripts/lumos`:`lumos macrobench` 加 `--stability` 與門檻的 `check` 欄位與七種判定;門檻驗證只對沒寫 `check` 的條目套原規則;有 `stability` 段時 `results_dirs` 可以不填;沒有 `.lumos/macrobench.json` 但給了 `--stability` 時照判;判定輸出與印字照 `check` 分支;數字走既有的只收有限數檢查。
- 工具鏈範本 `scripts/templates/`:新增收集腳本、兩支查詢範本、錄製設定,帶 SPDX 檔頭、登記工具組複製清單;範本檔頭寫明註解不以分號結尾(收據重跑腳本拿第一個分號當查詢結尾)。
- 新家節點 [[Systems/android-stability-collector]]:管收集腳本、兩支查詢範本與錄製設定,負責範圍寫「在主機端排順序、用 adb 收記憶體與穩定性資料寫成結果檔;不判過不過(判定在 lumos macrobench)」;它是第一支會接裝置的範本。
- 家節點 [[Systems/macrobenchmark-adapter]]:負責範圍加「讀收集結果檔判記憶體與穩定性」,「不接裝置」照留(Lumos 本體不接,接裝置的是收集腳本)。
- skill lumos-android-evidence:L3 段與「沒有人裁的保存規則不錄 L3」兩處改成照本計劃的保存規則,L3 手動錄的快照檔名用 `heap-*.pftrace`;L0 的往下條件加 `--stability` 的判定結果;記憶體檢查沒過直接進 L3;第三方 .so 沒符號停在哪;reference.md 加結果檔與 `check` 的寫法、驅動要自己測自己。
- skill lumos-project-notes:reference.md 與 commands/04-自檢與健康.md 的 macrobench 指令說明加 `--stability`。
- 圖譜:[[Projects/Android逐層診斷_計劃]] 的 S6(沒有保存裁定時停在 L2)與「L3 預設關閉」記成被本計劃的保存規則取代;[[Projects/Macrobenchmark驗收門檻_計劃]] 的 S5(缺必填欄位回 2)補一句「只對沒寫 check 的條目」;[[Projects/Android效能判定統計化_計劃]] 加第 6 條「記憶體峰值跟自己的基準比」。
- 實驗室:一個自己測自己的 UI Automator 開關畫面情境、假 SDK(Java 留物件)、沒有符號的 .so(漏原生記憶體)、StrictMode 設定、`.lumos/macrobench.json` 的 stability 段。

## 實務隱患

- 已排除:金流:不碰任何交易或點數,只讀測試裝置上的量測資料。
- 已排除:對外送出:量測、收集與判定都在本機跑,原始檔不上傳;快照只在宣告了測試資料時錄,進版控的只有結構不含內容。
- 已排除:不可逆:判定唯讀;收集腳本只刪自己產物目錄底下超過 7 天的 `heap-*.pftrace` 與自己在裝置上建的暫存檔,刪的是可重錄的量測檔。
- 已排除:守衛面:判定照舊只提醒、回 0,不新增擋推送或擋提交的檢查;代碼審的成對方法題移到後續另案。
- 系統結束紀錄的文字格式會隨 Android 版本改:收集腳本只讀 pid、timestamp、reason、description,標頭用行首比對且不分大小寫。
- `dumpsys meminfo --unreachable` 的前提官方文件沒寫:實驗室 SM-X710 Android 16 的 profileable 建置實測可以;輸出「0 bytes in 0 unreachable allocations」解析成 0;跑不動時那項列成跳過,REVISIT 綁第一個真實專案。
- 大快照與大追蹤檔:真實 App 的快照可能上百 MB,逾時預設照實驗室實測的倍數訂、可在設定裡調;逾時那個來源記成 failed,不會判通過。
- 沒有符號的 .so 診斷只到位移:報告照實標出停在哪一層,不假裝查到函式。
- 快照可能含個資:java_hprof 不含字串與位元組內容;只准在宣告了測試資料的專案錄。
- 查詢範本的自動測試用 Python 內建 sqlite3 照 Perfetto 文件建同名的表跑(跟寫法分流範本同一個做法),證明的是查詢邏輯;在真的 trace_processor 上跑得出來由實驗室那幾條人工驗收證明。

## 條款

- [S1] 當結果檔兩次掃描的沒人指著原生記憶體差值大於門檻時,lumos macrobench 應把 native_unreachable 那條列成沒過並印出差值位元組與塊數;差值等於門檻時列成通過 [test:t_android_memstab_native_unreachable]
- [S2] 當兩份快照裡某個不在排除清單的類別實例數增加量至少 N × 每輪門檻時,lumos macrobench 應把 java_growth 那條列成沒過並列出那些類別與增加量;少一個時列成通過;排除清單裡的類別增加再多也不算 [test:t_android_memstab_java_growth]
- [S3] 當門檻檔 instances 條目宣告的類別在第二份快照超過上限時,lumos macrobench 應列成沒過並印出類別名與實例數;只在第一份有、第二份沒有時算 0 個;兩份都沒有時列成跳過並說可能拼錯或被混淆 [test:t_android_memstab_instance_limit]
- [S4] 當 peak_vitals 判定時,lumos macrobench 應依結果檔的 total_mem_mb 與 category 照官方區間查前景上限(含下界不含上界),超過就列成沒過;低於 3200 或至少 18432 時列成跳過並說原因 [test:t_android_memstab_peak_vitals_floor]
- [S5] 當結果檔的 exits 有崩潰、原生崩潰、ANR、低記憶體被殺或記憶體上限的新紀錄、或三次 pid 不一樣時,lumos macrobench 應列成沒過並印出每筆的種類;只有其他原因的新紀錄時列成通過並回報 [test:t_android_memstab_exits]
- [S6] 當收集腳本拿到前後兩份結束紀錄時,應只留下後一份多出來的那幾筆(用 pid 加 timestamp 比)並依 reason 與描述分類;只有全域標頭、沒有套件區段時是零筆且 status 是 ok;連全域標頭都沒有時 status 是 failed [test:t_android_memstab_exit_info_diff]
- [S7] 當結果檔有 StrictMode 違規時,lumos macrobench 應列成沒過;設定沒宣告 strictmode 時列成跳過;日誌串流中斷使 status 為 failed 時列成跳過 [test:t_android_memstab_strictmode]
- [S8] 當結果檔的凍結幀數大於 0 時,lumos macrobench 應把 frozen 那條列成沒過;設了 max_block_ms 而最長阻塞超過時也列成沒過;幀數是 0 時列成跳過 [test:t_android_memstab_frozen_frame]
- [S9] 當追蹤檔查詢範本拿到照 Perfetto 文件建的行程計數、幀時間線與區段表時,應輸出一列,第一欄是字串 cycle,其後是匿名常駐記憶體加 swap 的最大值(swap 取每個時間點之前最近一次的值)、凍結幀數(有幀時間線用幀時間線,沒有用名稱以 Choreographer#doFrame 開頭的區段)、主執行緒最長的最上層區段、幀數;量不到的欄位輸出 -1 [test:t_android_memstab_cycle_query]
- [S10] 當快照查詢範本拿到照 Perfetto 文件建的堆積物件與類別表時,應每個類別輸出一列、第一欄是類別名,只算還有人指著的物件,同名類別加總成一列 [test:t_android_memstab_heap_query]
- [S11] 當結果檔某個來源的 status 不是 ok、欄位缺、值是 -1 或不是有限數時,lumos macrobench 應把用到它的那條列成跳過並說原因,不得列成通過;driver 來源不是 ok 時每一條都列成跳過 [test:t_android_memstab_source_not_ok_skipped]
- [S12] 當收集腳本、兩支查詢範本與錄製設定加進工具鏈時,應帶 SPDX 檔頭、登記在工具組複製清單、跟其他範本一起進消費專案 [test:t_android_memstab_vendored]
- [S13] 當門檻檔的條目沒寫 check 時,lumos macrobench 應照舊對 Macrobenchmark 結果檔判單值門檻,既有門檻檔的判定結果不變;寫了不認得的 check、缺了那種的欄位、或門檻數字不是有限數時應回 2 並說原因;沒給 --stability 時寫了 check 的條目列成跳過 [test:t_android_memstab_check_compat]
- [S14] 當給了 --stability 而專案沒有 .lumos/macrobench.json、或設定只有 stability 段沒有 results_dirs 時,lumos macrobench 應照樣判寫了 check 的條目;結果檔讀不了或不是 JSON 時應回 2 並印擋下 [test:t_android_memstab_stability_config]
- [S15] 當設定的 test_data 宣告不是帶署名與日期的 true 時,收集腳本不應錄 Java 快照,結果檔的 heap 來源 status 是 unsupported;收集腳本開跑時應刪掉產物目錄底下超過 7 天的 heap-*.pftrace、不刪別的檔 [test:t_android_memstab_collect_test_data_gate]
- [S16] 當驅動回傳碼不是 0、或 UI Automator 輸出沒有 INSTRUMENTATION_CODE: -1、或有 FAILURES!!! 時,收集腳本應把 driver 來源記成 failed [test:t_android_memstab_collect_driver_status]
- [S17] 當實驗室 App 的開關畫面情境正常版跑時(暖機 2 輪、量測 5 輪),七種檢查應全過或因裝置限制跳過並說明原因 [manual:macrobench-lab 實機跑一次收集腳本與 lumos macrobench --stability,判定與收據存進 macrobench-lab,寫進驗證紀錄]
- [S18] 當實驗室分別埋入「假 SDK 在 Java 留物件、關畫面時不呼叫 release」與「沒有符號的 .so 漏原生記憶體、關畫面時不呼叫 release」時,前者應被 java_growth 與 instances 擋下、後者應被 native_unreachable 擋下,診斷分別指到留住的欄位,以及哪支 .so、App 哪一行呼叫的 [manual:兩種各跑一次收集腳本與 skill,收據 L3 那筆寫明留住的欄位或 .so 位移與呼叫行;寫進驗證紀錄]
- [S19] 當實驗室用 am crash 讓 App 在量測輪中崩潰時,exits 應列成沒過 [manual:實驗室跑一次,判定存進驗證紀錄]

## 回退

- 判定只提醒不擋,出錯時把門檻檔裡寫了 check 的條目與設定的 stability 段拿掉就回到現狀;收集腳本、查詢範本與錄製設定是新檔,撤掉不影響既有的效能門檻與收據;skill 的 L3 改動回退成「沒有保存規則不錄」即可。
