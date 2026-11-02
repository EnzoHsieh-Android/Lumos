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
  - Systems/test-quality-scan
  - Systems/pitfalls-lint-adapter
---
# Android測試防竄改檢查_計劃

> 白話:讓 AI 寫測試時,最常見的壞事有兩種:一是它為了讓測試過,去改測試、跳過測試、改建置設定;二是它寫出永遠綠的測試(沒有斷言、例外被吞掉)。這份計劃做一支「比對改動前後」的工具,在推送前把這些寫法列成候選擋下來,誤報用既有的放行指令附理由放過;同時照論文全文研讀的結論改寫測試品質標準,修掉上一輪延後的六條小問題,再到考場 mOrangePos 實跑壞例子、拿它的真實歷史量誤報。

## 問題與最小解

立案(2026-11-02,Enzo 原話依序):「上網印證一下，我們的測試驗證覆蓋完全了嗎」→「先以Android為強化主軸」→「論文看全文，我們避免掉人家已經做過的實驗、吸收結論，再照建議看怎麼調整」→「不用等CI，直接開計劃、規劃實作，然後開始作業，給你最高裁量權＆簽核權，有問題就上網搜別人印證過的解法，把功能優化做好做滿」。

研讀:六組代理讀了約四十篇論文與官方文件的全文(預期答案問題、AI 作弊、變異測試實務、測試壞味道、不穩測試與屬性測試、2026 下半年新研究),另派一個沒看過結論的代理只拿原始問題核對標準缺口。報告去掉本機路徑後放在 `governance/eval/results/ai-test-verification-research-20261102/`(新增)。這份計劃只吸收它們已經量過的結論,不重做;它們沒量過、我們真的需要的,列在〈第二批〉。

吸收的結論(出處都在研讀報告):
- AI 看得到實作時,會把錯的行為寫成預期值:把錯寫成預期的測試是抓到錯的 3.5–6.5 倍(Python,145 個 PR),給有錯的程式時被誤導的測試多約 8 倍(Java,11 個模型);提醒它「程式可能有錯」沒用,把實作從眼前拿掉才有用;一直修到變綠會把強斷言改弱。
- AI 會為了讓測試過而作弊:測試可寫時直接改測試最常見;設成唯讀擋得住改測試,擋不住寫死測試輸入、查表、只做測試碰得到的路徑;LLM 當作弊偵測器最好約 63%,語意型幾乎抓不到;可靠的做法是「寬規則篩候選 → 人裁」,誤報要有正式出口。Google 的 Android Bench 2.0 在 Android 上看到改截圖容差、註解掉 `@Test`、DAO 回傳寫死資料。
- 測試壞味道多數不值得擋:寫死數字、一堆沒附說明的斷言在人寫測試也近 100%,偵測工具約四成誤報;真正會「永遠綠」的是沒有斷言、try/catch 裡斷言但 try 沒寫 `fail()`。detekt、Konsist、Android Lint、Sonar 都沒有現成規則抓這兩種(Android Lint 只有 `IgnoreWithoutReason`)。
- 不穩測試:重跑 10 次只找到約四分之一;打亂順序比原順序重跑有效;重試後才過要算不穩。
- 變異測試:只變異改到的行、存活的變異當審查意見、不設分數門檻(Google);Meta 在 Android Kotlin 上的 TestGen-LLM 與 ACH 是最貼近的工業證據。

現況(2026-11-02,分支起點 047031883):
- 推送前沒有任何一道看「測試被刪、斷言變弱、預期值被改、跳過標記、建置或 CI 的測試設定、截圖基準圖」。新增告警閘挑檔時排除路徑含 `test/`、`tests/` 這類樣式的檔(`_stack_changed_ok` 的測試檔樣式,所以 `src/test/` 被排除,`src/androidTest/` 不被排除),而且它只跑專案宣告的檢查工具、專案沒宣告時直接回「沒設定」——它問的是「工具有沒有多報告警」,不看測試本身被怎麼改。
- 關掉新增告警閘的三個出口(設定 off、設定 warn、`LUMOS_SKIP_LINT_NEW`)現在都不寫治理帳;只有「環境不可用、自動放行」會記。
- Kotlin 靜態掃描只有 `assertEquals(x, x)` 一條,Truth 的 `assertThat(x).isEqualTo(x)` 不認。
- 標準沒寫:寫測試的 AI 能不能看實作、新測試在現有程式上紅了怎麼辦、新測試重跑與打亂順序、裝置上的隔離、畫面重建與程序被回收後的狀態;範本測試只提到「在裝置變體會紅、收證時用類別篩選避開」,沒寫要刪掉或換成真測試;「重試到過才綠不算」有寫,但沒寫怎麼讓機器擋;變異測試那句的事實過時(PIT 的協程雜訊回報 2022 年已結案)。

