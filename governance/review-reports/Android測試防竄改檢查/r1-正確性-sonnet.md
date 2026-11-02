severity: major

審查對象:r1-snapshot.md(Android測試防竄改檢查_計劃)。我用小 git repo 與 Python 雛形實驗過,也讀了 `scripts/lumos` 和 `scripts/test_quality.py` 對照。表態:這份規則表有多處會判錯,其中幾處讓「該抓的作弊漏掉」,另有幾處讓「正常改動被擋」。

## Findings

**F1 — 〈做法二〉比對工具出錯「擋下」的承諾,對執行期例外不成立(會靜默放行)**
severity: major
blocking: 是(不改,實作者會做出「出錯等於關掉」的守衛,與計劃自己的裁定相反)
引句:「出錯多半是程式錯,放行等於靜默關掉」
- spec 位置:〈做法二〉「載入失敗…擋下」、〈實務隱患〉守衛面「比對工具自己出錯時擋下而不是放行」。
- 問題:只定義了「載入失敗」和「讀不出 git」兩種錯。比對工具執行中丟出的任何例外(括號配對遇到病態輸入、遞迴過深、記憶體),都會落到既有的 `_codeloop_lint_new_step` 的 `except Exception` 然後 fail-open。測試檔寫成能讓解析器丟例外,就能繞過整個比對。
- 佐證:file: `scripts/lumos:67958-67963`,`try: _lint_new_verdict(...) except Exception → _gate_failopen("新增告警閘出例外,這次放行")`。
- 另:放行檔讀不了也走 autopass(file: `scripts/lumos:38863-38866`)。cheater 把 `.lumos/lint-waivers.json` 弄成壞 JSON,整道閘連同比對一起 fail-open。spec 〈做法二〉把這條列為「維持既有」,理由是「不能把舊放行全部當不存在」。但這條理由只支持「別整批擋人」,不支持「連候選都不判」。候選可以照判,只是放行視為空。

**F2 — warn 出口是靜默的:「只報不擋」實際一條都不報,也不記帳**
severity: major
blocking: 是
引句:「目前這兩個出口不留痕,而它們是作弊比對擋錯人時的出口」
- spec 位置:〈做法二〉擋下訊息與出口、〈回退〉「`lint_new.gate` 設成 `warn`(只報不擋)」、S9。
- 問題:
  - warn 模式下 `blocked` 為 False,候選只存在 `out["new"]`,沒有任何地方印出來。
  - 放行路徑的小結(`_cl_say_ok_extras`)對 status="warn" 落到預設字串「沒有新增的告警」。有候選時印出的卻是「沒有新增的告警(跑了 0 條檢查命令)」。
  - spec 〈現況〉說三個出口(off、warn、環境變數)都不記帳,〈做法二〉只補 off 與環境變數,warn 仍不記帳。
  - `lint_new.gate` 是從工作目錄讀 `.lumos/config.json`,而 `.lumos/config.json` 不在五類被監看的檔裡。改動這個設定檔,警示整個消失,且沒有任何痕跡。
- 佐證:file: `scripts/lumos:38784-38785` warn 分支;file: `scripts/lumos:68995-68996` `_head` 對未列狀態一律回「沒有新增的告警」;file: `scripts/lumos:38429-38460` 設定從磁碟讀。
- 這與 spec 自己的理由矛盾(見上引句)。

