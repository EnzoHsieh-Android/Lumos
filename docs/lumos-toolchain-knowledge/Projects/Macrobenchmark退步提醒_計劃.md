---
type: project
status: doing
created: 2026-10-21
updated: 2026-10-21
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/macrobenchmark-adapter
related:
  - "[[Systems/compose-metrics-adapter]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Projects/併發與效能表態要合約背書_計劃]]"
  - "[[Projects/Android診斷證據接入_調研]]"
pending_questions:
  - id: Q1
    text: 三個 Android 專案都還沒有 Macrobenchmark 模組:要先在 Lumos 做好讀取器、用假結果檔測(建議),還是先在某個專案加基準測試模組並在實機跑出真結果檔再做?
    class: 範圍
    stage: 需求
    status: 已決
    blocking: true
    decision: "#d1"
  - id: Q2
    text: 退步要不要擋推送?
    class: 行為
    stage: 架構
    status: 自答
    source: Projects/併發與效能表態要合約背書_計劃 2026-10-01 WHY 行:推送前證據不收毫秒;本計劃只提醒
  - id: Q3
    text: 指令在哪裡被叫?
    class: 行為
    stage: 架構
    status: 自答
    source: 官方 CI 自動化頁建議基準排在每晚的建置跑;第一版由消費專案每晚 CI 手動呼叫,不接推送前檢查
  - id: Q4
    text: FrameTimingMetric 等幀耗時指標在結果檔裡的實際欄位名與 sampledMetrics 格式為何?
    class: 資料
    stage: 實作
    status: 自答
    source: "2026-10-21 Citrus_KDS 模擬器實跑的真結果檔(governance/research/macrobench/),鍵名與官方指標頁、Firefox 解析腳本一致;另見本篇〈實測〉"
  - id: Q5
    text: 容差預設值訂多少?
    class: 門檻
    stage: 效能
    status: 延後
    reason: 沒有真實數據量浮動;先用 10%,見 2026-12-21 的回頭條件
  - id: Q6
    text: Citrus_KDS 的基準測試要用哪台裝置跑?(專案已決 d2)
    class: 範圍
    stage: 需求
    status: 已決
    blocking: true
    decision: "#d3"
decisions:
  - content: 先在一個 Android 消費專案加 Macrobenchmark 模組、在實機跑出真結果檔,再依真檔寫 Lumos 讀取器
    id: d1
    context: 三個 Android 專案都沒有基準測試模組與結果檔,讀取器只能用照官方範例造的假檔測;幀耗時欄位格式只有二手來源
    why_chosen: 使用者選 2:格式一次對準真檔,避免照假檔寫完再改;代價是要動消費專案、要實體手機、時程拉長
    decided: 2026-10-21
    valid: true
  - content: 第一個消費專案用 Citrus_KDS
    id: d2
    context: 能用的 Android 專案只有 Citrus_KDS 與 mOrangePos;mOrangePos 啟動會初始化付款 SDK
    why_chosen: 使用者選 Citrus_KDS:Compose 訂單清單,啟動與滑動都能量,沒有付款 SDK 干擾;代價是建置工具較舊,要先確認 Macrobenchmark 版本相容
    decided: 2026-10-21
    valid: true
  - content: 拿結果檔格式、驗流程這一段用模擬器(Android 14 平板尺寸);正式基準與容差改用店裡實際用的平板量
    id: d3
    context: 本機沒接任何實體裝置;官方不建議用模擬器量效能
    why_chosen: 使用者問模擬器行不行並同意分兩步:結果檔格式與機器無關,模擬器足以讓讀取器照真檔寫;代價是容差與基準要等實機才訂得出來
    decided: 2026-10-21
    valid: true
  - content: 本計劃併入 Android 診斷證據調研的第零階段:用 KDS 既有的兩支基準加 Macrobenchmark 自帶的每輪 Trace,手寫一份驗證收據(manifest 加報告),不改 Lumos 核心;轉接 skill 與檢查指令等試跑證明需要再做
    id: d4
    context: Enzo 2026-10-23 帶進 Android 診斷證據接入調研,與本計劃重疊(都以 Citrus_KDS 的 Macrobenchmark 為第一個案例),裁定接手本計劃一起做
    why_chosen: 結果檔讀取器已寫完並驗過,收據試跑可直接沿用同一組基準與裝置設定;不選:另開計劃(兩篇講同一組基準,容易分岔)、先做轉接 skill(調研本身要求先試跑確認 manifest 欄位夠用)
    decided: 2026-10-23
    valid: true
