---
type: project
status: doing
created: 2026-11-02
updated: 2026-11-02
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
related:
  - "[[Projects/Android單元測試標準實機演練_計劃]]"
  - "[[Projects/新增告警閘_計劃]]"
  - "[[Systems/test-quality-cli]]"
  - "[[Issues/收證歸因第三輪留下的小問題]]"
lands_in:
  - Systems/test-quality-cli
  - Systems/pitfalls-lint-adapter
  - Systems/test-guard
  - Systems/pitfalls-code-loop
  - Systems/test-quality-multilang
---
# Android測試防竄改檢查_計劃

> 白話:讓 AI 寫測試時,最常見的壞事有兩種:一是它為了讓測試過,去改測試、跳過測試、改建置設定;二是它寫出永遠綠的測試(沒有斷言、例外被吞掉)。這份計劃做一支「比對改動前後」的工具,在推送前把這些寫法列成候選擋下來,誤報用既有的放行指令附理由放過、AI 放的要人看過;同時照論文全文研讀的結論改寫測試品質標準,處理上一輪延後的六條小問題,再到考場 mOrangePos 實跑壞例子、拿它的真實歷史量誤報。

## 問題與最小解

立案(2026-11-02,Enzo 原話依序):「上網印證一下，我們的測試驗證覆蓋完全了嗎」→「先以Android為強化主軸」→「論文看全文，我們避免掉人家已經做過的實驗、吸收結論，再照建議看怎麼調整」→「不用等CI，直接開計劃、規劃實作，然後開始作業，給你最高裁量權＆簽核權，有問題就上網搜別人印證過的解法，把功能優化做好做滿」。

研讀:六組代理讀了約四十篇論文與官方文件的全文(預期答案問題、AI 作弊、變異測試實務、測試壞味道、不穩測試與屬性測試、2026 下半年新研究),另派一個沒看過結論的代理只拿原始問題核對標準缺口。報告去掉本機路徑後放在 `governance/eval/results/ai-test-verification-research-20261102/`。這份計劃只吸收它們已經量過的結論,不重做;它們沒量過、我們真的需要的,列在〈第二批〉。

吸收的結論(出處都在研讀報告):
- AI 看得到實作時,會把錯的行為寫成預期值:把錯寫成預期的測試是抓到錯的 3.5–6.5 倍(Python,145 個 PR),給有錯的程式時被誤導的測試多約 8 倍(Java,11 個模型);把實作從眼前拿掉、只給意圖描述才明顯有用;在提示裡警告「程式可能有錯」沒有改變結果(這點只在 gpt-4o-mini 上測過);一直修到變綠會把強斷言改弱。
- AI 會為了讓測試過而作弊:測試可寫時直接改測試最常見;設成唯讀擋得住改測試,擋不住寫死測試輸入、查表、只做測試碰得到的路徑;LLM 當作弊偵測器最好約 63%,語意型幾乎抓不到;可靠的做法是「寬規則篩候選 → 人裁」,誤報要有正式出口。Google 的 Android Bench 2.0 在 Android 上看到改截圖容差、註解掉 `@Test`、DAO 回傳寫死資料。
- 測試壞味道多數不值得擋:寫死數字、一堆沒附說明的斷言在人寫測試也近 100%,偵測工具約四成誤報;真正會「永遠綠」的是沒有斷言、try/catch 裡斷言但 try 沒寫 `fail()`。detekt、Konsist、Android Lint、Sonar 都沒有現成規則抓這兩種(Android Lint 只有 `IgnoreWithoutReason`)。
- 不穩測試:重跑 10 次只找到約四分之一;打亂順序比原順序重跑有效;重試後才過要算不穩。
- 變異測試:只變異改到的行、存活的變異當審查意見、不設分數門檻(Google);Meta 在 Android Kotlin 上的 TestGen-LLM 與 ACH 是最貼近的工業證據。

現況(2026-11-02,分支起點 047031883):
- 推送前沒有任何一道看「測試被刪、斷言變弱、預期值被改、跳過標記、建置或 CI 的測試設定、截圖基準圖」。新增告警閘挑檔時排除路徑含 `test/`、`tests/` 這類樣式的檔(`_stack_changed_ok` 的測試檔樣式,所以 `src/test/` 被排除,`src/androidTest/` 不被排除),它只跑專案宣告的檢查工具、專案沒宣告時直接回「沒設定」——它問的是「工具有沒有多報告警」,不看測試本身被怎麼改。
- 新增告警閘的三個出口(設定 off、設定 warn、`LUMOS_SKIP_LINT_NEW`)都不寫治理帳;warn 模式下新增的告警一條都不印,放行小結照樣寫「沒有新增的告警」;判定函式丟出的任何例外,在代碼審檢查那一層被接住後一律自動放行(fail-open);放行檔讀不了時整道自動放行。
- `lumos lint-waive` 只檢查理由不是空的,放行人記的是 `$USER`,分不出是人還是 AI 在沒有互動終端時放的。
- Kotlin 靜態掃描只有 `assertEquals(x, x)` 一條,Truth 的 `assertThat(x).isEqualTo(x)` 不認。
- 標準沒寫:寫測試的 AI 能不能看實作、新測試在現有程式上紅了怎麼辦、新測試重跑與打亂順序、裝置上的隔離、畫面重建與程序被回收後的狀態;範本測試只提到「在裝置變體會紅、收證時用類別篩選避開」,沒寫要刪掉或換成真測試;「重試到過才綠不算」有寫,但沒寫怎麼讓機器擋;變異測試那句的事實過時(PIT 的協程雜訊回報 2022 年已結案)。

最小解:
- 在主程式加一支比對工具 `lumos test-guard`(跟 Room 守衛 `lumos room-guard` 同一層、同一種寫法),只讀一段 git 範圍兩端的檔案內容,吐出作弊候選;不跑測試、不改任何檔。測試函式辨識、剝字串與註解、括號配對、批次讀檔、git 呼叫全部重用主程式既有的函式(不另寫一套),既有函式缺的寫法就擴充它並補測試。它的家新開 `Systems/test-guard`。
- 它的候選併進新增告警閘的「新增告警」清單,放行沿用 `lumos lint-waive <指紋> --note`;不新增閘、不新增放行檔。專案沒宣告檢查工具時,作弊比對照樣判。
- 補新增告警閘的幾個洞:比對出錯擋下、warn 要印、關閘要留帳、同一次推送把閘關掉不算數、AI 放的放行要人看過(照搬 Android 端到端驗收的做法)。
- Semgrep 的自比規則補 Truth 兩條。
- 標準照研讀結論改寫;上一輪延後的六條一起處理。
- 考場實跑壞例子,並拿考場真實歷史量誤報。

PRIOR-ART: 「寬規則篩候選、再由人或 LLM 去掉誤報」借 FrogNano 的兩段式作弊偵測;規則清單持續補新招借 Verification Horizon;擋下後附理由放行借本專案的新增告警閘與 `lint-waive`;AI 放的放行要人看過借本專案 Android 端到端驗收的「AI 放的標記、健檢一直列到人看過」;在主程式讀 git 兩端、判 Android 檔借 Room 守衛(`_rg_*`)與它重用的 `_strip_c_comments`、`_rg_methods`、`_rg_is_test_path`,批次讀檔借 `_nodehome_cat_blobs_capped`;不宣稱擋得住特判與查表,照 ImpossibleBench「唯讀擋不住特判」的結論。外面沒有現成工具比對 Kotlin 測試的改動前後(研讀報告查過 detekt、Konsist、Android Lint、Sonar)。裁定:閘、放行、讀檔與辨識全部借用,只有規則本身自建。
RETIRE-IF: 人工抽查放行檔(`lumos lint-waive --list`,每筆記著規則代號、理由與放行的是人還是 AI)時,某條 `tq/` 規則三個月內的放行理由多數是「規則判錯」(不是「合理改動」),就收窄或拿掉那條;全部規則都這樣就撤掉整支比對工具 [retire:人裁] [until:2027-05-02]

