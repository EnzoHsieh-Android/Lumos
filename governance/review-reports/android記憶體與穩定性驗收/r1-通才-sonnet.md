severity: blocker

我讀完全份,程式碼端查證了 `scripts/lumos` 的門檻檢查與輸出函式、`scripts/templates/android-receipt-rerun.sh`、`skills/lumos-android-evidence/SKILL.md` 與 `Android逐層診斷_計劃.md`。平台端我試著抓 Android vitals 記憶體頁(`developer.android.com/google/play/vitals/memory`),回 404,所以 vitals 數字沒能核對(見 F11)。四篇 related 連結目標(`Android逐層診斷_計劃`、`Macrobenchmark驗收門檻_計劃`、`Android介面寫法分流_計劃`、`Android診斷證據接入_調研`)與 `Systems/macrobenchmark-adapter` 在工作樹都存在。`Android逐層診斷_計劃` 的 S6 也確實是「沒有保存裁定停在 L2」。

**F1 洩漏要跨輪累積,但 spec 沒規定每輪不殺行程**
severity: blocker
blocking: 是
判準:不寫清楚,實作者可能照 Macrobenchmark 預設做出每輪重啟行程的壞系統,洩漏永遠累積不起來,整個洩漏判定恆通過。
- 段落:〈資料怎麼流〉第 1 步、WHY 洩漏情境。
- 問題:spec 沒寫 `measureRepeated` 的 `startupMode`。COLD 每輪殺行程,Java 堆積與原生記憶體每輪歸零,「N 輪一路往上」不可能成立。
- 缺口:「一輪」是不是一次 iteration、每輪有沒有各自的追蹤檔、`MemoryUsageMetric` 在非 COLD 下行為如何,spec 都沒寫。
- 佐證:spec 全文沒出現 startupMode 或 COLD/WARM。
- 狀態:⚠ 平台行為憑我對 Macrobenchmark 的知識,沒有網查確認。

引句:「Macrobenchmark 的洩漏情境掛 MemoryUsageMetric,讓每輪追蹤檔都錄到記憶體計數」

**F2 N 輪後「錄一份 Java 堆積快照」流程跑不起來**
severity: blocker
blocking: 是
判準:實作者無法照 spec 做出快照這一步,實例數檢查(S4)會落成永遠「跳過」或做出別的流程。
- 段落:WHY 宣告類別實例數、〈資料怎麼流〉第 1 步、S4。
- 問題:Macrobenchmark 是在裝置上以 instrumentation 跑的,快照要在 N 輪之後、App 還活著時錄。
- 佐證:file: `skills/lumos-android-evidence/SKILL.md:125` 寫「重現跑完、App 還活著時 `java_heap_dump -n <套件> -o <檔>.perfetto-trace`」,那是從主機端執行的 Perfetto 腳本。
- 缺口:Gradle 的測試跑完時 Macrobenchmark 通常已殺掉 App,主機腳本無法插在最後一輪與測試結束之間。
- 缺口:spec 沒說由誰、用什麼觸發,也沒說 Macrobenchmark 要求的非 debuggable 建置能不能被 `java_heap_dump` 抓。
- 缺口:實例數查詢(堆積快照的 `heap_graph_object`)沒有任何查詢範本,spec 的 S10 只涵蓋每輪那支。

引句:「N 輪量完,門檻檔宣告了類別才錄一份 Java 堆積快照」

**F3 「原生記憶體 = 匿名常駐記憶體 − Java 堆積」的定義會把 Java 垃圾算進原生線**
severity: major
blocking: 是
判準:實作者照字面做,原生線會有假陽性或假陰性,報告會標錯是哪一條線。
- 段落:〈用到的詞〉、WHY 洩漏看兩條線、S1/S2。
- 問題:匿名常駐記憶體包含 Java 堆積已提交但尚未歸還系統的頁。Java 堆積計數是 GC 後存活大小,兩者相減會把「已釋放、還沒歸還的 Java 頁」算成原生。
- 後果:Java 洩漏造成的 RSS 增長,在「Java 計數已降、RSS 沒降」時會被誤歸成原生線;反向也可能出現負值,spec 沒規定負值怎麼處理。
- 缺口:spec 的 REVISIT 只承認「計數實際名稱與是否回收後」未知,沒處理這個減法本身。
- 狀態:⚠ 平台行為判斷,沒有實測。

引句:「原生記憶體在這裡指匿名常駐記憶體扣掉 Java 堆積」

