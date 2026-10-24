severity: major

審稿範圍:spec 全文,加上 `scripts/lumos` 的 macrobench 段、`scripts/templates/android-receipt-rerun.sh`、`android-ui-attribution.sql`、lumos-android-evidence 的 SKILL.md 與 reference.md、Projects/Macrobenchmark驗收門檻_計劃、Projects/Android逐層診斷_計劃、Systems/macrobenchmark-adapter,以及 macrobench-lab 的 LabBenchmarks.kt。

## Findings

**1.**
severity: major
blocking: 是
判準:major 對應 blocking 是,實作者無法照 spec 寫 S13 的測試,也不知道舊門檻驗證碼會不會把整個檔擋成 rc 2。
引句:「沒寫 `kind` 的照舊是 Macrobenchmark 結果檔的單值門檻,寫了的讀收集結果檔」
- 位置:〈WHY:門檻檔每一條加選填 kind〉、條款 S13 與 S11。
- 問題:spec 只說「每種有自己的必填欄位」,沒列任何一種的欄位。
  - leak 的容差與輪數、instances 的類別名與上限、peak 的「用官方底線」或「基準加容差」、frozen 的單次阻塞門檻放哪個欄位,全都沒定義。
  - exits 與 strictmode 要不要有條目、能不能沒有 `metric` 與 `stat`,也沒說。
  - S13 的「缺了那種的必填欄位時擋下」因此沒有判準,`t_android_memstab_kind_compat` 寫不出來。
- 現行程式的撞牆點:
  - `MACROBENCH_THRESHOLD_REQUIRED` 含 `metric`、`stat`,`_macrobench_threshold_item_err` 又要求 `max` 與 `min` 恰好一個有限數。
  - leak、instances、peak 的條目天生不合這個形狀。
  - `_macrobench_mode` 一開頭就對全部條目跑 `_macrobench_thresholds`,所以只要有一條 kind 條目,不帶 `--stability` 的 `lumos macrobench` 也會 rc 2,既有指令連帶壞掉。
  - `if cfg is None` 的早退在判門檻之前,只有 stability.json、沒有 `.lumos/macrobench.json` 的專案會得到「沒接」並回 0。
  - 帶 `--stability` 時,沒寫 kind 的條目該算跳過還是忽略,也沒說。
- 與其他計劃的衝突:Macrobenchmark驗收門檻_計劃 的 S5 寫「任一條缺必填欄位…回 2」,spec 改了這個行為卻沒有宣告修訂那條。
- 佐證:`scripts/lumos:39629`、`scripts/lumos:39632`、`scripts/lumos:39656`、`scripts/lumos:39730`。

**2.**
severity: major
blocking: 是
判準:major 對應 blocking 是,峰值「抓退步」這一層沒有基準來源,S6 無從實作;基準若放進門檻檔又會破壞人裁原則。
引句:「抓退步用 App 自己的基準加容差(容差規則同洩漏)」
- 位置:〈WHY:記憶體峰值分兩層〉、S6。
- 問題:「App 自己的基準加容差」沒說基準值存哪、誰更新。
  - `.lumos/macrobench-baseline.json` 只存 median、minimum、maximum 與 `source`。
  - `--update-baseline` 讀的是 benchmarkData.json,不讀 stability.json。
  - 如果把基準值寫進門檻檔,就違反 macrobenchmark-adapter 的責任句「不從量測產生門檻」與驗收門檻計劃的 `decided_by` 人裁原則。
- 容差來源也沒定義:
  - 既有 `tolerance_pct` 與 `abs_tolerance` 在 `.lumos/macrobench.json`,預設 abs 是 1。
  - 洩漏、峰值用的是 KB,abs 1 等於 1 KB,S3 的「第一輪值接近 0」情境因此判不出來。
  - spec 沒說 kind 條目是自帶容差,還是沿用 macrobench.json 並換單位。
- 佐證:`scripts/lumos:39358`、macrobenchmark-adapter 的 responsibility 欄。

**3.**
severity: major
blocking: 是
判準:major 對應 blocking 是,「查詢範本可整份貼進收據重跑」這個承諾,在現行重跑腳本下做不到。
引句:「查詢輸出第一欄是字串鍵(輪次 r1、r2…),因為重跑腳本拿第一欄的字串比對」
- 位置:〈資料怎麼流〉第 5 點、S10。
- 問題:S10 寫「拿到一份追蹤檔…輸出一列,第一欄是輪次字串 r1」,但 N 輪是 N 份追蹤檔。
  - 重跑腳本每條查詢只綁一個 `trace=<id>`,一條查詢只能出一份追蹤檔的一列。
  - 範本不知道自己是第幾輪。對照現有範本是用 `__PROCESS__` 之類的佔位符替換,spec 沒有輪次佔位符,也沒說收據要寫 N 條 Q。