## 名詞

- **作弊候選**:比對工具認為「可能是為了讓測試過而做的改動」的一處。只是候選,不是定罪;改掉或附理由放行都算處理完。
- **改動前、改動後**:git 範圍的起點版本與終點版本,兩邊的檔案內容都直接從 git 讀原始位元組(不經轉換程式、不看 `.gitattributes` 的 diff 設定),不讀工作目錄、不用 git diff 的輸出判內容。
- **測試檔、正式程式檔、建置檔、CI 檔、截圖基準圖**:比對工具依路徑分的五類檔,定義在做法第一節。
- **測試函式**:測試檔裡標了測試註記的函式,定義在做法第一節。**函式鍵**是「類別路徑加函式名」(巢狀類別用 `外層.內層.名稱`),同一支檔裡用它對改動前後。
- **斷言字、強斷言、弱斷言、預期值的位置**:算「這支測試有沒有在檢查結果、檢查得多嚴」用的呼叫名單,定義在做法第一節。
- **次數差**:同一條規則在改動後命中的次數減去改動前命中的次數;只有多出來的才算新增候選(跟新增告警閘「算次數不算有無」同一個做法)。
- **新增告警閘、放行**:推送前判「這次改動有沒有帶進新的告警」的那道閘;放行是 `lumos lint-waive <指紋> --note "<理由>"`,寫進要提交的 `.lumos/lint-waivers.json`。
- **AI 放的放行**:沒有互動終端時執行 `lint-waive` 寫下的放行,紀錄標成 AI 放的,直到人用互動終端確認看過。
- **考場**:mOrangePos 的本機演練工作樹與分支 `drill/android-unit-test-standard`,不推不併。
- **收證工具、配套**:收證工具是 `lumos test-quality` 這組子指令;配套是 `scripts/test_quality*.py` 這幾支檔,主程式先比對每支的 sha256(配套指紋表 `_TEST_QUALITY_BUNDLE_DIGESTS`)再載入,對不上整組拒跑。這次只改到其中的 `test_quality_semgrep.py`。
- **裝置那路、斷言歸因**:收證工具讀測試報告時判「這個失敗是不是斷言失敗」的規則叫斷言歸因;裝置那路是讀 Android 儀器測試報告(沒有例外型別欄、只能看失敗文字)的那一支判斷。
- **安全證據閘**:推送前判「登記過的資安護欄有沒有合格證據」的閘,它的故障敏感度那條路會用斷言歸因核對故障收據。

## 做法

### 一、比對工具 `lumos test-guard`

**用法與退出碼**:`lumos test-guard --diff <起點>..<終點> [--repo <根>] [--json]`,範圍只收兩個點的寫法;退出碼照 Room 守衛:沒有候選 0、有候選 1;不是 git 專案時回 0 並印一句「不是 git 專案,沒比」;參數錯(三個點、單一版本)或任一端解不出來回 2——起點例外接受空樹(新分支第一次推、找不到主線時推送掛鉤會這樣給),見下面〈空樹起點〉。新增告警閘呼叫它時直接傳已經算好的兩端,不再解析範圍字串。

**讀法**(全部借既有函式):
- 改了哪些檔:自己用 `_lens_git` 跑 `git diff --name-status -z -M --no-ext-diff --no-textconv <起點> <終點>`,含刪除(新增告警閘的 `_lint_new_changed_files` 刻意不收刪除,它的說明寫過「另開一支只給這道閘用的查詢」)。只取檔名清單,內容不從 diff 讀。
- 檔案內容:兩端都用 `_nodehome_cat_blobs_capped` 批次讀原始位元組(先問大小再讀內容,每端兩個 git 行程,不是逐檔開行程;不經轉換程式),帶單檔上限與截止時間;不存在的那一端(新增檔沒有改動前、刪除檔沒有改動後)當空檔,不算讀不出來。路徑含換行時批次讀取整批判不了,所以先把含換行的路徑挑出來各列一條 `tq/unreadable`,其餘照批次讀。
- 剝字串與註解:`_strip_c_comments(..., blank_strings=True, keep_newlines=True)`(全庫唯一那支,經 Room 守衛的 `_rg_strip`),行號不變。
- 測試函式:`_rg_methods(text, java, kinds=<測試註記>)` 加 `_rg_annotations`、`_rg_balanced`、`_rg_method_end`。測試註記:`Test`、`ParameterizedTest`、`RepeatedTest`、`TestFactory`、`TestTemplate`、`Theory`(`_rg_annotations` 取短名,`org.junit.Test`、`kotlin.test.Test` 都算)。既有函式要擴充的三處(擴充時補 Room 守衛那邊的回歸測試):運算式本體 `fun x() = runTest { … }` 的 `=` 後面接大括號時一路配到對應的右大括號(現在只到那一行行尾);每個註記行都對整份檔切片(`text[k:]`)是 O(註記行數×檔案大小),改成帶起始位置的比對、不切片(實測 2 MB、5 萬個註記行的檔要 20.5 秒);函式名改從**原文**同一行取——剝字串會把反引號整段清空(`` fun `adds two (numbers)`() `` 剝完變成 `` fun ``() ``),從剝過的文字取不到名字。函式鍵用類別路徑加名稱:沿著剝過的原文追蹤 `class`/`object`/`interface` 宣告的大括號深度。
- 路徑分類:測試路徑用 `_rg_is_test_path`(有一段 `src/<名稱>/`,名稱是 `test`、以 `test` 或 `androidTest` 開頭,或以 `Test` 結尾,所以 `commonTest`、`jvmTest`、`androidUnitTest`、`screenshotTest` 都算);檔名以 `Test`/`Tests` 結尾但不在 `src/main` 底下的也算。改動前與改動後兩個路徑任一邊是測試檔就當測試檔(改名成 `.disabled`、搬進 `src/main` 都看得到)。

**五類檔**:
- 測試檔:上面那條規則認出的 `.kt`/`.java`,或改名前是測試檔的任何檔。
- 正式程式檔:其他 `.kt`/`.java`,但不含 `buildSrc/`、`build-logic/` 底下。
- 建置檔:任何位置的 `*.gradle`、`*.gradle.kts`、`gradle.properties`、`robolectric.properties`,以及 `buildSrc/`、`build-logic/` 底下的 `.kt`/`.kts`。
- CI 檔:`.github/workflows/` 底下的 `.yml`/`.yaml`、`.github/actions/*/action.yml`/`action.yaml`、`.gitlab-ci.yml`、`bitrise.yml`、`Jenkinsfile`、`azure-pipelines.yml`、`.circleci/config.yml`、`codemagic.yaml`。
- 截圖基準圖:`.png`/`.webp`/`.jpg`/`.jpeg`,路徑在測試目錄裡,或含 `screenshots`、`snapshots`、`roborazzi`、`paparazzi` 這幾個目錄名(不分大小寫);路徑在 `docs/`、`fastlane/`、`metadata/` 底下、含 `phoneScreenshots`、`tabletScreenshots`(文件與商店截圖)、或在測試目錄的 `assets/`、`resources/` 底下(測試輸入圖)的不算。只看 git 物件編號,不讀圖檔內容。

