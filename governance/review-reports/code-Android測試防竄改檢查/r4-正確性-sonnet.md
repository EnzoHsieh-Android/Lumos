severity: major

我用修前提交 22cc667 和修後提交 fcd2743 各載入一份,逐項對照。修後的 `-k tq_guard` 251 條全綠,但下面兩個 major 都不在它們的覆蓋範圍內。先說白話:這次「回到寬判法」把任務名的判斷收成「引號整個是任務名形狀」,又把區塊情境只看一行第一個左大括號之前的字。這兩個收窄動作漏掉了修前能抓到的兩種寫法。

### F1 任務名帶字串插值時,測試被關掉不再被抓到
severity: major
blocking: 是 — 守衛的核心功能(抓出關掉測試的改動)對修前能抓到的常見 Android 寫法失效,現有測試抓不到
引句:「_TG_TASK_NAME_Q = re.compile(r'["\']:?(?:[\w-]+:)*[\w-]*[Tt][Ee][Ss][Tt][\w-]*["\']')」
file: `scripts/lumos:48973`(`_tg_names_test_task` 用這條判斷點名)
失敗場景:
- 輸入是 Android 逐變體迴圈的 `tasks.named("test${v.name.capitalize()}UnitTest") { enabled = false }`,也包括 `'test$name'`。
- 引號裡有 `$` 和 `{`,不符合 `[\w-]` 的任務名形狀,所以 `_tg_names_test_task` 回 False,`in_test` 不成立,`enabled = false` 不列。
- 修前是「呼叫點名函式加引號裡含 test」,這種寫法會列。
- 我造了 3650 個「點名形式 × 任務名 × 關閉語句」組合做修前修後差異。名字含 `${}` 或 `$name` 的 190 個組合全部從「列」變成「不列」。
- 計劃 S7 清單與新測試都沒列插值名,所以測試全綠。
重現(兩版各跑一次,在 `scripts/lumos` 同目錄):
```
python3.14 -c "…load…; print(m._tg_build_hits('tasks.named(\"test\${name}UnitTest\").configure { enabled = false }\n'))"
```
- 修前:回 1 條 `tq/build-config`。
- 修後:回 `{}`。
端到端再驗一次:臨時 repo 裡把 `app/build.gradle.kts` 改成帶 `tasks.named("test${v.name.capitalize()}UnitTest") { enabled = false }` 的版本,執行 `lumos test-guard --diff HEAD~2..HEAD~1`。修前 rc=1、1 條候選;修後 rc=0、0 條候選。
歸因:有證據的修復回歸。兩版查證命令與結果如上,修前抓得到、修後抓不到。

### F2 一行開兩個區塊時,測試區塊判斷只看第一個 `{` 之前的字
severity: major
blocking: 是 — 修前會列的 `subprojects { tasks.withType<Test> {` 寫法修後不列;同一個根因還造成外掛區塊的誤報
引句:「pre = norm.split("{", 1)[0]」
file: `scripts/lumos:48990`(`_tg_block_heads`,`head_test`、`head_plugin` 都從 `pre` 算)
失敗場景(漏判,同根因另有誤報見下):
- 輸入是 `subprojects { tasks.withType<Test> {`,下一行是 `enabled = false`,再下一行是 `} }`。`pre` 只剩 `subprojects `,兩個區塊都被判成非測試區塊。
- 修前用整行開頭判斷,會列;修後不列。
- 同款漏判還有 `subprojects { tasks.withType(Test).configureEach {`、`afterEvaluate { tasks.named("testDebugUnitTest") {`、`allprojects { test {`、`afterEvaluate { android.testOptions.unitTests.all {`。我實測的 6 種寫法,修前全部列,修後全部不列。
同根因的誤報(外掛排除也只看 `pre`):
- 輸入是 `tasks.matching { it.name == "detekt" }.configureEach {`,body 是 `ignoreFailures = true`。
- 外掛名在第一個 `{` 後面,`NOT_TEST_PLUGIN` 看不到。
- 修前不列,修後列 `tq/build-config`。lint、jacocoTestReport、koverVerify、kover 也是同樣結果。
重現:
```
subprojects { tasks.withType<Test> {
    enabled = false
} }
```
- 修前 `_tg_build_hits` 回 1 條。
- 修後回 `{}`。
- 臨時 repo 用 `lumos test-guard --diff` 驗:修前 rc=1、修後 rc=0。
歸因:有證據的修復回歸。兩版查證命令與結果如上。

