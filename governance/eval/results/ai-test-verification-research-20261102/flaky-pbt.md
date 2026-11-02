# 不穩測試／順序依賴 × AI 寫屬性測試：可直接吸收的結論(2026-11-02)

一句話：**「多跑幾次看會不會壞」只抓得到常壞的；偶爾壞的要上百上千次才看得到，所以新測試的重跑是篩子不是證明。順序依賴可以靠打亂與反轉便宜地抓，裝置上靠每測一個行程加清資料幾乎消掉。AI 寫的屬性測試能找到真錯，但約一半回報不成立、約五分之一斷言本身是錯的、能殺掉「違反該屬性」變體的只有約兩成，一定要人審。**

讀法：原文逐字句保留英文並加引號；「推論」是我把結論換算到 Android 的部分，不是論文說的。

下載檔在 `papers/flaky-pbt/`(PDF 與 pdftotext 轉出的 txt)，未執行任何下載內容。

---

## 主題 A：不穩測試與測試互相干擾

### A1. iDFlakies (Lam, Oei, Shi, Marinov, Xie, ICST 2019)

- **版本／全文**：作者站 preprint(mir.cs.illinois.edu，IEEE 版權頁，11 頁)，全文讀完。題目給的 NSF PAR 連結用 curl 逾時、沒讀到，以作者版為準。
- **設計**：Java、Maven + JUnit(非 Android)。683 個專案、5171 個模組，實際能探索 945 個模組；每專案上限 56 小時。五種排法：original-order(原順序重跑)、random-class、random-class-method(先亂類別再亂類別內方法，不跨類別交錯)、reverse-class、reverse-class-method。分類：失敗後重跑「截到失敗為止的失敗順序」，在失敗順序重現且在原順序過→OD(順序依賴)，否則 NOD(非順序依賴)。
- **主要數字**：
  - 共 422 支不穩測試，"213 (50.5%) are classified as OD tests and 209 (49.5%) as NOD tests"(§VI-A)。
  - 單一測試失敗率："varies a lot, from under 1% to over 50%"(§VI-B)。
  - 跑一輪就出現至少一個不穩失敗的機率：reverse-class-method "50.0% overall"(其中 OD 46.8%、NOD 5.3%)；只跑原順序 "2.7%"(§VI-B、Fig. 5)。
  - random-class-method 抓到 162 支 OD("88.0% of all OD tests")；reverse-class-method 只 47 支(25.5%)，但有 4 支是 random 沒抓到的(§VI-C)。
  - 原順序重跑 vs 亂序：NOD 偵測機率 "no generalizable differences"(§VI-C)。
  - 分類用的「重跑截斷的原順序」"failed in only 3 of 7441 classification runs, so we recommend that only truncated failing orders be run"(§III)。
  - 誤判：29 支先被判 OD、後來重查改判 NOD(§III-B，重查比例 20%)。
  - 23 支 OD 落在有 `@FixMethodOrder` 的類別(§VI-D)。
- **作者建議**："we strongly recommend developers to first run the reverse-class-method configuration once to quickly detect a portion of the OD tests and then use the random-class-method configuration to detect more OD tests."(§VI-C)；"simply rerunning tests in the original order where they pass is not a good configuration for detecting flaky tests—it cannot detect any OD test, and it does not have a much higher probability to detect even NOD tests."(§VI-C)；工具預設 "random-class-method with 20 rounds"(§III)；可把亂序併進日常 CI，偵測「for free」(§VI-D)。重查比例："we recommend setting this percentage to 100% when using our tool with spare machine time available"(§III-B)。
- **限制**：只跑 `mvn test` 的單元測試；NOD 很可能漏很多(每專案各自一台機器，沒有資源競爭)；不分析 NOD 成因；結果來自隨機順序，不易逐數重現。
- **不必重做**：「亂序比原順序重跑更能抓不穩測試、先反轉一次再亂序最划算、原順序重跑抓不到順序依賴」在 Java/JUnit 上已量過。

### A2. Wei, Yi, Xie, Marinov, Lam — 隨機順序抓順序依賴的機率分析(TACAS 2021)