---
# Macrobenchmark退步提醒_計劃

白話：Android 專案自己在實機上跑 Macrobenchmark（量啟動時間、每幀耗時的官方工具），Lumos 只讀它留下的結果檔，跟存好的基準比，列出「哪個情境比上次慢了」。Lumos 不跑測試、不接裝置、不擋推送。

WHY:第一版只提醒不擋推送 [出處:2026-10-21 本對話,使用者選先做 Android Macrobenchmark,擋不擋沿用既有決定] [因:毫秒隨機器與溫度浮動,[[Projects/併發與效能表態要合約背書_計劃]] 2026-10-01 已裁推送前證據不收毫秒] [不選:超過容差就擋推送(會隨機誤擋,且要先推翻那條決定)]
WHY:Lumos 只讀結果檔,不負責建置或執行基準測試 [出處:2026-10-21 本對話] [因:Lumos 是零依賴的 python 工具,沒有裝置也沒有 Gradle;[[Systems/compose-metrics-adapter]] 已用同一條界線] [不選:由 Lumos 呼叫 gradlew 或 adb 跑基準(要裝置、跨專案設定各異、執行時間以分鐘計)]
WHY:判退步要同時過兩道:中位數比基準中位數慢超過容差,而且比基準那次的最大值還慢 [出處:2026-10-21 本對話] [因:官方文件說基準結果本來就會浮動、要看趨勢;只看百分比,基準那次剛好跑得快就會誤報;要求落在基準那次的浮動範圍外,可以濾掉一部分雜訊] [不選:官方建議的 step fitting(拿前後多次建置的滾動視窗比),要存多次歷史且要每晚固定跑,第一版先不做] [代價:只比一次基準,單次跑得特別慢仍可能誤報]
PRIOR-ART: 結果檔格式照官方〈Benchmark in Continuous Integration〉頁的 `<套件>-benchmarkData.json` 範例(context 記裝置、benchmarks 每項有 metrics,每個指標有 minimum/maximum/median/runs) https://developer.android.com/topic/performance/benchmarking/benchmarking-in-ci ;幀耗時的 `sampledMetrics` 百分位鍵照官方指標頁 https://developer.android.com/topic/performance/benchmarking/macrobenchmark-metrics 與 Firefox CI 的解析腳本 https://searchfox.org/mozilla-central/source/taskcluster/scripts/tests/compute-macrobenchmark-results.py (2026-10-21 已用 KDS 真結果檔核對過鍵名,見〈實測〉);判退步的雙道規則借 [[Systems/compose-metrics-adapter]] 的「存基準、只報退步、用指令更新基準放行」形狀;官方 step fitting 見 https://developer.android.com/training/testing/continuous-integration/automation ,原文 Medium 文章本次抓不到(403),細節沒讀到。裁定:借用,不加依賴。
RETIRE-IF: 第一個消費專案接上後連續 8 週,提醒裡確認是真退步的次數為零、或誤報多過真報,就撤掉這個指令;消費專案改用 Android Studio 或雲端測試服務內建的趨勢比對時也撤。
REVISIT:2026-12-21 看有沒有消費專案接上 Macrobenchmark 並跑過這個指令;還沒有就判撤案或延後,延後要寫下一個日期。
REVISIT:2026-12-21 容差預設 10% 是拍的,有消費專案的真實數據後,用同一台裝置重跑同一版本至少 5 次量浮動,重訂預設值。

