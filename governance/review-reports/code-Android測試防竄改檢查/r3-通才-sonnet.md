severity: major

(以下實驗都在我自己的 clone 裡做,用 ea1e0b8 對 22cc667 各跑一次;原 repo 沒動,暫存目錄已用字面路徑刪掉。)

### F1 建置檔點名測試任務的判法收窄,舊版抓得到的關測試寫法現在放過
severity: major
blocking: 是 — 守衛原本擋得住的作弊寫法,修補後靜默放過,而且測試沒蓋到
引句:「_TG_TEST_BLOCK = re.compile(r"(?i)(?<![\w])test\s*\{|\btasks\.test\b|withType\s*[<(]\s*Test\b|^\s*test\b|\bunitTests\.all\b")」
file: `scripts/lumos:48567`(`_TG_TASK_REF` 與 `_tg_names_test_task`,在 r3-repair-code.patch 的 `_TG_TASK_REF = re.compile(...)` 一帶)
失敗場景:舊版的 `_TG_TEST_NAMED_LINE` 只要同一行有引號字串含 test 就算點名測試任務。新版要求一行同時有 `tasks.matching/named/getByName/register/…` 之類的呼叫字樣和引號裡的 test。`tasks.findByName("testDebugUnitTest")?.enabled = false`、`tasks["testDebugUnitTest"].enabled = false`、`tasks.getByPath(":app:testDebugUnitTest").enabled = false` 都不在新字表裡。S7 r2 的測試只放 named、matching、getByName 三種,抓不到這個縮小。
重現:
```
build.gradle.kts 起點 "android {\n}\n",終點多一行 tasks.findByName("testDebugUnitTest")?.enabled = false
python3.14 <clone>/scripts/lumos test-guard --diff A..B --json --repo <臨時 repo>
```
- 修前(ea1e0b8):`[('tq/build-config', 'app/build.gradle.kts', 3)]`
- 修後(22cc667):`candidates: []`
- 同樣結果:`tasks["testDebugUnitTest"].enabled = false`、`tasks.getByPath(":app:testDebugUnitTest").enabled = false`。對照組 `tasks.named("testDebugUnitTest") { enabled = false }` 兩版都列。

歸因:有證據的修復回歸

### F2 try 裡有 fail 或 assertThrows 就整個跳過,吞掉斷言失敗的 catch 現在放過
severity: major
blocking: 是 — 作弊候選規則在新增 fail 就能繞過,舊版會列
引句:「if has("fail", c.end(), cb_end) or has("ok", t.end(), tb_end):」
file: `scripts/lumos:48750`(`_tg_catch_no_fail`)
失敗場景:舊版的第三道檢查是「try 有斷言、catch 接得住 AssertionError/Error/Throwable、catch 沒有 throw」。新版把 try 裡有 `fail`/`assertThrows`/`assertFailsWith` 改成直接 `continue`,第三道檢查連帶不跑。可是 `fail()` 丟的就是 AssertionError,`try { assertEquals(5, f(1)); fail("x") } catch (e: Throwable) { println(e) }` 的斷言失敗與 fail 都被吞。AI 只要在 try 結尾補一行 `fail()` 就能躲過。S6 r2 的 ok1 只涵蓋「catch 裡有斷言」,沒有「catch 只印出」的樣本,所以翻不紅。
重現:測試檔新增
```
@Test fun s1() { try { assertEquals(5, f(1)); fail("x") } catch (e: Throwable) { println(e) } }
```
- 修前:`tq/catch-no-fail CalcTest.s1`
- 修後:`[]`
- 第二個樣本:try 裡 `assertThrows(...) { a() }` 加 `assertEquals(5, f(1))`,catch AssertionError 只印出,修前列、修後 `[]`。
- 對照組(try 裡沒有 fail)兩版都列。

歸因:有證據的修復回歸