- **版本／全文**：作者站 PDF(與 Springer 開放版同，含 CC BY 4.0 聲明，18 頁)，全文讀完。NSF PAR 連結 curl 逾時，未讀。
- **設計**：Java/JUnit，iDFlakies 資料集中 121 個有不穩測試的模組；249 支 OD(192 victim、57 brittle)。先跑 10 次單獨執行判 victim/brittle，再跑「每一對 ⟨t, v⟩」找 polluter、跑 ⟨p, t, v⟩ 找 cleaner，再用這個抽象**不實跑**就算出失敗率。
- **名詞**：victim＝單獨跑會過、前面跑了 polluter(汙染者)就壞；brittle＝單獨跑會壞、前面要有 state-setter；cleaner＝夾在中間能清掉汙染。
- **主要結論**：
  - 最簡情形(全在同一類別、所有 polluter 共用 cleaner)失敗率 = π/(π+γ+1)(π＝polluter 數，γ＝cleaner 數)(§4.2)。
  - 實測失敗率平均：不限類別順序 fA "38.4%"、JUnit 可跑的類別相容順序 fC "38.0%"(§4.3)；"some OD tests have a rather low flake rate, as low as 1.2%"(§1)。
  - Hadoop 範例：392 支測試，fC "4.5%"、fA 10.5%(§2、§4.3)。
  - **簡單改法：上一個順序全過，就跑它的反轉**。最簡情形下條件機率從 π/(π+γ+1) 升到 π/(π+γ)；249 支實測(各抽 100,000 順序)平均 "38.0%" → "45.3%"(ΩC)，p≈10⁻⁴²(§4.4)。iDFlakies 已改成預設這樣跑。
  - **系統化兩兩相鄰覆蓋(Tuscan square)**：一個類別有 n 支測試時，n 個順序就能讓每一對 ⟨t, t'⟩ 都相鄰一次(n=3 要 4 個、n=5 要 6 個)，"guaranteeing to detect all OD tests that depend on one other test"(摘要)。跨類別用貪婪法；跟「每一對單獨跑」比，順序數只剩 "3.68%"、測試執行次數 "51.8%"(§5.2)。只用類別內那部分順序就抓到 "44 new OD tests"。
  - 前作 iFixFlakies："in 98% of cases, binary search finds one test to be a polluter"(§4.1)；"91% of the truly OD tests in the iDFlakies dataset are victims"(§1)。
  - 單獨重跑 10 次判是否不穩："using 10 runs is a common industry practice to check whether a test is flaky"(§4.1)。
- **限制**：抽象可能與實跑不同(群組汙染、順序中變成 NOD 等，作者說少見)；只處理「依賴單一其他測試」的 OD；不處理 NOD。
- **不必重做**：「隨機順序對個別 OD 測試的失敗率分布(平均約 38%、最低 1.2%)」、「全過就反轉」能提高偵測率、「n 個順序覆蓋類別內所有相鄰對」的構造都已證明；我們只要套公式算預算。

### A3. 「重跑一萬次仍有漏網」的出處：FlakeFlagger(Alshammari, Morris, Hilton, Bell, ICSE 2021)

- **查證結果**：就是 FlakeFlagger。摘要原句："rerunning the test suites of 24 projects 10,000 times each, and found that even with this many reruns, some previously identified flaky tests were still not detected"。Gruber 等的 Python 研究是另一篇(重跑 400 次，見 A3b)，不是一萬次那篇。
- **版本／全文**：Jon Bell 網站 preprint(13 頁)，全文讀完。
- **設計**：Java/Maven，24 個專案、22,245 支測試，每個專案整套跑 10,000 次("over 5 years of computation time")；每次跑完重開機；**不打亂順序**(所以量的是 NOD)；Ubuntu 18.04、OpenJDK 8、4 CPU/8GB。
- **主要數字**(§II-B)：
  - 811 支不穩，"about 3.6% of the total number of tests"。
  - "only roughly a quarter of all of the flaky tests that we found in 10,000 runs would have been found with 10 reruns, roughly half with 100 reruns and roughly two thirds with 1,000 reruns."(假設每次失敗獨立)
  - "more than 33% of total flaky tests fail in less than or equal 10 times, 22% of flaky tests fail more than 10 and less than or equal 100 out of 10,000."
  - 換環境重現：iDFlakies 回報的 70 支 NOD 只重現 28 支；DeFlaker 的 20 支只重現 10 支；"even with 10,000 reruns, we could not detect all flaky tests."
  - 總結："only half of the flaky tests that we found failed more than 100 times out of the 10,000 runs."
  - 分類器(不重跑、靠特徵預測)：599/808 抓到，誤報 406(內文 §IV-B；貢獻列表寫 380，論文自身兩處數字不一)，對照的字彙法誤報 4,683；最有用的特徵是執行時間、涵蓋率、涵蓋最近改動行數、用到第三方函式庫；"we do not find test smells to be a strong indicator of flakiness"。
- **作者建議**：要找全不穩測試得重跑上千次，但這不實際；應發展不重跑的偵測(他們的分類器)。也引 Facebook "assume that all tests are flaky"、Google 多執行緒測試一律視為可能不穩。
- **限制**：單一平台；沒打亂順序；即使一萬次也沒找全。
- **不必重做**：「重跑 10／100／1000 次各能找到約 1/4、1/2、2/3」與「換機器只重現一半」已量過，我們不用自己跑萬次實驗。

### A3b. Gruber, Lukasczyk, Kroiß, Fraser — Python 不穩測試(ICST 2021)