最小解:
- 收證工具配套加第四支檔 `scripts/test_quality_guard.py`(新增):一支純 Python 的比對工具,只看一段 git 範圍的改動前後,吐出作弊候選;不跑測試、不改任何檔。它的家是 `Systems/test-quality-cli`(收證工具的家,實作時把這支檔加進那篇的 about_code)。
- 它的候選併進新增告警閘的「新增告警」清單,放行沿用 `lumos lint-waive <指紋> --note`、留痕與統計照舊;不新增閘、不新增放行檔。專案沒宣告檢查工具時,作弊比對照樣判。
- Semgrep 的自比規則補 Truth 一條。
- 標準照研讀結論改寫;上一輪延後的六條一起修。
- 考場實跑壞例子,並拿考場真實歷史量誤報。

PRIOR-ART: 「寬規則篩候選、再由人或 LLM 去掉誤報」借 FrogNano 的兩段式作弊偵測;規則清單持續補新招借 Verification Horizon;擋下後附理由放行借本專案的新增告警閘與 `lint-waive`(誤報第一天就要有出口);不宣稱擋得住特判與查表,照 ImpossibleBench「唯讀擋不住特判」的結論。沒有現成工具比對 Kotlin 測試的改動前後(研讀報告查過 detekt、Konsist、Android Lint、Sonar),所以規則自建,判讀只用逐行比對與括號配對,不做通用解析器。裁定:閘與放行借用,規則自建。
RETIRE-IF: 人工抽查放行檔(`lumos lint-waive --list`,每筆記著規則代號與理由)時,某條 `tq/` 規則三個月內的放行理由多數是「規則判錯」(不是「合理改動」),就收窄或拿掉那條;全部規則都這樣就撤掉整支比對工具 [retire:人裁] [until:2027-05-02]

## 名詞

- **作弊候選**:比對工具認為「可能是為了讓測試過而做的改動」的一處。只是候選,不是定罪;改掉或附理由放行都算處理完。
- **改動前、改動後**:git 範圍的起點版本與終點版本,兩邊都從 git 讀,不讀工作目錄。
- **測試檔、正式程式檔、建置檔、CI 檔、截圖基準圖**:比對工具依路徑分的五類檔,定義在做法第一節。
- **測試函式**:測試檔裡標了 `@Test`(含 `@org.junit.Test`、`@ParameterizedTest`、`@RepeatedTest`)的函式;Kotlin 認 `fun 名稱(`,Java 認 `void 名稱(`;用括號配對找函式本體,略過字串與註解裡的括號。
- **斷言字**:算「這支測試有沒有在檢查結果」用的呼叫名單,定義在做法第一節。**強斷言**是比對相等的那幾個,**弱斷言**是只查「不是空、不相等、型別對」的那幾個。
- **新增告警閘、放行**:推送前判「這次改動有沒有帶進新的告警」的那道閘;放行是 `lumos lint-waive <指紋> --note "<理由>"`,寫進要提交的 `.lumos/lint-waivers.json`。
- **考場**:mOrangePos 的本機演練工作樹與分支 `drill/android-unit-test-standard`,不推不併。
- **收證工具、配套**:收證工具是 `lumos test-quality` 這組子指令;配套是 `scripts/test_quality*.py` 這幾支檔,主程式先比對每支的 sha256(配套指紋表 `_TEST_QUALITY_BUNDLE_DIGESTS`)再載入,對不上整組拒跑。
- **裝置那路、斷言歸因**:收證工具讀測試報告時判「這個失敗是不是斷言失敗」的規則叫斷言歸因;裝置那路是讀 Android 儀器測試報告(沒有例外型別欄、只能看失敗文字)的那一支判斷。
- **安全證據閘**:推送前判「登記過的資安護欄有沒有合格證據」的閘,它的故障敏感度那條路會用斷言歸因核對故障收據。

## 做法

### 一、比對工具 `lumos test-quality guard`