**斷言字**(在剝過字串與註解的本體上比對,區分大小寫,後面要接 `(`、`{` 或 `<`):`assert` 接大寫開頭的名字(含 `assertThat`、`assertThrows`、`assertFailsWith`、Compose 的 `.assertIsDisplayed()`)、`fail`、`expectThat`、`expect.that`、`verify` 開頭(MockK/Mockito)、`coVerify` 開頭、`confirmVerified`、Turbine 的 `awaitItem`/`awaitError`/`awaitComplete`/`awaitEvent`/`expectNoEvents`/`expectMostRecentItem`/`cancelAndConsumeRemainingEvents`、Espresso 的 `.check(`、截圖比對的 `captureRoboImage`/`compareRoboImage`/`.snapshot`;另認 Kotest 的 `should` 開頭中綴,要求前後是字界而且後面不是 `=`(`shouldRefresh = true` 不算)。`@Test(expected = …)` 也算這支測試有檢查。
- 一個斷言敘述 = 從斷言字到它對應的右括號,再接上後面連著的 `.名稱(…)` 鏈(Truth 的 `assertThat(a).isEqualTo(b)` 是一個敘述);可以跨好幾行。
- 強斷言:敘述裡有 `assertEquals`、`assertArrayEquals`、`assertContentEquals`、`assertSame`、`isEqualTo`、`isSameInstanceAs`、`containsExactly` 開頭、`shouldBe`。其他都不是強斷言。
- 預期值的位置(依呼叫名與參數個數,參數用 `_rg_split_args` 切):
  - `assertEquals`/`assertNotEquals`/`assertArrayEquals`/`assertContentEquals`/`assertSame`:兩個參數 → 第一個;三個參數而第一個是字串常值 → 第一個是訊息、第二個是預期值;三個參數而第一個不是字串、第三個是數字 → 第一個是預期值、第三個是容差(容差改大也算預期值被改);四個參數 → 第二個是預期值、第四個是容差;具名參數 `expected =` 直接取。
  - `isEqualTo(…)`、`isSameInstanceAs(…)`、`containsExactly…(…)`:括號裡全部。
  - `shouldBe`:右邊。
  - Hamcrest 的 `assertThat(實際, 比對器)`:第二個參數。
  - 方向互換:`assertTrue`↔`assertFalse`、`assertNull`↔`assertNotNull` 參數不變只換名字,也算預期值被改。

**規則**(規則代號一律 `tq/` 開頭):

| 代號 | 什麼時候成立 | 例 |
|---|---|---|
| `tq/skip-added` | 測試檔裡 `@Ignore`、`@Disabled`、`@SdkSuppress`、`@FlakyTest`、`@Config(sdk`、`Assume.assume…(`、`assumeTrue(`/`assumeFalse(`/`assumeNotNull(`/`assumeThat(`、`Assumptions.assume…(` 的命中次數差大於 0;或改動前就有的測試函式新加了 `expected =` | 給一支紅的測試加 `@Ignore` |
| `tq/test-removed` | 改動前的測試函式(函式鍵)在改動後找不到,而且這次改動的所有測試檔裡沒有一支本體相同的函式(本體 = 宣告那一行之後的剝過字串註解、壓掉空白的文字;相同就算改名或搬家,不列);測試檔改名成非測試檔或被刪,裡面的函式一樣算;同一支檔的刪除合成一條,列出被刪的函式名,指紋綁那一組函式鍵 | 刪掉一支紅的測試;本體一字不改只改名不列 |
| `tq/assert-weakened` | 改動前後都有的同一個函式鍵(或本體相同對上的改名),斷言敘述變少,或強斷言變少 | `assertEquals(3, n)` 改成 `assertTrue(n > 0)` |
| `tq/expected-changed` | 改動前後都有的同一個函式鍵,把兩邊的斷言敘述清單按順序對齊(短清單逐項比,一支函式最多比 2000 個敘述),被替換的那幾對裡,除了預期值的位置之外全部相同、預期值的位置不同(含方向互換) | `assertEquals(88, total)` 改成 `assertEquals(90, total)`;跨行的斷言、`State.Loading` 改 `State.Error`、`assertTrue` 改 `assertFalse` 都算;只改 `total(listOf(40, 48))` 的參數不列;只改訊息字串不列 |
| `tq/no-assertion` | 新增的測試函式,或本體(上面那個定義)有變的測試函式,一個斷言字都沒有 | 只呼叫 `vm.load()` 不檢查任何結果 |
| `tq/catch-no-fail` | 新增或本體有變的測試函式裡有 `try { … } catch (…) { … }`,catch 區塊有斷言字或是空的,而 try 區塊沒有 `fail(`、`assertThrows`、`assertFailsWith`;catch 區塊裡有 `fail(`(預期不丟例外的寫法)不列;另外 `runCatching { … }` 區塊裡有斷言字、而後面沒有接 `.getOrThrow()` 也列(斷言失敗被包進結果、測試照樣綠) | 不丟例外時測試照樣綠 |
| `tq/build-config` | 建置檔裡下面這些的命中次數差大於 0(三種寫法都認:Kotlin 的 `x = v`、Groovy 的 `x v`、Provider 的 `x.set(v)`):`ignoreFailures` 設成 true、`excludeTestsMatching`、`exclude` 的字串含 `Test`、`failOnNoMatchingTests`/`isFailOnNoMatchingTests`/`failOnNoDiscoveredTests` 設成 false、`returnDefaultValues`/`isReturnDefaultValues` 設成 true、`failOnPassedAfterRetry` 設成 false、`notAnnotation`/`notClass`/`notPackage`、所在區塊的開頭(最近的左大括號那一行)有 `Test` 字樣而且有 `enabled` 設成 false 或 `onlyIf { false }`、`sourceSets` 裡 `test` 區塊的設定;重試外掛 `org.gradle.test-retry` 或 `maxRetries` 的命中次數差大於 0,但改動後的任何建置檔(用 `git grep` 查一次)都沒有 `failOnPassedAfterRetry` 設成 true;改動前有、改動後沒了的 `dependsOn(test` / `dependsOn("test` / `check.dependsOn` | `tasks.withType<Test> { ignoreFailures = true }`;`detekt { ignoreFailures = true }` 不在 `Test` 區塊、照樣列(要人看) |
| `tq/ci-config` | CI 檔裡呼叫 Gradle(同一行有 `gradlew` 或 `gradle ` 指令)的行:`-x`/`--exclude-task` 接含 `test` 或 `check` 的任務名、行尾 `\|\| true` 的命中次數差大於 0;同一個步驟(同縮排的 `-` 開頭到下一個)裡有 Gradle 呼叫而且 `continue-on-error: true`、`allow_failure: true` 或 `if: false` 的次數差大於 0;改動前呼叫 Gradle 測試或 check 任務的行,改動後沒有同樣的行 | `./gradlew build -x test`;`pytest -x tests/`、`mkdir -p a \|\| true` 不列 |
| `tq/timeout-raised` | 同一個函式鍵或同一個建置區塊裡,改動前與改動後各有一行逾時字樣(`timeout`、`Timeout`、`withTimeout(`,不分大小寫),兩行把數字換成佔位後一樣,而改動後的最大數字比較大 | `@Test(timeout = 30)` 改成 `45` |
| `tq/snapshot-changed` | 截圖基準圖有新增、修改或刪除(同一個目錄合成一條,指紋綁那批檔的路徑與 git 物件編號);或測試檔、建置檔裡 `changeThreshold`、`maxDistance`、`ImageComparator`、`roborazzi.test.record` 的命中次數差大於 0 | 功能改動跟重錄的基準圖放在同一批 |
| `tq/test-env-sniff` | 正式程式檔裡 `"robolectric"`(不分大小寫)、`isRunningTest`、`isRobolectric`、`Class.forName("org.junit`、`Class.forName("androidx.test`、`Class.forName("org.robolectric` 的命中次數差大於 0(`Build.FINGERPRINT` 單獨出現不算,模擬器偵測常用) | 程式偵測到在測試裡就走另一條路 |
| `tq/gate-config` | `.lumos/config.json` 裡 `lint_new.gate` 改動前與改動後的值不同,而改動後是 `warn` 或 `off` | 同一批改動把閘關掉 |
| `tq/too-large` | 測試檔或建置檔任一端超過比對工具自己的單檔上限(5 MB 或 10 萬行;不借新增告警閘那兩個給慢工具調小的設定);指紋綁路徑,同一支檔放行一次就好。改動前那端太大(例如把巨檔拆小或刪掉)也列,因為不讀改動前就比不出刪了哪些測試 | 不靜默略過 |
| `tq/unparsable` | 剝完字串與註解後大括號配不平(某端的深度沒有回到 0),那支檔的函式級規則判不了;指紋綁路徑與 git 物件編號 | 不靜默略過 |

