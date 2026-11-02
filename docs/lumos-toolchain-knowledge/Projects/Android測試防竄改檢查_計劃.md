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
  - Systems/room-guard
---
# Android測試防竄改檢查_計劃

> 白話:讓 AI 寫測試時,最常見的壞事有兩種:一是它為了讓測試過,去改測試、跳過測試、改建置設定(建置設定這一批不比,見〈第二批〉);二是它寫出永遠綠的測試(沒有斷言、例外被吞掉、實際值換成常數)。這份計劃做一支「比對改動前後」的工具,在推送前把這些寫法列成候選擋下來,誤報用既有的放行指令附理由放過、AI 放的事後要人看過;同時照論文全文研讀的結論改寫測試品質標準,處理上一輪延後的六條小問題,再到考場 mOrangePos 實跑壞例子、拿它的真實歷史量誤報。

## 問題與最小解

立案(2026-11-02,Enzo 原話依序):「上網印證一下，我們的測試驗證覆蓋完全了嗎」→「先以Android為強化主軸」→「論文看全文，我們避免掉人家已經做過的實驗、吸收結論，再照建議看怎麼調整」→「不用等CI，直接開計劃、規劃實作，然後開始作業，給你最高裁量權＆簽核權，有問題就上網搜別人印證過的解法，把功能優化做好做滿」。

研讀:六組代理讀了約四十篇論文與官方文件的全文(預期答案問題、AI 作弊、變異測試實務、測試壞味道、不穩測試與屬性測試、2026 下半年新研究),另派一個沒看過結論的代理只拿原始問題核對標準缺口。報告去掉本機路徑後放在 `governance/eval/results/ai-test-verification-research-20261102/`。這份計劃只吸收它們已經量過的結論,不重做;它們沒量過、我們真的需要的,列在〈第二批〉。