**F3 — 放行機制讓作弊者自己放行,指紋又只綁位置、不綁這次改動**
severity: major
blocking: 是
引句:「指紋 = sha256(規則代號、檔案、身分字串)前 16 碼」
- spec 位置:〈做法一〉指紋定義、身分字串用測試函式名或正規化後的那一行、RETIRE-IF、〈四〉「放行理由要寫為什麼這個改動是需求要的」。
- 問題一(誰能放行):擋下訊息把 `lumos lint-waive <指紋> --rule … --file … --note "<為什麼放行>"` 整行印出來給人照抄。`cmd_lint_waive` 只檢查 `--note` 非空,沒有最小字數,也沒有人或 AI 的標記。要防的對象就是 AI,它會直接照抄。同庫的 Android 端到端驗收閘已經做到「至少 10 字、無互動終端標成 AI 放行並一直列到人看過」,這裡沒有。
- 問題二(指紋綁位置):
  - `tq/skip-added` 的身分是「正規化後那一行」,不含函式名。一次 `@Ignore` 放行後,同檔以後每個 `@Ignore` 都已放行。
  - 同一個 push 在同檔加兩個相同 `@Ignore`,指紋相同,一條放行兩條都過。既有閘用 Counter 算次數。節點 pitfalls-lint-adapter 寫「指紋算次數不算有無」,tq 沒照做。
  - `tq/assert-weakened`、`tq/no-assertion`、`tq/catch-no-fail` 的身分是函式名。某測試因合理重構放行一次後,之後把它的斷言全拿掉,指紋不變,免審。
  - `tq/expected-changed` 若身分字串是「換成佔位後的行」(spec 沒講清楚,標 ⚠),同一行之後再改任何常值,指紋也不變。
- 佐證:file: `scripts/lumos:37856-37859`(只驗非空,`who` 取 `$USER`);file: `scripts/lumos:42069` `_e2e_waive_hint`(對照的較嚴做法);file: `scripts/lumos:38660-38676` 既有閘用 Counter 判次數。

**F4 — `tq/assert-weakened` 的弱斷言名單太窄,最常見的弱化寫法漏掉**
severity: major
blocking: 是
引句:「或強斷言變少而弱斷言變多」
- spec 位置:〈做法一〉規則表 `tq/assert-weakened`、「弱斷言」名單、S3。
- 輸入:`assertEquals(3, n)` 改成 `assertTrue(n > 0)`,或改成 `assertThat(n).isAtLeast(0)`、`assertThat(n, notNullValue())`、`assertThat(list).hasSize(1)`。
- 判法:
  - 斷言字總數不變。
  - 強斷言 -1,但弱斷言沒增加,因為弱名單只有 `assertTrue(true)`、`assertFalse(false)`、`assertNotNull`、`isNotNull` 這類。
  - 條件二「強斷言變少而弱斷言變多」不成立,沒有候選。
- 同類:`assertTrue`/`assertFalse` 互換、`assertNull`→`assertNotNull`(強不變、弱 +1,但字數不變),也不列。這是「讓測試變綠」最直接的弱化。
- 建議的判準方向(給實作者):改成「強斷言變少、且強斷言以外的斷言字沒有補回等量」就列。

**F5 — `tq/expected-changed` 對「斷言換行」與「預期值非數字/字串」都漏掉**
severity: major
blocking: 是
引句:「兩行都有斷言字,把數字、字串、字元常值換成佔位後一樣」
- spec 位置:〈做法一〉規則表 `tq/expected-changed`、預期值位置、S4。
- 輸入 A(換行):格式化器(ktlint、Android Studio 預設)常把長斷言折成
  ```
  assertEquals(
      88,
      total
  )
  ```
  改的是 `88,` 這一行,該行不含斷言字。規則要求「兩行都有斷言字」,所以整個不列。「逐行比對」無法處理。
- 輸入 B(提升成變數):`val expected = 88; assertEquals(expected, total)`,把 88 改成 90。改動行沒有斷言字,不列。
- 輸入 C(非數字/字串常值):`assertEquals(State.Loading, s)` 改成 `State.Error`、`assertEquals(true, f)` 改成 `false`、`assertEquals(listOf(1,2), x)` 改成 `listOf(1,2,3)`。佔位化後前兩者沒有常值差異,第三者佔位結構不同,都不列。
- 輸入 D(JUnit4 帶訊息):`assertEquals("msg", 88, total)` 的「第一個參數」是訊息字串。改預期值 88→90 不列(漏),改訊息卻列(誤報)。三參數 `assertEquals(exp, act, delta)` 與帶訊息版無法只靠位置區分。
- 輸入 E(⚠ 配對方式):「同一個 diff 區塊一行刪掉、一行新增」若嚴格解讀為恰一刪一增,連續多條斷言同時改值(AI 常見的「一次修好多個預期值」)會全數漏掉。S10 的雛形一次改 1,967 處,所以大概不是嚴格解讀,但 spec 沒寫明,實作者會猜。
- 補強:S4 只測了「改數字」和「只改被測呼叫參數」兩個例,沒有上面任何一個反例。

