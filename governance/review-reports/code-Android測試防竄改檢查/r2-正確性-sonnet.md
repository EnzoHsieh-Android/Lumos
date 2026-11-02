severity: major

本席在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/正確性-sonnet/` 裝了修前 `before`(ce5256bd)和修後 `after`(ea1e0b8a)兩份 clone,用同一套造 repo、跑 `lumos test-guard --diff A..B --json` 的腳本(`h.py`、`e1`~`e15.py`)比對。`python3.14 scripts/test_lumos.py -k tq_guard` 在 `after` 上 163 條全綠。下面每條退步的重現,現有測試都沒抓到。

### F1 CI「呼叫測試任務」改用任務名記,切法會把旗標當任務,也會漏掉 `-x` 之前的任務
severity: major
blocking: 是 — 計劃 S8 要求「刪掉呼叫 Gradle 測試任務的指令」要列,修後有一類寫法刪掉了不列。
引句:「for task in _TG_CI_TEST_TASK.findall(re.split(r"\s(?:-x|--exclude-task)\s+\S+|[|;&]", after)[0] if after else ""):」
file: `scripts/lumos:48875`
失敗場景:
- **漏列**。`re.split(...)[0]` 只取第一個 `-x X` 之前的文字。`./gradlew clean -x lint check` 只剩 `" clean"`,`check` 不記。`./gradlew -x lint testDebugUnitTest` 一個任務都不記。
- 把 base 的這行刪掉或改成別的,`(chh, cb)` 差集看不到任何被拿掉的測試任務,不列候選。
- **亂列**。`\w*[Tt]est\w*` 會把 `--tests`、`-PtestMode` 當任務。拿掉 `--tests com.x.Foo` 這個篩選(測試範圍變大)會列「拿掉了呼叫測試的 Gradle 指令:tests」。
重現(`python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/正確性-sonnet/e2.py`):

| 輸入(base → head) | 修前 | 修後 |
|---|---|---|
| `./gradlew -x lint testDebugUnitTest` 那行整行刪掉 | 列 tq/ci-config | 無候選 |
| `./gradlew clean -x lint check` → `./gradlew clean -x lint` | 列 | 無候選 |
| `./gradlew testDebugUnitTest --tests com.x.Foo` → 拿掉 `--tests …` | 列,訊息是整行文字 | 列,訊息是 `…指令:tests` |
| `./gradlew assembleDebug -PtestMode=fast` → 拿掉 `-PtestMode` | 列 | 列,訊息是 `…指令:PtestMode` |

歸因:有證據的修復回歸(漏列部分,修前列、修後不列)。亂列部分修前也列,是原有問題,修補只是把訊息改成任務名。

### F2 `ignoreFailures = true` 改成「只在測試區塊裡才算」,單行點名測試任務的寫法漏列
severity: major
blocking: 是 — 計劃 S7「新增 `ignoreFailures = true` 應列」,最短的作弊寫法在修後不列。
引句:「re.compile(r"\bignoreFailures" + _TG_SET + r"true\b"))」
file: `scripts/lumos:48761`(搭配 `_tg_build_hits` 的 `in_test` 判斷)
失敗場景:`ignoreFailures` 從 `_TG_BUILD_RES` 搬進 `_TG_IN_TEST_BLOCK`,要求該行落在測試區塊。`in_test` 只看外層區塊開頭和該行 `{` 之前的部分,不看沒有大括號的整行。所以 `test.ignoreFailures = true`、`tasks.test.ignoreFailures = true`、`testDebugUnitTest.ignoreFailures = true` 都不列。
重現(`e10.py`,build.gradle 新增下面各行,base 是 `android {\n}\n`):

| 新增的行 | 修前 | 修後 |
|---|---|---|
| `test.ignoreFailures = true` | 列 tq/build-config | 無 |
| `tasks.test.ignoreFailures = true` | 列 | 無 |
| `testDebugUnitTest.ignoreFailures = true` | 列 | 無 |
| `tasks.test { ignoreFailures = true }` | 列 | 列 |
| `tasks.withType(Test) {…}` | 列 | 列 |

歸因:有證據的修復回歸。

### F3 `_TG_TEST_NAMED_LINE` 太寬:JaCoCo 的 Kotlin DSL `exclude("**/*Test*.*")` 被當成測試設定
severity: major
blocking: 是 — 計劃 S7 明列「JaCoCo 報表的排除不列」,Kotlin 寫法修後被擋(候選可放行,但是無謂的擋推送)。
引句:「_TG_TEST_NAMED_LINE = re.compile(r"(?i)[\"'][^\"'\n]*test[^\"'\n]*[\"']|\bunitTests\.all\b")」
file: `scripts/lumos:48757`(使用處 `_tg_build_hits` 的 `in_test`)
失敗場景:任何一行有含 "test" 的引號字串(不分大小寫)就算「在測試區塊」。`fileTree(it) { exclude("**/*Test*.*", "**/R.class") }` 同時符合 `_TG_IN_TEST_BLOCK` 的 exclude 規則,列 `tq/build-config`。新增的 `featureFlags { register("unit-test") { enabled = false } }` 也被列。新測試只覆蓋 `exclude: ['**/*Test*.*']` 的 Groovy 冒號寫法,沒有覆蓋這一種。
重現(`e9.py`,base 是 `plugins { id("jacoco") }\nandroid {\n}\n`):
- head 加 `tasks.register<JacocoReport>("jacocoTestReport") { … fileTree(it) { exclude("**/*Test*.*", "**/R.class") } … }`。
- 修前無候選;修後列 `tq/build-config`(app/build.gradle.kts 第 6 行)。
歸因:有證據的修復回歸。

### F4 `_tg_class_has_body` 對每個類別宣告都往檔尾掃,單行大檔從 0.2 秒變 54 秒
severity: major
blocking: 是 — 計劃 S11 要求病態輸入 30 秒內;資源段寫「不會讓判讀變成平方級」。
引句:「brace = stripped.find("{", j)」
file: `scripts/lumos:48451`(同函式的 `stripped.find(">", j)` 在 `scripts/lumos:48440` 附近)
失敗場景:遇到 `class A: B` 就對剩下全文找 `{` 與換行,找不到就掃到檔尾。每個類別名都掃一次,全文是平方級。`_TG_MAX_BYTES` 是 5MB,沒有單行長度限制,所以 5MB 單行 `class A: B ` 重複約 45 萬次就能通過大小檢查。`_tg_functions` 是單支檔內不可中斷的呼叫,截止時間只在檔與檔之間檢查。
重現(`e7.py`、`e8.py`):
- 4.95MB 單行 `"class A: B "*450000`,直接呼叫 `_tg_functions`:修前 0.22 秒,修後 54.3 秒。
- 同樣內容放進 `FooTest.kt` 經 CLI 跑 `lumos test-guard`:修前 1.8 秒,修後 55.8 秒。
- 多行版本(5.9 萬行 `class A : B`)只有 0.64 秒,所以只有單行才會爆。
歸因:有證據的修復回歸(修補新增的函式,修前同輸入 0.2 秒)。

### F5 類別層級 `@Ignore` 的檔案若被改名或搬目錄,會被列成新增跳過
severity: minor
blocking: 否 — 作者已在 test-guard 節點的 WHY 寫明這個代價,可放行、不是漏洞。
引句:「who = owner.get(i) or "檔:" + path」
file: `scripts/lumos:48802`
失敗場景:類別層級的跳過標記身分是 `檔:<路徑>`,base 側用舊路徑、head 側用新路徑(`_tg_test_file` 傳 `old or path` 與 `new or path`)。`git mv a/FooTest.kt b/FooTest.kt` 時兩側身分不同,次數差變成 +1。這跟 S1「測試原樣搬到另一支檔帶過去的 `@Ignore` 不列」的精神相違。Android 搬 package 時常見。base 側改用新路徑就能解,`_tg_changes` 已經給了 old/new 配對。
重現(`e1.py`):FooTest.kt 帶類別層級 `@Ignore("wip")`,只改 package 並搬目錄。修前無候選;修後列 `tq/skip-added`(b/FooTest.kt 第 3 行)。
歸因:有證據的修復回歸,但作者已知並接受。

### F6 測試檔裡既有的比對門檻被放寬(`changeThreshold` 0.001→0.9)不再列
severity: minor
blocking: 否 — S9 字面是「比對門檻字樣新增」,修後符合字面;但訊息和規則名寫「比對門檻有變」,建置檔那條路仍會抓數值變更。
引句:「hits.setdefault(("tq/snapshot-changed", who, m.group(0)), []).append((path, i))」
file: `scripts/lumos:48807`
失敗場景:測試檔裡的門檻身分改成 (規則, 擁有者, 比到的那個字),不再帶整行。同一個字數量不變時,把 `changeThreshold = 0.001f` 改成 `0.9f` 的次數差是 0,不列。同一個值在 build.gradle 裡改仍會列,兩條路不一致。
重現(`e12.py`):修前列 `tq/snapshot-changed`,修後無候選;若是新增門檻字樣,兩版都列。
歸因:有證據的修復回歸。

### F7 一行裡的多個中綴斷言只算一條;把兩行斷言合成一行會被列「斷言變少」
severity: minor
blocking: 否 — 只有排版合併才會誤列,可放行。
引句:「if ls in done or len(out) >= _TG_MAX_STMTS:」
file: `scripts/lumos:48534`
失敗場景:`x shouldBe 1` 和 `y shouldBe 2` 原本分兩行,合成 `{ x shouldBe 1; y shouldBe 2 }` 後以行為單位只算 1 條。反向,同一行 3 個斷言刪成 1 個時,`assert-weakened` 不再列(目前靠 `expected-changed` 順帶列出,訊息不準)。
重現(`e11.py`):
- 兩行合一行:修前無候選;修後列 `tq/assert-weakened`,訊息「斷言 2→1」。
- 同行 3 個刪成 1 個:修前有 `assert-weakened`(3→1);修後只剩 `expected-changed`。
歸因:有證據的修復回歸。

## 圖譜鏡頭
- **`Systems/test-guard`**
  - 診斷:節點的 WHY 與實作大致對得上。已經寫下的代價有:跳過標記身分只用函式名(同名測試互抵)、檔案改名時類別層級跳過會被列一次(F5)、整道閘時間最多預算的兩倍。
  - 對不上的地方:`WHY:候選指紋用規則、檔案、函式名加本體簽名、第幾個`(`Systems/test-guard.md:21`)對 `tq/skip-added` 已不成立,身分現在是函式名加「跳過」,沒有本體簽名,同節點 24 行有另寫。
  - 計劃〈實務隱患〉效能段(計劃 260 行)還寫「比對工具算在同一個預算裡」,與修補後「比對時間不算進檢查命令預算」不符。
  - 計劃的 `_TG_LIMITS` 已列「同名兩支測試跳過一拿一加互抵」。我用 `e14.py` 實測:修前列、修後不列,屬已知取捨。
- **`Systems/pitfalls-lint-adapter`、`Systems/room-guard`、`Systems/測試假綠形態`**:這份修補不影響它們宣稱的行為。我在 10056 種 `_strip_c_comments` 參數組合(約 100 支測試檔加亂入引號、註解符號)上比對修前修後,輸出完全相同。`_rg_balanced` 沒變行為,`_tg_ci_blocks` 與舊的 `_tg_ci_block_has_gradle` 在 2 萬組隨機縮排下完全一致。
- **`Systems/測試假綠形態`(新測試的前置斷言與紅綠)**:`S12 r1 比對花的時間…` 這條有前置斷言。我把 `tools_deadline` 換回 `deadline` 後它會翻紅(「時間預算剩 28 秒,不足單條保底 30 秒」),判準獨立。F1~F4 對應的行為沒有測試,所以修補把它們弄壞時全綠。
- **既有放行指紋**:`.lumos/lint-waivers.json` 352 條沒有任何 `tq/` 規則,這個功能在 base 047031883 還不存在,所以沒有舊放行會整批失效。沒有 `origin` 欄的舊紀錄仍當人放的。

## 三問
1. **原問題的修復效果有何行為證據?** 下列已驗,證據都在 `after` 的實跑輸出:
   - Truth `isTrue`→`isFalse` 修前無候選、修後列 `expected-changed`。
   - JUnit 5 訊息在後(`"Alice"`→`"Bob"`)修前無、修後列 `expected-changed`;只改訊息兩版都不列。
   - `assertTrue(1 == 1)`、`|| true`、`assertThat(true).isTrue()` 修前無、修後列 `assert-weakened`;`assertTrue(x.size > 0)` 兩版不列。
   - catch 吞斷言(`catch (e: AssertionError) { println(e) }`)修前無、修後列 `catch-no-fail`;catch `IOException` 與 `throw e` 兩版不列。
   - 重複斷言交錯改兩版都列。
   - 比對時間不擠掉檢查命令預算已用變異驗證。
   - 首推用分岔點與 CI 阻擋集合、`_strip_c_comments` 重構的行為不變,見上節。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 大致成立,但有四處退步:F1~F4 是修補直接引入或放大的,F5~F7 是取捨或次要變動。其餘相鄰路徑未見回歸:
   - 隨機把 `{ } ( ) " ' ` class` 等字元插進 100 支真實測試檔,連跑 1500 輪,新舊函式沒有丟例外。
   - 在 drill 測試檔上,`_tg_functions` 的函式鍵、簽名新舊一致。
   - 另外觀察到,`class X @Inject constructor(...)`、`class X<T : List<String>>`、多行父型別會讓 `_tg_class_has_body` 判成沒本體,函式鍵少一段類別路徑(`FooTest.x`→`x`)。base/head 兩端一致,我沒找到會錯判的輸入,所以沒標 finding。
3. **新發現的同一案例在修前、修後各是什麼結果?** F1~F7 各條的「重現」都附了兩版結果。F2、F3、F4、F5、F6 屬於修前正確、修後出錯;F1 的漏列同屬此類,其亂列(`--tests`、`-P…`)修前就會列,只是訊息文字不同;F7 是修前無誤列、修後誤列。

未驗範圍:S17~S22 的 Semgrep、考場與歷史誤報量測;`lint-waive` 終端互動只讀碼,沒有自己開 pty;Jenkinsfile、Bitrise 等其他 CI 檔;角色卡沒附,略過。

我的臨時目錄 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/正確性-sonnet/` 還在,內含各 finding 的重現腳本,請編排者收貨後用字面絕對路徑刪除。

全份有四條會讓守衛判錯的退步(F1、F2、F3、F4),另有三條次要的取捨或次要退步(F5、F6、F7)。
