severity: major

## 範圍與歸因界線

我只審 r3 修補差異,修前是 ea1e0b8a,修後是 22cc66758。我把兩版各 clone 一份,放在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/正確性-sonnet/before` 和 `after`。下文的「兩版命令」都是在這兩份上跑的。修後版跑 `-k tq_guard` 是 203 條全綠,`-k lint_new` 73 條、`-k lint_waive` 29 條也全綠。所以下面的問題都是「測試沒蓋到的輸入」,不是現有測試紅。

### F1 單行上限之下,類別本體判斷的泛型迴圈仍是「行長平方 × 行數」
severity: major
blocking: 是 — 守衛對 AI 可控的測試檔會跑到超過 300 秒預算,而且是修補自己新加的 Python 逐字迴圈
引句:「depth += 1 if stripped[k] == "<" else -1 if stripped[k] == ">" else 0」
file: `scripts/lumos:48451`

失敗場景:
- 測試檔裡每行都是 `class A<` 重複 2487 次(19896 字,在 2 萬字上限之內,且 `()`、`{}` 都平衡,所以不會被判 unparsable)。
- `_tg_class_has_body` 每遇到一個 `class A<`,就用 Python 迴圈從 `<` 掃到行尾,因為 `<` 永遠沒收尾,深度回不到 0。
- 一行約 1.5 秒,所以 250 行(5 MB 單檔上限內)推算約 400 秒。這是推算,沒有實跑到 250 行。
- 截止時間只在檔與檔之間檢查,單一檔不會被中斷。推送會卡到比對跑完,然後沒有候選就放行。
- 計劃 S11 與 `Systems/test-guard` 的 WHY 都說「外層看門、判錯代價不是卡到超時」,這個輸入打破了這句話。
- 修前的 `stripped.find(">", j)` 是 C 速度,這個形狀幾乎不花時間。

重現(CLI):在 git 專案放 `app/src/test/java/x/AT.kt`,基底是三行 `class AT { @Test fun a() { assertEquals(1, f()) } }`。提交後再追加 10 行,每行都是 `"class A<"*2487`,然後跑 `python3.14 <clone>/scripts/lumos test-guard --diff HEAD~1..HEAD`。
- 修前:1.26 秒。
- 修後:17.15 秒。
- 直接呼叫 `_tg_analyze`,30 行:修前 1.1 秒,修後 48.4 秒。
- 直接呼叫 `_tg_class_at`,50 行:修前 1.6 秒,修後 79.3 秒。

歸因:有證據的修復回歸。兩版同一輸入的耗時差了 13 到 50 倍。測試沒釘住它:`t_tq_guard_cli_contract` 的大輸入裡沒有「未收尾的 `<`」。

### F2 單行上限擋不住「長區塊開頭行 × 多內層行」,建置檔每行都重掃整個開頭
severity: major
blocking: 是 — 計劃宣稱已由外層上限收掉的規模族,在建置檔還剩一條平方路徑,單檔跑過 300 秒預算
引句:「or _tg_names_test_task(head) or _tg_names_test_task(line))」
file: `scripts/lumos:48864`

失敗場景:
- `build.gradle.kts` 的第一行是 `tasks.register("a") { ` 加約 19.9k 字,之後有 N 行內層,最後 `}`。
- `_tg_block_heads` 給每個內層行同一個 2 萬字的 head。`_tg_build_hits` 每一行都重跑 `_TG_TEST_BLOCK.search(head)`、`_tg_names_test_task(head)` 的三個正規式,以及 `_TG_NOT_TEST_PLUGIN.search(head + " " + line)`,後者還會每行重組一個 2 萬字的字串。
- 這是行長 × 行數的乘積。2 萬字上限只限了其中一個因子。
- 5 MB、10 萬行的限制之內都放得進去。
- 修法方向:head 衍生的布林值按 head 字串只算一次。

重現:用 `h.py` 的 `run`,基底與修後各 N 行內層,改一行 `val x0 = 1` 成 `val x0 = 2`,然後跑 `_tg_analyze`。
- CLI 3000 行:修前 7.72 秒,修後 11.82 秒。
- `_tg_analyze` 10000 行:修前 23.3 秒,修後 36.1 秒。
- `_tg_analyze` 9 萬行:修前 284.8 秒,修後 323.5 秒。

歸因:有證據的原有漏查。r2 版本同輸入已經 285 秒,r3 的 `_tg_names_test_task`、`ignore_fail` 讓它再慢約 13%。r3 號稱收掉規模族,卻沒量到「長行 × 多行」這個角落。

### F3 CI 拿掉測試任務:任務名黏著 `)`、`}`、`>` 時整個認不出來,是修補後的新漏
severity: minor
blocking: 否 — 覆蓋面縮小(普通 `run: ./gradlew test` 仍抓得到),只有子殼層、`$()`、無空白轉向這幾種寫法漏
引句:「if tok.startswith(("-", "$")) or "=" in tok:」
file: `scripts/lumos:48948`

失敗場景:
- `_tg_ci_test_tasks` 用 `split()` 取字,再對整個字做 `fullmatch(r"\w*(?:[Tt]est\w*|check)")`。
- `(cd app && ./gradlew test)` 的字是 `test)`;`out=$(./gradlew test)` 也是;`./gradlew test>out.txt` 的字是 `test>out.txt`。這些都配不上。
- 這些寫法的測試任務不進記錄,CI 檔把它們換成 `assemble` 時沒有候選。
- 修前用 `\b…\b` 的 `findall`,抓得到。

重現:拿兩版各自的 `scripts/lumos` 跑 `_tg_analyze`,基底與修後的 CI 檔是 `.github/workflows/ci.yml` 的 `- run: ` 這一行。`(cd app && ./gradlew test)` 改成 `(cd app && ./gradlew assemble)` 時:
- 修前:列 `tq/ci-config` removed test。
- 修後:無候選。
- `$()` 與 `test>out.txt` 的形狀結果相同。
- `{ ./gradlew test; }` 與 `./gradlew test` 改 `assemble` 兩版都列,所以只有黏著標點的寫法回歸。

歸因:有證據的修復回歸。

### F4 `-x test` 的等價寫法 `--exclude-task=test`、`-xtest` 抓不到
severity: minor
blocking: 否 — S8 的 `-x test` 本身抓得到,漏的是 Gradle 接受的等價拼法,工具自己也承認是近似判讀
引句:「if gradle[idx] and (_TG_CI_X.search(code) or _TG_CI_TRUE.search(code)):」
file: `scripts/lumos:48882`

失敗場景:
- `_TG_CI_X` 要求 `-x` 或 `--exclude-task` 後面接空白再接任務名。
- 我在本機 Gradle 8.13 實測:`gradle build -m` 會列 `:test SKIPPED`;加 `-xtest -m` 或 `--exclude-task=test -m` 後,`:test` 從清單消失,只剩 `:check SKIPPED`。這兩種寫法確實把測試排除了。
- CI 檔把 `./gradlew build` 改成 `./gradlew build -xtest` 或 `./gradlew build --exclude-task=test`,工具回 `(none)`。

重現:兩版同一命令都回 `(none)`,基底是 `- run: ./gradlew build`。

歸因:有證據的原有漏查。r3 沒動 `_TG_CI_X`,兩版同輸入結果相同。

### F5 assume 身分改帶整行:一行寫完的測試改斷言、改排版會被誤列,多行條件改成 false 抓不到
severity: minor
blocking: 否 — 誤列可放行;漏的是 assume 條件換行寫的形狀
引句:「hits.setdefault(("tq/skip-added", who, "跳過:" + _tg_norm(line)), []).append((path, i))」
file: `scripts/lumos:48840`

失敗場景(全部兩版對照):
- **改一行寫完的測試**。`@Test fun a() { assumeTrue(ok); assertEquals(1, f()) }` 改成 `assertEquals(1, f(2))`,assume 沒動。修前無候選,修後列 `tq/skip-added`,身分是整行文字。
- **換行重排**。`assumeTrue(Build.VERSION.SDK_INT >= 26 && … && isEmulator())` 被 ktlint 換行成 `assumeTrue(` 加條件一行加 `)`,修後列 `tq/skip-added`,身分是 `assumeTrue(`。
- **括號內空白**。`assumeTrue(isOk())` 改成 `assumeTrue( isOk() )`,修後列。
- **漏抓**。`assumeTrue(` 換行 `isOk()` 換行 `)` 的條件那一行改成 `false`,修前修後都無候選,因為身分只有 `assumeTrue(`。S1 要求「把既有 assume 的條件改掉」,這個寫法沒做到。
- `changeThreshold =` 換行 `0.01f` 改 `0.9f` 同樣漏。
- 另一組正向:同一行兩個 assume 刪成一個仍會列,因為行文字變了;`assumeTrue(x); assumeTrue(y)` 加成三個會列;註解的改動不會列(註解先被剝掉)。

歸因:誤列三種是有證據的修復回歸,修前無候選。多行漏抓是有證據的原有漏查,修前同樣無候選。

### F6 建置檔 `ignoreFailures` 全檔判:靜態檢查外掛的排除字表只認字詞邊界、只看最內層區塊開頭,同時多誤擋也多漏
severity: minor
blocking: 否 — 誤擋可放行;漏的要靠同一行或區塊開頭剛好出現外掛字樣
引句:「ignore_fail = _TG_IGNORE_FAIL.search(joined) and not _TG_NOT_TEST_PLUGIN.search(head + " " + line)」
file: `scripts/lumos:48868`

失敗場景(兩版對照,基底 `android {\n}\n` 加下列段落):
- **多誤擋**。以下寫法修前無候選,修後列 `tq/build-config`:
  - `kotlinter { ignoreFailures = true }`;
  - `configure<DetektExtension> { ignoreFailures = true }`(`\bdetekt\b` 配不上 `DetektExtension`);
  - `findbugs { … }`、`animalsniffer { … }`;
  - `detekt { reports { ignoreFailures = true } }` 這種內層區塊;
  - `kover { reports { verify { ignoreFailures = true } } }`。
  - S7 寫的是「detekt 的 ignoreFailures 不列」。
- **多漏**。以下兩個真測試放寬,修前列、修後無候選:
  - `tasks.test { ignoreFailures = true; finalizedBy(jacocoTestReport) }`;
  - `tasks.named<Test>("jacocoTest") { ignoreFailures = true }`。
  - 外掛字樣在同一行或最內層開頭時,整條被排除。
- `project(":coverage") { tasks.test { ignoreFailures = true } }` 這類擁有者在外層的形狀同樣漏。

歸因:有證據的修復回歸。兩版同輸入結果相反,見上。

### F7 類別宣告的父型別寫在下一行時,類別路徑整個丟掉,誤報被刪的是哪支函式
severity: minor
blocking: 否 — 候選還列得出來,只是指紋與行號指向另一支同名測試
引句:「if stripped.find("{", j, end) >= 0:」
file: `scripts/lumos:48462`

失敗場景:
- `class A` 換行 `    : Base() {`,或 Java 的 `public class A` 換行 `extends B {`,或 Kotlin 的 `class A<T>` 換行 `where T : X {`,新版的 `_tg_class_has_body` 只看到那一行結尾與下一個非空白字,判成沒有本體。
- 巢狀類別 A、B 各有一支 `t`,父型別都換行寫。刪掉 A.t 後,修前列 `Outer.A.t`,修後列 `Outer.t#2`,行號 9 指向仍然存在的 B。
- 修前兩版的 `_tg_class_at` 對 `class A\n    : B() {` 回 `'A'`,修後回 `''`。

歸因:有證據的修復回歸。`t_rg_methods_expression_body_and_backtick` 新加的兩個案例只覆蓋同一行有 `{` 的寫法。

### F8 單行上限也套在線性分析的 main、CI、建置檔上,CRLF 差一字
severity: minor
blocking: 否 — 誤擋可放行;CRLF 只差一個字元
引句:「elif _tg_has_long_line(b) or _tg_has_long_line(h):」
file: `scripts/lumos:49148`

失敗場景:
- 正式程式檔含一行 25k 字的字串常值(內嵌資料之類),只改別行,修後列 `tq/too-large`,身分帶新物件編號,所以該檔每改一次都要重新放行。
- 修前無候選,因為 `_tg_main_hits`、CI、建置檔都是逐行線性,不需要這道限制。
- CI 檔含一行 25k 字的 `echo`,修後也列,修前無。
- 剛好 2 萬字:LF 檔與沒有結尾換行的檔(含最後一行)都不列,20001 字列;CRLF 檔的內容剛好 2 萬字時,`\r` 被算進長度,所以會列。
- 基底裡有超長行、改動後才拆開的檔,也會列。

歸因:有證據的修復新增行為。修前同輸入無候選。

### F9 關閘留帳:比對自己出錯也寫 `skipped`,健檢文案仍寫「有候選沒判」
severity: minor
blocking: 否 — 只影響健檢摘要的字,不影響擋與不擋
引句:「kind = "skipped-env" if skip_env else "skipped"」
file: `scripts/lumos:38996`

失敗場景:
- `_lint_new_off` 在比對出錯時用同一個 kind 寫帳。
- `doctor` 對 `skipped`、`skipped-env` 的固定文案是「設定關掉時作弊比對有候選沒判 N 次」(`scripts/lumos:4153` 一帶)。
- 沒有任何候選、只是比對壞了,健檢仍會印「有候選沒判」。
- 這是讀程式得出的結論,我沒有另外起跑。

歸因:有證據的修復新增行為,是文案與帳種類不對應。

## 圖譜鏡頭

- 沒有固定席,我自己讀了 `Systems/test-guard`、`Systems/測試假綠形態`,並對照 `_rg_bracket_map` 搬位置,以下三條要改:
  - `Systems/test-guard` 的 WHY「任一行超過 2 萬字的檔不解析……外層看門不靠逐條判斷」與事實不符(F1、F2)。
  - 同節點的 WHY「ignoreFailures 只排除 detekt、ktlint 這類靜態檢查外掛與 JaCoCo 報表區塊」與 F6 不符。
  - 「assume 呼叫與比對門檻改帶正規化後的那一行」不涵蓋多行形狀(F5)。
- `Systems/room-guard`:`_rg_bracket_map` 從 `_rg_expr_end` 之後搬到 `_rg_balanced` 之後,邏輯逐行相同;隨機字串測試也綠,不影響 Room 守衛。
- `Systems/pitfalls-lint-adapter`:`_lint_new_classify`、`_lint_new_verdict` 的 `autopass_reason` 初始化不改變既有早退路徑,`-k lint_new` 73 條綠,我判不影響。
- `Systems/測試假綠形態`:F1 是第④型的邊緣例子——新增的大輸入測試沒有走到「未收尾的 `<`」這條會慢的分支。

## 三問

**① 原問題的修復效果(同一案例,兩版)**
- 單行上限:`# ` 加 20001 字的測試檔,修後列 `tq/too-large`,20000 字不列。
- assume 條件改值:`assumeTrue(isOk())` 改成 `assumeTrue(false)`,修前無候選,修後列 `tq/skip-added`。
- 改名加跳過:`@Ignore class AT` 搬到 `BT.kt`,修前列,修後不列;改名同時在方法加 `@Ignore`,修後列方法那一條;改名同時加類別層級 `@Ignore`,兩版都列。
- 恆真判斷:`assertTrue(1L == 1L)`、`0x10 == 16`、`1.0f == 1.0f`,修前無候選,修後列 `tq/assert-weakened`;`x1 == 1` 兩版都不列。
- CI 切段:`./gradlew -x lint test` 改 `-x lint assemble`,以及 `&&` 串接拿掉後半,修後都列;`echo "a && b" && ./gradlew test` 的任務名仍是 `test`。
- 以上都在「已驗」範圍。

**② 修補處的正常、錯誤與相鄰路徑是否仍成立**
- 不成立的相鄰路徑:F1、F2(大輸入)、F3(CI 黏著標點)、F6(建置檔排除字表)、F7(類別本體判斷)、F5 的誤列三種。
- 成立:`-k tq_guard` 203 條、`-k lint_new` 73 條、`-k lint_waive` 29 條全綠;`autopass_reason` 初始化後,`env_undone` 與「早退」兩條路徑仍照舊。
- 未驗:`_tg_start` 先收遠端主線的情況,我只靠 `t_tq_guard_cli_contract` 的本機 main 領先案例,沒有另外造多遠端的樣本。

**③ 新發現的同一案例,修前、修後各是什麼**
- F1:CLI 10 行,修前 1.26 秒,修後 17.15 秒。
- F2:CLI 3000 行,修前 7.72 秒,修後 11.82 秒;9 萬行分別是 284.8 秒與 323.5 秒。
- F3:`(cd app && ./gradlew test)` 改 `assemble`,修前列,修後無。
- F4:`-xtest` 與 `--exclude-task=test`,修前無,修後無(原有漏查)。
- F5:誤列三種,修前無,修後列;多行條件改 false,修前無,修後無。
- F6:`kotlinter`、`configure<DetektExtension>` 修前無、修後列;`tasks.test { …; finalizedBy(jacocoTestReport) }` 修前列、修後無。
- F7:`class A\n : B() {` 的類別路徑,修前 `'A'`,修後 `''`。
- F8:正式程式含 25k 字行,修前無,修後列 `tq/too-large`。
- F9:讀程式得出,沒有起跑對照。
- 未驗範圍:多遠端與多主線的 `_tg_start`;`-k t_rg_methods` 與 `-k test_guard_registered` 沒有重跑;沒有對 `docs` 差異做任何查核。

規模那一族在兩個角落仍未收乾淨(F1 是修補自己引入,F2 是上輪沒人看的角落),其餘多為覆蓋面或誤列。
