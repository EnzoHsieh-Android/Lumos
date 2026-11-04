severity: major

以下八條 major 都有可重跑的重現。重現用的臨時 repo 在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/邊界-sonnet/<名>/`,指令是 `python3.14 /Users/enzo/harness/lumos-tq-android/scripts/lumos test-guard --repo <那個目錄> --diff HEAD~1..HEAD`。

### F1 同一支測試檔新增很多跳過標記時,候選定位是平方級:5.4 萬行檔跑 71 秒,超過 S11 的 30 秒
severity: major
blocking: 是 — 超過驗收條款 S11 寫死的 30 秒效能上限,而且 S11 現有壓力測試沒有走到這條路徑
引句:「path, ln = next(((p, _tg_line_of(h, line)) for p, _b, h, _fb, _fh, _kt in test_files if _tg_line_of(h, line)),」
file: `scripts/lumos:49080`(`_tg_hit_cands`)與 `scripts/lumos:48916`(`_tg_line_of`)
`_tg_hit_cands` 對每個新增的跳過標記或門檻字樣各呼叫一次 `_tg_line_of`(條件和取值各算一次)。每次呼叫從檔頭逐行做 `_tg_norm`(正規式替換)找子字串,所以是「命中數 × 檔行數 × 變動檔數」。
重現:
- `e1`:5.4 萬行、3000 支測試,每隔一支加一行不同的 `@Ignore("r{i}")`,共 1500 個命中。
- 指令是 `python3.14 .../scripts/lumos test-guard --repo .../e1 --diff HEAD~1..HEAD`。
- 實測 `rc=1`,耗時 71.1 秒;用 cProfile 看,`_tg_line_of` 占 99%,呼叫 8300 萬次 `_tg_norm`。
- `e9`:300 支檔、每檔 405 行、各加一個不同的 `@Ignore("flaky i")`,耗時 16.7 秒,隨檔數平方成長,500 支檔約 45 秒。
- 作者的 S11 壓力案例(6 萬行、2000 處預期值被改)走的是 `_tg_fn_cands` 路徑,我實測只要 2.0 秒,沒碰到這條。

### F2 同一行有多個 `should*` 中綴斷言時是平方級,而且截止時間在規則階段完全不生效;用 `LUMOS_SKIP_LINT_NEW` 也逃不掉
severity: major
blocking: 是 — 超過 S11 的 30 秒效能上限,也違反 S13 要求的「超過截止時間記成沒跑完並擋」
引句:「out.append(re.sub(r"\s+", " ", rb[ls:le if le >= 0 else len(rb)]).strip())」
file: `scripts/lumos:48500`(`_tg_statements`,中綴斷言迴圈),截止時間檢查在 `scripts/lumos:48940` 附近(`_tg_analyze` 的 `for kind, old, new, new_sha in rows` 迴圈)
- 每個 `shouldXxx` 命中就把「整行」當成一條斷言敘述,命中數 n 乘以行長 L 就是平方級。
- 這個迴圈沒有條數上限,`out[:_TG_MAX_STMTS]` 在迴圈跑完才截。
- 兩邊的敘述再各自進 `_tg_pairs` 和 `_tg_expected_changed`,每條都是整行字串。
- 截止時間只在 `_tg_analyze` 逐檔迴圈開頭看;`_tg_test_rules` 在迴圈外面,整段沒有檢查。
重現:
- `hl1000`、`hl2000`、`hl4000` 是同一支 `@Test` 本體只含一行 `a0 shouldBe 0; a1 shouldBe 1; …`,第二版在行尾再加一個 `shouldBe`。
- 實測耗時 2.2 秒、5.3 秒、17.1 秒,約 6000 個命中就破 30 秒。
- 用 `python3.14 dl.py <hl4000 目錄> skip` 直接呼叫 `_lint_new_verdict(..., deadline=monotonic()+3)`:
  - 設 `LUMOS_SKIP_LINT_NEW=1` 時,3 秒的截止時間不生效,輸出 `status off ... 15.7s`;
  - 不設該變數時同樣跑完 15.6 秒才 `blocked`,沒有記成沒跑完。
- 影響:`Systems/test-guard` 寫的「比對程式錯時用 `LUMOS_SKIP_LINT_NEW` 逃生」,在比對卡在病態檔時逃不掉。off 與環境變數跳過的路徑一樣照跑整個比對(S14)。
- 副作用:同一行的 n 個中綴斷言產生 n 條相同敘述,一處編輯就吐出 n 條指紋相同的候選(hl4000 吐 2000 條)。

### F3 只要改到呼叫 Gradle 測試的 CI 指令行,就被判成「拿掉了呼叫測試的 Gradle 指令」
severity: major
blocking: 是 — 正常的 CI 調整(加旗標)被擋推送
引句:「extra="拿掉了呼叫測試的 Gradle 指令:" + line[:80]))」
file: `scripts/lumos:48860`(`_tg_ci_cands` 的 `ci-config:test-call` 反向差集)與 `scripts/lumos:48800`(`_tg_ci_hits` 的 `test-call` 身分)
- 身分是整行正規化文字。只要那一行的文字有任何不同(加 `--stacktrace`、`--no-daemon`、`| tee`、`--tests`、`-x lint`),改前的那行在改後找不到,就被當成指令被拿掉,同時改後新行的 hit 沒人比。
- 計劃 S8 寫的是「刪掉呼叫 Gradle 測試任務的指令」,沒有寫「改了旗標」。`t_tq_guard_ci_config` 也沒有「改旗標不列」的案例。
重現:`ci_add_flag` 把 `- run: ./gradlew testDebugUnitTest` 改成 `... testDebugUnitTest --stacktrace`。
```
作弊候選 1 條
  .github/workflows/ci.yml:8 [tq/ci-config] CI 的 Gradle 步驟可能讓測試失敗不擋或不跑(拿掉了呼叫測試的 Gradle 指令:- run: ./gradlew testDebugUnitTest)