- 用法:`lumos test-quality guard --diff <起點>..<終點> [--repo <根>] [--json]`,範圍只收兩個點的寫法(`A..B`);三個點或單一版本回 2。退出碼:沒有候選 0、有候選 1、讀不了(不是 git、任一端不是提交)2。新增告警閘呼叫它時直接傳已經算好的兩端提交,不再解析範圍字串。
- 檔案分類(路徑一律用改動後的;改名用 git 的改名偵測對回改動前):
  - 測試檔:`.kt`/`.java`,路徑含 `src/test`、`src/androidTest`、`src/sharedTest`、`src/testFixtures` 或 `src/test<變體>` 這類目錄,或檔名以 `Test`/`Tests` 結尾。
  - 正式程式檔:其他 `.kt`/`.java`,但不含 `buildSrc/`、`build-logic/` 底下。
  - 建置檔:`build.gradle`、`build.gradle.kts`、`gradle.properties`、`robolectric.properties`,以及 `buildSrc/`、`build-logic/` 底下的 `.kt`/`.kts`/`.gradle`(慣例外掛常在這裡設測試)。
  - CI 檔:`.github/workflows/` 底下的 yml、`.gitlab-ci.yml`、`bitrise.yml`、`Jenkinsfile`、`azure-pipelines.yml`、`.circleci/config.yml`、`codemagic.yaml`。
  - 截圖基準圖:`.png`/`.webp`/`.jpg`,路徑在測試目錄裡,或含 `screenshots`、`snapshots`、`roborazzi`、`paparazzi` 這幾個目錄名。
- 只看新增行的規則,略過整行是註解的(去掉前導空白後以 `//`、`/*`、`*`、`#` 開頭)。
- 斷言字(區分大小寫,後面要接 `(`、`{` 或 `<`):`assert` 接大寫開頭的名字(含 `assertThat`、`assertThrows`、`assertFailsWith`、Compose 的 `.assertIsDisplayed()`)、`fail`、`expectThat`、`expect.that`、`verify` 開頭(MockK/Mockito)、`coVerify` 開頭、`confirmVerified`、Turbine 的 `awaitItem`/`awaitError`/`awaitComplete`/`awaitEvent`/`expectNoEvents`/`expectMostRecentItem`/`cancelAndConsumeRemainingEvents`、Espresso 的 `.check(`;另認 Kotest 的 `should` 開頭中綴(如 `x shouldBe y`)。`@Test(expected = …)` 也算這支測試有檢查。
  - 強斷言:`assertEquals`、`assertArrayEquals`、`assertContentEquals`、`assertSame`、`isEqualTo`、`isSameInstanceAs`、`containsExactly` 開頭、`shouldBe`。
  - 弱斷言:`assertNotNull`、`isNotNull`、`assertNotEquals`、`isNotEqualTo`、`isNotEmpty`、`isInstanceOf`、`shouldNotBeNull`、`assertTrue(true)`、`assertFalse(false)`。
  - 強、弱斷言各自獨立計數,不併進斷言字的總數(Truth 的 `assertThat(x).isEqualTo(y)` 算一個斷言字、一個強斷言)。
  - 預期值的位置:`assertEquals`、`assertArrayEquals`、`assertContentEquals`、`assertSame` 的第一個參數,`isEqualTo(…)`、`isSameInstanceAs(…)`、`containsExactly…(…)` 括號裡的全部參數,`shouldBe` 的右邊。
- 規則(規則代號一律 `tq/` 開頭,方便按規則統計放行):