### F3 `} else {` 被當成鏈結,承接了前一個區塊裡的「點名測試」標記
severity: minor
blocking: 否 — 要前一個區塊裡剛好有名字像測試任務的引號字串才會誤報,有放行出口
引句:「in_test = head_test or bool(par and par[1]) or (after_close and closed_named)」
file: `scripts/lumos:48997`
失敗場景:
- 輸入是 `if (System.getenv("CI") != null) {`,內層有 `tasks.named("test") { maxParallelForks = 4 }`,接著 `} else {`,else 內有 `tasks.named("lint") { enabled = false }`。
- 前一個區塊內有一行點名 test,`closed_named` 為真,同一行緊接著開的 else 區塊被當成測試區塊。
- 內層 `tasks.named("lint") { enabled = false }` 因此被列成 `tq/build-config`,但它不是測試任務。
- 修前不列,修後列。`} else {`、`}.also {` 這類「`}` 與 `{` 之間夾別的字」都會中。
重現:
```
if (System.getenv("CI") != null) {
    tasks.named("test") { maxParallelForks = 4 }
} else {
    tasks.named("lint") {
        enabled = false
    }
}
```
- 修前 `_tg_build_hits` 回 `{}`。
- 修後回 `('tq/build-config', 'tasks.named("lint") {', 'enabled = false')`。
歸因:有證據的修復回歸。命令與結果如上。

### F4 catch 內用 Kotest 中綴斷言或 `check(` / `require(` 檢查時,被當成沒檢查而誤列
severity: minor
blocking: 否 — 只影響「try 結尾 fail、catch 接 AssertionError 再用非 `assert*` 風格檢查」這個少見組合,有放行出口
引句:「catch_checks = has("assert", c.end(), cb_end)」
file: `scripts/lumos:48820`(catch 內是否有檢查只看 `_TG_ASSERT_RE`)
失敗場景:
- 輸入是 `try { foo(); fail("x") } catch (e: AssertionError) { e.message shouldBe "x" }`。
- 檔案裡的 `_TG_ASSERT_RE` 不含中綴 `shouldBe`、`shouldContain`,也不含 bare `check(` 或 `require(`。這一版 `catch_checks` 判成 False,走到「吞掉斷言失敗」分支被列 `tq/catch-no-fail`。
- 修前 try 結尾有 fail 就整個豁免,不列;修後列。
- 同樣會中的還有 `catch (e: Throwable) { check(e is Foo) }` 與 `catch (e: Throwable) { require(e is Foo) }`,它們會拋例外讓測試失敗,並未吞掉斷言失敗。
- 同檔的 `_TG_INFIX_RE` 已把 `shouldBe` 當斷言,這處沒用到。
歸因:有證據的修復回歸。修前三個輸入皆回 False,修後皆回 True。

### F5 CI 判斷有兩條空白長度平方級的正則,5 MB 檔內可卡住數小時
severity: minor
blocking: 否 — 要有數萬字元以上的連續空白才會觸發,單人使用、非刻意輸入的情境下不會出現;但計劃〈資安〉一節寫了病態輸入不會變平方級
引句:「_TG_CI_TRUE = re.compile(r"\|\|\s*(?:true|:|exit\s+0|echo\b[^|&;]*)\s*$")」
file: `scripts/lumos:49018`;另一條在 `scripts/lumos` 的 `_TG_GRADLE_CALL`(未改動的尾段 `^\s*-?\s*(?:arguments|gradle_task)\s*:`)
失敗場景:
- **本輪新增:** `./gradlew build || echo ` 後接 N 個空格,再接 `x | y`。`[^|&;]*` 吃到 `|` 停下,`\s*$` 失敗後在空白段內逐位回退,平方級。實測 N=10000、20000、40000 依序要 0.39 秒、1.56 秒、6.24 秒;修前同輸入都是毫秒。
- **原有:** CI 檔任一行只有 N 個前導空白再接內容。`^\s*-?\s*` 的兩個 `\s*` 互相回退,N=10000、20000、40000 要 1.26 秒、5.0 秒、19.8 秒,修前修後相同。
- 單行上限只套測試檔,CI 檔沒有這道上限,檔案上限是 5 MB。
- 比對迴圈只在檔與檔之間檢查截止時間,正則執行中打斷不了。
歸因:前一條是有證據的修復回歸(修前 0.007 秒、修後 6.24 秒,N=40000);後一條是有證據的原有漏查(兩版 19.8 秒對 21.9 秒,N=40000)。

### F6 assume 訊息字串裡有未配對的左括號時,身分會吞進後面最多 2000 字的程式
severity: minor
blocking: 否 — 要 assume 訊息字串裡有孤立的 `(`(例如 `:(`)才發生,結果只是多報
引句:「stmt, span_end = _tg_stmt_at(kept, m.start())」
file: `scripts/lumos:49112`
失敗場景:
- 輸入是 `assumeTrue("a ( b", ci)`。`_tg_stmt_at` 沒有避開字串內容(`kept` 留字串),左括號被算進深度,深度回不到 0,敘述一路延伸到 2000 字上限。
- 這個 assume 的身分因此含後面的程式碼。實測 head 在它後面只多一行 `val z = 1`,身分就變了,同樣的 assume 被當成「新增跳過」。
- 修前用整行正規化,後面加程式不影響身分。
歸因:有證據的修復回歸。修前兩版身分相同,修後不同(輸入與結果如上)。