- 次數差的身分:測試檔用(規則代號、函式鍵、正規化後的那一行),跨這次改動的全部測試檔一起算(測試搬到另一支檔,舊的註記不會在新檔被當成新增);建置檔與 CI 檔用(規則代號、檔案、所在區塊或步驟的開頭、正規化後的那一行);正規化是壓掉空白與行尾差異。整檔重新縮排、換行尾、函式搬位置都不會讓舊命中變成新增。
- 每條候選帶:規則代號、檔案、改動後的行號(刪除類用改動前行號並標明)、一句為什麼、該確認什麼、指紋。指紋 = sha256(規則代號、檔案、身分、這是第幾個相同身分)前 16 碼;`tq/expected-changed` 的身分是含常值的改動後原文。同一個身分第二次出現,指紋不同,放行第一個不會順帶放掉第二個。
- 判讀只用剝字串、括號配對與逐行比對,跟輸入大小成正比;括號配對每支檔一趟(配不平就列 `tq/unparsable`,不重掃)。雛形實測(2026-11-02,會談暫存區):接近 6 萬行的測試檔、一次改 1,967 處預期值,0.60 秒比完。
- **空樹起點**:起點是空樹時,先試主線分岔點(`git merge-base <主線> <終點>`,主線用推送掛鉤既有的判法);找得到就用它當起點;找不到就照比對、全部只印不擋,並寫一筆治理帳(新增告警閘的閘名、`skipped`、原因「沒有基準可比」)。
- **抓不到的**,寫進工具說明與標準,不宣稱:實作裡寫死測試輸入、查表、只做測試碰得到的路徑、多做沒人要的別名;預期值先放進變數再斷言(`val expected = 88`);參數化測試刪掉資料列;JUnit 3 那種不標註記、靠 `test` 開頭命名的測試;Kotest 字串式測試與 Spek;本體有改的改名(會列成刪除加新增);逾時換單位(`5.seconds` 改 `5.minutes`)、整行新增的逾時(沒有改動前那一行可比;`30_000`、`30L` 這類數字寫法照樣抓得到)、CI 的 `timeout-minutes`;catch 裡只印出例外(`println(e)`)的吞法;Kotlin 巢狀的區塊註解(剝註解那支不認巢狀);把測試檔搬進 Gradle 不編譯的目錄但路徑仍像測試目錄(工具不讀 `sourceSets` 的實際範圍);版本目錄 `libs.versions.toml`(只放版本,不放測試設定);lint 與 detekt 的基準檔改動(那是靜態檢查的放行,不是測試);合併主線後推送時,範圍裡別人的改動也會算進來(見回頭條件);Python 等其他棧(見〈第二批〉)。
- **已知的誤報**,有放行出口、在考場量測(S22)時一併記:只靠專案自訂的斷言輔助(例如 `checkState(...)`、`ensureX(...)`、`intended(...)`)的測試會被列成 `tq/no-assertion`;這次不加宣告口,等考場量出這類誤報的實際比例再決定(多就在第二批加,照收證工具掃描既有的 `--check-helper` 寫法)。一次大重構產生上百條候選時沒有整批放行,出口是那一次把閘設成 warn(印出、留帳);這次不加批次放行,因為「測試被刪」與「基準圖」已經按檔案、按目錄合成一條,剩下會大量出現的只有預期值大批改動,那正是要人逐條看的。

### 二、併進新增告警閘