## 現況(2026-10-21 查)

- 開案當時(2026-10-21)Lumos 沒有任何指令讀執行期的效能數字;現有效能機制是改程式時跳出的檢核題與推送前逐題表態([[Systems/效能檢核目錄]]、[[Systems/棧別提問表態閘]])。這句另派了一個沒看過結論的子代理用原始問題查過,結論相同。
- 最接近的是 [[Systems/compose-metrics-adapter]]:讀 Compose 編譯器報告比基準。它目前只能手動叫,沒有接進推送前的檢查或 CI。
- [[Projects/pitfalls棧別效能追問_計劃]] 寫過「不做效能自動評分(oracle 教訓)」。那條講的是由工具判斷作者對效能題的回答對不對;這次是拿實機量到的數字跟基準比,而且只提醒,不打分也不放行,所以不算翻案。
- 本機三個 Android 專案(mOrangePos、Compass_KDS、Citrus_KDS)的建置設定裡都沒有 Macrobenchmark 或 Baseline Profile 相依,也找不到任何結果檔。照 d1 先在 Citrus_KDS 加模組拿真檔,見下一節。

## 實測(2026-10-21,Citrus_KDS 在模擬器上跑一次)

- KDS 那邊的做法(基準測試模組、假 POS 伺服器、跑法與踩到的坑)記在 KDS 圖譜的 `Systems/效能基準`;改動放在 KDS 本機的 `macrobench` 分支工作目錄。
REVISIT:2026-11-06 KDS 那邊的基準測試模組提交進 KDS repo 了沒;沒有就判要不要提交或撤掉
- 真結果檔存在 `governance/research/macrobench/2026-10-21-kds-emulator-benchmarkData.json`,實作讀取器時拿來當測試資料。
- 跟原本依文件寫的計劃有出入、讀取器要照真檔做的地方:
  - 檔名是 `com_citrus_citruskds_macrobenchmark-benchmarkData.json`,套件名的點變成底線;官方範例寫成點。讀取器要用 `*-benchmarkData.json` 掃,不要拼檔名。2026-10-23 實機上 benchmark-macro 1.4.1 寫出的檔名反而保留點(`com.example.mblab.bench-benchmarkData.json`),兩種都要掃得到。
  - `sampledMetrics` 每個指標除了 `P50`/`P90`/`P95`/`P99`,還有 `runs`,是「每次重複各自的每幀數值」的陣列的陣列(這次五次各 29~33 幀)。
  - 這次的 `metrics` 只有 `timeToInitialDisplayMs`;沒有出現 `frameCount`。
  - `context.build` 有 `brand`、`device`、`fingerprint`、`model`、`version.sdk`;另有 `cpuLocked`、`cpuCoreCount` 等。判「裝置不同」用 `model` 加 `fingerprint`。
- 模擬器的數字:冷啟動中位數約 2188ms(最小 1927、最大 2562);滑動每幀 CPU 耗時 P50 約 36ms、P90 約 153ms。模擬器用軟體畫圖,這些數字只證明流程跑得通,不能當基準,也不能拿來訂容差。

## 要做的事

1. 新指令 `lumos macrobench`,選項比照 compose-metrics:`--repo`、`--json`、`--update-baseline`。
2. 設定檔 `.lumos/macrobench.json`:列出要掃的結果目錄(在目錄裡找 `*-benchmarkData.json`,見上一節的檔名坑)、容差百分比(預設 10)、哪些指標是「越大越好」(預設全部當越小越好)。
3. 基準檔 `.lumos/macrobench-baseline.json`:每個「測試類別 + 測試名 + 參數 + 指標」存中位數、最小、最大,以及裝置型號與系統指紋。
4. 兩種欄位分開判:
   - `metrics`(啟動時間這類,有 median/minimum/maximum/runs):照上面 WHY 的雙道規則。
   - `sampledMetrics`(滑動的幀耗時 `frameDurationCpuMs`、`frameOverrunMs`,只有 `P50`/`P90`/`P95`/`P99`,大寫 P):沒有最大值可比,只比 `P50` 與 `P90` 有沒有超過容差;`P99` 太吵,只列出不判退步。
   - `frameOverrunMs` 是「這一幀比期限晚多少」,負的代表準時。基準是負的、現在變成正的,不論差幅都列為退步,因為那代表開始掉幀。
   - `frameCount` 這類次數欄位不是效能指標,預設忽略(設定檔 `ignore_metrics` 可改)。