- null 與 expect 的衝突:
  - trace_processor 的 `-q` 輸出把 NULL 印成 `[NULL]`(帶引號),不是空字串。
  - S10 要求「空欄位輸出空值」,重跑腳本的 expect 無法表達。
  - 腳本對 `k=` 取 `v=''`,與 `[NULL]` 字串比對必不符。
  - 要不要 `COALESCE`,spec 沒定。
- 佐證:`scripts/templates/android-receipt-rerun.sh` 的 `trace` 查表與 `row = next(...)` 兩行、`scripts/templates/android-ui-attribution.sql:10`、reference.md:74。

**4.**
severity: major
⚠
blocking: 是
判準:major 對應 blocking 是,S14「正常版六種全過」與 S2 的原生趨勢判定,在定義上就可能誤報,spec 沒給前提。
引句:「原生記憶體在這裡指匿名常駐記憶體扣掉 Java 堆積,第三方 .so 用 C/C++ 配置的記憶體落在這裡」
- 位置:〈用到的詞〉的「原生記憶體 = 匿名常駐記憶體扣掉 Java 堆積」、S2。
- 問題:Java 堆積是「ART 每次回收後記一次大小」。
  - 兩次 GC 之間的 Java 垃圾、ART 保留的空堆積空間,都在匿名常駐記憶體裡,但不在「回收後大小」裡,於是全落進「原生」那條。
  - 一個沒有任何 .so 的正常 App,堆積容量隨輪次長大時,「原生」線會一路上升,被判成原生洩漏。
  - 兩個計數的取樣時間點也不同(GC 時才記 vs 輪詢 ≥100ms),相減會有時間差。
- 為什麼標 ⚠:REVISIT 只提「每輪結束值是不是回收後的值」,沒點出相減本身的口徑問題。實際影響大小我無法在不跑實機下確認。

**5.**
severity: major
blocking: 是
判準:major 對應 blocking 是,官方底線對照表在邊界上自相矛盾,且輸入值口徑會讓真實裝置落到表外。
引句:「4 GB 以下或 16 GB 以上沒有官方數字時列成跳過並說原因」
- 位置:〈WHY:峰值〉的表、S5。
- 問題一:表內有 4 GB 裝置 2.00 GB 與 16 GB 裝置 4.25 GB,S5 卻寫「4 GB 以下或 16 GB 以上沒有官方數字,列跳過」。4 GB 與 16 GB 整數裝置到底有沒有數字,自相矛盾。
- 問題二:輸入是 `total_mem_mb`(從裝置讀的總記憶體,常見是 `/proc/meminfo` 的 MemTotal)。
  - 標稱 4 GB 的機器實測遠小於 4096 MB,6 GB 標稱介於分級之間。
  - spec 沒給「實測值如何對到分級」的規則(往上或往下取整、區間邊界)。
  - 依字面,4 GB 手機會全部落在「4 GB 以下」被跳過,底線這層形同失效。

**6.**
severity: major
blocking: 是
判準:major 對應 blocking 是,量測到收集的交接動作沒人認領,照 spec 接真實專案會缺環。
引句:「最後用 adb 存系統結束紀錄、日誌與裝置總記憶體」
- 位置:〈資料怎麼流〉第 1、2 點、〈WHY:門檻檔可以宣告 SDK 類別的實例上限〉。
- 問題:
  - 第 1 點「最後用 adb 存系統結束紀錄、日誌與裝置總記憶體」在量測段,第 2 點收集段又說「讀」這些。adb 動作屬於誰(Macrobenchmark 在裝置上跑,不能呼叫主機 adb)沒說。
  - 追蹤檔怎麼從裝置拉進 `.lumos/artifacts/android/<run-id>/`、怎麼對應到 r1…rN,沒說。
  - 「N 輪量完才錄快照、門檻檔宣告了類別才錄」:觸發點在裝置上的測試生命週期裡,而門檻檔在主機。測試不讀 `.lumos`,誰通知「現在錄」、在 Macrobenchmark 收尾殺掉 App 之前,spec 沒定。
  - logcat 預設緩衝會滾動,StrictMode 違規在多輪長跑裡可能被擠掉。測試開始前清緩衝、結束後存的做法,spec 沒寫。
  - StrictMode 要在 App 的 Application 裡打開,這是改消費專案的 App 碼。spec 只把 LeakCanary 列為「要改 App 依賴所以不必要」,這一條同樣要改卻沒交代。