- 判定順序:算出兩端 → 從 git 讀兩端的 `.lumos/config.json` 的 `lint_new.gate`(不讀工作目錄)→ 決定這次的模式(改動後的值;但改動把它從 block 改成 warn 或 off 時,這一次照 block 判並列 `tq/gate-config`)→ 模式是 off 或設了 `LUMOS_SKIP_LINT_NEW` 時見下面〈關閘留帳〉→ **比對工具** → 有沒有宣告檢查工具 → 既有流程。比對候選轉成告警的形狀(`key`、`rule`、`file`、`line`、`message`,另加 `verify` 放「該確認什麼」),扣掉放行檔裡已有的,剩下的併進「新增告警」清單。沒宣告檢查工具、或這次沒有要掃的程式碼檔時,只要有作弊候選照樣判,沒有候選才回原本的狀態。
- 只有改動碰到五類檔或 `.lumos/config.json`(含刪除與改名,從自己那份檔名清單判)才跑比對;沒碰到就不跑,純 Python 這類專案改程式不受影響;CI 檔的規則只看呼叫 Gradle 的行與步驟,非 Gradle 專案改 CI 檔不會出候選。
- **比對出錯擋下**:比對工具在 `_lint_new_verdict` 裡自己包住例外,任何非預期例外都記成「沒跑完」裡的一種(`kind: guard`,跟既有的「時間預算沒跑到」同類),會擋;不會漏到外層 `_codeloop_lint_new_step` 的 fail-open。比對工具超過截止時間也一樣記成沒跑完、擋。不照新增告警閘「環境不可用就自動放行」的老路:Android 端到端驗收那道閘當初就否決過「照新增告警閘出錯就放行」,決定是判不清就擋(見 `lumos rejections` 的那一筆);既有閘的「時間預算沒跑到」「檔太大」也都是擋。出口是 `lint_new.gate` 設 warn(印出、留帳)或 off、或 `LUMOS_SKIP_LINT_NEW`(有候選時留帳),見下。
- 放行檔讀不了時,既有的檢查工具那半照舊自動放行並記帳;比對候選照判,放行視為空(這次推送帶進的候選數量有限,不會把舊放行整批復活成擋人)。兩端算不出來時照舊自動放行並記帳(連改了哪些檔都不確定)。
- **warn 要印**:設成 warn 時,新增告警(含比對候選)逐條印出來,小結寫「只報不擋,有 N 條」,不再寫「沒有新增的告警」;只有比對在跑、沒有檢查命令時,不印「跑了 0 條檢查命令」。有比對候選時寫一筆治理帳(閘名 `lint-new`、`warned`、候選條數)。
- **關閘留帳**:設定 off 或 `LUMOS_SKIP_LINT_NEW` 時,比對工具照樣在背後跑一次(只讀、不擋;它自己出錯也不擋),**有候選才**寫一筆治理帳(閘名 `lint-new`,種類照倉庫慣例:設定 off 寫 `skipped`、環境變數寫 `skipped-env`,原因寫這次被跳過的候選條數);沒有候選不寫,常駐關閘的 Android 專案正常推送不會每次多一行。健檢的新增告警閘段落把最近 30 天的這三種帳(`skipped`、`skipped-env`、`warned`)數出來。
- **同一次推送把閘關掉不算數**:這次改動把 `lint_new.gate` 改成 warn 或 off(`tq/gate-config`),這一次照 block 判,`tq/gate-config` 本身也要放行才過。
- **AI 放的放行要人看過**(照搬 Android 端到端驗收 `_e2e_waive_cmd` 的判法,套在全部新增告警閘的放行):`lint-waive` 的理由至少 10 個字而且有實字;放行時用既有的 `_confirm_tty` 在終端問一句「這筆放行是你本人確認的嗎?[y/N]」,有人答 y 才記 `by: human`,沒有互動終端、讀不到回答或答 n 都記 `by: ai`(只看是不是終端不夠,AI 在偽終端裡跑也是終端);`lumos lint-waive --list` 標出「AI 放的,還沒人看過」;`lumos lint-waive --ack --all` 只在互動終端上問一次確認後標成看過;健檢與推送前小結列出還沒人看過的 AI 放行(只提醒、不擋,跟端到端驗收一樣)。舊紀錄沒有 `by` 欄的當人放的。
- 擋下訊息:既有印法只印前 8 條、訊息截 70 字;`tq/` 候選改成最多印 50 條,每條印規則代號、檔案、完整原因、該確認什麼與放行指令(`--rule`、`--file` 填好),超過 50 條時最後一行寫「另有 N 條,全部列出:`lumos test-guard --diff <範圍> --json`」。`--json` 的擋下明細照帶 `verify`。
- 比對工具不進 `pitfalls` 的風險分級,不改任何既有判定的結果。
- `Systems/pitfalls-lint-adapter` 那條「lumos 只解 SARIF、不內建棧規則」的 KEY 補一句例外:新增告警閘另有一個內建來源(比對工具,規則在 `Systems/test-guard`),並給那篇補上負責範圍。
- 代碼審檢查每次推送都跑新增告警閘(不看風險分級;推送前掛鉤帶 `--keep-going`,其他道擋下也會跑到這一道);取不到範圍的少數情況(取不到 HEAD、分岔點等於 HEAD)在這道之前就放行,照舊。CI 也跑同一道,判的是被推的樹。

### 三、Semgrep 自比規則

- Kotlin 與 Java 的自比規則各加 `assertThat($X).isEqualTo($X)`、`Truth.assertThat($X).isEqualTo($X)`、`assertWithMessage(...).that($X).isEqualTo($X)` 與 Hamcrest 的 `assertThat($X, equalTo($X))`、`assertThat($X, is($X))`(2026-11-02 用 Semgrep 1.183.0 實測前一條:抓得到 `assertThat(x).isEqualTo(x)` 與 `assertThat(y.size).isEqualTo(y.size)`,正常的 `assertThat(f()).isEqualTo(3)` 不報)。`$X` 是有副作用的呼叫(`next()` 對 `next()`)會誤報,候選本來就要人裁。改了 `test_quality_semgrep.py` 要重算配套指紋表裡它那一格。
- CI 與這台機器的預設環境都沒有 Semgrep,現有掃描測試用假的 Semgrep 執行檔(只驗介面,不判樣式);這兩條規則的真實效果靠考場實跑留證(S17)。

### 四、標準改寫(`skills/lumos-project-notes/commands/test-quality-standard.md`)

- 〈開發時〉加「讓 AI 寫測試」一段:先開一個看不到實作本體的乾淨代理,只給需求、方法簽名與公開介面,產出「輸入→預期」答案表並提交,之後才讓 AI 讀實作、寫測試程式;新測試在現有程式上紅了,先對照需求來源判斷是程式錯還是測試錯,不准把預期值改成程式目前的輸出;AI 發現需求或測試互相矛盾時,停下回報給人,不自己挑一邊;用 AI 審預期值時不給它實作本體。附研讀出處,並寫明「警告語沒用」只在 gpt-4o-mini 上測過、「不給實作」的效果在 Kotlin 上還沒人量過(見〈第二批〉)。
- 新增〈推送前的防竄改檢查〉一節:比對工具抓什麼、抓不到什麼(做法一那份清單)、怎麼放行(理由寫「為什麼這個改動是需求要的」)、AI 放的要人看過、放行檔要提交。
- 〈審查時〉加審查題:預期值從哪來;有沒有明知漏了需求還照交;有沒有多出沒人要的別名或退路;截圖基準圖有變要看新舊比較圖;mock 與假資料的形狀要照真實上游輸出。
- 〈Android 本機單元測試的驗收標準〉:
  - 不算過的證據裡既有的「重試到過才綠」補上怎麼讓機器擋:本機用 test-retry 外掛時設 `failOnPassedAfterRetry`(Kotlin DSL 寫 `failOnPassedAfterRetry.set(true)`)為 true,它預設是 false,等於把不穩吞掉;裝置那路這個外掛管不到,重試後才過要寫進報告。
  - 既有「專案把零選中失敗關掉時要數 XML」那句旁邊補:關掉它的改動推送前會被列成作弊候選,要附理由放行。既有「`isReturnDefaultValues` 真的開了,設定旁邊寫理由」改成:設定旁邊寫理由,推送時另外在放行理由寫同一件事。
  - 新增「穩定與隔離」:新測試在 PR 跑原順序 1 次、反轉 1 次、打亂順序約 20 次都要綠(JUnit 4.13 起的 `Ordering.shuffledBy`,印出種子才能重放),而且寫明這只抓得到常壞的(重跑 10 次只找到約四分之一的不穩測試);裝置測試在 PR 跑 3–5 次;Robolectric 每支測試給新的 Application,但 App 自己的單例與靜態快取不會重設,這類最該打亂順序跑,不過 `RobolectricTestRunner` 吃不吃 `@OrderWith` 還沒人驗過(見〈第二批〉),先做最小實驗再用;裝置測試開 Orchestrator 加 `clearPackageData`(每支測試跑完清掉 App 資料,代價是每支都重啟 App)。
  - 加「畫面重建與程序被回收」:用 `ViewModelScenario.recreate()`(lifecycle-viewmodel-testing 2.9.0 起)模擬程序被回收再還原,斷言 SavedStateHandle 存的狀態還在。
  - 範本測試:既有那句只講「在裝置變體會紅、收證時用類別篩選避開」,補上專案建立時附的 `ExampleUnitTest`、`ExampleInstrumentedTest` 刪掉或換成真測試,不算進任何證據。
  - 故障證明那條改寫變異測試:只變異這次改到的類別、每行只送一個存活變異、先排除日誌、時間、設定旗標與產生的程式碼(Hilt、`R`、`BuildConfig`、`ComposableSingletons`),存活變異當審查意見逐條處置、不設分數門檻;每個目標模組都要真的產生新報告而且變異數大於 0,不然判沒跑(實例:有專案「只提醒」的排程因原本的測試沒全綠,13 個套用的模組只有 4 個開跑、3 個有結果,工作狀態卻顯示成功);協程雜訊那句改成事實:免費 PIT 沒有官方的協程過濾,PIT 維護者 2022 年以「改用 arcmutate 的 Kotlin 外掛」結案(付費,開源專案免費),arcmutate 的 Android 外掛仍是 beta、不支援裝置測試;`pl.droidsonroids.pitest` 是社群維護、自稱實驗性的 Gradle 外掛,跟 arcmutate 的 Android 外掛是兩回事。
  - 屬性測試(選配):金額拆帳、四捨五入、格式化與解析來回這類純函式可以加 Kotest 的屬性測試(`kotest-property` 可單獨用在 JUnit4 本機測試);屬性只收需求明寫的;審查時查輸入範圍有沒有被 `assume` 或篩選把會觸發錯的輸入排掉、用「把輸出故意改到違反屬性」做故障證明;jqwik 1.10 起附反 AI 使用條款並在每次執行時往輸出印字,不採用。
  - 「機器抓不到」那條:把「規則只有 `assertEquals(x, x)`,Truth 寫法的自比不在內」改成新的規則範圍;補寫死測試輸入、查表、只做測試碰得到的路徑只能靠 AI 看不到的組合或往返測試與審查;明列不採用的壞味道(寫死數字、一堆沒附說明的斷言、Eager Test、Lazy Test、Dependent Test)與理由;測試數量、斷言數量、涵蓋率都不當品質分數。
  - 〈裝置那一路收得到哪些失敗〉那條照實補一句:失敗訊息本身同時含像堆疊的一行與 `Caused by:` 時會被判成不是斷言(往拒收的方向錯),遇到時改訊息或在本機那路收(見做法五第二條)。
  - 改寫時保住兩支既有測試釘的字串:`t_test_quality_standard_android_drill_lessons` 與 `t_test_quality_drill_cli_cases_present`。
  - 來源清單補研讀報告與新引用的官方頁。