**F4 容差預設值單位是毫秒,記憶體是 KB,「取較大者」的絕對值項形同虛設**
severity: major
blocking: 是
判準:照「沿用既有規則」做出的洩漏判定,容差單位錯亂,S3 的「第一輪值接近 0」情境無法成立。
- 段落:WHY 洩漏用趨勢判、WHY 峰值兩層、S3、S6。
- 佐證:file: `scripts/lumos:39358` `MACROBENCH_DEFAULTS` 的 `abs_tolerance` 預設 1.0,`tolerance_pct` 預設 10.0。這是全域設定,用於毫秒類指標。
- 問題:記憶體欄位單位是 KB,絕對容差 1.0 等於 1 KB,所以實際只剩 10% 比例。
- 後果:Java 堆積第一輪值是數萬 KB,從不「接近 0」。10% 的比例容差下,第一輪 30 MB 的堆積要多漲 3 MB 才算洩漏,慢洩漏大多抓不到。
- 缺口:spec 沒說記憶體類是否有獨立的容差欄位、單位(KB 或 MB)與預設值。

引句:「第一輪值接近 0 時只靠百分比會被正常抖動誤報」

**F5 峰值「基準」的來源與更新方式沒定義**
severity: major
blocking: 是
判準:實作者無從實作「基準加容差」那條檢查,S6 沒有可比的基準資料。
- 段落:WHY 記憶體峰值分兩層、S6、門檻 `kind: peak`。
- 佐證:file: `scripts/lumos:39558`(`_macrobench_load_baseline`)和 `_macrobench_update` 只處理 `.lumos/macrobench-baseline.json` 裡 Macrobenchmark 的 median 與百分位指標。
- 缺口:`stability.json` 的峰值要存在哪、怎麼建立與更新(`--update-baseline` 只管現有檔)、同一情境多次執行取什麼,spec 沒寫。
- 缺口:門檻檔「每種有自己的必填欄位」,spec 只對 `scenario`、`contract`、`decided_by`、`decided_at` 有交代,六種 kind 各自的欄位(上限、輪數、類別名、`vitals` 旗標寫法、基準值)一個也沒列。S13 要擋「缺了那種的必填欄位」,卻沒有欄位清單可以擋。

引句:「抓退步用 App 自己的基準加容差(容差規則同洩漏)」

**F6 官方底線表在 WHY 和 S5 互相矛盾,裝置總記憶體對分級的對應也沒定義**
severity: major
blocking: 是
判準:實作者在 4 GB 與 16 GB 裝置上,會得到「有數字」或「跳過」兩種相反行為。
- 段落:WHY 記憶體峰值分兩層 vs S5。
- 矛盾:WHY 列了「4 GB 裝置 2.00 GB」與「16 GB 4.25 GB」,S5 寫「4 GB 以下或 16 GB 以上沒有官方數字時列成跳過」。
- 缺口:`total_mem_mb` 是 `/proc/meminfo` 的 MemTotal(標稱 4 GB 的裝置約 3.7 GB),spec 沒說怎麼落到 4/6/8/12/16 的級別。邊界值、介於級別之間的值(10 GB、7 GB)怎麼歸也沒寫。
- 狀態:⚠ 表中數字我沒能核對(vitals 頁 404),需要實作者重讀官方頁後再定。

引句:「4 GB 以下或 16 GB 以上沒有官方數字時列成跳過並說原因」

**F7 記憶體類 kind 的輸出紀錄形狀與現有輸出函式不相容,「沿用」只是口號**
severity: minor
blocking: 否
判準:實作者看現有碼就會發現不合並自行補齊,不會做出壞系統,但輸出欄位若沒統一,skill 的 L3 分流會讀不到。
- 段落:〈資料怎麼流〉第 3 步、S1/S2/S4。
- 佐證:file: `scripts/lumos:39708` 的 `_macrobench_print_thresholds` 對每筆失敗紀錄直接讀 `r['metric']`、`r['stat']`、`r['current']`,以及 `max` 或 `min`。leak、instances、exits、strictmode 這些 kind 沒有這些欄位,印出時會 KeyError。
- 缺口:`--json` 的 `threshold_failures` 項要帶 `kind`、「Java 或原生哪條線」、類別名等。S1/S2 要求「標明是哪條線」,但沒定義欄位,skill 要靠它決定走 L3。
- 缺口:`--stability` 沒給時,檔裡 kind 條目該列「跳過」還是靜默忽略,spec 沒說。

引句:「輸出沿用 threshold_failures、threshold_passed、threshold_skipped 與原因」

