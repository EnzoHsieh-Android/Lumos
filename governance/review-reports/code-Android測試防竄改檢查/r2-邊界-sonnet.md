severity: major

審查範圍:修前 ce5256bd、修後 ea1e0b8a。我在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/邊界-sonnet/` 建了暫存 repo,分別用修前、修後兩版的 `lumos test-guard --json` 實跑。以下每條都列兩版結果,沒有只靠讀碼推論的項目。

### F1 巢狀 try/catch 讓 `_tg_catch_no_fail` 變成平方級,5000 層超過 30 秒
severity: major
blocking: 是 — 超過 S11 的 30 秒上限,而且是修補新加的判斷造成的
引句:「if _TG_ASSERT_RE.search(tb) and _TG_CATCH_ASSERT.search(c.group(1)) and not re.search(r"\bthrow\b", cb):」
file: `scripts/lumos:48733`
失敗場景:新規則在判斷 catch 型別之前,先對每個 try 的整個本體做 `_TG_ASSERT_RE.search(tb)`。
- 修前只有 catch 本體有斷言字或是空的,才會去搜 try 本體。
- 現在每個 `catch (e: Exception) { log() }` 都要搜一遍。
- 巢狀 N 層時,搜尋總量是 N 的平方乘上單層長度。
- 注意順序:`_TG_CATCH_ASSERT` 比對便宜,卻排在昂貴的搜尋之後。
重現:一支新測試的本體是 `try { `×N + `x()` + ` } catch (e: Exception) { log() }`×N。
```
python3.14 .../邊界-sonnet/t10.py 3000 before,after   → before 1.2s / after 13.4s
python3.14 .../t10.py 5000 after                      → after 35.1s (rc=0,檔案約 185KB)
python3.14 .../t10.py 6000 before                     → before 1.3s
```
同一族 `runCatching { `×6000 兩版都是 17.4 秒(`t11.py`),約 8000 層就破 30 秒,這是原有問題。
歸因:有證據的修復回歸(try/catch 部分,修前 1.3 秒、修後 35 秒);runCatching 部分是有證據的原有漏查(兩版相同)。

### F2 `&&` 串接或 `-x` 在任務之前的 Gradle 指令,測試任務被拿掉不再列
severity: major
blocking: 是 — 漏報「刪掉呼叫測試任務的 CI 指令」這個真作弊(S8),而且是修補才漏的
引句:「for task in _TG_CI_TEST_TASK.findall(re.split(r"\s(?:-x|--exclude-task)\s+\S+|[|;&]", after)[0] if after else ""):」
file: `scripts/lumos:48875`
失敗場景:`after` 只取第一個 `-x …`、`|`、`;`、`&` 之前的那一段,後面所有測試任務都不記。
- `./gradlew assembleDebug && ./gradlew testDebugUnitTest` 刪掉後半,測試任務一個都沒記進 base,所以沒有任何東西「消失」。
- `./gradlew -x lint testDebugUnitTest` 改成 `-x lint assembleDebug`,`-x` 在最前面,切完是空字串,同樣漏。
- 修前整行文字都進次數表,改任何一個字都會列。
重現:`.github/workflows/ci.yml` 的一個 step,用 `t2.py` 的 case 2 與 3 跑。
```
case2  run: ./gradlew assembleDebug && ./gradlew testDebugUnitTest  → run: ./gradlew assembleDebug
  before rc=1 tq/ci-config(拿掉了呼叫測試的 Gradle 指令)   after rc=0
case3  run: ./gradlew -x lint testDebugUnitTest  → run: ./gradlew -x lint assembleDebug
  before rc=1                                                after rc=0
對照 3b(單一任務直接替換) before rc=1 / after rc=1
```
歸因:有證據的修復回歸。

### F3 測試檔裡把 `changeThreshold` 調高到 0.5 或 1.0,不再列 `tq/snapshot-changed`
severity: major
blocking: 是 — 漏報放寬截圖比對門檻這個典型作弊(修前會抓到)
引句:「hits.setdefault(("tq/snapshot-changed", who, m.group(0)), []).append((path, i))」
file: `scripts/lumos:48807`
失敗場景:身分從「整行文字」改成「命中的那個字」(`changeThreshold`)。同一行的數值從 0.01 改成 1.0,身分不變、次數不變,就不列了。
- 修前整行文字不同,會被當成新增。
- 計劃第 126 行的規格寫「命中次數差」,所以字面上可以辯稱沒違反。
- 但值改成 1.0 等於任何截圖都過,而且同一個檔案如果是建置檔(`.gradle.kts`),仍會列,兩邊不一致。
重現:`t17.py`。
```
17a 測試檔 changeThreshold = 0.01 → 0.5 : before rc=1 tq/snapshot-changed / after rc=0
17b 0.01 → 1.0                         : before rc=1                       / after rc=0
17c 同樣的行放在 build.gradle.kts      : before rc=1 / after rc=1
```
歸因:有證據的修復回歸(行為變化是修補造成,規格字面是否涵蓋由作者裁)。

### F4 Kotlin DSL 的 JaCoCo `exclude("**/*Test*.*")` 被誤擋
severity: major
blocking: 是 — 設定覆蓋率報表是正常改動,卻被擋;S7 明列 JaCoCo `exclude: [...]` 不列,這是同一族的 Kotlin 寫法
引句:「# 同一行點名了測試任務(引號裡含 test,或 unitTests.all)」
file: `scripts/lumos:48820`(`_TG_TEST_NAMED_LINE`,配合 `_tg_build_hits` 用 `or` 併入 `in_test`)
失敗場景:只要同一行有「引號裡含 test」的字串,就當成在測試區塊裡,於是 `exclude\s*\(?\s*["'][^"']*Test` 與 `enabled = false` 全部生效。
- JaCoCo 的 `exclude("**/*Test*.*")` 是標準寫法,字串本身含 Test。
- 依賴宣告的 `exclude("org.junit.Test")` 也中。
- `tasks.register("checkTestNames") { enabled = false }` 也中。
重現:`build.gradle.kts` 加入下列內容(`t16.py`)。
```
16a tasks.register<JacocoReport>("jacocoTestReport") { ... exclude("**/*Test*.*", "**/R.class") ... }
    before rc=0 / after rc=1 tq/build-config
16c val tree = fileTree("build/classes") { exclude("**/*Test*.*") }
    before rc=0 / after rc=1
16b implementation("com.x:y:1") { exclude("org.junit.Test") }
    before rc=0 / after rc=1
```
歸因:有證據的修復回歸。

### F5 同一族的多行寫法仍然漏報:`tasks.matching {…}.configureEach {` 換行 `enabled = false`
severity: major
blocking: 是 — 漏報整批停用單元測試這個真作弊;修補只涵蓋同一行寫法
引句:「# 測試任務的區塊:test {}、tasks.test、withType<Test>、任務名含 test 的 named(Android 的 testDebugUnitTest)、unitTests.all」
file: `scripts/lumos:48754`
失敗場景:`_TG_TEST_NAMED_LINE` 只看當行,不看區塊開頭那一行(`head`)。換行寫的 `matching`、`getByName`、`register` 開頭行裡有 `"UnitTest"`,但 `head` 判不出是測試任務。
重現:`build.gradle.kts` 加入下列內容(`t3.py`、`t4.py`)。
```
tasks.matching { it.name.contains("UnitTest") }.configureEach {
    enabled = false
}
  before rc=0 / after rc=0
同一行寫成 `...configureEach { enabled = false }` : after rc=1(這是修補涵蓋的)
tasks.getByName('testDebugUnitTest') {    (Groovy,換行 enabled = false)  before rc=0 / after rc=0
tasks.matching { it.name.startsWith('test') }.all { 換行 enabled = false }  兩版 rc=0
tasks.configureEach { if (name.startsWith("test")) { enabled = false } }    兩版 rc=0
```
歸因:有證據的原有漏查(兩版都 rc=0,修補只補了同一行的寫法)。

### F6 `_tg_hit_cands` 新寫的 `x not in fresh` 仍是平方級,6 萬行 31 秒
severity: major
blocking: 是 — 合法大小的檔(6 萬行、未達 10 萬行上限)超過 S11 的 30 秒上限
引句:「picks = (fresh + [x for x in reversed(locs) if x not in fresh])[:extra]」
file: `scripts/lumos:49225`
失敗場景:`fresh` 是 list。同一個身分(類別層級的 `@Ignore`、同一支函式裡的大量 `assumeTrue`)有 N 處新增命中時,N×N 次比對。
重現:新測試檔含 `@Ignore\n`×N,後面接一個類別(`t8.py`)。
```
N=60000 after 30.9s  / N=99000 after 82.2s
N=60000 before 167.1s(修前更慢,另有原因)
單獨量:list 版 `[x for x in reversed(locs) if x not in fresh]` 1 萬 0.8s、2 萬 3.2s、4 萬 13.1s
```
歸因:原有的平方級被修補縮小(167 秒降到 31 秒)但沒消除;`x not in fresh` 這一行是修補自己新增的,仍是有證據的修復缺漏。

### F7 CI 與建置檔其他平方級沒收乾淨:`_tg_ci_head`、`_tg_block_heads`、`named(` 的正規式
severity: major
blocking: 是 — 合法大小的 CI 或建置檔超過 30 秒,而且單檔內沒有截止時間檢查,整道閘預算(300 秒)攔不住
引句:「用堆疊一趟算完,跟行數成正比。」
file: `scripts/lumos:48906`(`_tg_ci_head`)、`scripts/lumos:48778`(`_tg_block_heads`)、`scripts/lumos:48754`(`_TG_TEST_BLOCK` 的 `named\s*[<(][^)]*["']…`)
失敗場景:修補把 `_tg_ci_blocks` 改成線性,但 `_tg_ci_head` 對每個命中行仍往回掃到縮排比自己淺的行,同層級的兄弟行就是平方級。
- `_tg_block_heads` 對一行裡每個 `{` 都做一次整行的 `_tg_norm`。
- `named(` 重複出現時,`[^)]*` 對每個出現處各掃到行尾。
重現(`t7.py`、`t7b.py`、`t13.py`):
```
yml 加 N 行 `      - run: ./gradlew assembleDebug || true`:N=20000 after 23.8s,N=40000 after 92.2s
yml 加 N 行 `        continue-on-error: true`(N=20000):before 44.4s / after 20.5s
build.gradle.kts 單行 `x { `×20000 後接 `}`×20000:before 68.0s / after 67.8s
build.gradle.kts 單行 `named(`×15000 + ` {` 換行 `enabled = false`:before 24.2s / after 24.2s
```
歸因:有證據的原有漏查(`_tg_ci_head`、`_tg_block_heads`、`named` 正規式本身都是修前就有);「CI 放寬鍵一趟算完」的修補只修了其中一半。

### F8 整支測試檔搬家或改名時,類別層級的註記被當成新增跳過,連 `@Config(sdk…)` 也中
severity: minor
blocking: 否 — 圖譜 `Systems/test-guard` 的跳過身分那條 WHY 已記為「代價」,且有 `lint-waive` 的逃生門;但範圍比記載的大
引句:「who = owner.get(i) or "檔:" + path」
file: `scripts/lumos:48802`
失敗場景:類別層級的註記身分帶檔路徑,而搬檔時改動前用舊路徑、改動後用新路徑(`old or path`、`new or path`)。
- 類別層級的 `@Config(sdk = [34])`(Robolectric 很常見,不是跳過)也中。
- 一次把整個套件搬家,每支檔各一條候選。
- 函式層級的註記不受影響。
重現:`t14.py`、`t2.py`。
```
14a 類別層級 @Config(sdk=[34]) 的檔,改名 FooTest.kt → FooRobolectricTest.kt:
    before rc=0 / after rc=1 tq/skip-added
14b 3 支同樣的檔整個目錄 a/ → b/:before rc=0 / after rc=1(3 條)
1b  函式層級 @Ignore 的檔搬家:兩版 rc=0
```
可行的收法:有改名配對時,改動前一側改用新路徑當身分。
歸因:有證據的修復回歸,但作者已記載為代價。

### F9 try 裡只有 `fail(...)`、catch 型別是 Throwable 或 Error 時,被新規則誤判為吞掉斷言
severity: minor
blocking: 否 — 只是候選,可放行;不影響漏報
引句:「# catch 接得住斷言失敗的型別:AssertionError 本身、或比它寬的 Error、Throwable(Kotlin 與 Java 寫法都認)」
file: `scripts/lumos:48733`(規則在 `_tg_catch_no_fail` 的新增分支)
失敗場景:`_TG_ASSERT_RE` 把 `fail(` 也算斷言,而第一條規則用 `_TG_TRY_OK` 豁免 try 裡的 `fail`,新分支沒有同樣的豁免。
重現:`t5.py` 的 6a。
```
try { h(); fail("should throw") } catch (e: Throwable) { assertTrue(e is IllegalStateException) }
  before rc=0 / after rc=1 tq/catch-no-fail,訊息「測試照樣綠」與事實不符(這段在 h() 不丟時會因為 e 型別不對而紅)
```
歸因:有證據的修復回歸(輕)。

### F10 恆真判斷漏掉同族寫法
severity: minor
blocking: 否 — 覆蓋面可更完整
引句:「if not re.search(r"[A-Za-z_]", re.sub(r"\b(?:true|false|null)\b", "", bare)):」
file: `scripts/lumos:48649`
失敗場景:判斷用「有沒有英文字母」,數字後綴 `1L == 1L`、`1.0f`、`0x10` 本身就有字母,而 `(g() || true) && true`、`g() || !false` 超出「結尾接 `|| true`」。
重現:`t5.py` 的 7f、7g、7i。這三種寫法兩版都 rc=0。
```
對照 7b assertTrue(2 > 1) / 7c assertTrue(g() || true) / 7j assertTrue("a" == "a"):before rc=0 / after rc=1
```
歸因:有證據的原有漏查(新規則的覆蓋面)。

### F11 CI 測試呼叫的任務名抽取把 `--tests` 與 `-Pxxxtest…` 都當任務
severity: minor
blocking: 否 — 候選可放行
引句:「_tg_count(hits, ("tq/ci-config:test-call", "", task))」
file: `scripts/lumos:48876`
失敗場景:`\b\w*[Tt]est\w*\b` 會抓到 `tests`、`FooTest`、`PtestMode`。拿掉 `--tests "FooTest"` 篩選(讓更多測試跑,是變強)會被當成「拿掉了呼叫測試的 Gradle 指令」。
重現:`t15.py`。
```
15a `testDebugUnitTest --tests "com.x.FooTest"` → `testDebugUnitTest`:
    before rc=1(整行) / after rc=1(tests、FooTest 兩條)
15e 拿掉 -PtestMode=full:after rc=1(PtestMode)
```
歸因:有證據的原有漏查(修前整行都擋,修後縮小但沒消除)。

## 圖譜鏡頭

- `lumos impact --diff` 固定席點到 `test-quality-cli`、`測試假綠形態`、`pitfalls-code-loop`、`bound-tests-gate` 等合約節點。我沒有發現修補違反其中任何 ★INVARIANT★ 的字面。
- `Systems/test-guard` 的 WHY「跳過標記的身分是函式名加跳過……類別層級另以所在檔區分」寫明代價是「測試檔整支改名時類別層級的跳過會被列一次」。F8 就是這個代價,實測範圍涵蓋 `@Config(sdk…)` 與整個目錄搬家,比記載的「跳過」大。
- 同一節點 WHY「比對自己出錯記成沒跑完並擋下」依賴截止時間。但 F6、F7 的平方級發生在單檔函式內(`_tg_ci_cands`、`_tg_build_hits`),`_tg_analyze` 每支檔、`_tg_test_rules` 每支函式才看一次截止時間,所以單檔病態輸入無法被這個機制攔下。
- 這條 WHY「比對花掉的時間不算進檢查命令預算,最壞兩倍」有 test 綁定;實測沒有違反。

## 三問

① 原問題的修復效果,行為證據(修前 → 修後)如下。
- 整檔重新縮排、CRLF、BOM、tab、尾端空白、註記跨行、註記之間插註解:`t12.py` 的 9a–9h 兩版都 rc=0。
- 跳過理由改字(9i)與 `@Ignore` 換 `@Disabled`(9j)、註記合併成同一行(9f):修前各列一條,修後 rc=0。
- 完整類別名 `@kotlin.test.Ignore`(8f)、`unitTests.all`、`tasks.named("testDebugUnitTest")`:修前 rc=0,修後列出。
- 一行寫的 `tasks.matching{…}.configureEach { enabled = false }` 與 `whenTaskAdded`:修前 rc=0,修後列出。
- `detekt { ignoreFailures = true }` 修前誤擋,修後 rc=0。
- 數量級:6 萬個同身分的跳過標記 167 秒降到 31 秒,2 萬個 `continue-on-error` 44 秒降到 20 秒。
- 這些修復成立,但上面 F1 到 F4 是同一輪修補帶出的新問題。

② 修補處的正常、錯誤、相鄰路徑。
- 正常路徑成立:9 組改格式與 S1 原有案例(函式層級搬檔、`@Ignore` 數量變化)不誤列。
- 錯誤路徑成立:多數 `@Ignore`/`expected =` 新增仍被列。
- 相鄰路徑出問題:CI 串接與 `-x` 前置(F2)、測試檔裡的門檻值(F3)、Kotlin DSL 的 exclude(F4)、try/catch 巢狀(F1)、多行 matching(F5)。

③ 新發現同一案例在修前、修後各是什麼結果。
- F1:5000 層巢狀,修前約 1.3 秒(6000 層量到),修後 35.1 秒。
- F2:兩個案例都是修前 rc=1、修後 rc=0。
- F3:兩個閾值案例都是修前 rc=1、修後 rc=0。
- F4:三個案例都是修前 rc=0、修後 rc=1。
- F5:兩版都 rc=0。
- F6:6 萬個命中,修前 167 秒、修後 31 秒。
- F7:各案例兩版時間相近(多數持平)。
- F8、F9:修前 rc=0、修後 rc=1。

證據不足、判不準的地方:F3 依規格第 126 行字面是否算違反,我只能報行為差異,由作者裁。

總結:本輪修補確實解掉多數第 1 輪問題,但新引入 4 條會誤擋或漏報的行為回歸(F1 巢狀 try 變慢、F2 CI 串接漏報、F3 門檻調高漏報、F4 Kotlin DSL 誤擋),另有 3 條殘留的平方級或同族漏報(F5、F6、F7),建議這 7 條處理完再過下一輪。