| 代號 | 什麼時候成立 | 例 |
|---|---|---|
| `tq/skip-added` | 測試檔新增行出現 `@Ignore`、`@Disabled`、`@SdkSuppress`、`@FlakyTest`、`Assume.assume…(`、`assumeTrue(`/`assumeFalse(`/`assumeNotNull(`/`assumeThat(`、`Assumptions.assume…(`;或改動前就有的測試函式新加了 `expected =` | 給一支紅的測試加 `@Ignore` |
| `tq/test-removed` | 改動前某測試檔有的測試函式,改動後同一支檔(含改名後)沒有了,而且這次改動的其他測試檔裡也沒有同名函式(搬家不算);同一支檔的刪除合成一條,列出被刪的函式名,指紋綁那一組名字 | 刪掉一支紅的測試 |
| `tq/assert-weakened` | 改動前後都有的同名測試函式,斷言字變少;或強斷言變少而弱斷言變多 | `assertEquals(3, n)` 改成 `assertNotNull(n)` |
| `tq/expected-changed` | 改動前後都有的同名測試函式裡,同一個 diff 區塊一行刪掉、一行新增,兩行都有斷言字,把數字、字串、字元常值換成佔位後一樣,而且不同的常值落在預期值的位置 | `assertEquals(88, total)` 改成 `assertEquals(90, total)`;只改 `total(listOf(40, 48))` 的參數不列 |
| `tq/no-assertion` | 新增的測試函式,或本體有改的測試函式,本體裡一個斷言字都沒有 | 只呼叫 `vm.load()` 不檢查任何結果 |
| `tq/catch-no-fail` | 新增或本體有改的測試函式裡有 `try { … } catch (…) { … }`,catch 區塊有斷言字或是空的,而 try 區塊沒有 `fail(`、`assertThrows`、`assertFailsWith` | 不丟例外時測試照樣綠 |
| `tq/build-config` | 建置檔新增行出現 `ignoreFailures` 設成 true、`excludeTestsMatching`、`exclude(` 後面字串含 `Test` 或 `**`、`failOnNoMatchingTests`/`isFailOnNoMatchingTests`/`failOnNoDiscoveredTests` 設成 false、`returnDefaultValues`/`isReturnDefaultValues` 設成 true、`failOnPassedAfterRetry` 設成 false、新增 `maxRetries` 或重試外掛 `org.gradle.test-retry` 但改動後那支檔沒有 `failOnPassedAfterRetry = true`(照標準開重試就不列)、`notAnnotation`/`notClass`/`notPackage`、同一行有 `test`(不分大小寫)而且有 `enabled = false` 或 `onlyIf { false }` | `tasks.withType<Test> { ignoreFailures = true }` |
| `tq/ci-config` | CI 檔新增行出現 `continue-on-error: true`、`allow_failure: true`、`\|\| true`、`-x` 接含 `test` 或 `check` 的任務名、`--exclude-task` 接含 `test` 或 `check` 的任務名 | `./gradlew build -x test` |
| `tq/timeout-raised` | 測試檔或建置檔裡,一行刪掉、一行新增,兩行都有逾時字樣(`timeout`、`Timeout.`、`withTimeout(`、`timeoutMillis`),把數字換成佔位後一樣,而新行的最大數字比舊行大 | `@Test(timeout = 30)` 改成 `45` |
| `tq/snapshot-changed` | 截圖基準圖有新增、修改或刪除(同一個目錄合成一條,指紋綁那批檔的路徑與內容);或測試檔、建置檔、`gradle.properties` 新增行出現 `changeThreshold`、`maxDistance`、`ImageComparator`、`roborazzi.test.record` | 功能改動跟重錄的基準圖放在同一批 |
| `tq/test-env-sniff` | 正式程式檔新增行出現 `"robolectric"`(不分大小寫)、`Build.FINGERPRINT`、`isRunningTest`、`isRobolectric`、`Class.forName("org.junit`、`Class.forName("androidx.test`、`Class.forName("org.robolectric` | 程式偵測到在測試裡就走另一條路 |
| `tq/too-large` | 測試檔、正式程式檔或建置檔任一版本超過新增告警閘的單檔上限(行數或位元組),沒比 | 不靜默略過 |
| `tq/unreadable` | 上面幾類檔任一版本從 git 讀不出來 | 不靜默略過 |

- 每條候選帶:規則代號、檔案、改動後的行號(刪除類用改動前行號並標明)、一句為什麼、該確認什麼、身分字串、指紋。指紋 = sha256(規則代號、檔案、身分字串)前 16 碼;身分字串用「測試函式名」或「正規化後的那一行」,不用行號(行號會因上下文位移而變)。併進新增告警閘時轉成它既有的鍵:`key`(指紋)、`rule`、`file`、`line`、`message`。
- 判讀只用逐行比對與括號配對,跟輸入大小成正比。雛形實測(2026-11-02,會談暫存區):接近單檔上限的 59,003 行測試檔、一次改 1,967 處預期值,1.86 秒比完;超過上限的 20 萬行檔直接列 `tq/too-large`、0.24 秒。
- 抓不到的寫進工具說明與標準,不宣稱:實作裡寫死測試輸入、查表、只做測試碰得到的路徑、多做沒人要的別名;Kotest 字串式測試(`"名稱" { }`)與 Spek 這類不用 `@Test` 的寫法;Python 等其他棧(見〈第二批〉)。

### 二、併進新增告警閘