### 五、上一輪延後的六條

六條是 [[Issues/收證歸因第三輪留下的小問題]] 的症狀 1–6(收證工具「認得 Truth 與裝置字串比較」那次代碼審跑滿三輪時延後的 minor)。

- 第一條:只補測試、不改判定,在 `scripts/test_test_quality_cli.py` 各加一支放寬就紅的測試:堆疊行的縮排、第一行去空白、Assert 片語前的字界、`fail|assert` 的限定、「第一行訊息自己含 `at org.junit.Assert.fail(` 又接一般堆疊時從第一個堆疊行起算」。
- 第二條:**不改判定**,改成照實記錄的已知取捨。r1 設計審實測,原本想的「改看報告尾端連續的堆疊區塊」會把現有一筆合法案例(訊息自帶 `Caused by:` 緊貼真實堆疊)判錯,也認不得真機輸出的 `... 27 trimmed` 截斷行;訊息裡的堆疊樣字串與真正的 `Caused by:` 在文字上分不出來,往拒收的方向錯是比較安全的那一邊。Issue 那條改寫成這個結論,標準補那一句(見做法四)。
- 第三條:安全證據閘補一支「裝置文字(沒有型別欄)的字串比較故障收據算抓到錯」的測試,測試輔助加一種沒有型別欄的失敗狀態。
- 第四到六條:錯字、舊註解、說明檔的層數與 WHY 用詞、三處承認句補回頭條件。順手清掉那篇 Issue 開頭空的重複標題。
- 這次不改 `scripts/test_quality.py`,掛在它身上的三條回頭條件(2026-11-08 到期)不受這份計劃觸發,照它們原本的時程處理;收證工具的家 `Systems/test-quality-cli` 那條順手確認一次還成立。

### 六、考場實跑與誤報量測

- 考場本機分支上,每條規則各做一個壞改動提交(例如給測試加 `@Ignore`、刪一支測試、把強斷言改弱、改預期值(單行與跨行各一)、加沒斷言的測試、加 try/catch 沒 `fail()`、build 檔加 `ignoreFailures = true`(Kotlin 與 Groovy 各一)、加一個 CI 檔 `-x test`、調大逾時、重錄一張基準圖、正式程式碼偵測 robolectric、把閘設成 off),逐一跑比對工具,記哪條抓到;再做幾個正常改動當對照(新增有斷言的測試、本體不變只改測試名、把測試原樣搬到另一支檔、整檔重新縮排、改正式程式碼),不應出候選。
- 拿考場 develop 的真實歷史(唯讀,不動 develop),對有改到測試、建置或 CI 檔的非合併提交逐一跑比對工具(合併提交跟第一個父提交比會把另一條分支的改動算進來,不算);每條候選人工裁成三類:作弊樣的改動、合理改動(例如把幾支測試重寫成整張表逐項比對)、規則判錯;規則判錯的比例寫進驗證紀錄,判錯多的規則當輪收窄。雛形先跑過一次(192 個非合併提交、38 條候選,其中「測試被刪」27 條、大多是合理的測試重寫)。公開卷證裡考場的檔名與測試名換代稱。
- Semgrep 在考場的測試目錄實跑一次自比規則(上一輪沒裝,沒跑到);跑過就把上一份計劃那行「Kotlin 靜態掃描這次沒跑」的回頭條件標成已結案。
- 卷證照上一輪的做法:公開 repo 只放去識別化摘要(`governance/eval/results/android-test-guard-drill-20261102/`(新增)),完整卷證留在考場本機分支。

## 第二批(另開計劃,這批推上去之後接著做)

- 變異測試收證:從改動算出要變異的類別、驗每個模組的 `mutations.xml` 是新的而且變異數大於 0、存活變異列成審查清單;在考場實跑免費 PIT 量協程雜訊比例,再決定要不要建議 arcmutate。
- 穩定性收證:同一個收證命令跑原順序、反轉、打亂順序各一次,全綠才算;先做最小實驗確認 `RobolectricTestRunner` 吃不吃 `@OrderWith`。
- 第二個考場:找一個有 SavedStateHandle 或資料層的類別,實跑 `ViewModelScenario.recreate()`。
- 在 Kotlin 上實測「答案表先行、不給實作」能擋掉多少把錯寫成預期的測試(論文全是 Java 或 Python)。
- 上一份計劃留下的回頭條件(Gradle 把包裝例外記成內層型別、裝置那路打錯類名誰擋、App 啟動的網路流量、收據重收、其他棧重跑)。

REVISIT:2026-12-15 第二批計劃開了沒有;沒開就把上面五項逐項開成計劃或 Issue
REVISIT:2026-12-15 比對工具只認 Kotlin 與 Java;Python(pytest 的 skip、unittest 的 skip)與 Swift、C# 的同類規則還沒有,第二批評估要不要加
REVISIT:2026-12-15 合併主線之後推送,範圍裡別人的改動也會被比對工具算成這次的候選;在考場或工具鏈實際碰到一次,記下誤報量,決定要不要改用分岔點起算
REVISIT:2026-12-15 Semgrep 的兩條 Truth 自比規則只在考場實跑過;CI 或預設環境裝了 Semgrep 時補一支真跑的測試