**F6 — 〈做法五〉第二條的「尾端堆疊區塊」文法,照字面會拒掉現有的合法案例與真機輸出**
severity: major
blocking: 是
引句:「報告尾端連續的堆疊行區塊(每一行都是堆疊行、`Caused by:`、`... N more` 或 `Suppressed:`)」
- spec 位置:〈五〉第二條、S13、〈實務隱患〉守衛面第二點。
- 問題一:區塊成員包含 `Caused by:` 行,Assert 堆疊必須在「區塊裡第一個 `Caused by:` 之前」。訊息自己帶的 `Caused by:` 行若緊貼真實堆疊,會被吃進區塊並成為「第一個」。我用 Python 照字面寫了一個雛形驗過。
  - 輸入:`org.junit.ComparisonFailure: expected:<Request failed[\nCaused by: timeout]> but was:<Request failed[]>\nat org.junit.Assert.assertEquals(Assert.java:115)\nat com.example.SampleTest...`。
  - 結果:判成 False,尾端區塊從 `Caused by: timeout]>…` 那行開始,Assert 堆疊在它之後。
  - 這正是 `test_device_hamcrest_and_caused_by_in_message_are_attributed` 的第二筆(現在判 True),也是這一節宣稱要修的案例。
- 問題二:真機輸出含 Android 的截斷行 `... 27 trimmed`,不在文法裡(只有 `... N more`)。結尾是它的真實失敗文字,由後往前掃第一行就停,區塊為空,合法斷言紅被拒。我實驗:`java.lang.AssertionError\nat org.junit.Assert.fail(...)\n...\nat SampleTest.bareTrue(...)\n... 27 trimmed` → False。這與現行 `own` 切法相比是回歸。
- 補強:spec 的反例清單(尾端區塊沒有 Assert、Caused by 包著、型別名後多字)沒有這兩個正例。
- 佐證:
  - file: `scripts/test_test_quality_cli.py:280-292` 現有正例;
  - file: `scripts/test_test_quality_cli.py:314-335` 現有反例;
  - file: `governance/review-reports/code-收證認得Truth與裝置字串比較/r2-snapshot.patch:703-710` 真機取樣含 `... 27 trimmed` 且堆疊行無縮排;
  - file: `scripts/test_quality.py:138-142` 現行 `own` 判法。

**F7 — 規則表之內矛盾:`tq/test-removed` 對「改測試名」會報,但〈六〉與 S14 把它列為不應出候選的對照**
severity: major
blocking: 是
引句:「新增有斷言的測試、改測試名、把測試搬到另一支檔、改正式程式碼」
- spec 位置:規則表 `tq/test-removed`、〈六〉「再做幾個正常改動當對照…不應出候選」、S14。
- 輸入:同一支檔裡把 `fun testTotal()` 改名成 `fun totalIsCorrect()`。
- 判法:改動前的 `testTotal` 在改動後同檔不存在,其他測試檔也沒有同名函式,規則成立,列一條 `tq/test-removed`。
- 結果:S14 的對照組不可能全綠。實作者要嘛偷偷加「函式本體相似度」(spec 沒寫、也沒給閾值),要嘛 S14 驗收失敗。
- 同類:被改名的函式也不會跟 `assert-weakened`、`expected-changed` 配對(名字不同),改名同時弱化斷言只會看到 test-removed 和新函式的 no-assertion,放行 test-removed 後弱化就沒有任何候選。

