severity: major

我的臨時目錄已用字面絕對路徑刪除,也沒有程序再開著它。以下重現命令都在 `/private/tmp/lumos-seat-work/code-Android測試防竄改檢查/邊界-sonnet/`(已刪)下跑過。我用 `git show` 取出修前版(22cc6675)與修後版(fcd27439)的 `scripts/lumos`,各自載入,對同一份輸入比對,再用臨時 git repo 跑 `lumos test-guard --json` 驗證。

### F1 點名測試任務改成純任務名形狀後,字串樣板的任務名全漏
severity: major
blocking: 是 — 漏報真作弊(標準的逐變體停用單元測試寫法修後抓不到),且是修前抓得到、修後抓不到的回歸
引句:「_TG_TASK_NAME_Q = re.compile(r'["\']:?(?:[\w-]+:)*[\w-]*[Tt][Ee][Ss][Tt][\w-]*["\']')」
file: `scripts/lumos:48490`(修後版 `_TG_TASK_NAME_Q`;`_tg_names_test_task` 只靠它點名)
失敗場景:引號內容必須整個是 `[\w-:]` 形狀才算點名。`"test${variant.name.capitalize()}UnitTest"`、`"test${v}UnitTest"` 含 `$` 和 `{`,整個不認。這正是 Android 逐變體引用測試任務的標準寫法。同族還有 `it.name == "test${v}UnitTest"` 和 `getByName("test${…}UnitTest").enabled = false`。
重現:
```
build.gradle.kts 新增:
android.applicationVariants.all { variant ->
    tasks.named("test${variant.name.capitalize()}UnitTest") {
        enabled = false
    }
}
lumos test-guard --repo R --diff A..B --json
修前: [('tq/build-config', 4)]
修後: []
```
函式層級也一樣:`_tg_build_hits` 對 `tasks.getByName("test${variant.name.capitalize()}UnitTest").enabled = false` 修前 1 筆、修後 0 筆。
歸因:有證據的修復回歸。修前版的點名判斷是「點名呼叫字樣加引號裡含 test」,這個寫法抓得到。

### F2 鏈結區塊判法只認同一行的 `}.configureEach {`,以 `.` 開頭換行的鏈結漏
severity: major
blocking: 是 — 漏報真作弊(Kotlin 鏈結換行的常見排版)
引句:「`tasks.matching { it.name.contains("UnitTest") }.configureEach {`(一行或換行寫):剛關掉的區塊裡有點名測試任務、」
file: `scripts/lumos:48478`(`_tg_block_heads` 的 `after_close` 只在同一行有效)
失敗場景:`after_close` 每行重設。鏈結的下一段寫在新的一行,以 `.` 開頭時,既不算「同一行剛關掉」,該行區塊開頭 `.configureEach {` 本身也沒有 Test 字樣,所以整個區塊不是測試情境。
重現:
```
tasks.withType<Test>()
    .configureEach {
        enabled = false
    }
```
另兩個同族輸入也是修前後都 0 筆:`tasks.matching { it.name.startsWith("test") }` 換行 `.configureEach {`,以及 `tasks` 換行 `.withType<Test>()` 換行 `.configureEach { enabled = false }`。對照:`tasks` 換行 `.named("testDebugUnitTest") {`(點名寫在 `.` 開頭那一行)兩版都抓到。
歸因:有證據的原有漏查(修前 0 筆)。但本輪宣稱把鏈結情境補齊,同族的換行寫法仍漏。

### F3 新增的 excludeTags/excludeCategories/excludeEngines 只認小括號呼叫,Groovy 與 `+=` 寫法漏
severity: major
blocking: 是 — 漏報真作弊(Groovy 的 build.gradle 是主流寫法)
引句:「re.compile(r"\bexclude(?:Tags|Categories|Engines)\s*\("))」
file: `scripts/lumos:48493`(`_TG_IN_TEST_BLOCK` 第三條)
失敗場景:Groovy 的 `excludeTags 'slow'`、`excludeEngines 'junit-vintage'`、`excludeCategories 'x'` 都沒有 `(`。Kotlin 的 `excludeTags += "slow"` 和 `excludeTags.add("slow")` 也漏。計劃 S7 說 Groovy 的 `x v` 寫法要認,這條新規則沒照做。
重現:
```
app/build.gradle 新增:
test {
    useJUnitPlatform {
        excludeTags 'slow'
    }
}
修前: []
修後: []
```
對照:`excludeTags('slow')` 修後 1 筆。
歸因:有證據的修復缺口。這條是本輪新加,只覆蓋小括號寫法;修前當然 0 筆。