**F8 `--stability` 與 `cfg is None` 早退、`lumos macrobench` 無設定檔路徑的互動沒寫**
severity: minor
blocking: 否
判準:實作者會自己發現並決定,最壞是 kind 門檻在沒有 `macrobench.json` 的專案被默默略過。
- 佐證:file: `scripts/lumos:39724` 的 `_macrobench_mode` 在 `cfg is None`(沒有 `.lumos/macrobench.json`)時直接印「沒接」並回 0,在做門檻判定之前就返回。
- 缺口:子案二 Maestro 專案可能沒有 Macrobenchmark 結果檔,但仍需要穩定性判定。spec 沒說這種專案是否仍得有 `macrobench.json`,以及 `--stability` 的 `kind` 條目是否獨立於它。

引句:「門檻檔裡寫了 `kind` 的條目對結果檔判,六種各自判」

**F9 結束紀錄與 StrictMode 的時間過濾用的時鐘沒定義**
severity: major
blocking: 是
判準:實作者可能拿主機時間去濾裝置時間戳,造成漏判或誤判上週的崩潰,而且讀起來合理、測不出。
- 段落:WHY 崩潰/ANR、S7、`started_utc`。
- 問題:`ApplicationExitInfo` 的時間戳是裝置時鐘,`started_utc` 沒說取自主機還是裝置;裝置時鐘常有偏移(模擬器與時區尤甚)。
- 缺口:logcat 的時間戳是裝置本地時區,spec 也沒說怎麼換成 UTC。
- 缺口:logcat 緩衝只有數百 KB,N 輪跑完後 StrictMode 日誌可能已輪替掉,spec 沒寫是否要在測試前清緩衝、測試中持續擷取。

引句:「用測試開始的時間點過濾系統結束紀錄」

**F10 蒐集失敗與「真的沒有事件」無法區分,守衛會靜默通過**
severity: major
blocking: 是
判準:這種守衛的主要失敗模式就是「解析不到所以全綠」,不處理等於做出會靜默放行的檢查。
- 段落:S7、S8、S11、〈實務隱患〉第一條。
- 問題:`dumpsys` 格式隨版本變,解析不到任何一筆時,`exits` 是空陣列,判定會通過。
- 缺口:S11 只涵蓋「欄位缺或 null」。spec 缺一個「蒐集成功」的證明欄位,例如原始輸出行數、解析器版本、`dumpsys` 是否回傳了任何紀錄。
- 補充:實務隱患只承諾每個版本一份樣本測試,沒有執行期的防線。

引句:「收集腳本只讀原因、時間與描述三個欄位,測試用不同版本的樣本各一份」

**F11 保存 7 天的承諾沒有執行機制**
severity: major
blocking: 是
判準:這是整份計劃賴以解鎖 L3 的隱私條件,只有提示、沒有刪除,承諾落空。
- 段落:WHY 記憶體快照只在測試資料下錄、S16、〈實務隱患〉不可逆一項。
- 問題:spec 寫「本機保留 7 天後刪」,S16 的行為只是「提示 7 天後刪」。
- 缺口:lumos 沒有背景程序,誰在什麼時機刪、依據什麼時間(檔案 mtime 或 `started_utc`)、刪失敗怎麼辦,都沒定義。
- 缺口:`.lumos/artifacts/` 在消費專案是否已被 `.gitignore`,spec 把它丟給手動驗證 S16。
- 補充:「追蹤檔不受 7 天限制、只有區段名、時間與計數」的說法也偏樂觀,自訂 trace 區段名可能含業務字串。⚠ 判不準,屬低風險。

引句:「快照原始檔只放產物目錄,並提示 7 天後刪」

**F12 凍結幀與最長阻塞的資料來源沒定義**
severity: minor
blocking: 否
判準:實作者會自選一個來源,結果數字語意可能與 vitals 的「凍結幀」不同,但只提醒、不擋,不會做出壞系統。
- 段落:S9、`frozen_frames`、`max_main_block_ms`。
- 缺口:「一幀」取自 `Choreographer#doFrame` 切片、`actual_frame_timeline_slice` 還是 `android-ui-attribution.sql` 的主執行緒切片,spec 沒說;前者需要 Android 12+ 的幀時間線資料。
- 缺口:「主執行緒阻塞」是主執行緒最長的最上層切片,還是只算 UI 相關切片,沒說。
- 缺口:第一輪的開畫面可能合法超過 700ms(首次載入),spec 沒說是否排除暖機輪。