- 實驗室佐證:`LabBenchmarks.kt:66` 的註解寫明 `StartupMode.COLD` 會在量測前殺掉 App。洩漏情境若沿用 COLD,每輪行程重啟,趨勢永遠平的。spec 沒規定洩漏情境的 startupMode 必須不殺行程。

**7.**
severity: major
blocking: 是
判準:major 對應 blocking 是,「子案二不用重做收集」的核心依據不成立,影響下一階段工作量估計。
引句:「量測只靠追蹤檔,子案二 Maestro 跑時一樣錄追蹤檔,收集與判定不用重做」
- 位置:〈WHY:量測、收集、判定三段分開〉、〈資料怎麼流〉第 1 點。
- 問題:每輪追蹤檔裡有記憶體計數,是靠 Macrobenchmark 的 MemoryUsageMetric 在錄製時掛上 process_stats。Maestro 驅動時沒有這個,也沒有「每輪一份追蹤檔」的切分。
  - 子案二的錄製設定(perfetto config、取樣頻率、按輪切分、輪次命名)要重做。
  - spec 的新增檔清單只有收集腳本與查詢範本,沒有錄製設定範本,所以這段會留在 Macrobenchmark 專屬的消費專案碼裡。
- 另外,Maestro 沒有 Macrobenchmark 的 iteration 邊界。`round` 字串由誰產生沒定義,子案二至少要重做「輪」的定義。

**8.**
severity: major
blocking: 是
判準:major 對應 blocking 是,隱私保存規則的唯一閘門不可判定,保存期限也沒有執行者。
引句:「當 skill 要錄記憶體快照時,應先確認跑的是測試資料」
- 位置:〈WHY:記憶體快照只在測試資料下錄〉、S16、〈實務隱患〉最後一條。
- 問題:
  - S16 要 skill「先確認跑的是測試資料」。spec 同時否決了「每次錄前問人」,理由是無人看顧時會停住。skill 無法機械判斷手機上是不是測試帳號,這個確認只能是 AI 自述。
  - 無人看顧的流程對著登入了真實帳號的開發機,仍會照錄一份可能含個資的 hprof。
  - 需要一個機械可查的宣告(例如專案設定標明該裝置與帳號是測試用)。
  - 「本機保留 7 天後刪」沒有任何執行者:沒有排程、`lumos` 也不在這裡做刪除,實務上等於永久保留。
  - `.gitignore` 靠 SKILL.md 既有的「確認在 .gitignore」文字提醒,不是檢查。
- 佐證:`skills/lumos-android-evidence/SKILL.md:23`。

**9.**
severity: major
⚠
blocking: 是
判準:major 對應 blocking 是,趨勢判定的主規則對有抖動的真洩漏太脆,而 spec 的主訴求(漏呼叫 release)靠它。
引句:「N 輪結束時的值一路往上(每一輪都不低於前一輪)」
- 位置:〈WHY:洩漏用趨勢判〉、S1 到 S3。
- 問題:規則要求 N 個值「每一輪都不低於前一輪」。N 預設 5 時,只要有一次輕微回落,就整條判通過。
  - 場景:每輪洩 0.5 MB、背景 GC 與配置器歸還造成 ±1 MB 抖動,洩漏必判通過。
  - 這是設計形狀(嚴格單調)的問題,不是 REVISIT 可校準的參數。
  - 原生那條線沒有實例數可補,只靠這條規則,spec 自己在〈代價〉也承認「SDK 物件全在原生那一側時看不到」。
- 為什麼標 ⚠:最終要換成斜率或多數輪上升之類的哪種判法,我無法不實測就定。

**10.**
severity: minor
blocking: 否
判準:minor 對應 blocking 否,實作時就會踩到並自行補,不改變設計方向,但〈這次要改到的地方〉的清單不完整。
引句:「`scripts/templates/` 新增收集腳本與查詢範本,登記工具組複製清單、帶 SPDX 檔頭」
- 位置:〈這次要改到的地方〉。
- 漏項:
  - 家節點 macrobenchmark-adapter 的 `about_code` 現在只列 `scripts/lumos` 和兩支範本,新增的收集腳本與查詢範本沒說要加進去。鐵則 5「每支檔有家」會在提交時擋,但清單沒寫。
  - SKILL.md 的步驟 8「往下條件」只認 `regressions` 與 `threshold_failures`,第 65、107 行的 L1/L2 到 L3 路由也要改。spec 只提 L3 段與保存規則那兩處。
  - `skills/lumos-android-evidence/reference.md` 與 `skills/lumos-project-notes/reference.md:87` 的 macrobench 旗標說明、`commands/04-自檢與健康.md:21` 的指令表,都沒有 `--stability` 與 `kind`。
  - Android逐層診斷_計劃 的 WHY(第 20 行「不選每次都錄記憶體」)、第 39 行「L3 預設關閉」與 S9 的「授權」前提,也被這份計劃部分取代。spec 只說 S6 記成被取代。
  - Macrobenchmark驗收門檻_計劃 的 S5 與〈門檻檔格式〉,見 finding 1。