### F4 `_TG_GRADLE_CALL` 加 lookbehind 後,路徑形式的 gradle 呼叫修前抓得到、修後漏
severity: major
blocking: 是 — 漏報真作弊(CI 加 `-x test`),是回歸
引句:「(?<![\w./-])gradle\s|\bgradle-build-action\b|\bgradle/actions\b"」
file: `scripts/lumos:48516`(修後版 `_TG_GRADLE_CALL`)
失敗場景:為了不把 `app/build.gradle` 檔名當成呼叫,lookbehind 排除了前面是 `/` 的 `gradle `。`/opt/gradle/bin/gradle build -x test`、`$GRADLE_HOME/bin/gradle build -x test` 因此不再算呼叫 Gradle。檔名需要排除的是 `.`,不是 `/`。另外,路徑形式的 wrapper 兩版都漏:`./android/gradlew build -x test`、`${GITHUB_WORKSPACE}/gradlew …`,因為第一個分支要求 `gradlew` 前面是空白或分隔符。
重現:
```
.github/workflows/ci.yml 的 run 改成 /opt/gradle/bin/gradle build -x test
修前: [('tq/ci-config', 4)]
修後: []
run 改成 ./android/gradlew build -x test → 修前 [],修後 []
```
歸因:`/opt/gradle/bin/gradle` 是有證據的修復回歸;路徑形式的 gradlew 是有證據的原有漏查(兩版都 0 筆)。

