severity: major

我在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/邊界-sonnet/` 用 `h.py`(臨時 git repo 加 `lumos test-guard --json`)把修前 `lumos_before` 和修後 `lumos_after` 各跑一遍。`t*.py` 是各條重現,用 `python3.14 tN.py` 執行。以下「前」是修前 ea1e0b8a、「後」是修後 22cc6675,數字取自實跑輸出。

### F1 點名測試任務的新判法漏掉修前抓得到的寫法(修復回歸)
severity: major
blocking: 是 — 漏報真作弊:`enabled = false` 關掉測試任務,修前列出、修後不列
引句:「_TG_TASK_REF = re.compile(r"\btasks\.(?:matching|named|getByName|register|whenTaskAdded|configureEach|all)\b|\b(?:getByName|named)\s*[<(]"」
file: `scripts/lumos:48750`(補丁行 545;`_tg_names_test_task` 在 `scripts/lumos` 約 48790)
失敗場景:修前只要同一行有引號含 test 就算點名測試任務(`_TG_TEST_NAMED_LINE`)。修後要先有 `tasks.matching/named/getByName…` 這類呼叫,漏掉:`tasks.findByName("test")?.enabled = false`、`tasks["test"].onlyIf { false }`、`tasks.getByPath(":app:testDebugUnitTest").enabled = false`、`allTasks.forEach { if (it.name == "testDebugUnitTest") it.enabled = false }`。另外 `withType<Test> { filter { exclude("**/*Test*") } }` 修前靠引號啟發式列出,修後也不列。
重現(在臨時目錄跑 `python3.14 t13.py`,節錄,括號內是 rc 與規則):
```
findByName   before=(1,[tq/build-config]) after=(0,[])
getByPath    before=(1,[tq/build-config]) after=(0,[])
tasks[]      before=(1,[tq/build-config]) after=(0,[])
name==       before=(1,[tq/build-config]) after=(0,[])
withType Test filter exclude  before=(1,…) after=(0,[])
```
單獨一條:base 是 `plugins{}`,head 多一行 `tasks.findByName("testDebugUnitTest")?.enabled = false`,`lumos test-guard --diff A..B --json`,修前 rc1,修後 rc0。
歸因:有證據的修復回歸

### F2 try 裡只要有 fail 就整段不判,catch 吞掉斷言失敗也放過(修復回歸)
severity: major
blocking: 是 — 漏報真作弊:斷言失敗被 catch 吞掉,測試永遠綠,修前列出、修後不列
引句:「if has("fail", c.end(), cb_end) or has("ok", t.end(), tb_end):」
file: `scripts/lumos:48762`(補丁行 503)
失敗場景:`try { assertEquals(1, f()); fail("x") } catch (e: Throwable) { println(e) }` 的 catch 接 `Throwable`,連 `fail()` 丟的 `AssertionError` 也一起接走,測試永遠綠。修前第二道判斷(try 有斷言、catch 接得住斷言失敗、catch 不重丟)會列出。修後 try 裡有 `fail`/`assertThrows` 就直接 `continue`,不看 catch 的型別。`catch (e: AssertionError) { }` 空 catch 加 `fail()` 也一樣。S6 只寫「try 裡有 `fail(` 而 catch 接 `Throwable` **再斷言型別**」不列,「catch 只印出」不在不列範圍。
重現(`python3.14 t2.py`):
```
try_fail_throwable   before (1, [catch-no-fail @3])  after (0, [])
try_fail_empty_AE    before (1, [catch-no-fail @3])  after (0, [])
```
對照:同一個 try 不放 `fail()`,catch 印出,前後都列(`t21.py` 的 `try no fail catch print`)。作者要保的 `catch (e: Throwable) { assertTrue(e is X) }` 在修後仍不列。
歸因:有證據的修復回歸(修前列、修後不列)。可行修法是只在 catch 型別接不住 `AssertionError`,或 catch 內有斷言或重丟時才放過。

### F3 assume 與比對門檻以單行當身分:多行寫法的條件改成永遠跳過列不到,重新換行又誤報
severity: major
blocking: 是 — 漏報真作弊(S1 的「把既有 assume 的條件改掉」),加上純換行重排的誤擋
引句:「hits.setdefault(("tq/skip-added", who, "跳過:" + _tg_norm(line)), []).append((path, i))」
file: `scripts/lumos:48905`(補丁行 613)
失敗場景:
- 格式化工具常把長條件拆成 `assumeTrue(` 換行 `條件` 換行 `)`。身分只取 `assumeTrue(` 那一行,把條件改成 `false` 時身分不變,不列。
- 同一支測試把一行 assume 重新換行(內容沒變),`assumeTrue(` 變成「新身分」,誤列 `tq/skip-added`。
- `changeThreshold =` 後面的值換到下一行時,同樣看不到調高。
重現(`python3.14 t20.py`,「前/後」為候選規則):
```
assume multi false      前 0 []   後 0 []          ← 漏報
assume multi lambda     前 0 []   後 0 []          ← 漏報
assume reflow (FP)      前 0 []   後 1 [skip-added] ← 誤報,修復引入
thr nextline            前 0 []   後 0 []          ← 漏報
assume single / thr single  前 0 → 後 1            ← 本輪修復的單行版有效
```
歸因:漏報是「有證據的原有漏查」,這輪只補單行版,多行同族前後都是 0;換行誤報是「有證據的修復回歸」(前 0、後 1)。根因同一個:身分取一行而不是一個完整呼叫(括號配平後的敘述)。

### F4 單行 2 萬字上限擋不住「區塊開頭行 × 行數」的平方級,建置檔實測 200 秒、CI 實測 39 秒
severity: major
blocking: 是 — 超過 S11 的 30 秒效能上限(且該輸入落在計劃宣稱的單行、行數、總量上限之內)
引句:「or _tg_names_test_task(head) or _tg_names_test_task(line))」
file: `scripts/lumos:48990`(補丁行 640;`_TG_TEST_BLOCK.search(head)` 同一表達式更早存在,逐行對區塊開頭行做全行掃描)
失敗場景:建置檔的區塊開頭行 `foo("x…19900 字…") {` 長度在 2 萬字之內,後面接 9 萬行 `bar()`。每一行都對整條開頭行跑 `_TG_TEST_BLOCK`,這輪又加一次 `_tg_names_test_task(head)`。單行 `_TG_TEST_BLOCK.search(head)` 實測 0.83ms,`_tg_names_test_task(head)` 0.27ms。
CI 同形:`_tg_ci_hits` 對每個命中行呼叫 `head(idx)`,把父行 `_tg_norm` 一次,父行 19900 字、9 萬個 `continue-on-error: true`。
重現(`python3.14 t3.py`、`python3.14 t11.py`):
```
build.gradle.kts(開頭行 19905 字 + 90000 行 + 1 行 excludeTestsMatching)
  after 200.7 秒, before 253.9 秒 (rc1, 結果正確但超時)
.github/workflows/ci.yml(父行 19900 字 + 90000 行 continue-on-error + 1 行 || true)
  after 39.1 秒
in-process: _tg_build_hits 5000 行 5.5 秒、10000 行 11 秒、20000 行 21.8 秒(線性,斜率 1.1ms/行)
```
歸因:有證據的原有漏查(修前同形 254 秒;這輪的上限讓單行有界,但沒讓「單行長度 × 行數」有界,`_tg_names_test_task` 又多加了一份固定成本)。

### F5 反斜線續行會合成邏輯行,繞過單行 2 萬字上限,CI 檔實測 64 秒
severity: major
blocking: 是 — 超過 30 秒效能上限
引句:「head = lambda idx: _tg_norm(rows[parent[idx]][1]) if parent[idx] >= 0 else ""  # noqa: E731」
file: `scripts/lumos:49010`(補丁行 689)
失敗場景:`_tg_has_long_line` 檢查實體行,而 `_tg_ci_lines` 把反斜線續行併成一個邏輯行。1 萬行各 96 字的續行會併成約 1MB 的父行,底下 3000 個 `continue-on-error: true` 各自對這個 1MB 的父行做一次 `_tg_norm`,每個命中花 O(父行長度)。實體行最長 96 字,上限完全不觸發。
重現(`python3.14 t19.py`):
```
lines 13003, bytes 1054038, max physical line 96
after 63.6 秒, before 62.9 秒   (rc1)
in-process 10000 續行 + 1000 子行 → 10.4 秒;5000+500 → 2.6 秒(線性於 父長 × 命中數)
```
歸因:有證據的原有漏查(修前 62.9 秒、修後 63.6 秒,同形)。這輪的 `parent` 堆疊沒解決它,只是把往回掃的成本換成每個命中行重新正規化一次。

### F6 `-xtest` 與 `--exclude-task=test` 兩種 Gradle 合法寫法不列
severity: major
blocking: 是 — 漏報真作弊:CI 加了排除測試任務的旗標卻不列(S8 的 `-x test` 同族)
引句:「_TG_CI_X = re.compile(r"(?:^|\s)(?:-x|--exclude-task)\s+:?[\w:.-]*(?:test|check)[\w:.-]*", re.I)」
file: `scripts/lumos:48851`(補丁行 662,這行是未改動的上下文)
失敗場景:這個正規式要求旗標後面接空白。我用本機 Gradle 8.13(`~/.gradle/wrapper/dists/gradle-8.13-bin/.../bin/gradle`)驗過,`gradle -m test -xtest` 和 `gradle -m test --exclude-task=test` 都被接受,而且和 `-x test` 一樣把 `:test` 整條排除(輸出沒有任何 `:test SKIPPED` 行)。`_tg_ci_test_tasks` 把以 `-` 開頭的字詞都略過,所以測試呼叫的計數也沒少,兩條路都看不到。
重現(`python3.14 t9.py`):base 是 `./gradlew test`,head 是 `./gradlew test -xtest`:
```
xtest_attached       前 rc0 []  後 rc0 []
exclude-task=        前 rc0 []  後 rc0 []
-x test(空白)       前 rc1  後 rc1   ← 對照組,有列
```
歸因:有證據的原有漏查(前後同樣不列;這輪新增 `_TG_CI_ARG_FLAGS` 時沒檢查附著形式)。

### F7 建置檔 `enabled = false` 只看最內層區塊開頭,這輪只把 ignoreFailures 改成全檔判
severity: major
blocking: 是 — 漏報真作弊;S7 明列「換行的 `tasks.matching { … }.configureEach {`」,同族的換行寫法卻判不到
引句:「_TG_TEST_BLOCK = re.compile(r"(?i)(?<![\w])test\s*\{|\btasks\.test\b|withType\s*[<(]\s*Test\b|^\s*test\b|\bunitTests\.all\b")」
file: `scripts/lumos:48837`(補丁行 543)
失敗場景:
- (a) lambda 本身換行:`tasks.matching {` 換行 `it.name.contains("UnitTest")` 換行 `}.configureEach {` 換行 `enabled = false`。`enabled = false` 那行的區塊開頭是 `}.configureEach {`,不含 test,也沒有點名任務的呼叫與引號。
- (b) `tasks.withType<Test> { if (cond) { enabled = false } }`:`enabled = false` 的區塊開頭是 `if (…) {`,不是測試區塊。
重現(`python3.14 t13.py`、`python3.14 t14.py`):
```
configureEach multi      前 0 後 0
withType Test nested if  前 0 後 0
ignoreFailures nested    前 0 後 1   ← 同形的 ignoreFailures 被這輪改成全檔判,抓得到
```
歸因:有證據的原有漏查(前後皆 0)。與 ignoreFailures 對照可見,這輪只修了其中一條。

### F8 ignoreFailures 全檔判之後,沒列進名單的靜態檢查外掛誤擋
severity: minor
blocking: 否 — 只對少見的外掛造成誤報,可用 `lint-waive` 放行,覆蓋名單可再補
引句:「_TG_NOT_TEST_PLUGIN = re.compile(r"(?i)\b(?:detekt|ktlint|spotless|checkstyle|pmd|spotbugs|lint(?:Options)?|jacoco\w*|kover\w*|coverage\w*)\b")」
file: `scripts/lumos:48820`(補丁行 530)
失敗場景:`kotlinter { ignoreFailures = true }`(Android 常見的 Kotlin 格式檢查外掛)修前 0 條候選,修後 1 條 `tq/build-config`。另一個方向:名單用 `\b…\w*` 比對整個區塊開頭行,`val coverageTest by tasks.registering(Test::class) { ignoreFailures = true }` 因為 `\bcoverage\w*` 被排除,真的測試任務的 ignoreFailures 反而放過。這條我沒實跑,是從正規式推的,標 ⚠。
重現:`python3.14 t1.py` 的 `kotlinter` 一列:`before (0, []) / after (1, [tq/build-config @3])`。
歸因:有證據的修復回歸(誤報部分)

### F9 正式程式檔與 CI、建置檔有單行超過 2 萬字時,任何改動都被擋
severity: minor
blocking: 否 — 計劃已把「任一行超過 2 萬字的檔不解析」列為標準的抓不到;誤擋只是要人放行
引句:「elif _tg_has_long_line(b) or _tg_has_long_line(h):」
file: `scripts/lumos:49000`(補丁行 923)
失敗場景:`src/main/.../Data.kt` 有一行 25000 字的字串常值,只改另一個函式,修前 0 條候選,修後 `tq/too-large`。指紋含新物件編號,每次改都要重新放行。正式程式檔唯一規則 `tq/test-env-sniff` 本來是逐行掃描,線性,沒有需要用上限保護。另外 CRLF 的邊界差一個字:20000 字加 `\r` 會被判超過,19999 字加 `\r` 不會(`_tg_has_long_line` 數到 `\n` 前,含 `\r`)。
重現(`python3.14 t17.py`):`main long line unrelated edit: before (0,[])  after (1,[tq/too-large])`;`python3.14 t12.py` 看邊界。
歸因:有證據的修復回歸(修前 0、修後 1)

### F10 同族的放寬寫法沒列進規則
severity: minor
blocking: 否 — 屬覆蓋面,計劃沒有承諾這些寫法
引句:「re.compile(r"\bexclude\s*\(?\s*[\"'][^\"']*Test"))」
file: `scripts/lumos:48846`(補丁行 552)
失敗場景:測試區塊裡的 `exclude("**/ui/**")`(樣式不含 Test)、`excludeTags("slow")`、`excludeCategories(…)`、`include("nothing/**")` 不列;CI 的 `./gradlew test || echo done`、`|| exit 0` 不列(只認 `|| true`)。
重現:`python3.14 t14.py`、`python3.14 t8.py`(`excludeTags after=(0,[])`、`exit0 after (0,[])`)
歸因:有證據的原有漏查(前後都是 0)

## 圖譜鏡頭
- `LUMOS-IMPACT` 範圍在會談專案算不出來,我改讀 `Systems/test-guard`。裡面的 WHY「任一行超過 2 萬字的檔不解析」寫的理由是「外層看門不靠逐條判斷」。F4、F5 顯示這道門只擋實體單行,擋不住「單行長度 × 行數」和續行合併,筆記的因果要補上這個限制。
- 同一篇的 WHY「ignoreFailures 不限在測試區塊…點名測試任務要有 tasks.named、matching、getByName 這類呼叫加上引號裡含 test」。這條就是 F1 的來源,筆記沒提到修前涵蓋的 findByName、索引 `tasks[]`、`it.name == "…"` 這幾種寫法會被放過。
- 計劃 S7 寫「換行的 `tasks.matching { … }.configureEach {` 裡的 `enabled = false` 也列」,綁定測試只覆蓋 lambda 在同一行(`t_tq_guard_build_config` 的「多行 matching UnitTest」),F7(a) 的換行 lambda 沒被測試涵蓋。
- S11 的 30 秒條款綁定的測試輸入是短區塊開頭和短續行,F4、F5 的輸入落在計劃宣稱的上限內,卻超過 30 秒,建議把這兩種形狀加進 `t_tq_guard_cli_contract`。
- S6、S1 同理:`t_tq_guard_catch_no_fail` 沒有「有 `fail()` 但 catch 吞掉」的反例;`t_tq_guard_skip_added` 沒有多行 assume。

## 三問
1. **原問題的修復效果**:有行為證據的修好項目有:
   - `changeThreshold` 單行調高(前 0、後 1)。
   - 單行 `assumeTrue(false)`(前 0、後 1)。
   - 點號寫法與巢狀的 ignoreFailures(前 0、後 1)。
   - `&&` 串接拿掉後半(前 0、後 1)。
   - JaCoCo 的 `exclude("**/*Test*.*")` 誤報(前 1、後 0)。
   - 嵌套 49000 層 try/catch 這種規模(40000 層後版 1.8 秒;修前版本在 120 秒內沒跑完,被我中止)。
   - 九種各 240 行近 2 萬字的病態單行測試檔,最慢 4.5 秒。

   兩個 4.8MB 級的測試檔輸入沒有逾時。但 CI、建置檔的「長開頭行 × 行數」與續行合併仍超時(F4、F5)。
2. **修補處的正常、錯誤與相鄰路徑**:
   - 正常路徑:類別層級 `@Ignore` 的檔改名不列;`internal open` 這類修飾詞只改不列;`-x lint` 不列;detekt 的 ignoreFailures 不列;`catch (e: Throwable) { assertTrue(e is X) }` 加 `fail()` 不列。這些都維持。
   - 相鄰路徑出問題:點名測試任務的相鄰寫法(F1)、`fail()` 後 catch 吞掉(F2)、assume 與門檻的相鄰換行寫法(F3)、單行上限相鄰的合成邏輯行與長開頭行(F4、F5)。
3. **新發現同一案例的前後結果**:
   - 修復造成的退步:F1(`findByName` 等四種寫法)、F2(兩種吞掉斷言的寫法)、F3 的換行重排誤報、F8、F9。每一條前後的規則都在上面的重現欄。
   - 原有漏查:F3 的多行 assume 與門檻、F4、F5、F6、F7、F10。這些輸入修前、修後結果相同,不是這輪造成的。
   - 未判定:F8 第二個方向(`coverageTest` 名稱被排除)。

F1、F2、F3、F4、F5、F6、F7 共七條 major,F8、F9、F10 三條 minor;其中 F1、F2 以及 F3 的換行重排誤報是這輪修補造成的退步。