- **版本／全文**：arXiv 2101.09077 v1(11 頁)，全文讀完。
- **設計**：Python/pytest，22,352 個 PyPI 專案、876,186 支測試；每專案同順序 200 次 + 隨機順序 200 次(共 400 次)；把 200 次切成 10 組×20 次跨機器、隔數小時，用來分出基礎設施造成的不穩。
- **主要數字**：
  - 7,571 支不穩；"Order dependency is a much more dominant problem in Python, causing 59 %"；基礎設施 28%；其餘 13% 主要是網路與亂數 API(摘要)。
  - 每支測試的偵測機率公式 Uₜ(n) = 1 − (1−P(FAIL))ⁿ − (1−P(PASS))ⁿ + …，假設每次獨立(§III-D3)。
  - (a) "In order to be 95 % sure that a test case is not flaky due to non-order-dependent reasons, one would have to run it at least 170 times. For order-dependent flakiness, this number is lower, at 31 random-order executions."
  - (b) "If you rerun your tests ten times, you should not expect to find more than 33 % of all NOD flaky tests and 54 % of all OD flaky tests on average."
  - (c) 找到 80% NOD 平均要 110 次(95% 信心要 472 次)；OD 49 次(95% 信心 209 次)。
  - (d) **失敗後要重跑幾次才能確認是不穩而非真錯**："for the majority of NOD flaky tests, only 1 rerun is needed to achieve a statistical confidence of 95 %. For OD flakiness, 3 reruns are needed"；"common practice of failure reruns [19] is generally sufficient (when ignoring infrastructure flakiness, which often manifests itself in failure bulks)."
- **不必重做**：「要證明一支測試不是 NOD 不穩，平均 170 次；OD 用隨機順序 31 次」「失敗後 1–3 次重跑多半夠判是否是不穩」已有大樣本估計(Python)。

### A4. Android 官方文件與 Gradle test-retry

