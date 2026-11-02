severity: major

## 範圍與做法
- 範圍:`22cc6675..fcd27439`(binding 確認,祖先關係成立),主要讀 `r4-repair-tests.patch`,對照 `r4-repair-code.patch`。
- 實驗在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/` 的 clone 做,修前版另開 worktree 對照。收尾時我已用字面絕對路徑刪光。
- 我也刪了自己跑測試留下的 14 個 `gctl-run-*` 現場,沒碰別的會談的。
- 改壞實驗共 22 處,其中 9 處在整份 `-k tq_guard`(251 條)或 `-k lint` 下仍全綠,列在 F4、F5、F6。

### F1 非測試檔拿掉單行上限後,建置檔與 CI 的正規式在長空白行上跑成平方級
severity: major
blocking: 是 — 5 MB 檔案上限之內的建置檔或 CI 檔,一行就能讓推送前比對卡死,deadline 在單次正規式比對裡中斷不了,違反 S11 的時限條款
引句:「(正式程式、建置檔、CI 是逐行線性,不設這道)」
file: `scripts/lumos:49293`(`_tg_analyze` 只對 `kind == "test"` 做 `_tg_has_long_line`)、`scripts/lumos:49005` 附近 `_TG_CI_TRUE`、`_TG_DEP_TEST`、`_TG_IN_TEST_BLOCK[1]`

失敗場景:
- 這輪把「單行超過 2 萬字」的上限收窄到只有測試檔,理由是其他三類檔「逐行線性」。這個前提不成立:
  - `_TG_DEP_TEST` 是 `\bdependsOn\s*\(?\s*...`,`dependsOn` 加 6 萬個空白實測 41 秒。
  - `_TG_IN_TEST_BLOCK[1]` 是 `\bexclude\s*\(?\s*["']...`,6 萬個空白實測 16 秒。
  - 這輪新增的 `_TG_CI_TRUE` 是 `echo\b[^|&;]*\s*$`,`|| echo` 後接 6 萬個空白再接 `;` 實測 13 秒。
  - 三個都是 `\s*` 與相鄰的貪婪量詞疊在一起,回溯變成平方級。
- 這些在修前被 2 萬字的行上限擋在外面。現在 5 MB 內的任意單行都放得進來,線性外推是數小時以上。
- 計劃筆記裡 r2 那條 WHY 寫的就是「逐點補線性補不完,外層看門」。這輪等於把外層門拿掉,只靠逐點補。

重現(兩版各跑一次,用真實 `_tg_analyze` 走 git repo 端到端):
- 建置檔:`dependsOn` 加 40000 個空白再接 `("y")`。
- CI:`./gradlew assemble || echo` 加 40000 個空白再接 `;x`。
- 修前 `22cc6675`:兩個都是 0.0 秒,回 `['tq/too-large']`。
- 修後 `fcd27439`:建置檔 18.6 秒、CI 6.0 秒,候選為空(沒列太大)。
- 把空白放大到 40 萬,依平方外推是十倍的十倍,即 100 倍以上的時間。
- 直接測正規式:`_TG_CI_TRUE.search("./gradlew test || echo" + " "*n + ";x")` 在 n=10000、20000、40000 分別是 0.39、1.57、6.27 秒。

最小修法:建置檔與 CI 也套單行上限,或把這些 `\s*\(?\s*` 改成不相鄰的寫法。

歸因:有證據的修復回歸(修前同輸入 0.0 秒,修後 18.6 秒)。

### F2 巢狀類別的記憶體修補只對「最深處一支測試」有效,每層一支測試仍是 GB 級
severity: major
blocking: 否 — 輸入要上萬層巢狀類別,且是修補不夠深而非新壞掉;但驗收條款的測試只涵蓋樣本最輕的形狀
引句:「check("S11 r3 2 萬層巢狀類別的記憶體峰值 200 MB 內(路徑不每層存一份整串)", _peak < 200 * 2**20, _peak // 2**20)」
file: `scripts/lumos:48541`(`_tg_functions` 的 `key = (path + "." ...) + name`)、`scripts/lumos:48460` 一帶 `_tg_class_path` 的 memo

失敗場景:
- 測試的樣本是 2 萬層類別、只在最深處放一支測試,所以只組一條路徑。
- 若每層類別各放一支測試,函式鍵本身就是整串類別路徑,總長是深度的平方。`memo` 再多存一份同樣的字串,記憶體約兩倍。
- 這個形狀在 5 MB 與 10 萬行上限內。

重現(`_tg_analyze` 端到端,每個 `class Ci {` 換行一支 `@Test`,尾端補右括號):
- 1 萬層(0.58 MB):2.2 秒、行程峰值 769 MB。
- 2 萬層(1.17 MB、4 萬行):7.6 秒、2753 MB。
- 依平方外推,10 萬行內最多約 5 萬層,約十倍以上、近 20 GB。
- 函式層(`_tg_functions`)對照,2 萬層每層一支測試:修前 21.3 秒、3673 MB;修後 7.4 秒、2838 MB。只改善 23%,不是測試宣稱的 200 MB。

歸因:有證據的原有漏查。修前同樣平方級,這輪只去掉每行存一份整串的那一半。

### F3 `--list` 清外來文字的測試只釘「理由」,檔名、規則、指紋三欄拿掉清理照綠
severity: major
blocking: 否 — 現行程式正確;但這是 S15 r3 該行為的唯一驗證,守衛被改壞測試抓不到
引句:「print(f"  {c(k, 80)}  {c(it.get('file', ''), 200)} [{c(it.get('rule', ''), 80)}] — {c(it.get('reason', ''), 300)}{_ai}")」
file: `scripts/lumos:37868` 一帶(`_lint_waive_show`);測試 `scripts/test_lumos.py` 的 `t_lint_waive_ai_marking` 末段

失敗場景:
- 新增的兩筆測試放行(k8、k9)只在 `--note`(理由)夾 `\x1b[8m` 與換行。`--rule` 和 `--file` 帶的都是正常值,指紋 `k` 也是正常值。
- `cmd_lint_waive` 對 `--file`、`--rule`、指紋完全沒驗證,三欄都能放控制字元。
- 把 `file` 與 `rule` 的 `c(...)` 拿掉,`-k lint_waive` 仍是 30 passed, 0 failed。

重現:
- 改壞 `{c(it.get('file', ''), 200)} [{c(it.get('rule', ''), 80)}]` 為不清理。
- 在 tmp git repo 跑 `lint-waive aaaa1111bbbb2222 --note <10 字以上理由> --rule tq/skip-added --file $'X.kt\x1b[8m' </dev/null` 再 `--list`。
- 改壞版輸出裡留著原始 ESC(`X.kt^[[8m [tq/skip-added] ...`),會把行尾的「AI 放的」標記藏掉。
- 現行版把 ESC 換成空白。

歸因:有證據的原有漏查(這輪新寫的清理只測了三欄中的一欄)。

### F4 `_lint_new_autopass` 四個呼叫點只有一個有測試,而讀取端的退路已經刪掉
severity: minor
blocking: 否 — 現行四處都經由同一支寫;缺的是各路徑的翻紅測試
引句:「_lint_new_autopass(out, dep_err)」
file: `scripts/lumos:39100`(另有 `:39087` 的 `err`、`:39109` 的 `werr`,和 `:38967`)

失敗場景:
- 這輪讀取端刪了 `or reason` 退路,所以每個呼叫點都是 `autopass_reason` 的唯一來源。
- 測試只走「範圍算不出版本代號」這一個點,即 `ha` 那個樣本。
- 把 `err`、`dep_err`、`werr` 三處各自改回舊寫法 `out.update(status="env-unavailable", autopass=True, reason=...)`,不寫 `autopass_reason`。
- 三個改壞各自跑 `-k lint`:各 501 passed,3 failed。那 3 個失敗是原本就紅的 `t_lint_files_substitution_has_one_implementation`,見圖譜一節。
- 結果是帳和小結退回「有檢查命令跑不動」或「原因不明」。

這違反你全域 CLAUDE.md 的規則:「每組替所有相似的程式路徑各寫一支先紅的測試,不只被點名的那條」。

歸因:有證據的原有漏查(同一輪新增的 helper 與讀取端改動沒配到各路徑測試)。

### F5 新增的判讀分支有一批沒有各自翻紅的測試(改壞全綠)
severity: minor
blocking: 否 — 現行行為合理;缺的是釘子
引句:「_TG_STMT_GOES_ON = ("=", ",", "(", "+", "&&", "||")」
file: `scripts/lumos:48940` 一帶(`_tg_stmt_at`)、`:48999` 一帶(`_TG_CI_TRUE`、`_TG_CI_X`)、`:48460` 一帶(`_tg_class_has_body`)

整份 `-k tq_guard`(251 條)或對應子集下全綠的改壞:
- `_TG_STMT_GOES_ON` 只剩 `("=",)`,即拿掉 `,`、`(`、`+`、`&&`、`||`。
- 拿掉 `startswith((".", "?.", "&&", "||"))` 那一支。
- `depth < 0` 時的 `break` 改成 `pass`。
- `_TG_CI_TRUE` 拿掉 `:` 這個寫法(`|| :`)。
- `_TG_CI_X` 拿掉引號的 `["']?`。
- `_tg_supertype_next_line` 拿掉 `,`。
- `_tg_next_stop` 快取的下界 `nxt[0] <= j`。
- `_TG_GENERIC_MAX` 改成 10**9。
- `exclude(?:Tags|Categories|Engines)` 縮成 `excludeTags`。
- `_TG_NOT_TEST_PLUGIN` 裡的 spotless、checkstyle、pmd、spotbugs、findbugs、animalsniffer 整批拿掉。

其中 `depth < 0` 那一個有可觀察的行為差,實測:
- 範例:`@Test fun a() { assumeTrue(ok) }` 後面接 `@Test fun b() { assertEquals(1, f()) }`,只把 b 的 `1` 改成 `2`。
- 現行版:a 的 assume 身分前後相同,不列。
- 改壞版:a 的身分被吞進後面一個測試的文字,**新增跳過**被誤列(`跳過:assumeTrue(ok)}@Testfunb(){assertEquals(2,f())}}`)。
- 現行測試用的樣本都有 `;` 收尾,蓋不到。

歸因:有證據的原有漏查。

### F6 `|| echo`、`|| :`、`|| exit 0` 加進去後,同一個「把檔名當成在叫 Gradle」的誤報只修了一半
severity: minor
blocking: 否 — 候選可放行,是誤報
引句:「# `gradle ` 前面不能緊接 . / 或字:`app/build.gradle || echo` 是檔名,不是在叫 Gradle」
file: `scripts/lumos:49005`(`_TG_GRADLE_CALL`)

失敗場景:
- 這輪只對 `gradle\s` 那條加了 `(?<![\w./-])`。
- 第一條 `(?:^|[\s;&|(:])(?:\./)?gradlew?...\b` 對前面是空白的 `gradle/wrapper/...`、`gradle.properties`、`gradle-wrapper.properties` 仍成立,同一個誤報族還在。
- 新放寬的失敗不擋寫法讓它露出來。

重現(CI 檔基底 `./gradlew test`,再加一行):
- `grep distributionUrl gradle/wrapper/gradle-wrapper.properties || echo none`:修前不列 `tq/ci-config`,修後列。
- `cat gradle.properties || echo missing`、`ls gradle || :`、`cd gradle || exit 0`:同樣修前不列、修後列。
- `cat gradle.properties || true` 修前就列(原有)。

歸因:有證據的修復回歸(新寫法新增的誤報面),同族根因是原有。

### F7 回到寬判法後,測試任務區塊的外層與鏈結繼承多出幾個誤報
severity: minor
blocking: 否 — 候選可放行,是誤報
引句:「in_test = head_test or bool(par and par[1]) or (after_close and closed_named)」
file: `scripts/lumos:48899` 一帶(`_tg_block_heads`)

重現(`_tg_build_hits`,修前 → 修後):
- `tasks.test { jacoco { enabled = false } }`:不列 → 列。外掛排除只套 `ignoreFailures`,沒套 `enabled=false`,而外層測試區塊現在向內繼承。
- `if (c) { dependsOn("testDebugUnitTest") } else { enabled = false }`(換行寫法):不列 → 列。`closed_named` 是整個函式的狀態,`} else {` 被當成 `}.configureEach {` 的鏈結。
- `create("qaTest") { firebaseCrashlytics { enabled = false } }`:不列 → 列。引號裡含 test 的名字都算點名,連 flavor 名字也算。

歸因:有證據的修復回歸。

## 圖譜鏡頭
- 讀了 `Systems/test-guard`、`Systems/測試假綠形態`;`LUMOS-IMPACT` 的範圍在我這邊算不出來,沒附。
- `Systems/test-guard` 的 WHY「(正式程式、建置檔、CI 是逐行線性,不設這道)」對建置檔與 CI 被 F1 的實測推翻。這是程式碼答得了的現況描述,依 CLAUDE.md 以程式碼為準,該筆記句子需要改,並應補一則 Issue。
- 圖譜「INVARIANT:還原翻紅釘必須配前置斷言」大致有守到:S11 的中綴、巢狀 try、CI 樣本都有 `★前置★`。F2 的 S11 r3 記憶體測試只有「類別路徑算得出來」的前置,沒有「每層都有測試」這個形狀。
- 順帶:`t_lint_files_substitution_has_one_implementation` 在修前版與修後版的 clone 裡都是 2 條斷言紅(白名單裡 `_lint_new_verdict` 已不碰佔位符、`_lint_new_run_cmds` 在名單外)。兩版都紅,不歸因於這輪;你們的推送前閘全套若是綠,可能是我這個 clone 環境的差異,⚠ 未判定。
- pitfalls manifest 只有 ruff 舊告警,略過。
- 慣例:無逐字可引的違反。

## 三問
1. **原問題的修復效果有何行為證據?** 有,修前 → 修後直接呼叫:
   - 建置檔:`findByName`、`tasks[…]`、`getByPath`、`it.name ==`、withType 巢狀 if、換行的 matching 鏈結、同一行帶 jacoco 字樣的 `tasks.test`、測試區塊加 `excludeTags`,八個都是不列 → 列。
   - catch:`try { assertEquals; fail() } catch (Throwable) { println }`、`catch (AssertionError) {}` 不列 → 列。
   - 類別路徑:父型別換行、建構子跨行再接父型別、Java extends 換行,鍵由 `['t']` 變 `['FooTest.t']`。
   - 我另對本機 96 份建置檔、87 份 CI 檔、46 份測試檔跑修前版與修後版:命中集合與鍵完全一致,沒有回歸。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 大部分成立,三處不成立:
   - 正常路徑:預期例外寫法(try 結尾 `fail()`、catch 接特定例外)、catch 重丟、JaCoCo 兩種 exclude、依賴的 exclude、detekt、kotlinter、`dependsOn("testX")` 都維持不列。
   - 相鄰路徑:`_tg_read` 與 `_tg_class_at` 只有 `_tg_analyze`、`_tg_functions` 在用;`_TG_GRADLE_CALL` 只在 `_tg_ci_*` 用,Room 守衛不受影響。
   - 不成立:F1 的相鄰路徑(建置檔、CI 的長行)被打穿;F2 的深巢狀每層一支測試;F6、F7 多出的誤報。
   - `LUMOS_SKIP_LINT_NEW` 只認 1,與其他 `LUMOS_SKIP_*` 的 `== "1"` 一致。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - F1:修前 `tq/too-large`、0.0 秒;修後建置檔 18.6 秒、CI 6.0 秒、候選為空。
   - F2:函式層修前 21.3 秒、3673 MB;修後 7.4 秒、2838 MB;端到端(修後)1 萬層 769 MB、2 萬層 2753 MB。
   - F6:修前 `grep … gradle-wrapper.properties || echo none` 不列;修後列。
   - F7 的三個樣本:修前都不列、修後都列。
   - F3、F4、F5 是現行行為正確、測試抓不住,所以兩版結果相同。

本輪最嚴重的是第 1 條:這輪把單行上限收窄到只剩測試檔,讓建置檔與 CI 的幾支非線性正規式重新暴露,實測 40000 個空白就從 0.0 秒變成 18.6 秒。