引句:「當追蹤檔裡有一幀超過 700ms 時,查詢範本應算出凍結幀數」

**F13 查詢範本如何知道輪次(第一欄字串鍵從哪來)**
severity: minor
blocking: 否
判準:實作者會補一個參數佔位,不改變設計。
- 段落:〈資料怎麼流〉第 5 步、S10。
- 問題:每輪一份追蹤檔,輸出一列「第一欄是輪次字串」,但追蹤檔本身不含輪次 r1/r2。
- 缺口:查詢範本沒有定義輪次佔位(類似 `__PROCESS__`),收據的重跑腳本是逐個查詢綁單一 trace(file: `scripts/templates/android-receipt-rerun.sh` 的 `trace=` 標頭)。
- 缺口:空值輸出(`[NULL]` 或空字串)跟重跑腳本只認以 `"` 開頭的列(同一檔 `rows = [l for l in ... startswith('"')]`)的互動沒驗證。

引句:「查詢輸出第一欄是字串鍵(輪次 r1、r2…),因為重跑腳本拿第一欄的字串比對」

**F14 實例數的類別名遇到混淆(R8)與合法持有沒處理**
severity: minor
blocking: 否
判準:屬已承認「判斷靠人」類的邊界,不改設計。
- 段落:WHY 宣告類別實例數、S4。
- 缺口:benchmark 建置通常開 R8,門檻檔宣告的類別名遇混淆就對不上,spec 沒說要求 keep 規則或讀 mapping。
- 缺口:「開關 5 次應是 0 或 1」沒處理當前存活的 Activity 與延遲 GC 造成的 +1;快照前是否強制 GC 沒寫。

引句:「實例數一翻兩瞪眼(開關 5 次後應是 0 或 1 個)」

**實務隱患鏡頭(逐類)**
- 併發:同一裝置多人或多個 run 同時跑會互踩 `.lumos/artifacts/android/<run-id>/` 以外的共享狀態(logcat 緩衝、`dumpsys` 的退出紀錄)。spec 沒寫序列化;低風險(單人情境,⚠ 判斷)。
- 效能:N 輪各一份追蹤檔外加一份堆積快照,檔案大小與保存量沒估;`trace_processor` 對大追蹤檔逐輪各跑一次,耗時沒預算。
- 資源:收集腳本呼叫 `adb`、`trace_processor` 子程序與暫存查詢檔,沒寫逾時與失敗清理(已有的重跑腳本有刪暫存的做法可借用)。
- 回退:〈回退〉一節可行(拿掉 kind 條目即回現狀),已讀,無 finding。

**逐節狀態**
- 〈用到的詞〉:見 F3。
- 〈WHY 各條〉:見 F1–F6、F9、F11、F14。
- 〈PRIOR-ART、RETIRE-IF、REVISIT〉:已讀,無 finding。
- 〈一份驗收看什麼(六種檢查)〉:已讀,無獨立 finding(併入 F6)。
- 〈資料怎麼流〉:見 F1、F2、F7、F8、F10、F13。
- 〈這次要改到的地方〉:已讀,無 finding。
- 〈實務隱患〉:見 F10、F11 與上面逐類。
- 〈條款〉:S1–S16 已讀。S4/S5/S9/S10/S11 的問題見前述;S12 的登記清單位置核對無誤(file: `scripts/lumos:31928` 的 `_VENDORED_TREE_FILES` 已存在同類登記);其餘無 finding。
- 〈回退〉:已讀,無 finding。

**固定席判斷:`Systems/macrobenchmark-adapter` 會不會被破壞**
不影響既有宣稱,前提是 S13 落實。理由:該節點宣稱的行為(只報變慢、驗收門檻另判、沒達也回 0、NaN 與非有限數拒收、`--update-baseline` 不整份重寫)都在不寫 `kind` 的既有門檻條目上,spec 的 S13 要求「沒寫 kind 的照舊判、既有門檻檔結果不變」。
需要同步的地方:
- 節點的 responsibility 欄寫「不接裝置、不從量測產生門檻」,新增「讀收集結果檔」要一併改成不衝突的寫法。
- 節點的 `about_code` 只列 `scripts/lumos` 與兩支範本,新增的收集腳本與查詢範本必須加進去,否則違反「每支檔有家」(鐵則 5)。這點 spec 〈這次要改到的地方〉只寫改負責範圍,沒提新檔入列。

總結:最高嚴重度 blocker,blocking 共 9 條