吸收的結論(出處都在研讀報告):
- AI 看得到實作時,會把錯的行為寫成預期值:把錯寫成預期的測試是抓到錯的 3.5–6.5 倍(Python,145 個 PR),給有錯的程式時被誤導的測試多約 8 倍(Java,11 個模型);把實作從眼前拿掉、只給意圖描述才明顯有用;在提示裡警告「程式可能有錯」沒有改變結果(這點只在 gpt-4o-mini 上測過);一直修到變綠會把強斷言改弱。
- AI 會為了讓測試過而作弊:測試可寫時直接改測試最常見;設成唯讀擋得住改測試,擋不住寫死測試輸入、查表、只做測試碰得到的路徑;LLM 當作弊偵測器最好約 63%,語意型幾乎抓不到;可靠的做法是「寬規則篩候選 → 人裁」,誤報要有正式出口。Google 的 Android Bench 2.0 在 Android 上看到改截圖容差、註解掉 `@Test`、DAO 回傳寫死資料。
- 測試壞味道多數不值得擋:寫死數字、一堆沒附說明的斷言在人寫測試也近 100%,偵測工具約四成誤報;真正會「永遠綠」的是沒有斷言、try/catch 裡斷言但 try 沒寫 `fail()`。Kotlin 這邊 detekt、Konsist、Android Lint、Sonar Kotlin 都沒有現成規則抓這兩種(Android Lint 只有 `IgnoreWithoutReason`;Sonar 的「測試沒有斷言」規則 S2699 只有 Java、C# 等語言版)。
- 不穩測試:重跑 10 次只找到約四分之一;打亂順序比原順序重跑有效;重試後才過要算不穩。
- 變異測試:只變異改到的行、存活的變異當審查意見、不設分數門檻(Google);Meta 在 Android Kotlin 上的 TestGen-LLM 與 ACH 是最貼近的工業證據。

現況(2026-11-02,分支起點 047031883):
- 推送前沒有任何一道看「測試被刪、斷言變弱、預期值被改、跳過標記、建置或 CI 的測試設定、截圖基準圖」。新增告警閘挑檔時排除路徑含 `test/`、`tests/` 這類樣式的檔(`_stack_changed_ok` 的測試檔樣式,所以 `src/test/` 被排除,`src/androidTest/` 不被排除),它只跑專案宣告的檢查工具、專案沒宣告時直接回「沒設定」——它問的是「工具有沒有多報告警」,不看測試本身被怎麼改。
- 新增告警閘的三個出口(設定 off、設定 warn、`LUMOS_SKIP_LINT_NEW`)都不寫治理帳;warn 模式下新增的告警一條都不印,放行小結照樣寫「沒有新增的告警」,而且推送掛鉤只轉印含「提醒」等幾個字的行;判定函式丟出的任何例外,在代碼審檢查那一層被接住後一律自動放行(fail-open);放行檔讀不了時整道自動放行。
- `lumos lint-waive` 只檢查理由不是空的;放行紀錄的 `by` 欄記的是 `$USER`(本 repo 352 筆全有),分不出是人還是 AI 在沒有互動終端時放的。
- Kotlin 靜態掃描只有 `assertEquals(x, x)` 一條,Truth 的 `assertThat(x).isEqualTo(x)` 不認。
- 標準沒寫:寫測試的 AI 能不能看實作、新測試在現有程式上紅了怎麼辦、新測試重跑與打亂順序、裝置上的隔離、畫面重建與程序被回收後的狀態;範本測試只提到「在裝置變體會紅、收證時用類別篩選避開」,沒寫要刪掉或換成真測試;「重試到過才綠不算」有寫,但沒寫怎麼讓機器擋;變異測試那句的事實過時(PIT 的協程雜訊回報 2022 年已結案)。

最小解:
- 在主程式加一支比對工具 `lumos test-guard`(跟 Room 守衛 `lumos room-guard` 同一層、同一種寫法),只讀一段範圍兩端的檔案內容,吐出作弊候選;不跑測試、不改任何檔。剝字串與註解、找測試函式、括號配對、切參數、批次讀檔、git 呼叫、主線分岔點全部重用主程式既有的函式(不另寫一套),既有函式缺的寫法就擴充它並補測試。它的家新開 `Systems/test-guard`。
- 它的候選併進新增告警閘的「新增告警」清單,放行沿用 `lumos lint-waive <指紋> --note`;不新增閘、不新增放行檔。專案沒宣告檢查工具時,作弊比對照樣判。
- 補新增告警閘的幾個洞:比對出錯擋下、warn 要印出來而且推送時看得到、關閘要留帳、同一次推送把閘放寬不算數、AI 放的放行事後要人看過(照搬 Android 端到端驗收的判法)。
- Semgrep 的自比規則補 Truth 與 Hamcrest 幾條。
- 標準照研讀結論改寫;上一輪延後的六條一起處理。
- 考場實跑壞例子,並拿考場真實歷史量誤報。

PRIOR-ART: 「寬規則篩候選、再由人或 LLM 去掉誤報」借 FrogNano 的兩段式作弊偵測;規則清單持續補新招借 Verification Horizon;擋下後附理由放行借本專案的新增告警閘與 `lint-waive`;AI 放的放行要人看過借本專案 Android 端到端驗收(`_e2e_waive_cmd`:在終端真的問一句、有人答 y 才算人放的);「被推的分支自己放寬設定不算數」借本專案從可信版本讀宣告的做法(`_lens_trusted_ref`、`_trusted_decl_ref`:被推的分支自己改的不算);在主程式讀 git 兩端、判 Android 檔借 Room 守衛(`_rg_*`)與它重用的 `_strip_c_comments`、`_rg_methods`、`_rg_is_test_path`、`_rg_split_args`,主線分岔點借 `_lens_default_base`,批次讀檔借 `_nodehome_cat_blobs_capped`;不宣稱擋得住特判與查表,照 ImpossibleBench「唯讀擋不住特判」的結論。外面沒有現成工具比對 Kotlin 測試的改動前後(研讀報告查過 detekt、Konsist、Android Lint、Sonar Kotlin)。裁定:閘、放行、讀檔與辨識全部借用,只有規則本身自建。
PRIOR-ART: catch 吞斷言照 Google Error Prone 的 AssertionFailureIgnored(try 有斷言或 fail、catch 接得住 AssertionError 就報,不看 catch 內容,建議改 assertThrows)與 MissingFail(try 沒 fail、catch 有斷言)兩條檢查的判法(代碼審 r7 上網查得,https://errorprone.info/bugpattern/AssertionFailureIgnored 、https://errorprone.info/bugpattern/MissingFail );效能另有 regexploit 只在開發時掃正規式的回溯(它看不到「每個起點各掃一段」的形狀,所以另加倍增耗時測試)
RETIRE-IF: 人工抽查放行檔(`lumos lint-waive --list`,每筆記著規則代號、理由與放行的是人還是 AI)時,某條 `tq/` 規則三個月內的放行理由多數是「規則判錯」(不是「合理改動」),就收窄或拿掉那條;全部規則都這樣就撤掉整支比對工具 [retire:人裁] [until:2027-05-02]

## 名詞

- **作弊候選**:比對工具認為「可能是為了讓測試過而做的改動」的一處。只是候選,不是定罪;改掉或附理由放行都算處理完。
- **改動前、改動後**:比對範圍的起點版本與終點版本,兩邊的檔案內容都直接從 git 讀原始位元組(不經轉換程式、不看 `.gitattributes` 的 diff 設定),不讀工作目錄、不用 git diff 的輸出判內容。起點的算法見做法一〈起點〉。
- **測試檔、正式程式檔、截圖基準圖**:比對工具依路徑分的三類檔,定義在做法一(建置檔與 CI 檔原本也在內,代碼審 r4 後移到〈第二批〉)。
- **測試函式、函式鍵、本體簽名**:測試函式是測試檔裡標了測試註記的函式;函式鍵是「類別路徑加函式名」;本體簽名是參數列右括號之後到函式結尾的原文(剝註解、留字串、去空白)。定義在做法一。
- **斷言字、斷言敘述、強斷言、常值斷言、預期值的位置**:算「這支測試有沒有在檢查結果、檢查得多嚴」用的名單與切法,定義在做法一。
- **次數差**:同一條規則在改動後命中的次數減去改動前命中的次數;只有多出來的才算新增候選(跟新增告警閘「算次數不算有無」同一個做法)。
- **新增告警閘、放行**:推送前判「這次改動有沒有帶進新的告警」的那道閘;放行是 `lumos lint-waive <指紋> --note "<理由>"`,寫進要提交的 `.lumos/lint-waivers.json`。
- **AI 放的放行**:放行時終端沒有人答「是本人確認」(沒有互動終端、讀不到回答)而寫下的放行,紀錄的 `origin` 欄標成 `ai`,直到人在互動終端確認看過。
- **考場**:mOrangePos 的本機演練工作樹與分支,不推不併。
- **收證工具、配套**:收證工具是 `lumos test-quality` 這組子指令;配套是 `scripts/test_quality*.py` 這幾支檔,主程式先比對每支的 sha256(配套指紋表 `_TEST_QUALITY_BUNDLE_DIGESTS`)再載入,對不上整組拒跑。這次只改到其中的 `test_quality_semgrep.py`。
- **裝置那路、斷言歸因**:收證工具讀測試報告時判「這個失敗是不是斷言失敗」的規則叫斷言歸因;裝置那路是讀 Android 儀器測試報告(沒有例外型別欄、只能看失敗文字)的那一支判斷。
- **安全證據閘**:推送前判「登記過的資安護欄有沒有合格證據」的閘,它的故障敏感度那條路會用斷言歸因核對故障收據。

## 做法

### 一、比對工具 `lumos test-guard`

**用法與退出碼**(照 Room 守衛 `cmd_room_guard`):`lumos test-guard --diff <起點>..<終點> [--repo <根>] [--json]`,範圍用 `_rg_range` 解(只收兩個點的寫法);沒有候選 0、有候選 1;不是 git 專案回 0 並印一句「不是 git 專案,沒比」;參數錯或終點解不出來回 2。新增告警閘呼叫它時直接傳已經算好的兩端,不再解析範圍字串。

**比對起點**(指令與閘都先做這一步,`--json` 與擋下訊息印出實際用的起點):比對從「跟主線的分岔點」起算——先用 `_lens_default_base(root, tip=終點, include_local=False)`(只看遠端主線;本機 main 上還沒推出去的提交不能當成已在主線,代碼審 r2 改定),沒有遠端主線才退回 `include_local=True`(Room 守衛手動跑用的同一支);找得到、而且不等於終點本身,就用它;找不到(沒有主線、推的就是主線)照給的起點。這樣合過主線之後推送,主線上的改動不會算到推送者頭上;同一條分支先前推送已經處理過的候選,不是改掉了就是已在放行檔,不會重複擋。給的起點是空樹而找不到主線時,照比對、全部只印不擋,並寫一筆治理帳(閘名 `lint-new`、`no-baseline`,跟關閘的 `skipped` 分開數)。

**讀法**(全部借既有函式):
- 改了哪些檔:用 `_lens_git_dl` 跑 `git diff --raw -z -M --no-abbrev --no-ext-diff --no-textconv <起點> <終點>`,輸出照位元組讀,含刪除與改名、帶改動後的 git 物件編號(截圖基準圖與太大檔的指紋要綁它;`_nodehome_name_status` 只解檔名狀態、拿不到物件編號,所以這裡讀 `--raw`)。檔名不是合法 UTF-8 或含換行的,各列一條 `tq/unreadable`,不讓替換字元把它變成讀不到的空檔。
- 檔案內容:兩端合成一批,用 `_nodehome_cat_blobs_capped` 批次讀原始位元組(先問大小再讀內容,總共兩個 git 行程;不經轉換程式),單檔上限 5 MB 或 10 萬行、一次推送總量上限 200 MB,超過的列 `tq/too-large`;不存在的那一端(新增檔沒有改動前、刪除檔沒有改動後)當空檔;內容照 UTF-8 解,不是 UTF-8 的位元組換成替換字元。
- 剝字串與註解:擴充全庫唯一那支 `_strip_c_comments`,加 `keep_length=True` 選項——剝掉的部分換成等長的空白(換行照留),位置跟原文一一對應;掃描樣式照舊是 `_C_STRIP_PAT`,不另寫一套,既有呼叫端輸出不變。依檔類用不同模式:測試檔分三種用法——找結構(函式範圍、括號配對)時連字串內容一起清(字串裡的括號不干擾配對)、取斷言敘述時在剝過的文字找位置再回原文取字(字串預期值保留)、算本體簽名與逐行規則(跳過標記、門檻字樣)時只剝註解留字串;正式程式檔只剝註解、留字串(`"robolectric"` 要看字串內容);建置檔與 CI 檔這一批不比(第二批另議剝法)。
- 測試函式:`_rg_methods(text, java, kinds=<測試註記>)` 加 `_rg_annotations`、`_rg_balanced`、`_rg_method_end`。測試註記:`Test`、`ParameterizedTest`、`RepeatedTest`、`TestFactory`、`TestTemplate`、`Theory`(`_rg_annotations` 取短名,`org.junit.Test`、`kotlin.test.Test` 都算)。既有函式要擴充的幾處(都補 Room 守衛那邊的回歸測試;`Systems/room-guard` 寫一句「這幾支被 test-guard 共用,改動兩邊測試一起跑」):
  - 運算式本體:`fun x() = …` 的本體改成「`=` 之後,小括號與中括號深度為 0 時遇到左大括號就配到對應的右大括號;深度為 0 的換行而且已經看過內容、下一行不是接續(開頭是 `.`、`?.`、`?:`、`{`、運算子或右括號)時結束」——`= runTest {`、`= runTest(d) {`、`=` 換行再接 `runTest {` 或接單行斷言都涵蓋。這會改變 Room 守衛對 `open fun x() = db.withTransaction { … }` 這類 DAO 方法的範圍(從只到第一行變成整個區塊),是修正不是不變,Room 守衛補一支這種寫法的回歸測試。
  - 反引號函式名:剝字串會把反引號整段清空,原本的宣告比對要求名稱是英數字,整支測試會被跳過;改成也認一對反引號,名稱由呼叫端回原文那一行取(含空白與括號的完整名稱)。
  - 效能:先判註記對不對、再找宣告;宣告只在註記後 600 個字元內找(同 `KOTLIN_TEST_RE` 的上限)——註記後面一直沒有左括號時,不限長的比對每個註記都掃到檔尾;行號用預先算好的行首位置二分搜尋,不每次從檔頭數換行。草稿實測(2026-11-02,會談暫存區):「`@A` 換行 `val x = 1`」重複 5 萬次的檔從十幾秒降到 0.05 秒;5 萬個全是 `@Test` 的病態檔 2.5 秒。
  - `_rg_split_args` 加 `angle=False` 選項:不把 `<`、`>` 當括號(比較運算 `a > b`、lambda 箭頭 `x -> x` 會讓深度歪掉);Room 守衛照舊預設把泛型的 `<>` 當括號。
- 函式鍵:類別路徑加名稱,沿著剝過的原文追蹤 `class`/`object`/`interface` 的大括號深度;同一類別裡同名的多載,第二個起加 `#2`、`#3`(依出現順序,用計數器給號,不逐個試名字——逐個試在幾萬支同名測試時是平方級)。
- 括號配對:每支函式在剝過的本體上一趟算出所有括號的對應表,斷言、try、runCatching 都查這張表,不各自重掃(極深巢狀不會變平方級)。剝完之後小括號或大括號總數配不平、或內容含 NUL,那支檔列 `tq/unparsable`,函式級規則不判。
- 路徑分類:測試路徑優先(`buildSrc/` 底下的 `src/test` 也是測試檔,不是建置檔);測試路徑用 `_rg_is_test_path`(有一段 `src/<名稱>/`,名稱是 `test`、以 `test` 或 `androidTest` 開頭,或以 `Test` 結尾,所以 `commonTest`、`jvmTest`、`androidUnitTest`、`screenshotTest` 都算);檔名以 `Test`/`Tests` 結尾但不在 `src/main` 底下的也算。改動前與改動後兩個路徑任一邊是測試檔就當測試檔(改名成 `.disabled`、搬進 `src/main` 都看得到)。

**三類檔**(下面的建置檔與 CI 檔兩行留作〈第二批〉的定義,這一批不比):
- 測試檔:上面那條規則認出的 `.kt`/`.java`,或改名前是測試檔的任何檔。
- 正式程式檔:其他 `.kt`/`.java`,但不含 `buildSrc/`、`build-logic/` 底下。
- 建置檔(第二批):任何位置的 `*.gradle`、`*.gradle.kts`、`gradle.properties`、`robolectric.properties`,以及 `buildSrc/`、`build-logic/` 底下的 `.kt`/`.kts`。
- CI 檔(第二批):`.github/workflows/` 底下的 `.yml`/`.yaml`、`.github/actions/*/action.yml`/`action.yaml`、`.gitlab-ci.yml`、`bitrise.yml`、`Jenkinsfile`、`azure-pipelines.yml`、`.circleci/config.yml`、`codemagic.yaml`。
- 截圖基準圖:`.png`/`.webp`/`.jpg`/`.jpeg`,路徑在測試目錄裡,或含 `screenshots`、`snapshots`、`roborazzi`、`paparazzi` 這幾個目錄名(不分大小寫);路徑任一段是 `docs`、`fastlane`、`metadata`,或含 `phoneScreenshots`、`tabletScreenshots`(文件與商店截圖)、或在測試目錄的 `assets/`、`resources/` 底下(測試輸入圖)的不算。只看 git 物件編號,不讀圖檔內容。

**斷言**(在剝過字串與註解的本體上找,區分大小寫):
- 斷言字(後面要接 `(`、`{` 或 `<`;前面可以帶 `Assert.`、`Assertions.`、`org.junit.Assert.` 這類限定):`assert` 接大寫開頭的名字(含 `assertThat`、`assertThrows`、`assertFailsWith`)、單獨的 `assert`(Kotlin 標準庫)、`fail`、`expectThat`、`expect.that`、`verify` 開頭(MockK/Mockito)、`coVerify` 開頭、`confirmVerified`、Turbine 的 `awaitItem`/`awaitError`/`awaitComplete`/`awaitEvent`/`expectNoEvents`/`expectMostRecentItem`/`cancelAndConsumeRemainingEvents`、截圖比對的 `captureRoboImage`/`compareRoboImage`;點號接的 `.assert…(`(Compose 的 `.assertIsDisplayed()`)、`.check(`(Espresso)、`.snapshot`(Paparazzi)、`.expect(`(JUnit 4 的 `ExpectedException`);`throw AssertionError`;Kotest 的 `should` 開頭中綴,前後是字界而且後面不是 `=`(`shouldRefresh = true` 不算)。`@Test(expected = …)` 也算這支測試有檢查。
- 斷言敘述 = 從斷言字到它對應的右括號(或右大括號),再接上後面連著的 `.名稱(…)` 鏈(Truth 的 `assertThat(a).isEqualTo(b)` 是一個敘述);可以跨好幾行;用剝過的文字找位置、回原文取字(字串常值保留)。一支函式最多取 2000 個敘述,超過的不比。
- 強斷言:敘述裡有 `assertEquals`、`assertArrayEquals`、`assertContentEquals`、`assertSame`、`isEqualTo`、`isSameInstanceAs`、`containsExactly` 開頭、`shouldBe`。
- 常值斷言:實際值是常值的敘述——`assertTrue(true)`、`assertFalse(false)` 這類條件是常值,或下面「實際值」全部是數字、字串、字元、`true`/`false`/`null` 常值(`assertEquals(88, 88)`、`assertThat(3).isEqualTo(3)`)。
- 預期值的位置與實際值(依呼叫名與參數個數,參數用 `_rg_split_args(…, angle=False)` 切):
  - `assertEquals`/`assertNotEquals`/`assertArrayEquals`/`assertContentEquals`/`assertSame`:兩個參數 → 第一個是預期值、第二個是實際值。三、四個參數依檔案匯入的斷言庫:匯入 `kotlin.test` 的斷言時照 kotlin.test 的順序(預期值、實際值,第三個是字串就是訊息、不是字串就是容差,四個參數時第三個是容差、第四個是訊息);否則照 JUnit(三個參數而第一個是字串常值 → 第一個是訊息、第二個預期值、第三個實際值;三個參數而第一個不是字串 → 預期值、實際值、容差;四個參數 → 訊息、預期值、實際值、容差)。容差改大也算預期值被改。具名參數 `expected =` 直接取。
  - `isEqualTo(…)`、`isSameInstanceAs(…)`、`containsExactly…(…)`:括號裡全部是預期值,`assertThat(…)` 裡是實際值。
  - `shouldBe`:右邊是預期值、左邊是實際值。
  - Hamcrest 的 `assertThat(實際, 比對器)`:第二個參數是預期值。
  - 方向互換:`assertTrue`↔`assertFalse`、`assertNull`↔`assertNotNull` 參數不變只換名字,也算預期值被改。

**規則**(規則代號一律 `tq/` 開頭):

| 代號 | 什麼時候成立 | 例 |
|---|---|---|
| `tq/skip-added` | 測試檔裡 `@Ignore`、`@Disabled`、`@SdkSuppress`、`@FlakyTest`、`@Config(sdk`、`Assume.assume…(`、`assumeTrue(`/`assumeFalse(`/`assumeNotNull(`/`assumeThat(`、`Assumptions.assume…(`、`TruthJUnit.assume(` 的命中次數差大於 0(`@Disabled…`、`@Enabled(On|If|For)…` 條件式與完整類別名寫法也算;assume 與門檻的身分是整個敘述,見〈次數差的身分〉);或改動前就有的測試函式新加了 `expected =` | 給一支紅的測試加 `@Ignore` |
| `tq/test-removed` | 改動前的測試函式(函式鍵)在改動後找不到,而且沒有跟這次改動裡任何一支「新出現的」函式本體簽名相同(一對一配對:兩支一樣的刪兩支只加一支,另一支照樣算刪除;本體簽名是空的不算改名證據);測試檔改名成非測試檔或被刪,裡面的函式一樣算;同一支檔的刪除合成一條,列出被刪的函式名,指紋綁那一組函式鍵 | 刪掉一支紅的測試;本體一字不改只改名、原樣搬到另一支測試檔不列 |
| `tq/assert-weakened` | 改動前後都有的同一個函式鍵(或本體簽名配上的改名),斷言敘述變少、強斷言變少,或常值斷言變多 | `assertEquals(3, n)` 改成 `assertTrue(n > 0)`;`assertTrue(r.isValid())` 改成 `assertTrue(true)`;`assertEquals(88, calc.total())` 改成 `assertEquals(88, 88)` |
| `tq/expected-changed` | 改動前後都有的同一個函式鍵,兩邊的斷言敘述清單用最長共同子序列對齊,被替換的那幾對裡,除了預期值的位置之外全部相同、預期值的位置不同(含方向互換) | `assertEquals(88, total)` 改成 `assertEquals(90, total)`;跨行的斷言、字串預期值、`State.Loading` 改 `State.Error`、`assertTrue` 改 `assertFalse` 都算;只改 `total(listOf(40, 48))` 的參數不列;只改訊息字串不列;中間插一條斷言不讓後面錯位 |
| `tq/no-assertion` | 新增的測試函式,或本體簽名、註記有變的測試函式,一個斷言字都沒有 | 只呼叫 `vm.load()` 不檢查任何結果 |
| `tq/catch-no-fail` | 新增或本體有變的測試函式裡有 `try { … } catch (…) { … }`,catch 區塊有斷言字(含 Kotest should…、`check(`、`require(`)或是空的,而 try 區塊沒有 `fail(`、`assertThrows`、`assertFailsWith`(catch 區塊裡有 `fail(`,也就是預期不丟例外的寫法,不列);或 try 裡有斷言(含結尾的 `fail(`)而 catch 接得住 AssertionError(型別名字以 Error、Failure 結尾或是 Throwable,代碼審 r8 改定)、catch 不重丟,不看 catch 裡寫了什麼(照 Error Prone 的 AssertionFailureIgnored,代碼審 r7 改定:r5–r7 靠名字猜「算不算檢查」連三輪被打穿);或 `runCatching { … }` 裡有斷言字、而後面沒有接 `.getOrThrow()` | 不丟例外時測試照樣綠 |
| `tq/build-config`(第二批,這一批不比) | 建置檔(留字串、剝註解)裡下面這些的命中次數差大於 0,三種寫法都認(Kotlin 的 `x = v`、Groovy 的 `x v`、Provider 的 `x.set(v)`):`ignoreFailures` 設成 true(不限在測試區塊,點號寫法 `test.ignoreFailures = true` 也算;只排除外層或同一行開的區塊是靜態檢查外掛或報表(detekt、ktlint、kotlinter、spotless、checkstyle、pmd、spotbugs、findbugs、animalsniffer、lint、jacoco、kover)而且不是測試任務的;比對的是區塊開頭左大括號之前那段,不是同一行後面的字)、`excludeTestsMatching`、`failOnNoMatchingTests`/`isFailOnNoMatchingTests`/`failOnNoDiscoveredTests` 設成 false、`returnDefaultValues`/`isReturnDefaultValues` 設成 true、`failOnPassedAfterRetry` 設成 false、`notAnnotation`/`notClass`/`notPackage`;所在區塊(含外層)是測試任務(`test {`、`tasks.test`、`withType<Test>`、`named<Test>`、`unitTests.all`;或區塊開頭、同一行裡有引號整個是含 test 的任務名:`"testDebugUnitTest"`、`":app:testDebugUnitTest"`,所以 findByName、`tasks[…]`、getByPath、`it.name ==` 都認得;檔名樣式與類別名有 `*` `/` `.` 不算,`"jacocoTestReport"` 這類報表外掛的任務名不算;`tasks.matching { … }` 換行 `}.configureEach {` 這種同一行接著開的區塊也算;`testCoverage {`、`testOptions {` 不算;代碼審 r3 改定,r2 版要求要有點名呼叫的字樣,漏了 findByName 這類寫法)時的 `enabled` 設成 false、`onlyIf { false }`、`exclude` 的字串含 `Test`、新增 `excludeTags`/`excludeCategories`/`excludeEngines`;重試外掛 `org.gradle.test-retry` 或 `maxRetries` 的命中次數差大於 0,但改動後的任何建置檔(用 `git grep` 查一次)都沒有 `failOnPassedAfterRetry` 設成 true;改動前有、改動後沒了(含被註解掉)的 `dependsOn("test")`、`check.dependsOn` | `tasks.withType<Test> { ignoreFailures = true }`;JaCoCo 報表的 `exclude: ['**/*Test*.*']` 不在測試任務區塊,不列 |
| `tq/ci-config`(第二批,這一批不比) | CI 檔(只剝 `#` 註解、併續行)裡呼叫 Gradle 的指令(含 `gradlew`、`gradle ` 指令、Gradle 官方 Action 的 `arguments:`、Bitrise 的 `gradle_task:`)的 `-x`/`--exclude-task` 接含 `test` 或 `check` 的任務名、行尾 `\|\| true` 的命中次數差大於 0;放寬鍵(`continue-on-error: true`、`allow_failure: true`、`if: false`、Azure 的 `continueOnError: true`、Bitrise 的 `is_skippable: true`、Codemagic 的 `ignore_failure: true`)所在的區塊(縮排比它淺的最近一行到下一個同層,步驟層與工作層都算)裡有 Gradle 呼叫時的次數差大於 0;改動前呼叫的 Gradle 測試或 check 任務,改動後呼叫它的次數變少(照 `&&`、`\|\|`、`;`、`\|` 切段,只看有 Gradle 呼叫的段,跳過旗標與 `-x`、`--tests` 這類旗標帶的參數,任務名黏著的 `)` `>` 這類標點拿掉,剩下的才是任務名;加旗標、改篩選、`-x` 寫在任務前面都不影響;`-x` 也認 `-xtest`、`--exclude-task=test`;行尾的 `\|\| true` 也認 `\|\| :`、`\|\| exit 0`、`\|\| echo …`) | `./gradlew build -x test`(含反斜線續行);`pytest -x tests/`、`mkdir -p a \|\| true` 不列 |
| `tq/timeout-raised` | 同一個函式(含註記那幾行)裡(建置檔的逾時移到第二批),改動前有、改動後沒有的逾時行(`timeout`、`Timeout`、`withTimeout(`,不分大小寫),配上改動後有、改動前沒有的逾時行:把數字換成佔位後一樣,而改動後的最大數字比較大 | `@Test(timeout = 30)` 改成 `45` |
| `tq/snapshot-changed` | 截圖基準圖有新增、修改或刪除(同一個目錄合成一條,指紋綁那批檔的路徑與 git 物件編號);或測試檔裡 `changeThreshold`、`maxDistance`、`ImageComparator`、`roborazzi.test.record` 的命中次數差大於 0 | 功能改動跟重錄的基準圖放在同一批 |
| `tq/test-env-sniff` | 正式程式檔(留字串、剝註解)裡 `"robolectric"`(不分大小寫)、`isRunningTest`、`isRobolectric`、`Class.forName("org.junit`、`Class.forName("androidx.test`、`Class.forName("org.robolectric` 的命中次數差大於 0(`Build.FINGERPRINT` 單獨出現不算,模擬器偵測常用) | 程式偵測到在測試裡就走另一條路 |
| `tq/too-large` | 三類檔(截圖除外)任一端超過比對工具自己的上限(單檔 5 MB 或 10 萬行、一次推送總量 200 MB;測試檔有一行超過 2 萬字也列一條,那幾行抹掉後其餘照比(代碼審 r3 改定:只套測試檔、不再整支不解析);不借新增告警閘那兩個給慢工具調小的設定);指紋綁路徑與改動後的 git 物件編號(那支檔再改要再看一次) | 不靜默略過 |
| `tq/unparsable` | 剝完字串與註解後括號總數配不平,或內容含 NUL,那支檔的函式級規則判不了;指紋綁路徑與 git 物件編號 | 不靜默略過 |
| `tq/unreadable` | 那支檔從 git 讀不出來,或檔名不是 UTF-8、含換行;指紋綁路徑 | 不靜默略過 |

- 次數差的身分(代碼審 r1、r2 改定,原本寫的是「函式名加本體簽名」):測試檔用(規則代號、函式名(類別層級的註記用「檔:路徑」)、種類),種類是:跳過註記一律算「跳過」(`@Ignore` 換 `@Disabled`、改跳過理由、只改本體都不算新增),assume 呼叫與比對門檻是整個敘述、字串外的空白整理過(字串常值原樣,頭尾與逗號後的空白都算內容,代碼審 r5 改定;括號配平、跨行照接;條件改成永遠跳過、門檻數值調高都算新增,只換行重排、改同一行別的斷言不算;代碼審 r3 改定,原本只取一行);測試檔改名或搬家時兩邊都用新路徑;跨這次改動的全部測試檔一起算(測試原樣搬到另一支檔、類別名跟著變,帶過去的註記也不會被當成新增)。整檔重新縮排、換行尾、函式搬位置都不會讓舊命中變成新增。
- 每條候選帶:規則代號、檔案、行號(刪除類用改動前行號並標 `side: base`)、一句為什麼、該確認什麼、身分字串、指紋。指紋 = sha256(規則代號、檔案、身分、這是第幾個相同身分)前 16 碼;`tq/expected-changed` 的身分是含常值的改動後原文。同一個身分第二次出現,指紋不同,放行第一個不會順帶放掉第二個。新增告警閘既有的指紋不含序號(多出來的幾條共用同一個指紋),這兩種算法並存,寫進 `Systems/pitfalls-lint-adapter`。
- 斷言敘述清單的對齊用 `difflib.SequenceMatcher`(不開自動略過);被替換的區塊兩邊一樣長時逐對比,長度不同時只比前面成對的那幾個,多出來或少掉的由「斷言變少、強斷言變少」那條規則接。
- 判讀跟輸入大小成正比:剝字串一趟、每支函式的括號對應表一趟、逐行比對一趟,宣告比對有 600 字元上限;斷言、try、fail 的位置每支函式各算一次再用二分查,catch 的括號用同一張括號對應表找右括號,行號在收集命中時記下。代碼審 r1、r2 兩輪都被病態單行輸入打穿平方級,r2 起在外層加一道不靠逐條判斷的上限:測試檔裡超過 2 萬字的行抹掉不比、那支檔另列一條可放行的 `tq/too-large`(代價是那種檔每次要人放行)。r3 又被兩種乘積打穿(很長的區塊開頭乘很多內層行、CI 續行併成的長邏輯行),那兩類在 r4 後隨建置檔與 CI 規則移到第二批。類別本體的泛型改成同一行、最多 400 字的 C 層查找,下一個大括號、括號、換行的位置共用快取;巢狀類別的路徑在開類別時接一次,超過 200 字換成摘要加最內層那段(每層都有測試時,函式鍵總長也跟深度成正比;代碼審 r4 改定)。r5 又找到三處原本就有的乘積形狀,改成跟長度成正比:catch 的型別括號原本用 `[^)]*` 掃到很遠的右括號(很多 try 乘距離)、類別名後面接大段空白時每個宣告各掃一次(宣告數乘空白長)、測試宣告找不到名字時每行再找一次名字而泛型角括號沒有上限;換行後第一個非空白字與一行最後一個非空白字每個位置只找一次。比對工具每支檔開始前看一次截止時間,超過就丟出「超過截止時間」,單一檔案跑到一半不會被打斷(單檔有 5 MB 上限)。草稿實測:接近 6 萬行、一次改兩千處預期值的測試檔 0.6 秒;300 支檔 0.4 秒;2 萬支同名測試切完不到 5 秒;考場 192 個提交逐一比完 12 秒。
- **抓不到的**,寫進工具說明與標準,不宣稱(實作後以工具輸出的清單為準,標準那條由 `t_tq_guard_cli_contract` 釘成逐字同一份;下面是設計時的清單,其中 Kotlin 巢狀區塊註解、版本目錄、lint 與 detekt 基準檔、其他棧屬於範圍外的說明,不列進工具輸出):實作裡寫死測試輸入、查表、只做測試碰得到的路徑、多做沒人要的別名;預期值先放進變數再斷言(`val expected = 88`);參數化測試刪掉資料列;JUnit 3 那種不標註記、靠 `test` 開頭命名的測試;Kotest 字串式測試與 Spek;本體有改的改名(只列成刪除);逾時換單位(`5.seconds` 改 `5.minutes`)、整行新增的逾時、CI 的 `timeout-minutes`;catch 裡只印出例外(`println(e)`)的吞法;在測試本體裡提早 `return` 或包一個永假的 `if`;Truth 的 `assume()` 以外的自訂跳過輔助;JUnit 5 的測試改成 `private` 或 `static`(不再被執行;修飾詞改動不算測試有變);不同類別裡同名的兩支測試一支拿掉跳過另一支加上(會互抵);Kotlin 巢狀的區塊註解(剝註解那支不認巢狀);把測試檔搬進 Gradle 不編譯的目錄但路徑仍像測試目錄(工具不讀 `sourceSets` 的實際範圍);版本目錄 `libs.versions.toml`(只放版本,不放測試設定);lint 與 detekt 的基準檔改動(那是靜態檢查的放行,不是測試);Jenkinsfile 的 `catchError` 這類 Groovy 包裝(Jenkinsfile 只認呼叫 Gradle 的行);同一處先被合理放行、之後重新啟用又被同樣改回(指紋相同,會沿用舊放行);Python 等其他棧(見〈第二批〉)。
- **已知的誤報**,有放行出口、在考場量測(S22)時一併記:只靠專案自訂的斷言輔助(例如 `checkState(...)`、`ensureX(...)`、`intended(...)`)的測試會被列成 `tq/no-assertion`;新模組照範本抄來的 `isReturnDefaultValues = true`、Robolectric 測試必帶的 `@Config(sdk = …)` 每處各算一條。這次不加宣告口,等考場量出這類誤報的實際比例再決定(多就在第二批加,照收證工具掃描既有的 `--check-helper` 寫法)。一次大重構產生上百條候選時沒有整批放行,出口是那一次設環境變數 `LUMOS_SKIP_LINT_NEW=1`(有候選或比對出錯時留帳;只認 1);這次不加批次放行,因為「測試被刪」與「基準圖」已經按檔案、按目錄合成一條,剩下會大量出現的只有預期值大批改動,那正是要人逐條看的。

### 二、併進新增告警閘

- **判定順序**:閘的模式照舊從工作目錄的 `.lumos/config.json` 讀(`_lint_new_config`,既有測試與 `docs/指令參考.md` 那句「`lint_new` 讀工作目錄那份」不變);例外是**這次的推送範圍本身把 `lint_new.gate` 放寬了**——用 `_nodehome_reader` 從 git 取推送範圍給的起點(換成比對起點之前的那一個)與終點兩個版本的設定檔位元組,交給 `_lint_new_config(text=…, from_snapshot=True)` 解出 `lint_new.gate`(沒寫當 block),終點比起點寬(block 改成 warn 或 off、warn 改成 off),這次照起點的值判並印一行「提醒:這次推送把新增告警閘放寬,照放寬前的設定判;放寬從下一次推送起生效」,寫一筆治理帳(`lint-new`、`relax-deferred`)。只在工作目錄改、沒提交時,本機照工作目錄的值(既有行為)。接著:模式是 off 或設了 `LUMOS_SKIP_LINT_NEW` 時見〈關閘留帳〉→ 算出兩端 → 比對工具 → 有沒有宣告檢查工具 → 既有流程。比對候選轉成告警的形狀(`key`、`rule`、`file`、`line`、`message`,另加 `verify`),扣掉放行檔裡已有的,剩下的併進「新增告警」清單。沒宣告檢查工具、或這次沒有要掃的程式碼檔時,只要有作弊候選照樣判,沒有候選才回原本的狀態。
- 只有改動碰到三類檔(含刪除與改名,從自己那份 `--raw` 清單判)才跑比對;沒碰到就不跑。觸發條件只看路徑與副檔名,不判是不是 Android:任何 Kotlin 或 Java 專案(含 JVM 後端)改到測試檔或正式程式檔都會跑,截圖基準圖不分技術棧都會跑;建置檔與 CI 檔這一批不比(第二批)。
- **比對出錯擋下**:比對工具在 `_lint_new_verdict` 裡自己包住例外與截止時間,記成「沒跑完」裡的一種(`kind: guard`,跟既有的「時間預算沒跑到」同類),會擋;不會漏到外層 `_codeloop_lint_new_step` 的 fail-open。`_lint_new_classify` 的擋下理由與 `_cl_say_lint_block` 的訊息對 `guard` 另寫一句(「作弊比對沒跑完:<原因>」),不套「因為時間預算沒跑到」與放行指令。不照新增告警閘「環境不可用就自動放行」的老路:Android 端到端驗收那道閘當初就否決過「照新增告警閘出錯就放行」,決定是判不清就擋(見 `lumos rejections` 的那一筆);既有閘的「時間預算沒跑到」「檔太大」也都是擋。單一怪檔不會讓整道卡住:配不平、含 NUL、太大、讀不出來都落到可放行的候選(`tq/unparsable` 等),只有比對工具本身的程式錯才走「沒跑完」;那時同一次推送的出口是 `LUMOS_SKIP_LINT_NEW=1`(比對出錯也會留一筆 `skipped-env` 帳;只認 1,殘留的 0 或 false 不關閘;改設定在同一次推送不算數)。
- **放行檔讀不了**時:比對沒有候選 → 照既有的自動放行並記帳;有候選 → 擋下,理由寫「放行檔 `.lumos/lint-waivers.json` 讀不了,先修好它再放行」,不再印放行指令(那時放行指令一定失敗),也不記自動放行的帳。兩端算不出來時照舊自動放行並記帳(連改了哪些檔都不確定)。
- **warn 要印、推送時看得到**:設成 warn 時,新增告警(含比對候選)逐條印出來,每行以「提醒:」開頭(推送掛鉤 `pre-push` 只轉印含「提醒」等幾個字的行,Android 端到端驗收的同類輸出也是這樣開頭),小結寫「提醒:新增告警閘只報不擋,有 N 條」;只有比對在跑、沒有檢查命令時,不印「跑了 0 條檢查命令」。有比對候選時寫一筆治理帳(`lint-new`、`warned`、候選條數)。
- **關閘留帳**:設定 off 或 `LUMOS_SKIP_LINT_NEW` 時,比對工具照樣在背後跑一次(只讀、不擋;它自己出錯也不擋),**有候選、或比對自己出錯**才寫一筆治理帳(`lint-new`,設定 off 寫 `skipped`、環境變數寫 `skipped-env`,原因寫被跳過的候選條數或比對出錯的原因;比對壞了被擋、改用環境變數繞過的那一次因此留得下痕跡,代碼審 r2 改定);沒有候選也沒出錯不寫。這讓 off 不再等於「完全不執行」(鄰居 Room 守衛、筆記形狀擋的 off 都是不執行),是刻意的例外,寫進 `Systems/test-guard` 與 `Systems/pitfalls-lint-adapter`:代價是 off 的專案仍付比對成本,換到「關閘放過了什麼」有痕跡。健檢的新增告警閘段落把最近 30 天的 `skipped`、`skipped-env`、`warned`、`relax-deferred`、`no-baseline` 各自數出來。
- **AI 放的放行事後要人看過**(判法照搬 Android 端到端驗收 `_e2e_waive_cmd`,套在全部新增告警閘的放行):
  - 理由至少 10 個字而且有實字(套到全部放行,不只 `tq/`;既有測試 `t_lint_waive_cli_records_rule_and_file` 的兩字理由跟著改)。
  - 放行時用 `_confirm_tty(…, stdin_timeout=True)` 在終端問一句「這筆放行是你本人確認的嗎?[y/N]」:答 y 記 `origin: human`;答 n 不放行、回 1(跟端到端驗收一樣);沒有互動終端、逾時、讀不到回答記 `origin: ai`。`by` 欄照舊記 `$USER`(既有語意不動,新開 `origin` 欄;沒有 `origin` 欄的舊紀錄當人放的,`by` 不管寫什麼都不影響)。
  - 放行檔每筆既有的 `key`、`rule`、`file`、`reason`、`by`、`ts` 欄名照舊不改;新加 `origin`、`acked`、`acked_by`、`acked_at`(後三個欄名照端到端驗收)。`lumos lint-waive --list` 標出「AI 放的,還沒人看過」;`lumos lint-waive --ack --all` 只在互動終端上問一次確認後標成看過。放行的治理帳(`waived`)多帶 `origin`。
  - 健檢與推送前小結列出還沒人看過的 AI 放行(「提醒:」開頭,只提醒、不擋,跟端到端驗收一樣;推送前小結照 `_cl_say_e2e_notes` 的做法,擋下與放行兩種小結都印);端到端驗收另有開場掛鉤提示,這裡不做(健檢與推送兩處已涵蓋,開場掛鉤要另一份逐字複本與一致性測試)。
  - 這只讓 AI 放的放行事後可見,不阻擋推送;AI 照抄擋下訊息裡的放行指令仍然推得出去,差別是人一定看得到它放了什麼。
  - 跑測試時要隔離終端:新測試與改到的既有測試都設 `LUMOS_TTY=/nonexistent-tty`(端到端驗收測試的做法),不然開發者在終端跑全套時每筆放行會等確認。
- 擋下訊息:既有印法只印前 8 條、訊息截 70 字;`tq/` 候選改成最多印 50 條,每條印規則代號、檔案、完整原因、該確認什麼與放行指令(`--rule`、`--file` 填好),超過 50 條時最後一行寫「另有 N 條,全部列出:`lumos test-guard --diff <範圍> --json`」。`--json` 的擋下明細照帶 `verify`。
- 比對工具不進 `pitfalls` 的風險分級,不改任何既有判定的結果。
- `Systems/pitfalls-lint-adapter` 那條「lumos 只解 SARIF、不內建棧規則」的 KEY 補一句例外(新增告警閘另有一個內建來源,規則在 `Systems/test-guard`),寫明兩種指紋算法並存與 off 的例外語意,並給那篇補上負責範圍。`Systems/pitfalls-code-loop` 只寫「代碼審檢查那一步怎麼接比對、小結印什麼」。
- 治理帳由誰寫:`_lint_new_verdict` 只把要寫的帳放進回傳值(`out["events"]`),由 `_codeloop_lint_new_step` 那一層寫(照既有慣例,判定函式不直接寫帳)。
- 代碼審檢查每次推送都跑新增告警閘(不看風險分級;推送前掛鉤帶 `--keep-going`,其他道擋下也會跑到這一道);取不到推送範圍的少數情況(取不到 HEAD、推送範圍的起點等於 HEAD)在這道之前就放行,照舊。CI 也跑同一道,判的是被推的樹。
- **新頂層指令的同步點**(漏一處全套測試就紅):`HELP_WHEN` 說明表加一句、argparse 子指令與 `main` 分派、`ARCHITECTURE.md` 與 `skills/lumos-project-notes/reference.md` 寫死的指令總數(97 → 98,`t_docs_command_count` 釘)、`reference.md` 的子命令全覽歸類、`skills/lumos-project-notes/commands/06-代碼審與推送.md` 與 `INDEX.md` 提到 `lumos test-guard`(`t_command_index_complete` 釘);另寫一支 `t_test_guard_registered` 釘這幾處(照 Room 守衛的 `t_room_guard_registered`)。`README.md` 與 `docs/指令參考.md` 沒列 `room-guard`,`test-guard` 照前例也不列;推送掛鉤不另接(走代碼審檢查)。
- **既有文件要改的句子**:`docs/指令參考.md` 與 `docs/command-reference.md` 第 162 行一帶(`lint_new` 讀工作目錄那份)補「這次推送本身把它放寬時照放寬前判」;第 174 行一帶 `lint_new.gate` 的說明補「也管作弊比對的候選」;第 139 行一帶與 `06-代碼審與推送.md` 的 `lint-waive` 說明補理由門檻、`origin`、`--list`/`--ack`。回退時這幾處一起還原。

### 三、Semgrep 自比規則

- 自比規則的樣式(2026-11-02 用 Semgrep 1.183.0 逐條實跑,再合成一條規則實跑,`--strict` 沒有錯誤,正常的 `assertThat(f()).isEqualTo(3)` 不報):
  - Kotlin:既有的 `assertEquals($X, $X, ...)`,加 `assertThat($X).isEqualTo($X)`、`Truth.assertThat($X).isEqualTo($X)`、`assertWithMessage(...).that($X).isEqualTo($X)`、`assertThat($X, equalTo($X))`。Hamcrest 的 `is` 在 Kotlin 是保留字(要寫成反引號),`assertThat($X, is($X))` 在 Kotlin 不解析錯也抓不到,不加。
  - Java:既有的兩條,加上同樣四條,再加 `assertThat($X, is($X))`。
  - 實作時再加(2026-11-02 實跑):上面每一種另加一條帶任意類別前綴的 `$Q.` 版(`$Q.assertEquals($X, $X, ...)`、`$Q.assertThat($X).isEqualTo($X)`、`$Q.assertThat($X, equalTo($X))`,Java 另加 `$Q.assertThat($X, is($X))`)——不帶前綴的樣式抓不到 `Assert.assertEquals(x, x)`、`MatcherAssert.assertThat(x, equalTo(x))`;`Truth.assertThat` 那條被 `$Q.` 版涵蓋,不另列。
- `$X` 是有副作用的呼叫(`next()` 對 `next()`)會誤報,候選本來就要人裁。改了 `test_quality_semgrep.py` 要重算配套指紋表裡它那一格。
- CI 與這台機器的預設環境都沒有 Semgrep,現有掃描測試用假的 Semgrep 執行檔(只驗介面,不判樣式);這幾條規則的真實效果靠考場實跑留證(S17)。
- 改了配套指紋與 Semgrep 的發現轉換,觸發 `Verification/測試品質第四輪修補驗證` 的重驗條件(「bundle digest 或 Semgrep finding 轉換時」):實作後重跑收證工具掃描的測試(`scripts/test_test_quality_scan.py`,含 Semgrep 熱路徑)與 S17 的實跑,結果記在這份計劃的驗證紀錄,並在那篇的正文補一行「2026-11 這次改動後已重跑,見 <新驗證紀錄>」。

### 四、標準改寫(`skills/lumos-project-notes/commands/test-quality-standard.md`)

- 〈開發時〉加「讓 AI 寫測試」一段:先開一個看不到實作本體的乾淨代理,只給需求、方法簽名與公開介面,產出「輸入→預期」答案表並提交,之後才讓 AI 讀實作、寫測試程式;新測試在現有程式上紅了,先對照需求來源判斷是程式錯還是測試錯,不准把預期值改成程式目前的輸出;AI 發現需求或測試互相矛盾時,停下回報給人,不自己挑一邊;用 AI 審預期值時不給它實作本體。附研讀出處,並寫明「警告語沒用」只在 gpt-4o-mini 上測過、「不給實作」的效果在 Kotlin 上還沒人量過(見〈第二批〉)。
- 新增一個二級標題 `## 推送前的防竄改檢查`,放在 `## 審查時` 之後、`## 工具接入` 之前(不夾進 `### C#、Android、iOS 的原生收證接入` 與 `### Android 本機單元測試的驗收標準` 之間,`t_test_quality_standard_android_unit_section` 釘那兩節相鄰):比對工具抓什麼、抓不到什麼(做法一那份清單)、怎麼放行(理由寫「為什麼這個改動是需求要的」)、AI 放的要人看過、放行檔要提交;升級說明:觸發只看路徑與副檔名,任何 Kotlin/Java 專案與截圖檔都會跑,不想擋的專案設 `lint_new.gate` 為 warn 或 off(提交後從下一次推送起生效,同一次推送照放寬前判)。`commands/03-寫回圖譜.md` 的〈實作測試品質〉末段導覽句補一句指到這一節與「讓 AI 寫測試」那段。
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
  - 改寫時保住既有測試釘的字串與結構:`t_test_quality_standard_android_unit_section`(兩節相鄰、三段粗體依序、關鍵詞)、`t_test_quality_standard_android_room_section`、網頁前端那節的測試、`t_test_quality_standard_android_drill_lessons`、`t_test_quality_drill_cli_cases_present`。
  - 來源清單補研讀報告與新引用的官方頁。

### 五、上一輪延後的六條

六條是 [[Issues/收證歸因第三輪留下的小問題]] 的症狀 1–6(收證工具「認得 Truth 與裝置字串比較」那次代碼審跑滿三輪時延後的 minor)。

- 第一條:只補測試、不改判定,在 `scripts/test_test_quality_cli.py` 各加一支放寬就紅的測試:堆疊行的縮排、第一行去空白、Assert 片語前的字界、`fail|assert` 的限定、「第一行訊息自己含 `at org.junit.Assert.fail(` 又接一般堆疊時從第一個堆疊行起算」。每支先寫前置斷言證明那個樣本真的走到被測的那條分支(`Systems/測試假綠形態` 的規矩)。
- 第二條:**不改判定**,改成照實記錄的已知取捨。r1 設計審實測,原本想的「改看報告尾端連續的堆疊區塊」會把現有一筆合法案例(訊息自帶 `Caused by:` 緊貼真實堆疊)判錯,也認不得真機輸出的 `... 27 trimmed` 截斷行;訊息裡的堆疊樣字串與真正的 `Caused by:` 在文字上分不出來,往拒收的方向錯是比較安全的那一邊。Issue 那條改寫成這個結論,標準補那一句(見做法四)。
- 第三條:安全證據閘補一支「裝置文字(沒有型別欄)的字串比較故障收據算抓到錯」的測試,測試輔助加一種沒有型別欄的失敗狀態。
- 第四到六條:錯字、舊註解、說明檔的層數與 WHY 用詞、三處承認句補回頭條件。順手清掉那篇 Issue 開頭空的重複標題。
- 這次不改 `scripts/test_quality.py`,掛在它身上的三條回頭條件(2026-11-08 到期)不受這份計劃觸發,照它們原本的時程處理。

### 六、考場實跑與誤報量測

- 考場本機分支上,每條規則各做一個壞改動提交(例如給測試加 `@Ignore`、刪一支測試、把強斷言改弱、把實際值換成常值、改預期值(單行、跨行、字串各一)、加沒斷言的測試、加 try/catch 沒 `fail()`、build 檔加 `ignoreFailures = true`(Kotlin 與 Groovy 各一)、加一個 CI 檔 `-x test`(含續行;這三種在代碼審 r4 縮範圍後不再列,留作第二批的對照)、調大逾時、重錄一張基準圖、正式程式碼偵測 robolectric、在同一次推送把閘設成 off),逐一跑比對工具,記哪條抓到;再做幾個正常改動當對照(新增有斷言的測試、本體不變只改測試名、把測試原樣搬到另一支檔、整檔重新縮排、改正式程式碼),不應出候選。
- 拿考場 develop 的真實歷史(唯讀,不動 develop),對有改到測試、建置或 CI 檔的非合併提交逐一跑比對工具(合併提交跟第一個父提交比會把另一條分支的改動算進來,不算);每條候選人工裁成三類:作弊樣的改動、合理改動(例如把幾支測試重寫成整張表逐項比對)、規則判錯;規則判錯的比例寫進驗證紀錄,判錯多的規則當輪收窄。草稿跑過兩次:第一版 192 個非合併提交、38 條候選;第二輪折入後(字串常值看得到、改名一對一)44 條,其中「測試被刪」26 條、「預期值被改」14 條;另有 1 個提交是 repo 的第一個提交、沒有上一版可比(真推送時那種情況走空樹起點)。正式版實跑(2026-11-02)涵蓋全部 776 個非合併提交(第一個提交跟空樹比):44 條、0 個錯誤,裁定與規則判錯率見 [[Verification/2026-11-02_Android測試防竄改檢查實跑]]。公開卷證裡考場的檔名與測試名換代稱。
- Semgrep 在考場的測試目錄實跑一次自比規則(上一輪沒裝,沒跑到);跑過就把上一份計劃那行「Kotlin 靜態掃描這次沒跑」的回頭條件標成已結案。
- 卷證照上一輪的做法:公開 repo 只放去識別化摘要(`governance/eval/results/android-test-guard-drill-20261102/`(新增)),完整卷證留在考場本機分支。
- 去識別化範圍照使用者 2026-11-01 明列的:考場的套件名、類別名、測試名與本機路徑不進公開 repo(專案名可以寫)。考場的短提交編號與本機分支名不再寫進新的公開筆記、標準與評測摘要;代碼審與設計審的卷證(凍結審材、席報告、設計審快照)保留當時的寫法——那些檔的指紋已寫進治理帳,改一個字處置閘就判不過,短編號只在考場本機解得開、不含業務內容(代碼審 r2 資安、合約兩席點名,取捨照實報給使用者)。

## 第二批(另開計劃,這批推上去之後接著做)

- 建置檔與 CI 的作弊比對(原條款 S7、S8,代碼審 r4 後移出這一批):四輪代碼審裡這兩類的 major 佔大宗,用正規式猜 Gradle DSL 與 shell 的寫法,每輪都被新寫法打穿(字串模板的任務名、一行開兩個區塊、鏈結換行、路徑形式的 gradle、病態長行的回溯)。另開計劃時先做最小實驗比較別的做法(例如讀 Gradle 的任務圖或 `--dry-run` 的實際任務清單、只認少數固定寫法加人工放行),再寫條款。原條款留在這裡當起點:
  - 建置檔(原 S7):當建置檔新增 `ignoreFailures = true`、Groovy 的 `ignoreFailures true`、`failOnPassedAfterRetry.set(false)`、`excludeTestsMatching`、`isFailOnNoMatchingTests = false`、`isReturnDefaultValues = true`、`test { … }` 或 `withType<Test>` 區塊裡的 `enabled = false`(跨行、外層區塊裡夾著已關閉的內層區塊也算)、拿掉或註解掉 `dependsOn("test")`、或開重試外掛卻沒有任何建置檔設 `failOnPassedAfterRetry` 為 true 時,應列 `tq/build-config`;點號寫法 `tasks.test.ignoreFailures = true`、重試區塊或 `subprojects { … }` 裡的 `ignoreFailures`、`getByName("testDebugUnitTest")`、findByName、`tasks[…]`、getByPath、`it.name ==`、`withType<Test>` 裡巢狀的區塊、換行的 `tasks.matching {` … `}.configureEach {` 裡的 `enabled = false`,同一行帶 jacoco 字樣的 `tasks.test { ignoreFailures = true; … }`、測試區塊新增 `excludeTags` 也列;照標準開重試(`.set(true)` 或 `= true`)、依賴宣告的 `exclude(group = …)`、JaCoCo 報表的 `exclude: ['**/*Test*.*']` 與 Kotlin 寫法 `exclude("**/*Test*.*")`、`fileTree` 的 exclude、detekt(含 `configure<DetektExtension>`、內層 `reports {}`)與 kotlinter 的 `ignoreFailures`、任務的 `dependsOn("testX")` 不列;`failOnPassedAfterRetry = true` 只寫在行註解或區塊註解裡不算設定。
  - CI(原 S8):當 CI 檔有這幾種改動時,比對工具應列 `tq/ci-config`:呼叫 Gradle 的指令新增 `-x test`(含反斜線續行、Gradle 官方 Action 的 `arguments:`)或行尾 `|| true`、含 Gradle 呼叫的步驟或工作(GitHub 工作層級、GitLab 的 job)加 `continue-on-error: true` 或 `allow_failure: true`、刪掉呼叫 Gradle 測試任務的指令(`-x` 寫在任務前面、`&&` 串接的後半段、子殼層與 `$()` 裡、轉向黏著的任務被拿掉也算)、新增 `-xtest`、`--exclude-task=test`、`|| exit 0`、`|| echo …`;`pytest -x tests/`、`mkdir -p a || true`、不含 Gradle 呼叫的區塊加 `continue-on-error: true`、加 `-x lint`、拿掉 `--tests` 篩選或 `-PtestMode` 這類參數、檔名 `build.gradle` 後面接 `|| echo`(那不是在叫 Gradle)不列;網址後面接的 `|| true` 不被當成註解吞掉。

- 變異測試收證:從改動算出要變異的類別、驗每個模組的 `mutations.xml` 是新的而且變異數大於 0、存活變異列成審查清單;在考場實跑免費 PIT 量協程雜訊比例,再決定要不要建議 arcmutate。
- 穩定性收證:同一個收證命令跑原順序、反轉、打亂順序各一次,全綠才算;先做最小實驗確認 `RobolectricTestRunner` 吃不吃 `@OrderWith`。
- 第二個考場:找一個有 SavedStateHandle 或資料層的類別,實跑 `ViewModelScenario.recreate()`。
- 在 Kotlin 上實測「答案表先行、不給實作」能擋掉多少把錯寫成預期的測試(論文全是 Java 或 Python)。
- 上一份計劃留下的回頭條件(Gradle 把包裝例外記成內層型別、裝置那路打錯類名誰擋、App 啟動的網路流量、收據重收、其他棧重跑)。

REVISIT:2026-12-15 第二批計劃開了沒有;沒開就把上面六項逐項開成計劃或 Issue
REVISIT:2026-12-15 比對工具只認 Kotlin 與 Java;Python(pytest 的 skip、unittest 的 skip)與 Swift、C# 的同類規則還沒有,第二批評估要不要加
REVISIT:2026-12-15 Semgrep 的 Truth 與 Hamcrest 自比規則只在考場實跑過;CI 或預設環境裝了 Semgrep 時補一支真跑的測試
REVISIT:2026-12-15 catch 吞斷言改照 Error Prone 只看結構後,考場歷史沒有 catch 的改動、誤報量沒量到;找一個寫很多預期例外測試的 Kotlin 專案跑真實歷史,數這條規則的誤報
REVISIT:2026-12-15 考場量測裡「只靠自訂斷言輔助」與「新模組範本設定」兩類誤報的比例;多就在第二批加宣告口
REVISIT:2026-12-15 起點是空樹又找不到主線時比對只印不擋(新 repo 第一次推送、CI 淺層 clone);數一次這種推送實際發生幾次(`no-baseline` 帳),多就改成照比對照擋

## 驗收條款

- [S1] 當改動在測試檔新增 `@Ignore`、`@Disabled`、`@SdkSuppress`、`@FlakyTest`、`@Config(sdk`、`Assume.assumeTrue(`、`TruthJUnit.assume()` 或給既有測試函式加上 `expected =`、或把既有 assume 的條件改掉(例如改成 `assumeTrue(false)`,條件寫成多行也算)時,比對工具應各列一條 `tq/skip-added` 候選;整行是註解的、新寫的測試帶 `expected =`、整檔重新縮排後舊的 `@Ignore`、測試原樣搬到另一支檔帶過去的 `@Ignore`、類別層級 `@Ignore` 的檔改名或搬目錄、同一個 assume 只換行重排、只改 assume 同一行的斷言、字串外的空白重排都不列;assume 字串常值裡多或少一個空白(字詞中間、頭尾、逗號後)要列;一行寫完的 assume 不吞進下一支測試、Truth 的 assume 鏈寫在下一行也算同一個敘述;同一支檔加兩個相同的 `@Ignore` 得到兩個不同指紋。 [test:t_tq_guard_skip_added]
- [S2] 當改動前的測試函式在改動後不見、整支測試檔被刪或被改名成非測試檔時,應列 `tq/test-removed`(同一支檔合成一條、列出被刪的函式名);一行寫完的測試被刪、只差字串常值的兄弟測試被刪、兩支一樣的刪兩支只加回一支時要列;本體一字不改只改名、原樣搬到另一支測試檔時不列;巢狀類別裡同名的兩支只刪一支時要列。 [test:t_tq_guard_test_removed]
- [S3] 當同一函式的斷言敘述變少(同一行好幾個中綴斷言照個數算)、強斷言變少(例如 `assertEquals(3, n)` 改成 `assertTrue(n > 0)`)或常值斷言變多(例如 `assertTrue(r.isValid())` 改成 `assertTrue(true)`、`assertEquals(88, calc.total())` 改成 `assertEquals(88, 88)`)、或改成恆真寫法(`assertTrue(1L == 1L)`、`assertFalse(x && false)`)時,應列 `tq/assert-weakened`;斷言數不變、只改被測呼叫的參數、兩行中綴斷言合成一行時不列。 [test:t_tq_guard_assert_weakened]
- [S4] 當同一函式裡一個斷言的預期值被改(單行、跨行、字串、`assertEquals("訊息", 88, total)` 的 88、匯入 kotlin.test 時 `assertEquals("Alice", name, "訊息")` 的 `"Alice"`、容差 `0.01` 改 `0.1`、`State.Loading` 改 `State.Error`、`assertTrue` 改 `assertFalse`、參數裡有 lambda 箭頭或比較運算、連續好幾個斷言一起改)時,應列 `tq/expected-changed`;只改被測呼叫的參數(`total(listOf(40, 48))` 改成 `total(listOf(48, 40))`)、只改訊息字串、改被測呼叫名、中間插一條斷言時不列。 [test:t_tq_guard_expected_changed]
- [S5] 當新增或本體有變的測試函式沒有任何斷言字時,應列 `tq/no-assertion`;用 Truth、Turbine、MockK `verify`、Espresso `.check(`、Kotest `shouldBe`、`captureRoboImage`、Kotlin 的 `assert(`、`thrown.expect(`、`@Test(expected = …)` 的測試,運算式本體 `= runTest { … }`、`= runTest(d) { … }`、`=` 換行接 `runTest {` 裡有斷言的測試,反引號函式名的測試不列;本體沒變的舊測試不列。 [test:t_tq_guard_no_assertion]
- [S6] 當 try 區塊沒有 `fail(`/`assertThrows`/`assertFailsWith` 而 catch 區塊有斷言字(含 Kotest 的 should… 與 `check(`、`require(`)或是空的、或 `runCatching { … }` 裡有斷言而後面沒接 `.getOrThrow()` 時,應列 `tq/catch-no-fail`;try 裡有斷言(含結尾的 `fail(`,它丟的也是 AssertionError,含 Kotest 斷言)而 catch 接得住 AssertionError(型別名字以 Error、Failure 結尾或是 Throwable,含 `ComparisonFailure`、`MultipleFailuresError`)、catch 不重丟時也要列(try 側的斷言同樣把 should 開頭的字寬判進去),不看 catch 裡寫了什麼檢查(照 Error Prone 的 AssertionFailureIgnored;catch 裡用 `shouldBeInstanceOf`、`assertTrue(e is X)` 真的檢查型別的寫法也列,附理由放行或改用 assertThrows);catch 裡有 `fail(`、try 結尾有 `fail(` 而 catch 接的是特定例外、catch 把例外重新丟出、`runCatching { … }.getOrThrow()` 時不列;catch 型別只看括號裡的型別字(catch 本體裡出現 `Error` 不算);catch 接 `IOException` 這類一般例外不列;catch 裡把例外存成 `val throwable = e` 不算重丟、呼叫 `failure(e)`、`xfail(` 不算 fail。 [test:t_tq_guard_catch_no_fail]
- [S9] 當逾時數字被調大(含寫在 `@Test(timeout = …)` 註記上)、截圖基準圖有變或比對門檻字樣新增時,應列 `tq/timeout-raised` 或 `tq/snapshot-changed`(同一目錄的基準圖合成一條);逾時被調小、路徑任一段是 docs、fastlane、metadata 的圖、測試目錄 `assets/` 底下的圖不列。 [test:t_tq_guard_timeout_and_snapshot]
- [S10] 當正式程式檔新增 `"robolectric"` 或 `Class.forName("org.junit…")` 時,應列 `tq/test-env-sniff`;同樣的字出現在測試檔、正式程式只用 `Build.FINGERPRINT` 時不列。 [test:t_tq_guard_test_env_sniff]
- [S11] 當執行 `lumos test-guard --diff` 時,沒有候選應回 0、有候選回 1、不是 git 專案回 0 並說明、參數錯或終點解不出來回 2;`--json` 每條候選有規則代號、檔案、行號、原因、該確認什麼、指紋;上下文位移與整檔重新縮排後指紋不變;檔案加 `-diff` 的 `.gitattributes` 照樣抓得到;檔名不是 UTF-8 列 `tq/unreadable`、內容含 NUL 列 `tq/unparsable`、超過單檔上限列 `tq/too-large`,測試檔有一行超過 2 萬字也列(其餘照比,同檔加的跳過照樣列;正式程式檔不套這道),其他檔照比;合過主線之後推送,主線上刪掉的測試不算進來,本機 main 上還沒推出去的提交照樣算進來(分岔點優先取遠端主線);接近 6 萬行、改約兩千處的測試檔,「`@A` 換行 `val x = 1`」重複 5 萬次的檔,3000 層巢狀的斷言,與一次改 300 支檔,以及同一支函式 8 萬個 assume、5000 層巢狀 try,都應在 30 秒內比完;30 行沒收尾的泛型 10 秒內、250 行 5 秒內;2 萬層巢狀類別 5 秒內、記憶體峰值 200 MB 內,每層都有一支測試時 10 秒內、300 MB 內、每把函式鍵不超過 400 字;1 萬 6 千個 `catch(` 的右括號擠在最後、1800 個類別宣告後接 240 萬字空白、40 行各 3990 個沒收尾的 `fun <` 各 3 秒內,1 萬 2 千層巢狀的 catch 型別括號 3 秒內,二十種觸發字各自重複的輸入加到 4 倍時耗時不超過 8 倍(照 Python 官方 timeit 的建議量 5 次取最小、量行程 CPU 時間、量的時候關垃圾回收,機器忙時不誤紅);兩個頂層類別底下最內層 100 字相同的深鏈,函式鍵靠摘要裡的雜湊分開;建置檔與 CI 檔改了不出候選(這一批不比);`test-guard` 的說明與 skill 參考頁不宣稱比對建置檔或 CI,太大的訊息分得出整支沒比與只有超長行沒比(整支超過上限的那條另附「這支整支沒比對」)。 [test:t_tq_guard_cli_contract]
- [S12] 當推送的改動有作弊候選時,新增告警閘應把它們算進新增告警並擋下(設定是 block 時),即使專案沒宣告任何檢查工具;`lumos lint-waive <指紋> --note` 放行後同一條不再擋;改動沒碰到三類檔時不跑比對;`tq/` 候選最多印 50 條、超過時印列出全部的指令;放行檔讀不了而有候選時擋下並說先修放行檔,不印放行指令、不記自動放行。 [test:t_lint_new_includes_test_guard]
- [S13] 當比對工具丟出非預期例外或超過截止時間時,新增告警閘應記成沒跑完並擋下(不走 fail-open),擋下訊息寫「作弊比對沒跑完」而不是時間預算;起點是空樹而找不到主線分岔點時只印不擋並寫一筆 `no-baseline` 帳;git 讀不出改動的內容(逾時或失敗)也記成沒跑完,不列成可放行的 `tq/unreadable`;`LUMOS_SKIP_LINT_NEW` 只認 1,設成 0 或 false 照常判;這幾筆帳由 `_codeloop_lint_new_step` 寫,判定函式只回傳;自動放行的另外三個出口(依賴宣告壞掉、放行檔壞掉、git 算不出改動清單)各寫原因。 [test:t_lint_new_test_guard_failure_blocks]
- [S14] 當閘的設定是 warn、off、`LUMOS_SKIP_LINT_NEW`,或這次範圍把 `lint_new.gate` 放寬時,新增告警閘應這樣處理:warn 逐條印出新增告警、每行以「提醒:」開頭、小結寫「只報不擋」,有比對候選時寫一筆 `warned` 帳;off 或環境變數跳過時比對照樣在背後跑,有候選或比對出錯才各寫一筆 `skipped`/`skipped-env` 治理帳、都沒有不寫;範圍本身把它放寬(從 git 讀起點與終點兩版比)時這次照起點的值判、印提醒並寫一筆 `relax-deferred` 帳;只在工作目錄改、沒提交時照工作目錄的值(既有行為,`t_lint_gate_modes` 照綠)。 [test:t_lint_new_warn_off_and_relax]
- [S15] 當執行 `lint-waive` 時,理由少於 10 個字或沒有實字應被拒;終端有人答 y 才記 `origin: human`,答 n 不放行、回 1,沒有互動終端、逾時或讀不到回答記 `origin: ai`;`by` 欄照舊記使用者帳號;`lint-waive --list` 與健檢應列出還沒人看過的 AI 放行;`lint-waive --ack --all` 在沒有互動終端時應拒絕、在互動終端確認後標成看過;沒有 `origin` 欄的舊紀錄(不管 `by` 寫什麼)當人放的;`--list` 印出的理由、檔名、規則欄都不帶控制字元。 [test:t_lint_waive_ai_marking]
- [S16] 當找測試函式時,運算式本體 `= runTest { … }`、`= runTest(d) { … }`、`=` 換行接 `runTest {` 應配到對應的右大括號、反引號函式名(含空白與括號)應被找到並從原文取得完整名稱、「`@A` 換行 `val x = 1`」重複 5 萬次的檔應在 5 秒內切完;Room 守衛的 DAO 方法擷取除了 `= db.withTransaction { … }` 這類運算式本體改成整個區塊之外不變,`_rg_split_args` 預設照舊把 `<>` 當括號;`_strip_c_comments` 的既有呼叫輸出不變;比對工具的類別路徑在父型別換行時接得上(行尾逗號或冒號後接長註解、行尾空白、空行、註解行,CRLF 換行,行尾是 FF、VT、全形空白),測試宣告的泛型一層巢狀(`fun <T : List<Int>> t()`)找得到名字,`buildSrc/`、`build-logic/` 底下的測試仍算測試檔。 [test:t_rg_methods_expression_body_and_backtick]
- [S17] 當在考場用 Semgrep 1.183.0 對含做法三那幾種自比寫法的 Kotlin 與 Java 測試檔跑 `lumos test-quality scan --semgrep` 時,每一種都應列成候選、`assertThat(f()).isEqualTo(3)` 不列,結果記在驗證紀錄;收證工具掃描的測試照樣全綠。 [manual:看驗證紀錄的 Semgrep 實跑輸出與掃描測試結果]
- [S18] 當讀測試品質標準時,應寫到:答案表先行而且寫的人看不到實作、現有程式上紅了不准改預期值、矛盾時停下回報、推送前的防竄改檢查(它自己一個二級標題)與它抓不到的與升級說明、AI 放的放行要人看過、重試後才過不算(`failOnPassedAfterRetry`)、原順序反轉與打亂順序與次數、Orchestrator 與 `clearPackageData`、`ViewModelScenario.recreate()`、範本測試、變異測試只變異改到的類別與每模組要有新報告、arcmutate 的事實、屬性測試的審法與不採用 jqwik、不採用的壞味道,而且連到研讀報告與這份計劃;`03-寫回圖譜.md` 的〈實作測試品質〉有一句指到新節。 [test:t_test_quality_standard_ai_test_guard]
- [S19] 當收證工具裝置那路判定的縮排、第一行去空白、字界、`fail|assert` 限定或「從第一個堆疊行起算」任一條被放寬時,收證工具的測試應翻紅。 [test:t_test_quality_cli]
- [S20] 當安全證據閘的故障敏感度那條路核對沒有型別欄的裝置字串比較故障收據時,應算抓到錯。 [test:t_secev_tq_device_text_fault_counts_like_assertion]
- [S21] 當在考場對這一批每條規則的壞改動跑比對工具時(建置檔與 CI 的壞改動在代碼審 r4 縮範圍後不列,留作第二批的對照),每條都應被對應規則抓到;正常改動的對照組不應出候選;結果記在驗證紀錄。 [manual:看驗證紀錄的考場對照表與公開卷證]
- [S22] 當拿考場 develop 的真實歷史跑比對工具時,每條候選應有人工裁定(作弊樣、合理改動、規則判錯)與規則判錯率,判錯多的規則有收窄紀錄。 [manual:看驗證紀錄的誤報量測表]
- [S23] 當新頂層指令 `lumos test-guard` 上線時,說明表、指令總數(兩份文件)、子命令全覽與指令索引都應提到它。 [test:t_test_guard_registered]

每條 `[test:]` 的測試照 `Systems/測試假綠形態` 的規矩:先寫前置斷言證明樣本真的走到被測的那條路(例如 S14 先證明 off 時比對真的跑了、S19 先證明樣本真的走到那條判定分支),再斷言結果;實作時每道判斷逐條改壞一次,確認對應的檢查各自會紅。

## 回退

- 工具鏈:還原這份計劃、比對工具與它的測試、新增告警閘那幾段(含訊息與留帳)、`lint-waive` 的理由門檻與 `origin` 標記、`_rg_methods`/`_rg_method_end`/`_rg_annotations`/`_rg_split_args`/`_strip_c_comments` 的擴充、Semgrep 規則與配套指紋表、標準改寫與 `03-寫回圖譜.md` 的導覽句、`docs/指令參考.md`/`docs/command-reference.md`/`06-代碼審與推送.md`/`INDEX.md`/`ARCHITECTURE.md`/`reference.md` 的同步、六條小修、驗證紀錄與卷證的提交(同一個提交,一起還原)。還原後推送前不再看作弊候選;已寫進放行檔的 `tq/` 放行與 `origin` 欄留著無害(指紋不再出現,舊版不讀 `origin`)。Room 守衛對運算式本體 DAO 方法的範圍回到只到第一行。
- 只想關掉作弊比對、不還原程式:專案在 `.lumos/config.json` 把 `lint_new.gate` 設成 `warn`(只報不擋、印出)或 `off`(連原本的新增告警一起關),提交後從下一次推送起生效;單次推送用 `LUMOS_SKIP_LINT_NEW=1`。off 與環境變數跳過時有候選或比對出錯才留帳。
- 考場:演練提交只在本機分支;刪分支前先打包 `drill-evidence/`。

## 實務隱患

- 守衛面:新增告警閘多了一個來源,原本「沒宣告檢查工具就不判」的 Kotlin/Java 專案(不只 Android,JVM 後端也算),只要改到測試檔或正式程式檔就可能被擋(建置檔與 CI 這一批不比),截圖基準圖不分技術棧;誤報的出口是放行附理由(AI 放的事後要人看過),整道關掉是設定 off 或環境變數 `LUMOS_SKIP_LINT_NEW=1`(有候選或比對出錯時留帳);比對工具自己出錯時擋下而不是放行,壞的是推送體驗、不是靜默漏判;單一怪檔落到可放行的候選,不會卡住整道。消費專案要等 `lumos update` 才拿到。
- 守衛面:warn 模式改成會印、放行檔讀不了而有比對候選時擋下、同一次推送放寬閘不算數、`lint-waive` 理由門檻與終端確認——這幾處讓既有新增告警閘比現在嚴,原本靠 warn 靜默、壞放行檔、兩字理由放過去的會開始被看到或被擋;終端確認在沒有互動終端的流程(AI、CI)不會等,只記成 AI 放的。
- 守衛面:Room 守衛共用的方法擷取改了運算式本體的範圍,`= db.withTransaction { … }` 這類 DAO 方法的改動範圍變大,Room 守衛判「改到的 DAO 方法」可能比以前多抓到幾支(修正方向)。
- 效能:比對工具每端兩個 git 行程批次讀改到的檔、剝字串與配對各一趟,跟改動大小成正比;S11、S16 釘住大檔、病態註記檔、深巢狀與 300 支檔。新增告警閘原本有 300 秒預算;比對每支檔開始前看一次截止時間,超過就記成沒跑完、擋;比對花掉的時間不算進檢查命令的預算(代碼審 r1 改定,最壞整道閘跑到預算的兩倍)。一次推送最多讀 200 MB;測試檔超過 2 萬字的行不比對。
- 資安:比對工具讀的是 AI 可控的檔案內容;病態輸入(極深的括號巢狀、沒收尾的字串、註記後一直沒有括號、大量換行、NUL、非 UTF-8 檔名)只會讓那支檔列成 `tq/unparsable`、`tq/too-large` 或 `tq/unreadable`,不會讓判讀變成平方級或丟例外放行(S11、S13);測試檔的超長行在外層抹掉。
- 併發:放行檔寫入沿用既有的上鎖;治理帳沿用既有的追加寫法,新增的 `warned`、`skipped`、`skipped-env`、`relax-deferred` 跟其他閘一樣寫進要提交的 `docs/.governance-log.jsonl`(不在只留本機的名單裡),warn 模式有候選的推送會多一行。
- 已排除:金流:不碰付款;考場只在本機分支改測試與建置檔,不跑 App。
- 已排除:對外送出:比對工具只讀 git,不連網;研讀報告是公開論文的摘要,去掉本機路徑才放進公開 repo。
- 已排除:不可逆:考場提交不推不併;工具鏈改動走一般提交,可還原。

## 審計修正紀錄

- r1(2026-11-02,三席加架構對齊,全 sonnet 同門):58 條/blocking 35/設計的方向對,但比對工具該放在主程式重用既有的辨識與讀檔函式(不是收證工具配套)、判法要改成兩端整檔的次數差(不靠 git diff 的新增行)、指紋要綁函式與第幾次出現、比對出錯與 warn 與關閘三個出口都要補、AI 放的放行要有人看;裝置歸因「尾端堆疊區塊」的改法被實測推翻,改成照實記錄的取捨。全部折入。卷證 `governance/review-reports/Android測試防竄改檢查/`。
  - 例:測試檔整檔重新縮排(舊有一個 `@Ignore`)→ 改前:那行出現在 diff 新增側、列成 `tq/skip-added`;改後:兩端各一次、次數差 0、不列。
  - 例:`FooTest.kt` 改名成 `FooTest.kt.disabled` → 改前:改動後路徑不是 `.kt`、整支略過;改後:改名前是測試檔、裡面的函式全列 `tq/test-removed`。
  - 新增機制(不加它的最小解為什麼不夠):`lint-waive` 的 AI 標記——不加的話,推送者(AI)照抄擋下訊息裡的放行指令放行自己的作弊,事後也沒有任何痕跡分得出是誰放的;加了之後仍然推得出去,補的是「人一定看得到 AI 放了什麼」,不是阻擋。判法照 Android 端到端驗收 `_e2e_waive_cmd`(r2 起人或 AI 記在新開的 `origin` 欄,因為既有放行檔的 `by` 欄已經存帳號),`--list`/`--ack` 與 `acked` 三欄照它的形狀,套到另一本放行檔。
  - 一支綁定測試涵蓋好幾種行為(S7、S12 等)不拆:每種行為在那支測試裡各有一條會單獨翻紅的檢查,實作時逐條改壞一次確認各自會紅;拆成十幾支只是把同一個建置輔助複製很多份。
  - 折入後派鏡像核對(sonnet):漏折 13、鏡像段沒跟上 4、新洞 5,全部再折入。
- r2(2026-11-02,三席加架構對齊,全 sonnet 同門):58 條/blocking 22/r1 的方向被確認(真的重用了既有函式),但重用的那幾支有坑:剝字串會清掉字串預期值與反引號名、方法擷取有兩個平方級來源、運算式本體只認一種寫法、參數切法把 `>` 當括號;「本體相同算改名」太鬆;實際值換成常值四條規則都漏;CI 規則漏續行、官方 Action、工作層級;`tq/gate-config`(r1 時提過、r2 拿掉的規則)是專案裡第三種「同一次推送放寬不算數」的做法,改成照既有的「從可信版本讀」;舊放行的 `by` 欄本來就有值,AI 標記改開 `origin` 欄;warn 的輸出會被推送掛鉤濾掉;新頂層指令的同步點與既有測試、文件都沒列。全部折入;比對規則先在會談暫存區的草稿實作並跑測試(S1–S10、S16 與 S11 的壓力、檔名、NUL 項全綠,含 r2 新增的 17 種情境;S11 的退出碼、`--json`、`-diff` 與 S12–S15 的閘整合還沒實作)再寫進計劃。折入後派鏡像核對(sonnet):漏折 5、鏡像段沒跟上 8、計劃與草稿對不上 12(其中草稿真錯 6 處:同名多載給號是平方級、`named("test")` 區塊判不到、`Assert.fail` 不算斷言、kotlin.test 三參數容差、`buildSrc` 底下的測試檔、yml 引號裡的 `#`),全部再折入並各補一支先紅後綠的草稿測試。卷證同目錄 r2-*。
  - 例:`@Test fun b() { assertEquals(2, g()) }`(一行寫完)被刪 → 改前:本體是空字串,跟任何空本體都「相同」,判成改名不列;改後:本體簽名是參數列之後的原文 `{assertEquals(2,g())}`,沒有新出現的同簽名函式,列 `tq/test-removed`。
  - 例:CI 裡 `./gradlew build \` 換行 `-x test` → 改前:第二行沒有 `gradlew`、不列;改後:續行併進同一行、列 `tq/ci-config`。
  - 新增機制(不加它的最小解為什麼不夠):`relax-deferred`(範圍本身放寬閘時照起點判)——不加的話同一次推送把 `lint_new.gate` 改成 off 就整道關掉;做法照 `_lens_trusted_ref` 的「被推的分支自己改的不算」,只套在「範圍裡真的改了這個鍵」的情況,工作目錄沒提交的改動照舊生效(不破 `t_lint_gate_modes` 與文件)。