## 圖譜鏡頭
- `Systems/test-guard` 宣稱「assume 或比對門檻的整個敘述」當身分、「`LUMOS_SKIP_LINT_NEW` 只認 1」,與程式一致。
- 它的責任範圍也寫了測試函式切法與斷言判讀。F1、F2 讓它宣稱的 S7 建置檔偵測在這兩種寫法下失靈,筆記本身沒寫錯。
- `Systems/pitfalls-lint-adapter`:`_lint_new_autopass` 把狀態、原因、自動放行的原因一起寫。我核對了 `autopass` 的所有設定點,只有分類函式那一處和這個輔助函式,都帶得到原因,拿掉 `reason` 備援不會漏掉原因。
- `Systems/room-guard`、`Systems/測試假綠形態`:這次的差異沒碰共用的剝註解與括號配對函式,Room 守衛行為不受影響。
- 新測試的前置斷言與獨立判準大致合格。但它們的樣本都是「單行單區塊」,漏掉 F1、F2 這兩類形狀。

## 三問
1. **原問題修復效果的行為證據**
   - 「父型別換行」:輸入 `class Foo : Base(\n 1,\n 2\n) {`、`class Foo<T>\n where T : Any {`、`public class Foo\n extends Base {`、`implements A {`。修前函式鍵無類別前綴(`t`),修後是 `Foo.t`。
   - CI 的 `-xtest`、`--exclude-task=test`、`|| exit 0`、`|| echo`、`(./gradlew test)`、`$()`、轉向黏著:對 8 種呼叫前綴、8 種任務、16 種尾綴、7 種前綴共數千組輸入,修前能抓的修後都沒掉。
   - `build.gradle || echo` 不列:修前修後都不列。
   - 長行抹掉:臨時 repo 的測試檔加一行 25000 字,修後列 `tq/too-large`,其餘照比,另外列到 `tq/assert-weakened`,行號正確;修前只有 `tq/too-large`。
   - 修後 `-k tq_guard` 251 條全綠,`-k tq_guard_build_config` 48 條全綠。
2. **修補處的正常、錯誤與相鄰呼叫路徑**
   - 正常路徑成立:多行 `tasks.matching {…}.configureEach {` 現在抓得到(修前抓不到);預期例外寫法(try 結尾 fail、catch 接特定例外)、catch 重丟、catch 內用 assert 系列都不列。
   - 相鄰路徑出問題:F1、F2 是修前能抓、修後抓不到;F3、F4、F6 是新增的誤報。
   - 沒修好:`) : Base(),` 換行接 `Other {`、`class Foo :` 換行接 `Base() {`、Java `extends` 在行尾的寫法,類別路徑仍然是空的。這些只會讓同名測試的鍵編號與報告名稱變不精確,仍會列出候選,所以不算 finding。
   - 沒修好且修前就有:`}` 換行後用 `.configureEach {` 起頭的寫法(`tasks.matching {…}` 換行 `.configureEach {`)修前修後都不列。這種寫法在 Kotlin DSL 並不罕見,但不是這次修補造成。
3. **同一案例在修前、修後各是什麼結果**
   - F1:`tasks.named("test${name}UnitTest").configure { enabled = false }`。修前 1 條,修後 0 條。
   - F2:`subprojects { tasks.withType<Test> {` 接 `enabled = false`。修前 1 條,修後 0 條。
   - F3:`} else { tasks.named("lint") { enabled = false } }` 緊接在含 `tasks.named("test")` 的區塊後面。修前 0 條,修後 1 條。
   - F4:`catch (e: AssertionError) { e.message shouldBe "x" }`。修前 False,修後 True。
   - F5:`|| echo ` 後接 40000 個空格,修前 0.007 秒、修後 6.24 秒;前導 40000 個空格,兩版相同。
   - F6:`assumeTrue("a ( b", ci)` 後面加一行 `val z = 1`。修前身分相同,修後不同。
   - 未驗範圍:`lint-waive` 的 AI 放行標記與終端問人(這一輪沒動)、`_tg_retry_ok` 對含非 ASCII 路徑的 `git grep -l` 輸出是否被引號包住、實機推送路徑上的 `deadline` 行為。
   - 我在臨時 repo 的前提下驗證,沒改原 repo。

這一輪修補發現 2 個 major 回歸(任務名插值、單行雙區塊的區塊判斷)和 4 個 minor,都有兩版對照證據。