### F3 「5000 層巢狀 try」與「一行 4000 個中綴」的效能測試被單行上限短路,已不再走到被測的程式
severity: major
blocking: 是 — 測試註解宣稱「任一處逐命中重掃改回平方級 → 紅」,改壞實跑照綠(第④型:現場走不到被測分支)
引句:「nest = _tqg_kt("    @Test fun a() { " + "try { " * 5000 + "x()" + " } catch (e: Exception) { log() }" * 5000 + " }\n")」
file: `scripts/test_lumos.py:121346` 前的 `t_tq_guard_cli_contract`(S11 r2 巢狀 try;r1 的 `line = "; ".join(f"a{i} shouldBe {i}" for i in range(4000))` 同理)
失敗場景:這兩個樣本都是單行,長度約 19.5 萬字和 8.2 萬字,超過新加的 `_TG_MAX_LINE_CHARS = 20_000`,所以一律在 `_tg_analyze` 外層被列成 `tq/too-large`,根本沒進 `_tg_catch_no_fail` 和 `_tg_statements`。測試只量時間,沒有前置斷言證明樣本走到解析。
重現(改壞實驗,在 `mut` clone):
- M5:把 `_tg_catch_no_fail` 整支換回修前版本(逐 try 重掃),跑 `-k tq_guard_cli_contract` → `33 passed, 0 failed`。
- 同一個樣本用 CLI 量:修後 1.3 秒,回的是 `tq/too-large`,不是 `no-assertion`。
- 同樣的巢狀改成每層一行(5000 層),修前 35.5 秒,修後 1.7 秒。這證明修補本身有效,但沒有測試守它。
- M8:把 `_tg_statements` 的 `nls` 改成每個命中重算,`-k tq_guard_cli_contract` 同樣 `33 passed`。用多行的 5 萬行 `x shouldBe 1` 量:原版 1.9 秒,改壞 53.4 秒。
- 作對照,M6(`_tg_timeout_raised` 改回舊版)和 M7(`fresh_set` 改回 list)有翻紅,所以只有這兩處失效。

歸因:有證據的修復回歸(測試是這一輪的上限修補讓它失效)

### F4 類別宣告的父型別換行寫法,類別路徑丟了
severity: minor
blocking: 否 — 只讓函式鍵少了類別前綴,候選仍在,但位置與名稱可能指錯
引句:「nl = stripped.find("\n", j)」
file: `scripts/lumos:48430`(`_tg_class_has_body`)
失敗場景:新版只在「建構子之後那一行」找 `{`,或下一個非空白字就是 `{`。`class FooTest\n    : BaseTest() {`、`class FooTest(\n  val a: A,\n)\n    : Base() {`、Java 的 `public class FooTest\n    extends Base {` 都找不到本體。多行的 `@Inject constructor(\n...\n) {` 與 `private constructor(` 也一樣。S16 r2 只測單行 `@Inject constructor(...) {`。
重現:`_tg_functions` 對這些輸入,修前回 `['FooTest.t']`,修後回 `['t']`(多行 `@Inject` 兩版都是 `['t']`)。
再把兩個頂層類別(都是父型別換行)各有同名 `t`,刪掉 `FooTest.t`:修前列 `FooTest.t`(第 5 行),修後列 `t#2`(第 9 行,是 BarTest 的測試)。
歸因:有證據的修復回歸(多行 `@Inject` 那一型是原有漏查,S16 r2 只修到單行)

### F5 單行上限對正式程式、CI、建置檔也生效,而那三類沒有平方風險
severity: minor
blocking: 否 — 擋下可放行,但會對無害的檔反覆誤擋
引句:「elif _tg_has_long_line(b) or _tg_has_long_line(h):」
file: `scripts/lumos:49152`(`_tg_analyze`)
失敗場景:`_tg_main_hits`、`_tg_ci_hits` 對長行是線性的。含一行 2.5 萬字常數的 `Res.kt`,只改別處,現在列 `tq/too-large`。CI 檔有 2.1 萬字單行也一樣。
重現:`val BLOB = "AAAA…(25000 個)"` 在 main 檔,只把 `fun a()=1` 改 2。修前 `[]`,修後 `[('tq/too-large', 'app/src/main/java/x/Res.kt', 0, …:line)]`。CI 檔同樣。
歸因:有證據的修復回歸