**F8 — 「測試函式」的認法與按名字配對,在 Kotlin/Java 常見寫法下配錯**
severity: major
blocking: 是
引句:「Kotlin 認 `fun 名稱(`,Java 認 `void 名稱(`」
- spec 位置:〈名詞〉測試函式、規則表 `tq/test-removed`、`tq/assert-weakened`、`tq/expected-changed`。
- 輸入 A(同名):`@Nested inner class` 或同檔多個 class 裡有同名測試(`returns error`、`initialState`、`setUp` 類名稱)。刪掉其中一個,名字還在另一個 class,不列 `tq/test-removed`;`assert-weakened` 配對到哪一個 class 的同名函式沒有定義。
- 輸入 B(跨檔同名):「搬家不算」只比函式名。刪掉 A 檔的 `testLoad`,同一個改動在 B 檔新增(哪怕是空殼)一個 `testLoad`,不列。名字撞上常見名稱時是意外漏報,也可以故意利用。
- 輸入 C(backtick 名稱):Kotlin 單元測試主流寫法是 `` fun `returns total (with tax)`() ``,名稱含空白與括號。spec 寫「Kotlin 認 `fun 名稱(`」,沒說 backtick。依字面寫的辨識會漏掉(整支檔 0 個測試函式),或被括號配對切歪。
- 輸入 D(⚠ 字元常值):「略過字串與註解裡的括號」沒提 `'{'`、`'"'` 這類字元常值,也沒提 Kotlin 巢狀 `/* /* */ */`。測試格式化或解析器的測試常出現,一個 `'"'` 就會把之後的字串開關顛倒,函式邊界連鎖錯位。
- 輸入 E(無 `@Test` 的舊式測試):`extends TestCase` / `InstrumentationTestCase` 以 `test*` 命名,沒有 `@Test`,整個不被看見,也沒列進「抓不到的」。

**F9 — 檔案分類:把測試檔「改名/搬出編譯範圍」或換成非測試路徑,所有規則都看不到**
severity: major
blocking: 是
引句:「路徑一律用改動後的;改名用 git 的改名偵測對回改動前」
- spec 位置:〈做法一〉檔案分類。
- 輸入 A:`FooTest.kt` 改名成 `FooTest.kt.disabled`(或 `.bak`、搬到 `src/test/disabled/` 這種 Gradle 不編譯的目錄)。
  - 前者:git 回 R100,改動後路徑不是 `.kt`,不屬任何一類,整組略過。`tq/test-removed` 不列。
  - 後者:改動後路徑仍含 `src/test`,檔案內容函式全在,沒有任何候選,但 Gradle 已不跑它。`sourceSets` 的改動也不在 `tq/build-config` 名單。
- 輸入 B(已刪除的檔):「路徑一律用改動後的」對被刪除的檔沒有改動後路徑,spec 沒說用哪一邊。`_lint_new_changed_files` 的既有查詢直接丟掉 D,實作者若沿用就不會看到「整支測試檔被刪」,S2 的後半(整支測試檔被刪)就做不出來。file: `scripts/lumos:38490-38491`(`elif code == "D": i += 2` 不收)。
- 輸入 C(KMP 與官方截圖測試目錄):`src/commonTest`、`src/androidUnitTest`、`src/androidInstrumentedTest`、`src/screenshotTest/…/reference/*.png` 都不在清單,檔名不以 Test 結尾的輔助檔、基準圖歸入「其他」或「正式程式」。
- 輸入 D(反向誤分):main 裡檔名以 `Test` 結尾的正式程式(如 `AbTest.kt`、`SpeedTest.kt`)被歸成測試檔,`tq/test-env-sniff` 對它不判。

**F10 — 建置與 CI 規則只認「新增行」關鍵字,拿掉測試步驟、改任務、跨行寫法都漏**
severity: major
blocking: 是
引句:「同一行有 `test`(不分大小寫)而且有 `enabled = false` 或 `onlyIf { false }`」
- spec 位置:規則表 `tq/build-config`、`tq/ci-config`、S6。
- 輸入 A(刪除/替換):CI 把 `./gradlew testDebugUnitTest` 那步整行刪掉,或換成 `./gradlew assembleDebug`,或加 `if: false`;build 檔拿掉 `check.dependsOn(test)`。刪掉的行不是新增行,新增的 `assembleDebug` 不含 `-x`,全數不列。研讀報告 hacking.md 自己列了「拿掉 check 依賴」,spec 沒收。
- 輸入 B(多行 DSL):
  ```
  tasks.withType<Test>().configureEach {
      enabled = false
  }
  ```
  「同一行有 test 而且有 `enabled = false`」只認單行,`enabled = false` 那行沒有 test 字樣,不列。反向:若 `enabled = false` 比對不分大小寫,`isTestCoverageEnabled = false`、`testCoverageEnabled = false`(正常的 AGP 設定)會誤報(⚠ spec 沒寫大小寫)。