- 新增告警閘的判定在「閘關掉(設定 off 或 `LUMOS_SKIP_LINT_NEW`)」與「算出兩端提交」之後、「有沒有宣告檢查工具」之前,先跑比對工具;候選轉成告警的形狀,扣掉放行檔裡已有的,剩下的併進「新增告警」清單。沒宣告檢查工具、或這次沒有要掃的程式碼檔時,只要有作弊候選照樣判(擋或只報看設定),沒有候選才回原本的狀態。比對工具要的放行檔由閘提早讀一次,兩邊共用同一份。
- 只有這次改動碰到比對工具看的五類檔(Kotlin/Java、建置檔、CI 檔、截圖基準圖)才載入比對工具;沒碰到就不載入、不判,純 Python 這類專案不受影響。
- 兩端提交算不出來、放行檔讀不了時,維持新增告警閘既有的處理(環境不可用、自動放行並記帳):這時連改了哪些檔都不確定,也不能把舊放行全部當不存在、整批擋人。
- 閘被設定 off 或 `LUMOS_SKIP_LINT_NEW` 跳過時,補寫一筆治理帳(新增告警閘的閘名、「跳過」、原因);目前這兩個出口不留痕,而它們是作弊比對擋錯人時的出口。
- 改動碰到那五類檔、而比對工具載入失敗(配套指紋對不上、例外)時**擋下**,訊息寫明是作弊比對沒跑、出口是 `lint_new.gate` 設 warn(只報不擋)或 off、或 `LUMOS_SKIP_LINT_NEW`(off 與環境變數跳過會記帳,見下);某支檔從 git 讀不出來就對那支檔列一條 `tq/unreadable` 候選(不是 UTF-8 的位元組照換字元讀,不算讀不出來),同樣可放行。不照新增告警閘「環境不可用就自動放行」的老路:Android 端到端驗收那道閘當初就否決過「照新增告警閘出錯就放行」,決定是判不清就擋(見 `lumos rejections` 的那一筆);比對工具只讀 git、不靠外部工具,出錯多半是程式錯,放行等於靜默關掉。
- 測試函式一律讀兩個版本的整份檔、自己配對括號找,不靠 diff 的區塊標頭:風險分級曾試過用區塊標頭判斷測試函式,縮排在 class 裡的方法判不到,被否決(同一份清單)。
- 擋下訊息:既有印法只印前 8 條、訊息截 70 字;`tq/` 候選改成全印,每條印規則代號、檔案、完整原因、該確認什麼與放行指令(`--rule` 帶規則代號、`--file` 帶檔案)。其他來源的告警照舊。
- 比對工具不進 `pitfalls` 的風險分級,不改任何既有判定的結果。
- 加一支配套檔要同步五處,漏一處所有專案的 `test-quality` 都會回部署不完整:隨工具安裝進消費專案的檔案清單 `_VENDORED_TOOLKIT`、配套指紋表(新檔與改了的 `test_quality.py` 都重算)、載入順序 `_TEST_QUALITY_LOAD_ORDER`、pre-commit 與 post-commit 兩支掛鉤的工具檔豁免清單、指令說明表與文件裡的指令數。
- 代碼審檢查每次推送都跑新增告警閘(不看風險分級;推送前掛鉤帶 `--keep-going`,其他道擋下也會跑到這一道);取不到範圍的少數情況(取不到 HEAD、分岔點等於 HEAD)在這道之前就放行,照舊。

### 三、Semgrep 自比規則

- Kotlin 與 Java 的自比規則各加 `assertThat($X).isEqualTo($X)`(2026-11-02 用 Semgrep 1.183.0 實測:抓得到 `assertThat(x).isEqualTo(x)` 與 `assertThat(y.size).isEqualTo(y.size)`,正常的 `assertThat(f()).isEqualTo(3)` 不報)。

### 四、標準改寫(`skills/lumos-project-notes/commands/test-quality-standard.md`)

- 〈開發時〉加「讓 AI 寫測試」一段:先開一個看不到實作本體的乾淨代理,只給需求、方法簽名與公開介面,產出「輸入→預期」答案表並提交,之後才讓 AI 讀實作、寫測試程式;新測試在現有程式上紅了,先對照需求來源判斷是程式錯還是測試錯,不准把預期值改成程式目前的輸出;AI 發現需求或測試互相矛盾時,停下回報給人,不自己挑一邊;用 AI 審預期值時不給它實作本體。附研讀出處。
- 新增〈推送前的防竄改檢查〉一節:比對工具抓什麼、抓不到什麼、怎麼放行(放行理由要寫「為什麼這個改動是需求要的」)、放行檔要提交。
- 〈審查時〉加審查題:預期值從哪來;有沒有明知漏了需求還照交;有沒有多出沒人要的別名或退路;截圖基準圖有變要看新舊比較圖;mock 與假資料的形狀要照真實上游輸出。
- 〈Android 本機單元測試的驗收標準〉:
  - 不算過的證據裡既有的「重試到過才綠」補上怎麼讓機器擋:本機用 test-retry 外掛時設 `failOnPassedAfterRetry = true`(它預設是 false,等於把不穩吞掉);裝置那路這個外掛管不到,重試後才過要寫進報告。
  - 新增「穩定與隔離」:新測試跑原順序、反轉、打亂順序(JUnit 4.13 起的 `Ordering.shuffledBy`,印出種子才能重放)都要綠,而且寫明這只抓得到常壞的(重跑 10 次只找到約四分之一的不穩測試);Robolectric 每支測試給新的 Application,但 App 自己的單例與靜態快取不會重設,這類最該打亂順序跑;裝置測試開 Orchestrator 加 `clearPackageData`(每支測試跑完清掉 App 資料,代價是每支都重啟 App)。
  - 加「畫面重建與程序被回收」:用 `ViewModelScenario.recreate()`(lifecycle-viewmodel-testing 2.9.0 起)模擬程序被回收再還原,斷言 SavedStateHandle 存的狀態還在。
  - 範本測試:既有那句只講「在裝置變體會紅、收證時用類別篩選避開」,補上專案建立時附的 `ExampleUnitTest`、`ExampleInstrumentedTest` 刪掉或換成真測試,不算進任何證據。
  - 故障證明那條改寫變異測試:只變異這次改到的類別、每行只送一個存活變異、先排除日誌、時間、設定旗標與產生的程式碼(Hilt、`R`、`BuildConfig`、`ComposableSingletons`),存活變異當審查意見逐條處置、不設分數門檻;每個目標模組都要真的產生新報告而且變異數大於 0,不然判沒跑(實例:有專案「只提醒」的排程因原本的測試沒全綠,13 個模組只跑了 3 個,工作狀態卻顯示成功);協程雜訊那句改成事實:免費 PIT 沒有官方的協程過濾,PIT 維護者 2022 年以「改用 arcmutate 的 Kotlin 外掛」結案(付費,開源專案免費),arcmutate 的 Android 外掛仍是 beta、不支援裝置測試;`pl.droidsonroids.pitest` 是社群維護、自稱實驗性的 Gradle 外掛,跟 arcmutate 的 Android 外掛是兩回事。
  - 屬性測試(選配):金額拆帳、四捨五入、格式化與解析來回這類純函式可以加 Kotest 的屬性測試(`kotest-property` 可單獨用在 JUnit4 本機測試);屬性只收需求明寫的;審查時查輸入範圍有沒有被 `assume` 或篩選把會觸發錯的輸入排掉、用「把輸出故意改到違反屬性」做故障證明;jqwik 1.10 起附反 AI 使用條款並在每次執行時往輸出印字,不採用。
  - 「機器抓不到」那條補:寫死測試輸入、查表、只做測試碰得到的路徑,只能靠 AI 看不到的組合或往返測試與審查;明列不採用的壞味道(寫死數字、一堆沒附說明的斷言、Eager Test、Lazy Test、Dependent Test)與理由;測試數量、斷言數量、涵蓋率都不當品質分數。
  - 來源清單補研讀報告與新引用的官方頁。