## 驗收條款

- [S1] 當改動在測試檔新增 `@Ignore`、`@Disabled`、`@SdkSuppress`、`@FlakyTest`、`@Config(sdk`、`Assume.assumeTrue(` 或給既有測試函式加上 `expected =` 時,比對工具應各列一條 `tq/skip-added` 候選;整行是註解的、新寫的測試帶 `expected =`、整檔重新縮排後舊的 `@Ignore` 都不列。 [test:t_tq_guard_skip_added]
- [S2] 當改動前的測試函式在改動後不見、整支測試檔被刪或被改名成非測試檔時,應列 `tq/test-removed`(同一支檔合成一條、列出被刪的函式名);本體一字不改只改名、原樣搬到另一支測試檔時不列;巢狀類別裡同名的兩支只刪一支時要列。 [test:t_tq_guard_test_removed]
- [S3] 當同一函式的斷言敘述變少、或強斷言變少(例如 `assertEquals(3, n)` 改成 `assertTrue(n > 0)`)時,應列 `tq/assert-weakened`;斷言數不變、只改被測呼叫的參數時不列。 [test:t_tq_guard_assert_weakened]
- [S4] 當同一函式裡一個斷言的預期值被改(單行、跨行、`assertEquals("訊息", 88, total)` 的 88、容差 `0.01` 改 `0.1`、`State.Loading` 改 `State.Error`、`assertTrue` 改 `assertFalse`、連續好幾個斷言一起改)時,應列 `tq/expected-changed`;只改被測呼叫的參數(`total(listOf(40, 48))` 改成 `total(listOf(48, 40))`)、只改訊息字串、改被測呼叫名時不列。 [test:t_tq_guard_expected_changed]
- [S5] 當新增或本體有變的測試函式沒有任何斷言字時,應列 `tq/no-assertion`;用 Truth、Turbine、MockK `verify`、Espresso `.check(`、Kotest `shouldBe`、`captureRoboImage`、`@Test(expected = …)`、運算式本體 `= runTest { … }` 裡有斷言、反引號函式名的測試不列;本體沒變的舊測試不列。 [test:t_tq_guard_no_assertion]
- [S6] 當 try 區塊沒有 `fail(`/`assertThrows`/`assertFailsWith` 而 catch 區塊有斷言字或是空的、或 `runCatching { … }` 裡有斷言而後面沒接 `.getOrThrow()` 時,應列 `tq/catch-no-fail`;catch 裡有 `fail(`、try 結尾有 `fail(`、`runCatching { … }.getOrThrow()` 時不列。 [test:t_tq_guard_catch_no_fail]
- [S7] 當建置檔新增 `ignoreFailures = true`、Groovy 的 `ignoreFailures true`、`failOnPassedAfterRetry.set(false)`、`excludeTestsMatching`、`isFailOnNoMatchingTests = false`、`isReturnDefaultValues = true`、`Test` 區塊裡跨行的 `enabled = false`、拿掉 `check.dependsOn(test)`、或開重試外掛卻沒有任何建置檔設 `failOnPassedAfterRetry` 為 true 時,應列 `tq/build-config`;照標準開重試(`.set(true)` 或 `= true`)、依賴宣告的 `exclude(group = …)`、JaCoCo 的 `exclude("**/R.class")` 不列。 [test:t_tq_guard_build_config]
- [S8] 當 CI 檔有這幾種改動時,比對工具應列 `tq/ci-config`:呼叫 Gradle 的行新增 `-x test` 或行尾 `|| true`、含 Gradle 呼叫的步驟加 `continue-on-error: true`、刪掉呼叫 Gradle 測試任務的行;`pytest -x tests/`、`mkdir -p a || true`、不含 Gradle 呼叫的步驟加 `continue-on-error: true` 不列。 [test:t_tq_guard_ci_config]
- [S9] 當逾時數字被調大、截圖基準圖有變或比對門檻字樣新增時,應列 `tq/timeout-raised` 或 `tq/snapshot-changed`(同一目錄的基準圖合成一條);逾時被調小、文件目錄與商店截圖目錄(路徑以 docs、fastlane 開頭)底下的圖不列。 [test:t_tq_guard_timeout_and_snapshot]
- [S10] 當正式程式檔新增 `"robolectric"` 或 `Class.forName("org.junit…")` 時,應列 `tq/test-env-sniff`;同樣的字出現在測試檔、正式程式只用 `Build.FINGERPRINT` 時不列。 [test:t_tq_guard_test_env_sniff]
- [S11] 當執行 `lumos test-guard --diff` 時,沒有候選應回 0、有候選回 1、不是 git 專案回 0 並說明、範圍是三個點或任一端解不出來回 2(起點是空樹不算解不出來);`--json` 每條候選有規則代號、檔案、行號、原因、該確認什麼、指紋;上下文位移與整檔重新縮排後指紋不變;同一支檔加兩個相同的 `@Ignore` 得到兩個不同指紋;檔案加 `-diff` 的 `.gitattributes` 照樣抓得到;超過單檔上限列 `tq/too-large`、括號配不平列 `tq/unparsable`、路徑含換行列 `tq/unreadable` 而其他檔照比;接近 6 萬行、改約兩千處的測試檔,2 MB、5 萬個非測試註記行的檔,與一次改 300 支檔,都應在 30 秒內比完。 [test:t_tq_guard_cli_contract]
- [S12] 當推送的改動有作弊候選時,新增告警閘應把它們算進新增告警並擋下(設定是 block 時),即使專案沒宣告任何檢查工具;`lumos lint-waive <指紋> --note` 放行後同一條不再擋;改動沒碰到五類檔時不跑比對;`tq/` 候選最多印 50 條、超過時印列出全部的指令。 [test:t_lint_new_includes_test_guard]
- [S13] 當比對工具丟出非預期例外或超過截止時間時,新增告警閘應記成沒跑完並擋下(不走 fail-open);放行檔讀不了時比對候選照判;起點是空樹而找不到主線分岔點時只印不擋並寫一筆 `skipped` 帳。 [test:t_lint_new_test_guard_failure_blocks]
- [S14] 當閘的設定是 warn、off、`LUMOS_SKIP_LINT_NEW`,或這次改動把 `lint_new.gate` 改掉時,新增告警閘應這樣處理:warn 逐條印出新增告警、小結寫「只報不擋」,有比對候選時寫一筆 `warned` 帳;off 或環境變數跳過時比對照樣在背後跑,有候選才各寫一筆 `skipped`/`skipped-env` 治理帳、沒候選不寫;這次改動把它改成 warn 或 off(從 git 讀兩端的設定比)時這次照 block 判並列 `tq/gate-config`,只改這支設定檔也會觸發。 [test:t_lint_new_warn_off_and_gate_config]
- [S15] 當執行 `lint-waive` 而終端沒有人答 y(沒有互動終端、讀不到回答或答 n)時,紀錄應標成 AI 放的,有人答 y 才標人放的;理由少於 10 個字或沒有實字應被拒;`lint-waive --list` 與健檢應列出還沒人看過的 AI 放行;`lint-waive --ack --all` 在沒有互動終端時應拒絕、在互動終端確認後標成看過;沒有 `by` 欄的舊紀錄當人放的。 [test:t_lint_waive_ai_marking]
- [S16] 當找測試函式時,運算式本體 `fun x() = runTest { … }` 應配到對應的右大括號、反引號函式名(含空白與括號)應從原文取得完整名稱、2 MB 有 5 萬個註記行的檔應在 5 秒內切完,而 Room 守衛既有的方法擷取行為不變。 [test:t_rg_methods_expression_body_and_backtick]
- [S17] 當在考場用 Semgrep 1.183.0 對含 `assertThat(x).isEqualTo(x)` 與 `assertWithMessage("m").that(x).isEqualTo(x)` 的測試檔跑 `lumos test-quality scan --semgrep` 時,兩條都應列成候選、`assertThat(f()).isEqualTo(3)` 不列,結果記在驗證紀錄。 [manual:看驗證紀錄的 Semgrep 實跑輸出]
- [S18] 當讀測試品質標準時,應寫到:答案表先行而且寫的人看不到實作、現有程式上紅了不准改預期值、矛盾時停下回報、推送前的防竄改檢查與它抓不到的、AI 放的放行要人看過、重試後才過不算(`failOnPassedAfterRetry`)、原順序反轉與打亂順序與次數、Orchestrator 與 `clearPackageData`、`ViewModelScenario.recreate()`、範本測試、變異測試只變異改到的類別與每模組要有新報告、arcmutate 的事實、屬性測試的審法與不採用 jqwik、不採用的壞味道,而且連到研讀報告與這份計劃。 [test:t_test_quality_standard_ai_test_guard]
- [S19] 當收證工具裝置那路判定的縮排、第一行去空白、字界、`fail|assert` 限定或「從第一個堆疊行起算」任一條被放寬時,收證工具的測試應翻紅。 [test:t_test_quality_cli]
- [S20] 當安全證據閘的故障敏感度那條路核對沒有型別欄的裝置字串比較故障收據時,應算抓到錯。 [test:t_secev_tq_device_text_fault_counts_like_assertion]
- [S21] 當在考場對每條規則的壞改動跑比對工具時,每條都應被對應規則抓到;正常改動的對照組不應出候選;結果記在驗證紀錄。 [manual:看驗證紀錄的考場對照表與公開卷證]
- [S22] 當拿考場 develop 的真實歷史跑比對工具時,每條候選應有人工裁定(作弊樣、合理改動、規則判錯)與規則判錯率,判錯多的規則有收窄紀錄。 [manual:看驗證紀錄的誤報量測表]