- 輸入 C(Kotlin DSL 的 Property 寫法):`failOnPassedAfterRetry.set(false)` / `.set(true)`。spec 與標準都寫 `failOnPassedAfterRetry = true`。Gradle test-retry 外掛的 Kotlin 範例用 `.set(...)`,所以 `.set(false)` 不列(漏);照標準開重試的 `.set(true)` 不被認為合格(誤報,那條豁免永遠不生效)。⚠ 我沒有取得外掛 README 逐字,屬記憶;`gradle.properties`/`build.gradle` 的 Groovy 無等號寫法 `ignoreFailures true` 同理未定義。
- 輸入 D(檔案範圍):`*.gradle` 腳本外掛(`gradle/test.gradle`、`jacoco.gradle`)、`settings.gradle(.kts)`、`libs.versions.toml` 不在建置檔清單。
- 輸入 E(誤報):`exclude("**/R.class", "**/BuildConfig.*")` 是 JaCoCo 覆蓋率排除的常見寫法,「exclude( 後面含 `**`」會列。

**F11 — `tq/ci-config` 與「碰到五類檔才載入」的範圍:不是 Android 專用,「純 Python 不受影響」不成立**
severity: major
blocking: 是
引句:「沒碰到就不載入、不判,純 Python 這類專案不受影響」
- spec 位置:〈做法二〉、〈做法一〉CI 檔定義、`tq/ci-config`。
- 問題:CI 檔(`.github/workflows/*.yml`)幾乎每個 repo 都有。只要改到它,比對工具就載入並判 `|| true`、`continue-on-error: true`。
  - `|| true` 在 shell 片段裡非常普遍(`mkdir -p x || true`、`git branch ... || true`、`grep … || true`),跟測試無關。
  - 本 repo 自己的 CI 就有:file: `.github/workflows/ci.yml:41,93,159,170,173,241,299`(`|| true`)與 `:289`(`continue-on-error: true`)。
  - 在預設 block 下,任何 Python/Node/iOS 專案改 workflow 都可能被擋,而且比對工具載入失敗還要擋(spec 的新決定),等於 CI 檔一改就多一個全專案的必經關卡。
- 同源問題:規則只看「新增行」,不去掉 base 中本來就有的等價行。縮排調整、搬移、貼註解造成的 `-`/`+` 對會讓「既有的 `|| true`」重新被列為候選。既有閘靠 Counter 的多重集比對避免這件事,節點 pitfalls-lint-adapter 的 PITFALL(搬家被當新增)已記過同款誤報。
  - 連帶:把已有 `@Ignore`/`@SdkSuppress` 的測試搬到另一個檔(對照組「把測試搬到另一支檔」),新檔所有行都是新增行,`tq/skip-added` 對搬過去的既有註記全數報,與對照組「不應出候選」矛盾。

**F12 — 新增行的取得方式沒寫,git 的 `-diff` 屬性就能讓所有行級規則看不到任何新增行**
severity: major
blocking: 是(⚠ 取決於實作者怎麼取新增行,spec 沒定)
引句:「判讀只用逐行比對與括號配對,跟輸入大小成正比」
- spec 位置:〈做法一〉「只看新增行的規則」、「判讀只用逐行比對」、「兩邊都從 git 讀」。
- 問題:若用 `git diff` 輸出取新增行,同次改動加一行 `.gitattributes`(`*.kt -diff`)就會得到「Binary files differ」,零新增行。我實驗過:加了 `@Ignore` 的測試檔在這個屬性下 `git diff -U0` 沒有任何 `+` 行,加 `--text` 才有。
- 本 repo 已有先例:file: `scripts/lumos:58619-58627`(以 `show --no-textconv` 讀原始 blob,明寫 `-diff` 與 NUL 都影響不了);Systems/pitfalls-code-loop 的 r3 記錄也寫過「.gitattributes 標 -diff 或塞 NUL 就沒有刪除行可數」。spec 沒有照辦。
- 若改用兩份完整內容自己做行差集(用 `difflib`),59,003 行且大半被改動時 `SequenceMatcher` 有二次方風險,S10 只釘了「改約兩千處」這種稀疏情況。

**F13 — 規則表的其他誤報/漏報(各自小)**
severity: minor
blocking: 否
引句:「catch 區塊有斷言字或是空的,而 try 區塊沒有 `fail(`、`assertThrows`、`assertFailsWith`」
- `tq/catch-no-fail`(〈做法一〉):`try { foo(); assertEquals(1, r) } catch (e: Exception) { fail("unexpected: $e") }`(預期不丟例外的寫法)。catch 內有 `fail(` 算「有斷言字」,try 沒有 `fail(`,規則成立,但這個測試在例外時會紅,不是永遠綠。反過來 `catch (e: Exception) { println(e) }`、`runCatching { … }` 吞例外的測試不列(catch 非空、無斷言字)。
- `tq/no-assertion`:自訂斷言輔助名稱不是 `assert*`/`verify*`/`expect*`(`checkX`、`ensureX`、`thenX`、`intended(...)`、`thrown.expect(...)`)的測試被報;全檔重新格式化碰到本體就把舊的零斷言測試全算「本體有改」。
- 斷言字計數沒說是否排除註解:把斷言整行註解掉(`// assertEquals(...)`)若註解裡的算數,`assert-weakened` 看不到。⚠ spec 只在「新增行規則」裡寫略過註解。
- `tq/timeout-raised`:`10.seconds`→`1.minutes`(最大數字變小但時間變長)、逾時行整行新增(不是一刪一增)、`30_000`/`30L` 的數字抓法,spec 沒說。
- `tq/snapshot-changed`:`.jpeg` 不在清單;`src/androidTest/assets/*.png`(測試輸入圖)、`phoneScreenshots`/`docs/screenshots/*.png`(商店截圖、README 配圖)會被當基準圖;用 `@ParameterizedTest` 的資料列(`@CsvSource`/`@MethodSource`)刪列、表格驅動測試刪案例,屬於「刪測試」但不列,也沒寫進「抓不到的」。
- `tq/test-env-sniff`:`Build.FINGERPRINT` 在正式程式用來做模擬器/root 偵測很常見。

**F14 — 配套指紋表漏列被修改的 `test_quality_semgrep.py`**
severity: major
blocking: 是
引句:「指紋表(新檔與改了的 `test_quality.py` 都重算)」
- spec 位置:〈做法二〉最後一段「加一支配套檔要同步五處」、〈做法三〉Semgrep 自比規則。
- 問題:同步清單的「配套指紋表」寫「新檔與改了的 `test_quality.py` 都重算」。〈做法三〉改的是 `test_quality_semgrep.py`(規則 `PATTERNS` 在這支檔),它也在指紋表裡。照 spec 字面做,只重算兩個,`test_quality_semgrep.py` 的 sha256 對不上,所有專案的 `test-quality` 都回「配套版本不一致:test_quality_semgrep.py」。這正是這一段想防的失敗。
- 佐證:file: `scripts/lumos:69701`(三支檔都有指紋);file: `scripts/lumos:69734-69744`(逐檔比對);file: `scripts/test_quality_semgrep.py:17-18`(規則寫在這支)。
- 附帶:現行 `_test_quality_load_bundle()` 在每次 `main()` 開頭無條件載入,與〈做法二〉「沒碰到五類檔就不載入、不判」不一致。實作者要嘛改成延遲載入(spec 沒寫),要嘛「載入失敗」是全域狀態。

**F15 — 預算與資源:比對工具超出 300 秒預算時行為沒定義,且每檔一次 git 呼叫**
severity: minor
blocking: 否
引句:「新增告警閘原本有 300 秒預算,比對工具算在同一個預算裡」
- spec 位置:〈實務隱患〉效能。
- 問題:沒寫超過預算時是擋、放行還是記帳。既有閘的 `undone` 分類(預算不足→硬擋)沒有說比對工具要不要走同一條。大型改動(數千支 main 檔改名重構)每檔讀兩版做 too-large 判斷,若逐檔 `git show`,耗時以子行程數線性成長。S10 只釘單檔大小,沒釘檔案數。
- 另:`tq/expected-changed` 一次幾千條時,擋下訊息全印、每條要單獨 `lint-waive`(指紋逐條),沒有整批放行,實際的出口會變成改設定為 warn(又是 F2 的靜默路)。`tq/test-removed` 和 `tq/snapshot-changed` 已有合併,其他規則沒有。

**F16 — Semgrep 自比規則**
severity: minor
blocking: 否
引句:「Kotlin 與 Java 的自比規則各加 `assertThat($X).isEqualTo($X)`」
- spec 位置:〈做法三〉、S11。
- 問題:只加 `assertThat($X).isEqualTo($X)`,沒帶現有規則的 `, ...)` 尾巴,Truth 常見形 `assertWithMessage("m").that(x).isEqualTo(x)`、`Truth.assertThat(x)…`、`assertThat(x, equalTo(x))` 不認。`$X` 為有副作用的呼叫(`next()` 對 `next()`)會誤報。均屬規則覆蓋度,不影響已實測的兩例。
- 佐證:file: `scripts/test_quality_semgrep.py:15-18` 現有寫法。

## 各節紀錄

- 〈問題與最小解〉「現況」逐項查證:`_PITFALL_DIFF_TEST_PAT` 排除 `src/test/`、不排除 `src/androidTest/`(file: `scripts/lumos:37566`)、三個出口(off、warn、環境變數)現在都不記帳(file: `scripts/lumos:38820-38824`、`38784-38785`)均屬實。已讀,現況宣稱無 finding。
- 〈名詞〉、〈回退〉:已讀,除 F2 提到的 warn 出口外無 finding。
- 〈做法四〉標準改寫、〈做法六〉考場實跑:已讀,無 finding(標準文字不在我的鏡頭;S14/S15 的矛盾見 F7)。
- 交叉引用:`Projects/Android單元測試標準實機演練_計劃`、`Projects/新增告警閘_計劃`、`Systems/test-quality-cli`、`Issues/收證歸因第三輪留下的小問題` 均存在;`lumos rejections` 的「判不清就擋,不走 fail-open」那筆確實在 Android端到端驗收_計劃。
- 〈做法二〉判定順序:「閘關掉→兩端提交→(比對)→有沒有宣告檢查工具」的重排可行,但 `_lint_new_changed_files` 丟掉刪除檔,需要比對工具自己用 git 查檔案清單(見 F9);`pitfalls` 失敗時非 `--keep-going` 路徑不會跑到這道(file: `scripts/lumos:68095-68100`),spec 已說推送前掛鉤帶 `--keep-going`,可接受。

## 固定席節點逐條判
- `Systems/test-quality-cli`:這份設計會破壞該節點在「裝置那路斷言歸因」記下的防回歸測試的行為(F6:字面文法讓 `test_device_hamcrest_and_caused_by_in_message_are_attributed` 的第二筆由真轉假)。新增第四支配套檔需要同步的四道守衛(精確列在該節點 PITFALL)spec 都有列,但漏了 `test_quality_semgrep.py` 的指紋(F14)。
- `Systems/test-quality-scan`:不影響其宣稱的行為,因為這份設計不改 `test_quality_scan.py` 的判讀,只有 Semgrep 規則在別支檔加一條;責任範圍(候選與裁決分開)與比對工具「只列候選、人裁」一致。
- `Systems/pitfalls-lint-adapter`:新增告警閘的合約是「指紋算次數不算有無」「保留前導縮排」,比對工具的指紋不算次數(F3)、只看新增行不做多重集扣除(F11),與該節點宣稱的比對語意不一致。這是旁路另立一套規則,不算破壞既有閘的行為。

## 實務隱患鏡頭
- 守衛面:有隱患,見 F1(出錯放行)、F2(warn 靜默)、F3(放行可自助)、F11(對所有棧的 CI 檔生效)。
- 效能:見 F12(二次方風險取決於實作)、F15(預算語意、檔案數)。
- 資源:無額外隱患。比對工具只讀 git、不寫暫存檔;單檔受 5MB/60000 行上限約束,同時只讀一檔。唯一例外是基準圖指紋要讀全內容,檔案數沒設上限(併在 F15)。
- 測試證據:實驗用的暫存 repo 與雛形腳本已刪除。

總計:最嚴重等級 major,blocking 共 13 條(F1–F12、F14)。

總結:最嚴重等級 major,blocking 共 13 條