**[測試穩定性(Big test stability)](https://developer.android.com/training/testing/instrumented-tests/stability)**(WebFetch 讀全頁)
- 主因是同步："These synchronization issues are a primary source of flakiness"。
- 不要 sleep："You should avoid pausing your tests for an arbitrary period (sleep)…"；"Key Point: Use Idling Resources if needed in small UI tests, and wait-until APIs in bigger UI tests."
- 換成可查詢閒置的版本：協程用 `TestDispatcher`、RxJava 用 RxIdler。
- 裝置狀態：避免系統更新對話框、磁碟不足打斷測試。
- Gradle 管理裝置 "contain mechanisms to retry in the event of device disconnections"。
- 重試："a retrying mechanism can help maintain developer productivity by running the test a number of times until it passes"；"Key Point: Add retrying mechanisms to big tests, but always fix flaky tests."；典型做法是 JUnit rule、CI 重試步驟、重開無回應的模擬器。
- 這頁**沒有**談 Orchestrator、清資料、測試隔離、「新測試要跑幾次」。

**[Android Test Orchestrator](https://developer.android.com/training/testing/instrumented-tests/androidx-test-libraries/runner)**
- "allows you to run each of your app's tests within its own invocation of `Instrumentation`"。
- "**Minimal shared state:** … To remove _all_ shared state from your device's CPU and memory after each test, use the `clearPackageData` flag."；Gradle 註解："run its "pm clear" command after each test invocation. This command ensures that the app's state is completely cleared between tests."
- 設定：`testOptions { execution 'ANDROIDX_TEST_ORCHESTRATOR' }`、`testInstrumentationRunnerArguments clearPackageData: 'true'`、`androidTestUtil 'androidx.test:orchestrator:…'`。
- 代價："a possible increase in test execution time as the Android Test Orchestrator restarts the application after each test."
- 另有分片 `-e numShards / -e shardIndex`；頁面**沒有**隨機順序選項。

**[Gradle test-retry plugin README](https://github.com/gradle/test-retry-gradle-plugin)**(raw README.adoc 讀全文)
- "By default, all failed tests passing on retry prevents the test task from failing. … This setting can be changed so that flaky tests cause build failure, which can be used to identify flaky tests."
- "**NOTE:** Retrying tests alone is not a viable flaky test mitigation strategy. This plugin should only be used alongside processes for tracking and fixing discovered flaky tests."
- `failOnPassedAfterRetry`："Whether tests that initially fail and then pass on retry should fail the task. This setting defaults to `false`"。**設 `true` 就把「重試才過」變成建置失敗，但報告裡會區分出它是不穩(先紅後綠)而不是穩定的紅。**
- 其他：`maxRetries`(預設 0＝不重試)、`maxFailures`(一輪失敗太多就不重試，防磁碟滿這類全面壞掉)、`failOnSkippedAfterRetry`(預設 true)、`filter`(只讓某些類別／註解重試)、`classRetry`(整個類別一起重試，給共用狀態的類別)。測過 JUnit4 4.13.2、JUnit5 5.9.2。
- 它是「augments Gradle's built-in test task」；遇到自訂 TestFramework 會停用重試。→ **推論**：它管本機 `test<變體>UnitTest`，管不到 `connectedAndroidTest`；裝置那路的重試要另做(JUnit rule 或 CI 步驟)。

### A5. 執行順序與跨測試狀態(官方文件)

- **JUnit4**：`MethodSorters` 只有固定順序："DEFAULT: Sorts the test methods in a deterministic, but not predictable, order"、"JVM: … the order from the JVM may vary from run to run"、"NAME_ASCENDING"。但 **JUnit 4.13 起有 `Ordering`**："An `Ordering` can reverse the order of tests, sort the order or even shuffle the order."，`Ordering.shuffledBy(Random random)`，透過 `Request.orderWith(Ordering)` 或類別上的 `@OrderWith`(PR #1130)。4.13 的釋出說明：`@FixMethodOrder` 的類別不會被重排，同時標 `@OrderWith` 和 `@FixMethodOrder` 會驗證失敗(PR #1638)。→ 所以「JUnit4 只有固定順序」不完全對：**`@FixMethodOrder` 只能固定，但 4.13 的 Ordering 能洗牌**；Gradle 沒有直接開洗牌的旗標，要自己寫 runner 包裝或 `@OrderWith` 工廠。
- **JUnit 5/6**(頁面顯示 JUnit 6.1.3)：`MethodOrderer.Random`(since 5.4)，"orders methods pseudo-randomly"；預設種子是 "the value returned by System.nanoTime() during static class initialization"，"logged at `CONFIG` level"(較舊 5.7 版 Javadoc 寫 INFO，版本間不同)；固定種子用 `junit.jupiter.execution.order.random.seed`；全域預設排序器用 `junit.jupiter.testmethod.order.default`；沒指定時 "deterministic but intentionally non-obvious"。另有 `ClassOrderer`。JUnit Vintage 能在 Platform 上跑 JUnit4，但頁面說它已棄用、只供遷移期。→ **推論**：`MethodOrderer`／`ClassOrderer` 是 Jupiter 的 API，套不到 Vintage 跑的 JUnit4 測試(未實測)。
- **Gradle Test 任務**：沒有隨機順序選項；`forkEvery`："The maximum number of test classes to execute in a forked test process. The forked test process will be restarted when this limit is reached."
- **Robolectric**：`@Resetter` Javadoc："Indicates that the annotated method is used to reset static state in a shadow."，且 "The Robolectric test runner will call Resetter annotated methods during test teardown" "if the shadow class or its targeted Implements class has been loaded by the ClassLoader"——**它只重設 Android 框架影子的靜態狀態**。App 自己的靜態狀態：Robolectric 貢獻者(非官方文件，issue #3108)說 "You actually get a new Application object for each test because tests should be hermetic"、若壞了 "you have some static state somewhere that is not being torn down"，建議讓測試用 Application 實作 `TestLifecycle` 在 `afterTest()` 清。→ 官方文件沒找到明講「App 單例會跨測試殘留」的句子；這條屬社群說法，標註清楚。

---

## 主題 B：AI 來寫屬性測試

### B1. Agentic Property-Based Testing(Maaz, DeVoe, Hatfield-Dodds, Carlini；arXiv 2510.09907)＋ Anthropic 文章

- **版本／全文**：arXiv v1(唯一版本，NeurIPS 2025 DL4Code workshop，21 頁含提示詞附錄)，全文讀完；Anthropic 文章(2026-01-14)用 WebFetch 讀。
- **設計**：Python + Hypothesis。代理＝Claude Code 上的一份提示詞(六步：分析目標、讀懂、提屬性、寫測試、執行與分流、寫報告)。100 個套件(15 標準函式庫、15 熱門第三方、70 隨機抽自前 5000 名)、933 個模組；Claude Opus 4.1；136.6 小時、$5,474.20。
- **主要數字**：
  - 984 份錯誤報告；人工抽 50 份(雙人獨立評，κ = 0.31，協商定案)："56.0% (95% CI: 42.2%, 69.8%) of reports were determined to be valid bugs, and 32.0% (95% CI: 19.1%, 44.9%) were valid and worth reporting."(§4)
  - 用 15 分評分表讓 Opus 4.1 打分，滿分的 21 份："18 of the 21 top-scoring reports were valid, and 17 of those were both valid and worth reporting"(摘要寫 86% / 81%)。
  - "the false discovery rate has a 95% CI of [30.2%, 57.8%]"(§5)。
  - 每份報告 $5.56，換算 "$9.93/valid bug"。
  - 回報 5 個、3 個 patch 合併；dateutil 那個被維護者判為刻意行為。
  - Anthropic 文章補第二階段(Sonnet 4.5、10 個重要套件、由評估代理查正確性與嚴重度、高嚴重度給 3 位專家審，"we then discarded any bug where any of the three manual reviewers were uncertain of its validity")。文章也承認代理自己寫的修補 "is not correct"(numpy 那個)。
- **怎麼過濾假陽性**(提示詞附錄 A，逐字)：
  - "**Only test properties that the code is explicitly claiming to have.** … Do not make up properties that you merely think are true. Proposed properties should be **strongly supported** by evidence."
  - 失敗分流三步：重現檢查(做出最小獨立重現、同一輸入是否穩定失敗)→合法性檢查("Does the failing input represent realistic usage?"、"Do callers of this code make assumptions that prevent this input?"、"Is the property you're testing actually claimed by the code?")→影響評估。
  - 測試**過了**也要查："Does the test actually exercise the claimed property?"(文章舉例：有個屬性因為被 try-catch 包住才「過」，拿掉後才露出真錯)。
  - 寫策略："If soundness and completeness are in conflict, prefer writing sound but incomplete properties."；"Do not constrain strategies unnecessarily."
  - 事後：評分表排序 + 人工審。
- **作者自述限制**："we did not manually review all 984 bug reports"；"intent ambiguity: the agent cannot distinguish intentional design violations from bugs"(requests 的 LookupDict 例)；文章："only the library maintainers can decide what the correct property to test is"。
- **不必重做**：「讓代理照『只測程式明說的屬性＋失敗三步分流＋過了也查』去跑，約一半報告是真錯、評分表可把前段精度拉到八成以上」在 Python 上已量過。

### B2. PBT-Bench(Jing, Wang, Zhang, Du；arXiv 2605.15229)

- **版本／全文**：v4(2026-10-06，27 頁)，全文讀完。
- **設計**：Python + Hypothesis。100 題、40 個純 Python 函式庫、共 365 個人工把關的植入錯(平均 3.65 個／題)，植入點在公開 API 下至少兩層、原有測試照樣綠；難度 L1 87、L2 184、L3 94。評分是 F→P：每支測試函式對每個錯「在有錯版紅、只拿掉這個錯就綠」才算抓到。8 個模型 × 兩種提示(開放式 vs 明說用 Hypothesis＋屬性分類)× 3 輪＝4,800 條軌跡；另加 Claude Opus 4.8(OpenHands 與 Claude Code)。
- **主要數字**：
  - PBT 模式抓錯率 42.1%–83.4%；最好 Sonnet 4.6 83.4%；Opus 4.8 81.2%，Claude Code 中 78.6%(表 1)。"No configuration finds all bugs on more than 67% of problems"。
  - 16 格聯集 "reliably finds 99.5% of bugs, 12.7 points above the best single cell"；同一模型兩種模式互補佔新增的 65%。
  - Opus 4.8 開放式提示下 "stops after exposing one bug"：中位數只寫兩支測試，完整抓全只 12%；改用「涵蓋整份規格」的框架指示就 +41.5pp，屬性分類表只再 +0.2pp(表 2)。
  - **失敗原因**(每格抽 20 個失敗、規則判別，§6.2、附錄 A.12)：開放式的失敗 "mostly incorrect assertions (59%; the test's expected value is itself wrong) and overly concrete tests (32%)"，另有 "8% Flaky Oracle (agent re-uses the library under test as its own oracle…)"、1% 屬性過弱；PBT 模式的失敗主要是搜尋問題："assume misuse (31%, up to 75% for GLM 5.1) … to exclude exactly the inputs that trigger the bug; and wrong strategy range (31%…)"，錯誤斷言降到 21%。
  - 防作弊：明確叫它作弊的 30 條軌跡 "zero attack signatures such as hard-coded assertions or version checks"。
  - 測試本身的不穩：重算 7,699 個判定只有 2 個因 "test nondeterminism" 改變；輪間差異來自 "Hypothesis's random search"。
- **假陽性怎麼處理**：F→P 評分本身排除「在修好版也紅」的測試(錯誤斷言那類)；資料另記 test precision(有用的／全部測試函式)，但正文沒給總數。
- **作者建議**：主指標用 PBT 模式抓錯率，完整抓全率當次要；提示詞要警告 "do not use assume() to skip inputs that look suspicious; inputs that look suspicious are exactly the ones that expose the bug"(**尚未驗證**，作者明說留待未來)。
- **限制**：植入錯而非真實錯；只 Python、英文文件；`max_examples=200` 可能壓低 L2/L3；多數只用一種代理框架；Codex 沒跑出檔案未納入。附錄 A.17 說換 jqwik 等語言要處理編譯、逐函式執行、文件品質與上游測試強度。
- **不必重做**：「AI 寫屬性測試最大的漏是用 assume／過窄的產生範圍把觸發區排掉，其次是預期值自己就錯」「要它涵蓋整份規格而不是找一個錯」「多模型或多模式聯集明顯更全」已量過。

### B3. Can LLMs Write Good Property-Based Tests?(Vikram, Lemieux, Sunshine, Padhye；arXiv 2307.04346)

- **版本／全文**：v2(2024-07-22，12 頁；v1 只 2 頁)，全文讀完。
- **設計**：Python + Hypothesis；10 個函式庫 40 個 API；GPT-4、Gemini-1.5-Pro、Claude-3-Opus；單段 vs 兩段提示(先抽最多 5 條屬性、每條寫一支)；每種取樣 5 次、temperature 0.7；每支測試呼叫 1,000 次。
- **三個指標**：有效(1,000 次呼叫都沒有非斷言錯)、健全(1,000 次都沒有斷言錯；假設「斷言錯多半是屬性錯而不是程式有 bug」，作者自稱 "This is a weak assumption")、屬性覆蓋(LLM 產生「屬性變體」：呼叫原 API 後把輸出改到違反該屬性，測試要能殺掉)。
- **主要數字**：
  - 3,110 支測試函式："1,221 (39.26%)" 有效、"814 (26.17%)" 有效且健全；最好 GPT-4 兩段 41.74%，"synthesize valid and sound property-based test functions in 2.4 samples on average"(表 2)。
  - **屬性本身錯**：人工標 219 條斷言，"173 (79%) were sound"(各模型 74–83%)，κ = 0.862(表 3)。→ 約 21% 斷言是錯的。錯的來源："hallucination of properties outside of the API documentation" 與 "assertions only failing due to very specific edge cases"。
  - 健全度指標對人工標註 "precision of 100% and recall of 97.14%"；唯一漏的是 1,000 次沒產生到那個邊界輸入。
  - **屬性過弱**：有效且健全的測試只殺掉 "40–80% of property mutants"(表 4)；最好的組合 "covering 20.5% of documented properties"(表 5)。
- **作者建議**：兩段提示(一支只測一條屬性)明顯較好；用「屬性變體」量強度。
- **限制**：只 Python；成熟函式庫，文件與程式可能在訓練資料裡；有等價變體問題；斷言錯也可能是真 bug。
- **不必重做**：「AI 寫的屬性約五分之一是錯的、能真正抓違規的只有兩成、一支只測一條屬性較好、用『改輸出違反屬性』的變體量強度」已有方法與數字。

### B4. Kotlin 屬性測試工具現況與 Android 本機測試

- **Kotest property(6.2)**：`kotest-property` 可獨立使用——"You do not need to be using Kotest as your test framework"；`forAll` 收回傳 Boolean 的函式、`checkAll` 用斷言("valid if no exceptions are thrown")；"By default, Kotest will run the property test 1000 times."；失敗時 "Kotest will output the seed that was used"，用 `PropTestConfig(seed = …)` 固定；失敗種子寫到 `~/.kotest/seeds/<spec>/<testname>`、下次先用、過了刪掉，`PropertyTesting.writeFailedSeed = false` 可關；預設 "tolerates no failure"(`maxFailure` 可放寬)。Kotest 自家說明(context7，repo 內 PROPERTY-TESTING-REFERENCE)給在 JUnit 測試裡用 `runBlocking { forAll … }` 的寫法，並提醒 "a @Test method with a block body that returns a value is silently skipped by JUnit"。→ **推論**：在 Android 的 JUnit4 本機測試(含 `RobolectricTestRunner`)裡，用 `runTest { checkAll(...) }` 或 `runBlocking` 包起來即可用；沒在專案實測。
- **jqwik(1.10.2)**："an alternative test engine for the JUnit 5 platform"，可跟 Jupiter 或 Vintage 並存；Gradle 要 `useJUnitPlatform { includeEngines 'jqwik' }`；預設 1000 次(`jqwik.tries.default`)；失敗後預設 `SAMPLE_FIRST`(先重跑上次縮小後的樣本)、有 `.jqwik-database`；邊界值預設 `MIXIN`；有 Kotlin 模組。**不能**在 JUnit4 runner(含 Robolectric)底下跑。另外：**1.10 起附「Anti-AI Usage Clause」，聲明不供 AI 代理使用，並在每次執行時往 stdout 印一行針對 AI 代理的文字**——對「AI 寫、AI 跑、AI 讀結果」的流程是採用上的硬傷(輸出被刻意汙染、也違反作者意願)。→ **推論**：我們這種流程選 Kotest property。

---

## 綜合：換算到 Android(以下除引號外都是推論)

### 1. 新測試要重跑幾次

- **先分清兩件事**：「失敗後重跑確認是不是不穩」跟「新測試證明自己不是不穩」成本差兩個量級。前者 1–3 次(Gruber (d))；後者要證到 95% 不是 NOD 不穩平均 170 次、OD 31 次隨機順序(Gruber (a))，FlakeFlagger 說 10 次只能抓到約 1/4。
- **所以重跑是篩子**：每個 PR 對「新增或改動的測試類別」跑一個固定小預算，抓常壞的；稀有不穩靠排程大預算與上線後追蹤，不在 PR 閘上假裝能證明。
- **建議預算**(本機單元測試很便宜，主要防 OD；單元測試照標準應該已經沒有網路、真時間、真執行緒，NOD 來源少)：
  - PR 閘：改動的類別**原順序 1 次 + 反轉 1 次 + 隨機順序約 20 次**，全過才算。依據：iDFlakies 預設 20 輪、反轉一輪就有 50% 機率露出失敗輪；Wei 的平均失敗率約 38%，套 1−(1−f)ⁿ：f=38% 時 5 次約 91%、10 次約 99%；但 f=4.5%(Hadoop 例)20 次只約 60%，95% 要約 65 次；f=1.2% 要約 249 次。**PR 閘只保證抓到中高失敗率的，這句要寫進規則，不要讓人以為 20 次是證明。**
  - 打亂順序時：上一個順序全過，下一個用它的反轉(Wei 實測平均 38%→45.3%)。
  - 類別內方法數 n 不多時，可以用 Tuscan square 的 n 個順序代替隨機，**保證**抓到所有「依賴單一其他測試」的類別內 OD；這是確定性的、可當證據，比隨機 20 次更好講。
  - 排程(夜間)：整個模組亂序跑上百輪，量稀有的；這時 FlakeFlagger 的 1/4、1/2、2/3 曲線是預期上限。
- **裝置測試**：一次重跑要好幾分鐘，預算小得多。建議新加的裝置測試在 PR 跑 **3–5 次**(只抓高失敗率的)，重點放在消除原因(同步、sleep、裝置狀態)而不是次數；排程再多跑。

### 2. 怎麼打亂順序

- **本機 JUnit4**(Android 本機測試的預設)：JUnit 4.13 的 `Ordering.shuffledBy(Random)` 搭 `@OrderWith` 工廠或包 `Request.orderWith`；種子要印出來、可重放。`@FixMethodOrder` 的類別 4.13 不會被重排——這種類別本身就是順序依賴的宣告，iDFlakies 在這類別裡抓到 23 支 OD，審查時應該問它還需不需要。`RobolectricTestRunner` 能不能吃 `@OrderWith` 沒驗，要先做一次最小實驗。
- **類別順序**：Gradle 沒有洗牌旗標。最小解是改變 `--tests` 篩選的組合分批跑，或寫一個 JUnit4 Suite 用 shuffle 排類別；類別間的靜態殘留用 `forkEvery = 1`(每個類別新 JVM)切斷，但代價高，只建議在排程或懷疑跨類別汙染時開。
- **若已用 JUnit Platform(Jupiter)**：`junit.jupiter.testmethod.order.default = org.junit.jupiter.api.MethodOrderer$Random`(類別用 ClassOrderer 對應設定)，失敗時用 `junit.jupiter.execution.order.random.seed` 重放；Vintage 跑的 JUnit4 測試套不到。
- **Robolectric 特別注意**：它每支測試給新的 Application、會重設框架影子，但 App 自己的 `object`、單例、靜態快取不會被重設；這正是 Robolectric 本機測試最可能的 OD 來源，亂序最該跑的就是這些類別。

### 3. 裝置上怎麼隔離

- 開 **Orchestrator + `clearPackageData`**：每支測試自己的 Instrumentation、跑完 `pm clear`，消掉 App 自己的記憶體與磁碟狀態，一支當掉不拖垮其他。代價是每支都重啟 App。
- 清不掉的：系統設定、權限、其他 App、外部儲存、帳號、時區語系；這些要在測試裡自己設、自己還原。
- NOD 主因是同步：用 Idling Resource(小測試)／wait-until(大測試)、注入 `TestDispatcher`，不用 sleep。
- 重試：官方建議大測試加重試，但**重試過的要留紀錄並算成不穩**。本機用 test-retry plugin 設 `maxRetries = 2`、`failOnPassedAfterRetry = true`(Gruber (d)：多數不穩 1–3 次重跑就會過，2–3 次夠把「不穩」跟「真紅」分開)、`maxFailures` 設上限；裝置那路 plugin 管不到，用 JUnit rule 或 CI 步驟，並把「重試後才過」寫進報告。

### 4. 哪些純函式適合屬性測試

- 優先：有明說規則、沒有副作用、輸入空間大的。
  - **金額**：拆帳 `sum(split(total, n)) == total` 且每份差不超過 1 分；折扣與稅「價格變大結果不變小」；四捨五入兩次等於一次；不同計價單位換算來回不損失(在規格允許的精度內)。用整數分或 BigDecimal 產生器，邊界放 0、負數、最大值、會溢位的值。
  - 格式化／解析來回：`parse(format(x)) == x`(金額字串、日期、`kotlinx.serialization` JSON)。
  - 排序、篩選、分頁：長度不增、元素保留、排序後有序、分頁合起來等於全部。
  - 有參考實作的：快的 vs 簡單的同結果。
  - 狀態機：一串操作後的不變量(PBT-Bench 的 L3；最難、AI 最常漏)。
- 不適合：依賴裝置、網路、時鐘、資料庫的(PBT-Bench 的「可測性」條件明確排除這些)。

### 5. 屬性測試的結果怎麼審(AI 寫的一律走這套)

1. **屬性有沒有出處**：只接受需求或文件明說的(Agentic PBT 的規則)；約 21% 的 AI 斷言是錯的(Vikram)，來源是自己編的屬性和沒處理邊界。
2. **失敗時先做三步分流**：能最小重現嗎(印出種子／縮小後輸入)→ 輸入在合法範圍內嗎(看呼叫端有沒有先驗)→ 屬性真的是規格說的嗎。預期約一半 AI 回報不成立(56% 成立，誤報 95% 信賴區間 30–58%)，一定要人裁。
3. **過了也要查**：產生器有沒有用 assume／filter 或太窄的範圍把觸發區排掉(PBT-Bench 最大的失敗原因，各 31%)；是不是拿被測程式自己當答案(8%)；有沒有 try-catch 吞掉失敗。
4. **強度用故障證明**：照 Vikram 的「屬性變體」做——把被測函式的輸出改到違反這條屬性，測試必須翻紅、還原翻綠；最好的 AI 也只覆蓋 20.5% 的屬性，所以這一步不能省。
5. **一支測一條屬性**、要求涵蓋整份規格(PBT-Bench：Opus 4.8 不被要求就只找一個錯)。
6. **可重現性**：種子要進收據；CI 上 `~/.kotest/seeds` 不會留，失敗種子要另存；屬性測試本身也是隨機的，同一版本兩次結果不同時要分清是搜尋運氣還是測試不穩。

---

## 跟〈各技術棧測試撰寫與工具檢驗接入標準 v1〉的對照

檔案：`skills/lumos-project-notes/commands/test-quality-standard.md`

**一致**
- 標準〈審查時〉："合法性質測試、确定性與 snapshot 可提供補充證據，配獨立已知答案或其他足夠約束。例如只驗排序兩次等於一次，永遠回傳空陣列也能過；再驗元素保留、順序與已知例子。" ↔ Vikram 的「有效且健全但斷言弱」(只殺 40–80% 變體、覆蓋 20.5%)、PBT-Bench 的「屬性過弱」「拿自己當答案」。兩邊都說：屬性測試過了不代表對，要另有約束。
- 標準〈Android 本機單元測試的驗收標準〉不算過的證據："重試到過才綠:官方說重試只是保住開發速度,不穩的測試一定要修。" ↔ 官方 "Add retrying mechanisms to big tests, but always fix flaky tests."、test-retry README "Retrying tests alone is not a viable flaky test mitigation strategy."。
- 標準 "不用 `Thread.sleep` 或真實時間等結果,用虛擬時間;非同步工作改用可控制的 dispatcher,固定等待只會讓測試又慢又不穩。" ↔ 官方穩定性頁的 sleep 警告與 `TestDispatcher` 建議。
- 標準〈開發時〉的「expected 要有獨立來源」↔ PBT-Bench 開放式失敗 59% 是「預期值自己就錯」。

**補強(標準沒寫、文獻給得出做法)**
- 標準只說「重試到過才綠」不算，沒說**機械怎麼擋**：本機建議寫明 `failOnPassedAfterRetry = true`(預設是 false，預設就是會吞掉)；裝置那路 plugin 管不到，要另外記。
- 標準沒有**順序依賴**這一類：沒提亂序、反轉、`@FixMethodOrder`、Robolectric 下 App 單例殘留、`forkEvery`、裝置上的 Orchestrator + `clearPackageData`。可補一條「新測試在 PR 閘跑原順序＋反轉＋小預算亂序，並明講只抓得到中高失敗率」。
- 標準沒說**新測試要重跑幾次、能證明到什麼程度**：可補 Gruber/FlakeFlagger 的數字當上限說明，防止有人把「跑 10 次都綠」當成「不是不穩」。
- 性質測試：標準只說「補充證據」，可補**怎麼審**(上面五步，特別是 assume／範圍排掉觸發區、屬性變體當故障證明、種子進收據)。「屬性變體」正好是標準「故障證明挑本次需求」在屬性測試上的具體做法。
- 工具選擇：標準表格寫「純JVM評估PIT」，沒提屬性測試工具；可補「Kotest property 可在 JUnit4 本機測試裡用；jqwik 要 JUnit Platform、跑不了 Robolectric，且有反 AI 條款」。

**衝突或張力**
- **跑的次數 vs「只跑受影響的模組」**：標準 "單元測試在本機 JVM 跑,每次提交跑、只跑受影響的模組。" 文獻說抓稀有不穩要上百上千次；兩者不直接衝突，但若加「新測試重跑 N 次」，要寫清楚只套在改動的類別、預算多少，不然會跟「快」的要求打架。
- **重試本身**：官方建議大測試加重試、Gruber 說失敗後 1–3 次重跑多半足以判不穩；標準只說「不算過」，沒說能不能開重試。建議明講「可以開，但重試後才過＝報不穩、建置照紅(或至少進追蹤)」，否則有人會以為標準禁止重試。
- **「性質測試只是補充證據」vs 屬性測試能找到真錯**：Agentic PBT 用屬性測試找到 numpy 等真 bug。不衝突：屬性測試在**找錯**時很有用，但當**驗收證據**時仍要獨立答案或故障證明；標準的定位可以保留，但建議加一句「屬性測試可以當找錯工具，失敗走分流、通過走強度檢查」。
- 標準 "所有執行限隔離的本機、可信 fixture" ↔ Kotest 預設把失敗種子寫到 `~/.kotest/seeds`(家目錄)：在共用機器或 CI 上這是測試之間的跨次狀態，收證時要嘛關掉(`writeFailedSeed = false`)、要嘛把種子納入收據。

---

## 沒讀到或沒驗的

- 題目給的兩個 NSF PAR 連結 curl 都逾時，改讀作者站同篇全文。
- Robolectric「App 單例跨測試殘留」沒有找到官方文件原句，只有 issue 裡貢獻者的話。
- `RobolectricTestRunner` 吃不吃 JUnit 4.13 的 `@OrderWith`、Jupiter 排序器套不套到 Vintage，都沒實測。
- PBT-Bench 的 test precision 總數只在釋出資料裡，正文沒給。
- 四篇屬性測試研究全是 Python + Hypothesis；換到 Kotlin/Kotest 的數字都還沒有人量過。