### 五、上一輪延後的六條

六條是 [[Issues/收證歸因第三輪留下的小問題]] 的症狀 1–6(收證工具「認得 Truth 與裝置字串比較」那次代碼審跑滿三輪時延後的 minor)。

- 第一條:裝置那路判定補測試,釘住堆疊行的縮排、第一行去空白、Assert 片語前的字界、`fail|assert` 的限定,以及「第一行訊息自己含 `at org.junit.Assert.fail(` 又接一般堆疊時從第一個堆疊行起算」。
- 第二條:改判「真正的堆疊」為報告尾端連續的堆疊行區塊(每一行都是堆疊行、`Caused by:`、`... N more` 或 `Suppressed:`),Assert 堆疊要在這個區塊裡第一個 `Caused by:` 之前;訊息裡的堆疊樣字串與 `Caused by:` 不再讓合法的字串比較失敗被拒。由後往前一次掃完,跟輸入大小成正比。
- 第三條:安全證據閘補一支「裝置文字(沒有型別欄)的字串比較故障收據算抓到錯」的測試,測試輔助加一種沒有型別欄的失敗狀態。
- 第四到六條:錯字、舊註解、說明檔的層數與 WHY 用詞、三處承認句補回頭條件。順手清掉那篇 Issue 開頭空的重複標題。改歸因會讓舊收據重算不同,照上一輪的寫法提醒重收。

### 六、考場實跑與誤報量測

- 考場本機分支上,每條規則各做一個壞改動提交(例如給測試加 `@Ignore`、刪一支測試、把強斷言改弱、改預期值、加沒斷言的測試、加 try/catch 沒 `fail()`、build 檔加 `ignoreFailures = true`、加一個 CI 檔 `-x test`、調大逾時、正式程式碼偵測 robolectric),逐一跑比對工具,記哪條抓到;再做幾個正常改動當對照(新增有斷言的測試、改測試名、把測試搬到另一支檔、改正式程式碼),不應出候選。
- 拿考場 develop 的真實歷史(唯讀,不動 develop),對有改到測試、建置或 CI 檔的非合併提交逐一跑比對工具(合併提交跟第一個父提交比會把另一條分支的改動算進來,不算);每條候選人工裁成三類:作弊樣的改動、合理改動(例如把幾支測試重寫成整張表逐項比對)、規則判錯;規則判錯的比例寫進驗證紀錄,判錯多的規則當輪收窄。雛形先跑過一次(197 個提交、101 條候選,其中「測試被刪」85 條、大多是合理的測試重寫),同一支檔的刪除因此合成一條。公開卷證裡考場的檔名與測試名換代稱。
- Semgrep 在考場的測試目錄實跑一次自比規則(上一輪沒裝,沒跑到)。
- 卷證照上一輪的做法:公開 repo 只放去識別化摘要(`governance/eval/results/android-test-guard-drill-20261102/`(新增)),完整卷證留在考場本機分支。