### F6 這一輪新增或改寫的幾處判斷,改壞測試照綠
severity: minor
blocking: 否 — 覆蓋面,不是驗收條款的唯一驗證
引句:「h6 = c2({T: _tqg_kt(helper.replace("fun a()", "internal fun a()"))})」
file: `scripts/test_lumos.py`(S5 r2、S11 r2)
改壞實跑:
- M2:`_TG_MODIFIERS` 只留 `internal`,拿掉 public、private、open、static 等 → `-k tq_guard_no_assertion` 全綠。測試註解寫「internal、private、Java 去掉 public」,實際只測 internal 一種。
- M3:`_tg_has_long_line(b) or …` 改成只看 h,以及改成只對 test 種類判 → `-k tq_guard_cli_contract` 都 `33 passed`。基礎版有長行而終點正常、以及非測試檔,都沒有案例(F5 的行為也因此沒被測試描述)。
- M4:`_tg_retry_ok` 不剝 `//` 行註解,或 `true` 判斷改成「提到 failOnPassedAfterRetry 就算」→ `-k tq_guard_build` 都 `32 passed`。從 `git grep -E` 改寫成 Python 句式後,整支沒有測試。

歸因:未判定(新增的改寫本來就沒測試)

### F7 assume 條件跨多行時,條件改成永遠跳過仍抓不到
severity: minor
blocking: 否 — 只修到單行寫法,被依賴的是 S1 r2 條款
引句:「(assume 的條件改成永遠跳過、門檻數值調高都算新增)。」
file: `scripts/lumos:48630`(`_tg_test_hits`,身分取 `_tg_norm(line)` 一行)
失敗場景:`assumeTrue(\n    BuildConfig.HAS_EMU\n)` 改成 `assumeTrue(\n    false\n)`,第一行相同,身分相同,沒有新增。ktfmt 排版後的長條件常見這種寫法。重現:修前修後都是 `[]`。
歸因:有證據的原有漏查(兩版相同)

### 圖譜鏡頭
`lumos impact --diff 047031883..22cc667` 列出 `Systems/test-quality-cli`、`Systems/測試假綠形態`(★INVARIANT★)、`Systems/bound-tests-gate`、`Projects/Android測試防竄改檢查_計劃` 等。`Systems/測試假綠形態` 的 INVARIANT 要求翻紅釘附「現場成立」前置斷言,F3 的兩個效能測試正是缺這一條。標準檔 `test-quality-standard.md` 的「抓不到」那條,現在沒有 F1 的 `findByName`/索引寫法、F2 的 `fail()` 繞過,也沒有 F4、F7。S11 的逐字相同測試只是把兩邊釘住,不保證清單完整。

### 三問
1. 原問題的修復效果:規模一族確有行為證據。多行 5000 層巢狀 try 修前 35.5 秒、修後 1.7 秒;`x shouldBe` 5 萬行約 1.9 秒;8 萬個 assume(M7 能翻紅)、9 萬行建置檔(M6 能翻紅)有效。單行巢狀 try 與單行 4000 個中綴現在被上限短路,效果由上限提供,不是由逐點線性化提供(F3)。
2. 修補處相鄰路徑:建置檔點名測試任務(F1)、try/catch 的 fail 判斷(F2)、類別本體偵測(F4)、長行上限範圍(F5)四處有行為變化,其中 F1、F2、F4 修前能抓而修後抓不到。CI 呼叫測試任務的分段與跳旗標參數、`_tg_start` 遠端主線優先(改回舊行為會翻紅)、放行時間帶時區、`_lint_new_off` 比對出錯也記帳、`_tg_timeout_raised`、`_rg_bracket_map` 搬位置,我試過沒找到破口。
3. 同一案例修前修後:見 F1、F2、F4、F5 的兩版輸出;F7 兩版相同;F3 的巢狀 try 單行樣本兩版時間都約 1.3 秒,但修前走完整解析,修後直接 too-large。

F1、F2、F3 三條是這一輪修補讓守衛或測試變弱,其餘是覆蓋與邊角。