### F5 每層都有測試的深巢狀類別仍是平方級,超過 30 秒與記憶體上限
severity: major
blocking: 是 — 超過效能上限(計劃 S11 的 30 秒;計劃寫的「2 萬層巢狀類別 5 秒內、峰值 200 MB」只有葉子層才有測試的形狀成立)
引句:「(memo 只存被查過的那個節點」
file: `scripts/lumos:48419`(`_tg_class_path`)與 `scripts/lumos:48374`(`_tg_functions` 的 `key = (path + "." if path else "") + name`)
失敗場景:每個有測試的節點都組一整串路徑當函式鍵,鍵長總和是深度的平方。壓力測試只放一支葉子測試(`t_tq_guard_cli_contract` 的 121466 行),量不到這個。
重現(兩行一層:`class C{i} {` 換行 `@Test fun t{i}() { assertEquals(1,1) }`,結尾一次關閉):
```
N=20000:修前 45.7s / 5.75 GB;修後 22.6s / 4.07 GB
N=26000(測試檔只有 1.5 MB):修後 38.8s / 5.14 GB
只有葉子有測試(對照):修後 0.08s / 53 MB
```
`_tg_functions` 單獨量,峰值記憶體是 3000 層 98 MB、5000 層 205 MB、10000 層 766 MB、20000 層 3042 MB,明顯平方級。
歸因:有證據的原有漏查(修前更慢),修補只解了葉子形狀。

### F6 區塊堆疊把字串或字元裡的大括號也算進去,測試情境錯位
severity: minor
blocking: 否 — 要字串裡有不成對的大括號才觸發;誤報有放行出口
引句:「heads.append(stack[-1] if stack else "")」
file: `scripts/lumos:48533`(修後版 `_tg_block_heads`;它吃的是 `keep_strings=True` 的行)
失敗場景:
- 漏報:測試區塊裡的 `println("}")`、`systemProperty("x", "}")` 或三引號字串裡的 `}`,會把測試區塊提早彈出,後面的 `enabled = false` 不再算測試情境。
- 誤報(修後新增,因為現在繼承外層):`systemProperty("json", "{")` 留下一個永不關閉的幽靈區塊,把測試情境延伸到後面不相干的 `lint { enabled = false }`。
重現:
```
tasks.withType<Test> {
    println("}")
    enabled = false
}
修前 0、修後 0

tasks.withType<Test> {
    systemProperty("json", "{")
}
lint {
    enabled = false
}
修前 0、修後 1(head 為 lint {)
```
歸因:漏報是有證據的原有漏查;誤報是有證據的修復回歸(區塊情境改成含外層)。

### F7 assume 的敘述擷取把字串或字元裡的括號也配進深度,後面的行被吞進身分
severity: minor
blocking: 否 — 要 assume 裡有不成對的括號才觸發,誤報有放行出口
引句:「if not (t[i:k].rstrip().endswith(_TG_STMT_GOES_ON) or t[k + 1:k + 200].lstrip().startswith((".", "?.", "&&", "||"))):」
file: `scripts/lumos:48715`(`_tg_stmt_at`;它吃的是留字串的文字)
失敗場景:`assumeTrue(s == "(")`、`assumeTrue(c == '(')`、`Regex("(a|b")`、訊息 `"skip :("` 讓深度停在 1,換行不收尾,一路吞到 2000 字。之後 2000 字內任何無關行改動,身分都變成新的,於是列新增跳過。
重現:
```
@Test fun t() {
    assumeTrue(s == "(")
    assertEquals(1, f(1))   // 只把 f(1) 改成 f(2)
}
修前: []
修後: [('tq/skip-added', 3)]
```
歸因:有證據的修復回歸。修前身分只是一行,不受影響。

### F8 `_tg_retry_ok` 改成 `git grep -l` 再 `git show` 後,路徑被引號或超過 50 支時誤報
severity: minor
blocking: 否 — 要新增重試外掛,且設 true 的檔路徑特殊或有 50 支以上檔提到該字
引句:「for ref in r.stdout.splitlines()[:50]:            # git grep -l 對提交印「提交:路徑」」
file: `scripts/lumos:48849`(`_tg_retry_ok`)
失敗場景:`git grep -l` 預設把非 ASCII 路徑印成帶引號的八進位跳脫(`"\344\270\255/..."`),`git show` 找不到,判成沒有 true 設定。超過 50 支檔提到該字時,設 true 的那支排在後面也被截掉。
重現(新增重試外掛):
```
true 設定在 中文/build.gradle.kts:      修前 []、修後 [('tq/build-config', 'app/build.gradle.kts')]
60 支檔設 false,第 61 支(zz/)設 true:  修前 []、修後 多報一條 app/build.gradle.kts
```
`buildSrc/` 與 `build-logic/` 的 `.kt` 兩版都 `[]`,沒問題。
歸因:有證據的修復回歸(修前用 `git grep -h` 看行內容)。

### F9 測試任務裡的 `reports {}`、`jacoco {}` 內的 `enabled = false` 被當成停用測試
severity: minor
blocking: 否 — 舊 Groovy 風格才常見,有放行出口
引句:「in_test = ctx_test or line_test or _tg_names_test_task(line)」
file: `scripts/lumos:48563`(`_tg_build_hits` 的 `in_test`)
失敗場景:繼承外層測試情境後,`tasks.withType(Test) { reports { html.enabled = false } }`、`test { jacoco { enabled = false } }` 這些關報表、關覆蓋率的設定被列成測試被停用。`ignoreFailures` 有外掛排除,`enabled` 規則沒有。
重現:`tasks.withType(Test) { reports { html.enabled = false } }` 展開成多行,修前 0 筆、修後 1 筆(head 為 `reports {`);`test { jacoco { enabled = false } }` 同樣修前 0、修後 1。
另有 `} else {` 誤報:`if (x) { println("latest") } else { lint { enabled = false } }` 修前 0、修後 1。原因是 `closed_named` 不重設,任何帶 `"latest"`、`"test"`、`"kotlin-test"` 這類引號詞的 if 區塊,關掉後同行接開的 else 都被當成測試區塊。
歸因:有證據的修復回歸(「含外層」與「同一行接著開」是本輪改動)。

### F10 覆蓋面:同族寫法沒認到(各自兩版同為漏,多半是原有漏查)
severity: minor
blocking: 否 — 覆蓋面可更完整,逐項在計劃抓不到清單之外
引句:「# 失敗不擋:|| true、|| :、|| exit 0、|| echo …」
file: `scripts/lumos:48508`(`_TG_CI_TRUE`)與 `scripts/lumos:48456`(`_TG_TEST_BLOCK`)
失敗場景(每項我都實跑,修前修後同為 0 筆,除非另註明):
- **CI 吞失敗**:`./gradlew test; true`、`; exit 0`、`|| true;`、`|| (exit 0)`、`|| /bin/true`、`sh -c './gradlew test || true'`(尾端引號)都不列。YAML 折疊或 `|` 區塊裡 `-x test` 單獨寫在下一行不列,包括 `arguments: |` 換行 `-x test`。
- **try/catch**:`try { assertEquals(1,2) } catch (e: IOException) { throw e } catch (e: Throwable) { println(e) }` 只看第一個 catch,第二個吞掉不列。Java 的 `try (res) {` 不認。
- **測試任務選擇器**:`withType<AbstractTestTask>`、`withType<AndroidUnitTest>`、完整型別名、`testOptions { unitTests { all { it.enabled = false } } }`、點名跨行 `tasks.named(` 換行 `"testDebugUnitTest"` 換行 `) {`、無括號的 `tasks.test.get().enabled = false`。
- **其他停用寫法**:`setIgnoreFailures(true)`、AGP 的 `enableUnitTest = false`。
- **tasks 的 exclude 規則**:`test { exclude '**/integration/**' }`(規則要求字串含 `Test`)。
- **類別路徑**:`class A<T, U>` 換行 `where T : Foo,` 換行 `U : Bar {`,以及接 9 個介面的 Java 類別,類別路徑掉成 `t` 而非 `A.t`,兩版一致。
- **assume 太長**:assume 超過 2000 字時,尾端條件改成永遠跳過不列。
- **記憶體(誤判不影響)**:4.9 MB 全是 `{` 的建置檔,`_tg_build_hits` 峰值 564 MB(修前 123 MB);一個 `"` 後接 2.45M 個 `a:` 的建置檔,峰值 633 MB(修前 43 MB)。時間都在 3 秒內,沒超 30 秒。
歸因:`-xtest`、`--exclude-task=`、`|| exit 0`、`|| echo` 是本輪新增且確認有效(修前 0、修後有列);上列各項是有證據的原有漏查。記憶體兩項是修後變大,時間未超限。

## 圖譜鏡頭

`LUMOS-IMPACT` 範圍在會談專案算不出來,我改讀 `Systems/test-guard`(fcd27439 版)和計劃〈做法一〉〈驗收條款〉S1–S16,逐條對照程式。

- `Systems/test-guard` 寫「點名測試任務看引號裡是不是整個含 test 的任務名形狀」。這句是 F1 的設計來源。它沒寫「樣板字串的任務名」,而 S7 又說 findByName、`tasks[…]`、getByPath 都認。樣板字串寫法被排除在外,筆記沒有交代。
- 計劃 S11 寫「2 萬層巢狀類別 5 秒內」,測試只放葉子層測試,F5 的形狀沒被條款涵蓋。
- 計劃 S7 寫「三種寫法都認(Kotlin 的 `x = v`、Groovy 的 `x v`、Provider 的 `x.set(v)`)」,新增的 `excludeTags` 類只認 `(`,與 F3 衝突。
- 計劃 S6 明寫「try 結尾補 `fail()` 而 catch 接得住 AssertionError 又只印出或是空的,照樣要列」。我實跑 `try { foo(); fail("x") } catch (e: AssertionError) { println(e) }` 修後列出,符合條款,不算誤報。

## 三問回答

1. **原問題的修復效果有何行為證據?**
   - 確認有效:`-xtest`、`--exclude-task=test`、`|| exit 0`、`|| echo ok`、`build.gradle || echo`(不誤報)。
   - 其餘四項:
     - `findByName`、`tasks["…"]`、`getByPath` 這類引號純任務名,修前 0 筆、修後 1 筆。
     - `}.configureEach {` 同一行鏈結:修前 0、修後 1。
     - detekt、kotlinter 的 `ignoreFailures`(含單行、`configure<DetektExtension>`、內層 `reports`)修後不列,JaCoCo 兩種 exclude 與 fileTree、依賴的 exclude 修後不列。
     - 單行上限只套測試檔:正式程式、建置檔、CI 的長行不再列 `tq/too-large`;5 MB 單行的建置檔與 CI 都在 3 秒內。
   - 沒有完全生效:巢狀類別的記憶體只解了葉子形狀(F5);點名判斷收窄後漏了樣板字串(F1)。

2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 正常路徑:`tasks.named("testDebugUnitTest") { enabled = false }`、`tasks.withType<Test> { ignoreFailures = true }`、`./gradlew build -x test`、`./gradlew test || true` 都還抓得到。
   - 錯誤與不列路徑:detekt 與 JaCoCo 排除、`-x lint`、`-x detekt`、`pytest -x`、`build.gradle.kts || true`、CRLF 的 CI 都維持。
   - 相鄰路徑出問題:F1(樣板字串)、F4(路徑形式的 gradle)是修前抓得到、修後漏。F6、F7、F8、F9 是修後新增的誤報。

3. **新增發現的同一案例在修前、修後各是什麼結果?**
   - F1:`tasks.named("test${…}UnitTest") { enabled = false }` 修前 `[('tq/build-config', 4)]`,修後 `[]`。
   - F2:`tasks.withType<Test>()` 換行 `.configureEach { enabled = false }` 修前 `[]`,修後 `[]`。
   - F3:Groovy `excludeTags 'slow'` 修前 `[]`,修後 `[]`;`excludeTags('slow')` 修前 `[]`,修後 1 筆。
   - F4:`/opt/gradle/bin/gradle build -x test` 修前 `[('tq/ci-config', 4)]`,修後 `[]`;`./android/gradlew build -x test` 兩版都是 `[]`。
   - F5:20000 層每層一支測試,修前 45.7s / 5.75 GB,修後 22.6s / 4.07 GB;26000 層修後 38.8s / 5.14 GB。
   - F6、F7、F8、F9 的修前後數字已寫在各條重現裡。

五個 major(F1 到 F5)都附了修前修後的對照;兩個「原有漏查」(F2、F5)與三個「修復回歸或缺口」(F1、F3、F4)已分開標。

最高嚴重度為 major,共 5 條 major、5 條 minor。