5. 比對結果分四種:退步、新出現的情境、這次沒跑到的情境、裝置不同不比。裝置不同時整項不比、只列出來,因為不同手機的毫秒數不能互比。
6. 退步不改結束碼(維持 0);設定檔壞掉才回 2,比照 compose-metrics。
7. 不接進推送前的檢查。建議消費專案在每晚的 CI 上跑完基準後呼叫一次,寫法放進使用說明。

## 條款

- [S1] 當結果檔的某指標中位數比基準中位數慢超過容差、而且比基準最大值還慢時,指令應列為退步並附基準值、現值與差幅 [test:t_macrobench_regression_needs_both]
- [S2] 當只滿足其中一道(超過容差但仍在基準浮動範圍內,或超出範圍但差幅小於容差)時,指令應不列為退步 [test:t_macrobench_single_gate_not_enough]
- [S3] 當結果檔的裝置型號或系統指紋跟基準不同時,指令應整項不比對、列為裝置不同 [test:t_macrobench_device_mismatch_skips]
- [S4] 當指標被設定為越大越好時,指令應反過來判退步 [test:t_macrobench_higher_is_better]
- [S5] 指令算容差時應取「基準絕對值 × 容差百分比」與設定的絕對容差(預設 1)兩者較大的那個:基準是負數(例如每幀超時毫秒數)也按絕對值算比例,基準是零時就是絕對容差,不得除以零,也不得把變快判成變慢 [test:t_macrobench_nonpositive_baseline]
- [S8] 當 `sampledMetrics` 的 `P50` 或 `P90` 比基準慢超過容差時,指令應列為退步;只有 `P99` 變慢時應只列出、不算退步 [test:t_macrobench_sampled_percentiles]
- [S9] 當 `frameOverrunMs` 的基準 `P90` 不大於零、現值大於零時,指令應列為退步,不看差幅 [test:t_macrobench_overrun_crosses_zero]
- [S6] 當帶 `--update-baseline` 時,指令應只用成功解析的結果檔更新基準,解析失敗的檔不得清掉既有基準 [test:t_macrobench_update_baseline_skips_failed]
- [S7] 當設定檔 JSON 壞掉或缺必要欄位時,指令應回 2 並印出哪裡壞;設定檔不存在(專案沒接)或有退步時應回 0,比照 compose-metrics [test:t_macrobench_exit_codes]
- [S10] 當結果目錄裡是 Macrobenchmark 實際寫出的檔(檔名裡套件名的點變底線或保留點、放在子目錄裡)時,指令應找得到並讀出啟動與幀耗時指標 [test:t_macrobench_reads_real_kds_file]
- [S11] 當基準檔裡任何一項缺欄或型別不對(手改、寫壞)時,指令應整份當基準讀不了:回 0、印基準讀不了、不比對,`--update-baseline` 也不得蓋掉它 [test:t_macrobench_corrupt_baseline_entry]
- [S12] 當同一個情境出現在兩個以上的結果檔時,指令應兩份都不收,並明講是重複出現,不得說成結果檔讀不了 [test:t_macrobench_duplicate_scenario]
- [S13] 當用實機跑出的正常版結果當基準時,注入已知變慢那次的結果應剛好報出變慢的那幾項,同一版本正常重跑的結果不得報任何一項 [test:t_macrobench_real_tablet_lab]