- 佐證:`skills/lumos-android-evidence/SKILL.md:39`、`skills/lumos-android-evidence/SKILL.md:65`、`skills/lumos-android-evidence/SKILL.md:107`。

**11.**
severity: minor
blocking: 否
判準:minor 對應 blocking 否,會造成噪音提醒,但不會誤擋。
引句:「Macrobenchmark 的洩漏情境掛 MemoryUsageMetric,讓每輪追蹤檔都錄到記憶體計數」
- 位置:〈資料怎麼流〉第 1 點(掛 MemoryUsageMetric)與既有基準比對。
- 問題:洩漏情境掛 MemoryUsageMetric 後,benchmarkData.json 會多出記憶體類 metrics。
  - 既有基準比對對每個 metric 套 `tolerance_pct` 10 與 `abs_tolerance` 1,而 `ignore_metrics` 預設只忽略 `frameCount`。
  - 這些記憶體 metrics 單位是 KB,會被當成一般指標比,出現與 stability 判定重複、且 abs 容差 1 KB 太小的「變慢」提醒。
  - spec 沒說要把它們加進 `ignore_metrics` 或在文件裡提醒。
- 佐證:`scripts/lumos:39358`、`scripts/lumos:39492`。

**12.**
severity: minor
blocking: 否
判準:minor 對應 blocking 否,只影響收據的可驗證範圍,spec 已知其代價。
引句:「快照 7 天後刪,收據裡的實例數只留結果,不重算」
- 位置:〈資料怎麼流〉第 5 點「收據裡的實例數只留結果,不重算」。
- 問題:SKILL.md 與逐層診斷計劃的 S7 要求「沒脈絡的 Agent 只靠收據與原始檔,用 rerun.sh 重跑出 expect」。S15 要求 L3 那筆寫明留住的欄位或 .so 位移,這類結論無法重跑,等於承認收據裡有一類結論不受乾淨 Agent 檢驗。spec 沒說這類結論在收據中如何標記(例如不標 `[SQL]`)。
- 佐證:`skills/lumos-android-evidence/SKILL.md:141`。

## 逐節讀完的結論

- 〈一份驗收看什麼〉表格:已讀,除 finding 5 外無 finding。
- 〈資料怎麼流〉第 3 點(`--stability` 的輸出沿用三欄、只提醒回 0):與驗收門檻計劃的 S7 一致,無 finding;早退與驗證前置問題見 finding 1。
- 〈資料怎麼流〉第 4 點(診斷路由):已讀,無 finding;漏改項見 finding 10。
- 〈回退〉:已讀,無 finding。回退說明「拿掉 kind 條目即回到現狀」,在 finding 1 修好前不成立,因為現行驗證會把含 kind 的檔擋掉(反向,舊版 lumos 讀到新檔也會 rc 2)。
- 〈實務隱患〉:除上述隱私項外已讀,無 finding。

## 此功能碰到的風險類

- 資料保存與隱私(hprof 敏感檔):隱患見 finding 8。
- 相容性與既有合約(門檻檔格式、重跑腳本、基準檔):見 finding 1、2、3、11。
- 對外送出:已讀,無隱患。spec 的「不上傳」與現行 SKILL.md 一致。
- 金流、不可逆:已讀,無隱患。
- 守衛面:已讀,無隱患。判定只提醒、回 0,與驗收門檻計劃的 WHY 一致,這次沒新增擋推送或擋提交的檢查。
- 跨專案、真實消費專案落地(第三方 SDK、多模組):見 finding 6、7,多模組下追蹤檔與 `scenario` 的對應 spec 沒說。

## 固定席:macrobenchmark-adapter

判:**部分影響**。

- 責任句「不接裝置、不從量測產生門檻」:與 spec 可共存,因為 adb 只在範本腳本裡。但 peak 基準加容差若寫進門檻檔,就會破壞「不從量測產生門檻」,見 finding 2。
- 摘要的「只提醒、回 0」與「基準與門檻分開」:不影響,spec 的判定同樣只提醒。
- WHY「滑動類 P50 與 P90 判退步」「容差取兩者較大」:不影響。spec 沿用同一公式,只是單位換成 KB 的預設值需要另定,見 finding 2。
- PITFALL「新增範本要登記 `_VENDORED_TREE_FILES`」:S12 已涵蓋,不影響。
- `about_code` 清單與 `responsibility` 需同步更新,見 finding 10。

總結:最高嚴重度 major,blocking 共 9 條。