## 第二批(另開計劃,這批推上去之後接著做)

- 變異測試收證:從改動算出要變異的類別、驗每個模組的 `mutations.xml` 是新的而且變異數大於 0、存活變異列成審查清單;在考場實跑免費 PIT 量協程雜訊比例,再決定要不要建議 arcmutate。
- 穩定性收證:同一個收證命令跑原順序、反轉、打亂順序各一次,全綠才算。
- 第二個考場:找一個有 SavedStateHandle 或資料層的類別,實跑 `ViewModelScenario.recreate()`。
- 在 Kotlin 上實測「答案表先行、不給實作」能擋掉多少把錯寫成預期的測試(論文全是 Java 或 Python)。
- 上一份計劃留下的回頭條件(Gradle 把包裝例外記成內層型別、裝置那路打錯類名誰擋、App 啟動的網路流量、收據重收、其他棧重跑)。

REVISIT:2026-12-15 第二批計劃開了沒有;沒開就把上面五項逐項開成計劃或 Issue
REVISIT:2026-12-15 比對工具只認 Kotlin 與 Java;Python(pytest 的 skip、unittest 的 skip)與 Swift、C# 的同類規則還沒有,第二批評估要不要加

## 驗收條款

- [S1] 當改動在測試檔新增 `@Ignore`、`@Disabled`、`@SdkSuppress`、`@FlakyTest`、`Assume.assumeTrue(` 或給既有測試函式加上 `expected =` 時,比對工具應各列一條 `tq/skip-added` 候選;整行是註解的不列。 [test:t_tq_guard_skip_added]
- [S2] 當改動前的測試函式在改動後不見、整支測試檔被刪時,應列 `tq/test-removed`(同一支檔合成一條、列出被刪的函式名);同名函式出現在這次改動的另一支測試檔(搬家)時不列。 [test:t_tq_guard_test_removed]
- [S3] 當同名測試函式的斷言字變少、或強斷言變少而弱斷言變多時,應列 `tq/assert-weakened`;斷言字數不變、只改了被測呼叫的參數時不列。 [test:t_tq_guard_assert_weakened]
- [S4] 當同名測試函式裡一行斷言只改了常值(例如 `assertEquals(88, total)` 改成 `assertEquals(90, total)`)時,應列 `tq/expected-changed`;改了變數名、或只改被測呼叫的參數常值(例如 `total(listOf(40, 48))` 改成 `total(listOf(48, 40))`)時不列。 [test:t_tq_guard_expected_changed]
- [S5] 當新增或改了本體的測試函式沒有任何斷言字、或 try 區塊沒有 `fail(`/`assertThrows`/`assertFailsWith` 而 catch 區塊有斷言字或是空的時,應分別列 `tq/no-assertion` 與 `tq/catch-no-fail`;用 Truth、Turbine、MockK `verify`、Espresso `.check(`、Kotest `shouldBe` 或 `@Test(expected = …)` 的測試不列 `tq/no-assertion`;本體沒動的舊測試不列。 [test:t_tq_guard_no_assertion_and_catch]
- [S6] 當建置檔新增 `ignoreFailures = true`、`excludeTestsMatching`、`isFailOnNoMatchingTests = false`、`isReturnDefaultValues = true`、`failOnPassedAfterRetry = false` 或 CI 檔新增 `continue-on-error: true`、`-x test` 時,應列 `tq/build-config` 或 `tq/ci-config`;依賴宣告裡的 `exclude group:` 不列。 [test:t_tq_guard_build_and_ci_config]
- [S7] 當逾時數字被調大、截圖基準圖有變或比對門檻字樣新增時,應列 `tq/timeout-raised` 或 `tq/snapshot-changed`(同一目錄的基準圖合成一條);逾時被調小不列。 [test:t_tq_guard_timeout_and_snapshot]
- [S8] 當正式程式檔新增 `"robolectric"`、`Build.FINGERPRINT` 或 `Class.forName("org.junit…")` 時,應列 `tq/test-env-sniff`;同樣的字出現在測試檔不列。 [test:t_tq_guard_test_env_sniff]
- [S9] 當推送的改動有作弊候選時,新增告警閘應把它們算進新增告警並擋下(設定是 block 時),即使專案沒宣告任何檢查工具;`lumos lint-waive <指紋> --note` 放行後同一條不再擋;設定 off 或設了 `LUMOS_SKIP_LINT_NEW` 時不判、並寫一筆治理帳;改動碰到 Kotlin/Java、建置、CI 或截圖檔而比對工具載入失敗時應擋下並印出關閉出口,沒碰到這些檔時不載入、不擋;`tq/` 候選超過 8 條時全部印出。 [test:t_lint_new_includes_test_guard]
- [S10] 當執行 `lumos test-quality guard --diff` 時,沒有候選應回 0、有候選回 1、範圍不是兩個版本回 2;`--json` 每條候選有規則代號、檔案、行號、原因、該確認什麼、指紋;同一處改動重跑指紋不變、上下文位移後指紋不變;超過單檔上限的檔應列 `tq/too-large` 而不是略過;接近單檔上限(5.9 萬行)、改了約兩千處的測試檔應在 10 秒內比完。 [test:t_tq_guard_cli_contract]
- [S11] 當 Kotlin 或 Java 的測試檔有 `assertThat(x).isEqualTo(x)` 時,Semgrep 自比規則應列成候選,`assertThat(f()).isEqualTo(3)` 不列。 [test:t_test_quality_scan_truth_self_compare]
- [S12] 當讀測試品質標準時,應寫到:答案表先行而且寫的人看不到實作、現有程式上紅了不准改預期值、矛盾時停下回報、推送前的防竄改檢查與它抓不到的、重試後才過不算(`failOnPassedAfterRetry`)、原順序反轉與打亂順序、Orchestrator 與 `clearPackageData`、`ViewModelScenario.recreate()`、範本測試、變異測試只變異改到的類別與每模組要有新報告、arcmutate 的事實、屬性測試的審法與不採用 jqwik、不採用的壞味道,而且連到研讀報告與這份計劃。 [test:t_test_quality_standard_ai_test_guard]
- [S13] 當裝置那路的失敗文字訊息裡同時有像堆疊的一行和 `Caused by:`、但尾端的堆疊區塊第一個 `Caused by:` 之前有 JUnit `Assert` 堆疊時,應判成斷言失敗;縮排、第一行去空白、字界、`fail|assert` 限定與「從第一個堆疊行起算」各有一支放寬就紅的測試;安全證據閘的故障敏感度那條路,沒有型別欄的裝置字串比較故障收據應算抓到錯。 [test:t_secev_tq_device_text_fault_counts_like_assertion]
- [S14] 當在考場對每條規則的壞改動跑比對工具時,每條都應被對應規則抓到;正常改動的對照組不應出候選;結果記在驗證紀錄。 [manual:看驗證紀錄的考場對照表與公開卷證]
- [S15] 當拿考場 develop 的真實歷史跑比對工具時,每條候選應有人工裁定(真或誤報)與誤報率,誤報多的規則有收窄紀錄。 [manual:看驗證紀錄的誤報量測表]