## 實機端到端(2026-10-23,SM-X710 平板、Android 16)

- KDS 那組基準(benchmark-macro 1.2.4)在這台平板上兩支都失敗:錯誤是確認不了畫面啟動完成。系統日誌顯示 App 352ms 就顯示了,函式庫查 15 秒的畫格資料都是空的;手動查畫格資料正常、格式也對得上它的解析程式,所以不是格式問題。真正原因沒查出來。
- 另開小專案 `/Users/enzo/orca/workspaces/macrobench-lab`(一個 300 列清單的 App,可從啟動參數注入已知的變慢),用 benchmark-macro 1.4.1 在同一台平板上兩支都跑通。所以 KDS 失敗最可能是 1.2.4 太舊;1.4.1 只要求 compileSdk 34、建置外掛 8.1.1,KDS 都符合。這仍是推論,KDS 升級後跑一次才算證實。
- 三次實跑:正常、注入變慢(啟動多 300ms、每列多 8ms)、正常重跑,結果檔存在 `governance/research/macrobench/2026-10-23-lab-tablet/`。變慢那次報出四項,正常重跑那次原本誤報一項(每幀超時 P90 -1.7→-0.9,容差只按 10% 算是 0.17ms),所以把容差改成有下限(條款 S5、S13)。
- 這台不是店裡實際用的機型時,數字只能證明工具判得對,不能當 KDS 的效能基準。
REVISIT:2026-11-06 KDS 的基準測試函式庫升到 1.4.1 後在實機跑一次,確認兩支都過;還是失敗就查畫格資料為什麼在測試程序裡是空的

## 下一段:驗證收據試跑(2026-10-23 併入,決策 d4)

2026-10-23 已跑完(改用實驗室 App 與實體平板,不是 KDS 模擬器),結果見 [[Verification/2026-10-23_Android驗證收據第零階段試跑]];後續逐層診斷另開 [[Projects/Android逐層診斷_計劃]]。以下是當時的步驟。

調研全文在 [[Projects/Android診斷證據接入_調研]]。這一段只做調研的第零階段,不改 Lumos 核心:

1. 等評測實驗跑完、機器空出來,裝 Google 官方 android-profiler skill,釘調研時看的版本。
2. 用 KDS 既有的兩支基準在模擬器上重跑一次;Macrobenchmark 每輪都會留一份 Perfetto Trace,一起拉回本機。
3. 用 trace_processor 對最慢那一輪跑查詢,把實際跑的 SQL 與結果存下來。
4. 手寫一份收據:manifest 照調研的草案欄位填,報告用 `[MEASURED]`、`[INFERRED]`、`[GAP]` 標籤;原始 Trace 只留本機、記雜湊。
5. 寫成一份驗證紀錄,狀態照調研的寫回規則:模擬器只能算流程驗證,不寫成效能通過。
6. 派一個沒看過對話的 Agent,只靠節點、收據與原始檔重跑核心查詢,記下它卡在哪個欄位;卡住的欄位就是 manifest 要改的地方。

這一段不做:轉接 skill、檢查 manifest 的指令、HPROF、正式環境資料。第 6 步證明人工寫收據容易出錯,才另開設計。

## 不做

- 不跑 Gradle、adb,不管裝置與溫控。
- 不擋推送,不接進推送前檢查與 CI 閘。
- 不做 step fitting 與多次歷史保存。
- 不讀 Play Console 的 Android vitals 這類線上數據。

## 實務隱患

已排除:金流:只讀本機結果檔,不碰交易
已排除:對外送出:不發網路請求
已排除:不可逆:只在帶 `--update-baseline` 時寫基準檔,基準檔在消費專案版控裡可還原
已排除:守衛面:只提醒,不改任何推送前檢查或閘的判定

## 回退

拿掉 `macrobench` 子指令與它的解析函式;消費專案留著的兩個設定檔會被忽略,不影響其他指令。