## 回退

- 工具鏈:還原這份計劃、比對工具與它的測試、新增告警閘那幾段、`lint-waive` 的 AI 標記、`_rg_methods` 的擴充、Semgrep 規則與配套指紋表、標準改寫、六條小修、驗證紀錄與卷證的提交(同一個提交,一起還原)。還原後推送前不再看作弊候選;已寫進放行檔的 `tq/` 放行留著無害(指紋不再出現),`by` 欄被舊版忽略。
- 只想關掉作弊比對、不還原程式:專案在 `.lumos/config.json` 把 `lint_new.gate` 設成 `warn`(只報不擋)或 `off`(連原本的新增告警一起關,碰到五類檔時留帳);單次推送用 `LUMOS_SKIP_LINT_NEW=1`(碰到五類檔時留帳)。同一次推送改這個設定那一次不算數。
- 考場:演練提交只在本機分支;刪分支前先打包 `drill-evidence/`。

## 實務隱患

- 守衛面:新增告警閘多了一個來源,原本「沒宣告檢查工具就不判」的 Android 專案,只要改到 Kotlin 或 Java 測試、建置檔、呼叫 Gradle 的 CI 行就可能被擋;誤報的出口是放行附理由(AI 放的要人看過),整道關掉是設定 off 或環境變數(這次補上留帳);比對工具自己出錯時擋下而不是放行,壞的是推送體驗、不是靜默漏判。消費專案要等 `lumos update` 才拿到。
- 守衛面:warn 模式改成會印、放行檔讀不了時比對候選照判、同一次推送把閘關掉不算數——這三處讓既有新增告警閘比現在嚴,原本靠 warn 靜默或壞放行檔放過去的告警會開始被看到。
- 效能:比對工具一個 git 行程批次讀改到的檔、剝字串與配對各一趟,跟改動大小成正比;S11 釘住大檔與 300 支檔各 30 秒內。新增告警閘原本有 300 秒預算,比對工具算在同一個預算裡,超過就記成沒跑完、擋。
- 資安:比對工具讀的是 AI 可控的檔案內容;病態輸入(極深的括號巢狀、沒收尾的字串、大量換行)只會讓那支檔列成 `tq/unparsable` 或 `tq/too-large`,不會讓判讀變成二次方或丟例外放行(S11、S13)。
- 併發:放行檔寫入沿用既有的上鎖;治理帳沿用既有的追加寫法,沒有新的共用寫入點。
- 已排除:金流:不碰付款;考場只在本機分支改測試與建置檔,不跑 App。
- 已排除:對外送出:比對工具只讀 git,不連網;研讀報告是公開論文的摘要,去掉本機路徑才放進公開 repo。
- 已排除:不可逆:考場提交不推不併;工具鏈改動走一般提交,可還原。

## 審計修正紀錄

- r1(2026-11-02,三席加架構對齊,全 sonnet 同門):58 條/blocking 35/設計的方向對,但比對工具該放在主程式重用既有的辨識與讀檔函式(不是收證工具配套)、判法要改成兩端整檔的次數差(不靠 git diff 的新增行)、指紋要綁函式與第幾次出現、比對出錯與 warn 與關閘三個出口都要補、AI 放的放行要有人看;裝置歸因「尾端堆疊區塊」的改法被實測推翻,改成照實記錄的取捨。全部折入。卷證 `governance/review-reports/Android測試防竄改檢查/`。
  - 例:測試檔整檔重新縮排(舊有一個 `@Ignore`)→ 改前:那行出現在 diff 新增側、列成 `tq/skip-added`;改後:兩端各一次、次數差 0、不列。
  - 例:`FooTest.kt` 改名成 `FooTest.kt.disabled` → 改前:改動後路徑不是 `.kt`、整支略過;改後:改名前是測試檔、裡面的函式全列 `tq/test-removed`。
  - 新增機制(不加它的最小解為什麼不夠):`lint-waive` 的 AI 標記——不加的話,推送者(AI)照抄擋下訊息裡的放行指令就能放行自己的作弊,沒有任何人看,整道比對被架空;判法照 Android 端到端驗收 `_e2e_waive_cmd`(在終端真的問一句、有人答 y 才算人放的),紀錄欄位與 `--list`/`--ack` 照它的形狀,套到另一本放行檔。`tq/gate-config`——不加的話,同一次推送把 `lint_new.gate` 改成 off 就整道關掉、只留一筆帳。
  - 一支綁定測試涵蓋好幾種行為(S7、S12 等)不拆:每種行為在那支測試裡各有一條會單獨翻紅的檢查,實作時逐條改壞一次確認各自會紅;拆成十幾支只是把同一個建置輔助複製很多份。
  - 折入後派鏡像核對(sonnet):漏折 13、鏡像段沒跟上 4、新洞 5(反引號名被剝掉、`_rg_methods` 切片成本、批次讀檔遇換行、AI 判法寫錯、退出碼寫錯),全部再折入。