rc=1
```
`ci_add_nodaemon`(加 `--no-daemon`)、`ci_pipe_cat`(加 `| tee out.log`)結果相同。

### F4 預期值被改、同時在它前面插一條新斷言,漏報 `tq/expected-changed`
severity: major
blocking: 是 — 漏報核心作弊場景「改預期值」的同族寫法
引句:「out.extend(zip(old[i1:i2], new[j1:j2]))」
file: `scripts/lumos:48535`(`_tg_pairs`)
- `replace` 區塊兩邊長度不同時,按位置硬配對。被改的那一條若不在新清單的同一位置,就配到不相干的新斷言,`_tg_expected_changed` 判成不同呼叫、不列。
- S4 只釘「中間插一條不列」,沒釘「插入加上改值同一次」。
重現:`ins_before`,改前只有 `assertEquals(5, total(list))`。改後:
```
+        assertNotNull(r)
+        assertEquals(6, total(list))
```
輸出 `作弊候選 0 條`、`rc=0`。把新斷言放在後面(`ins_after`)就正確列出 `tq/expected-changed`。

### F5 常值判斷只認字面常值:`|| true`、`assertThat(true).isTrue()`、`assertTrue(1 == 1)` 都漏;強斷言的計數還會被訊息字串騙
severity: major
blocking: 是 — S3 明列「`assertTrue(r.isValid())` 改成 `assertTrue(true)`」要列,同族寫法全漏
引句:「return bool(sp and sp[2] and all(_TG_CONST.fullmatch(a) for a in sp[2]))」
file: `scripts/lumos:48463`(`_tg_const_stmt`)與 `scripts/lumos:48494`(`_tg_strong`,用含字串內容的原文敘述比對)
重現:改前都是 `assertTrue(r.isValid())`,改後分別是下面的寫法,全部輸出 `0 條`、`rc=0`:

| 目錄 | 改後的斷言 |
|---|---|
| `taut_or_true` | `assertTrue(r.isValid() \|\| true)` |
| `taut_truth_true` | `assertThat(true).isTrue()` |
| `taut_one_eq_one` | `assertTrue(1 == 1)` |
| `taut_notnot` | `assertTrue(!false)` |
| `msg_bypass`(改前是 `assertEquals(3, n)`) | `assertTrue(n > 0, "assertEquals 3")` |

- 最後一列的成因:`_tg_strong` 用 `_TG_STRONG.search(s)` 搜原文敘述,字串裡的 `assertEquals` 也算一個強斷言,所以強斷言數沒降。
- 此外 `assertThat(x).isTrue()` 改成 `isFalse()`、`isEmpty()` 改成 `isNotEmpty()`(`truth_flip`、`truth_empty`)也不列,因為只有 `assertTrue/False/Null/NotNull` 做了方向互換。

### F6 JUnit 5「訊息放最後」的 `assertEquals` 位置判錯:字串預期值被改漏報,只改訊息反而誤報
severity: major
blocking: 是 — 同一個判錯同時造成漏報(核心作弊)和誤擋(正常改字)
引句:「if len(args) == 3 and _TG_LIT.fullmatch(args[0].strip()):」
file: `scripts/lumos:48440`(`_tg_split_first_arg`),`kotlin_test` 只由 `import kotlin.test.` 判斷(`scripts/lumos:48974` 附近)
- 檔案匯入 `org.junit.jupiter.api.Assertions`(訊息在最後)時,仍照 JUnit 4(訊息在前)切。
- 3 個參數而第一個是字串常值,就被當成訊息,真正的預期值被丟掉。
- 3 個參數而第一個不是字串,第三個(訊息字串)被當成 `delta` 放進預期值。
重現:
- 漏報,`j5_str_expected`:`assertEquals("Alice", name, "msg")` 改成 `assertEquals("Bob", name, "msg")`,輸出 `0 條`、`rc=0`。
- 誤報,`j5_msg_only`:`assertEquals(5, total, "m1")` 改成 `assertEquals(5, total, "m2")`,列出 `tq/expected-changed`。
- `t_tq_guard_expected_changed` 沒有 Jupiter 匯入的案例。

### F7 建置檔只認 `named("test")`:Android 真正的單元測試任務 `testDebugUnitTest` 被關掉漏報
severity: major
blocking: 是 — Android 模組裡沒有叫 `test` 的任務,S7「`test {}` / `withType<Test>` 內的 `enabled = false`」在 Android 實際寫法上抓不到
引句:「_TG_TEST_BLOCK = re.compile(r"(?i)(?<![\w])test\s*\{|\btasks\.test\b|withType\s*[<(]\s*Test\b|named\s*[<(][^)]*[\"']test[\"']|^\s*test\b")」
file: `scripts/lumos:48160`(`_TG_TEST_BLOCK`)
重現:`app/build.gradle.kts` 的 `named_testDebug` 新增一行:
```
tasks.named("testDebugUnitTest") { enabled = false }
```
輸出 `0 條`、`rc=0`。
- 同樣漏報(rc=0):`android.testOptions.unitTests.all { it.enabled = false }`(`unitTests_all`)、`tasks.whenTaskAdded { if (name.startsWith("test")) enabled = false }`、`tasks.matching { it.name.contains("UnitTest") }.configureEach { enabled = false }`。
- 對照:`named("test")` 和 `withType<Test>` 會列。

### F8 try 區塊有斷言、catch 只印記錄,漏報 `tq/catch-no-fail`
severity: major
blocking: 是 — S6「try 沒 fail」同族的最常見吞例外寫法(`println`、`printStackTrace`、`Log.e`)漏報
引句:「if (_TG_ASSERT_RE.search(cb) or not cb.strip()) and not _TG_TRY_OK.search(tb):」
file: `scripts/lumos:48180`(`_tg_catch_no_fail`)
- 只有 catch 本體含斷言字或是空的才列,catch 本體是 `println(e)` 就放過。
- 另外它不要求 try 區塊有斷言:清理程式碼的空 catch 也會被列(誤報)。
重現:`catch_exception_nofail`,改前測試本體是 `assertEquals(5, f(1))`,改後:
```
try {
    assertEquals(5, f(1))
} catch (e: AssertionError) {
    println(e)
}
```
輸出 `0 條`、`rc=0`。把 catch 本體清空(`catch_all`)就列出,所以只差一行 `println`。

### F9 JUnit 5 的條件式跳過註記漏掉
severity: minor
blocking: 否 — 屬 S1 註記清單覆蓋面,沒有誤擋
引句:「_TG_SKIP_RE = re.compile(r"@(?:org\.junit\.)?Ignore\b|@Disabled\b|@SdkSuppress\b|@FlakyTest\b|@Config\s*\(\s*sdk\b"」
file: `scripts/lumos:48150`(`_TG_SKIP_RE`)
`@Disabled\b` 後面接字母的 `@DisabledOnOs(OS.LINUX)`、`@DisabledIfEnvironmentVariable(...)`、`@EnabledOnOs(OS.WINDOWS)`、`Assumptions.assumingThat(` 都沒有字界匹配。`skip_DisabledOnOs`、`skip_DisabledIfEnv`、`skip_EnabledOnOs`、`assumingThat` 全 `rc=0`,對照 `skip_Disabled` 會列。CI 在 Linux 時加 `@DisabledOnOs(LINUX)` 等於把測試關掉。

### F10 候選被記到錯的檔案:同一行文字在別支檔已存在時,指到舊檔的舊行
severity: minor
blocking: 否 — 只是定位錯,指紋不受影響;但指紋綁的檔案是錯的,檔案順序一變指紋就變
引句:「(test_files[0][0] if test_files else "", 0))」
file: `scripts/lumos:49083`(`_tg_hit_cands`)
- 次數表跨檔累計,出處卻取「第一支含這行文字的變動檔」。
- 重現 `e12`:`A.kt` 改前改後都有類別層級 `@Ignore("Flaky")`,另外新增 `B.kt` 也有同一行。輸出 `tq/skip-added  A.kt:3`,指到舊的那個,B.kt 完全沒被點名。
- `_tg_line_of` 用「子字串包含」比對,裸 `@Ignore` 會對到更早的 `@Ignore("舊理由")` 那行。

### F11 兩種誤報:把 `ignoreFailures` 一律當測試設定;`@Ignore` 換成 `@Disabled` 被當新增跳過
severity: minor
blocking: 否 — 有放行出口,但每次都要逐條放行
引句:「re.compile(r"\bignoreFailures" + _TG_SET + r"true\b"),」
file: `scripts/lumos:48155`(`_TG_BUILD_RES`)
- 重現 `detekt_ignoreFailures`:`detekt { ignoreFailures = true }` 和 `ktlint { ignoreFailures.set(true) }` 都列 `tq/build-config`,訊息卻說「建置檔改了測試設定」。
- 重現 `ignore_to_disabled_migration`:`@Ignore("flaky")` 換成 `@Disabled("flaky")`,數量不變,仍列 `tq/skip-added`,因為身分是整行文字。

## 圖譜鏡頭
- `Systems/test-guard` 的 WHY 寫「比對程式錯時那一次推送要用 `LUMOS_SKIP_LINT_NEW`(留帳)」,又寫「off 或環境變數跳過時比對照樣在背後跑」。F2 實測顯示:比對卡在病態檔時,這條逃生路徑同樣被卡住,截止時間在 `_tg_test_rules` 階段不生效。這兩條 WHY 合起來並不成立,節點宣稱的行為會被這份 diff 破壞。
- `Systems/test-guard` 的「規則一覽、抓不到什麼」指向測試品質標準。本審的 F4 到 F9 屬於標準裡沒寫的「抓不到」項目,標準需要補列或修實作。
- `Systems/room-guard` 的 WHY 說運算式本體的範圍變大「只會多要求、不會少要求測試」。我用 `_rg_methods` 做過 `@A\nval x = 1` 重複 5 萬次(`pathann`,1.2 秒)、3000 層巢狀類別(`nestclass`)、`@Test @Ignore` 3000 組(`manytests`)三種病態輸入,都沒壞。600 字視窗在 700 字註解與 30 行 KDoc 夾在註記和 `fun` 之間時也仍找得到函式,因為 `_RG_ANN_RE` 尾端的 `\s*` 會吃掉空白。判定不影響 Room 守衛既有行為。
- `Systems/測試假綠形態`:本次新測試沒有新增假綠形態,但 F3、F4、F6 的缺口都屬「斷言只驗了會列的方向,沒驗不該列的方向」(「不列」案例太少),與該節點第⑤型(fixture 產不出有鑑別力的值)同類。
- 無異動:`_TEST_QUALITY_BUNDLE_DIGESTS['test_quality_semgrep.py']` 的雜湊與檔案實際 sha256 相符(`cad1b274…`)。
- 臨時資料在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/邊界-sonnet/`,留給編排者收貨後刪除。

最嚴重等級 major,blocking 共 8 條(F1 到 F8)。