## 回退

- 工具鏈:還原這份計劃、比對工具與它的測試、新增告警閘那段、配套指紋表、Semgrep 規則、標準改寫、六條小修、驗證紀錄與卷證的提交(同一個提交,一起還原)。還原後推送前不再看作弊候選;已寫進放行檔的 `tq/` 放行留著無害(指紋不再出現)。
- 只想關掉作弊比對、不還原程式:專案在 `.lumos/config.json` 把 `lint_new.gate` 設成 `warn`(只報不擋)或 `off`(連原本的新增告警一起關,會記帳);單次推送用 `LUMOS_SKIP_LINT_NEW=1`(會記帳)。
- 考場:演練提交只在本機分支;刪分支前先打包 `drill-evidence/`。

## 實務隱患

- 守衛面:新增告警閘多了一個來源,原本「沒宣告檢查工具就不判」的專案,只要改到 Kotlin 或 Java 測試、建置檔、CI 檔就可能被擋;誤報的出口是放行附理由,整道關掉是設定 off 或環境變數(這次補上記帳);比對工具自己出錯時擋下而不是放行,壞的是推送體驗、不是靜默漏判。消費專案要等 `lumos update` 才拿到。
- 守衛面:裝置那路的斷言歸因改成看尾端的堆疊區塊,訊息裡有堆疊樣字串的合法失敗會從拒收變成接受(放行面變大);反例測試釘住尾端區塊裡沒有 Assert 堆疊、Caused by 包著、型別名後多字這幾種照樣拒收。
- 效能:比對工具只讀改到的檔、逐行比對,跟改動大小成正比;S10 釘住 20 萬行 10 秒內。新增告警閘原本有 300 秒預算,比對工具算在同一個預算裡。
- 已排除:金流:不碰付款;考場只在本機分支改測試與建置檔,不跑 App。
- 已排除:對外送出:比對工具只讀 git,不連網;研讀報告是公開論文的摘要,去掉本機路徑才放進公開 repo。
- 已排除:不可逆:考場提交不推不併;工具鏈改動走一般提交,可還原。

## 審計修正紀錄
