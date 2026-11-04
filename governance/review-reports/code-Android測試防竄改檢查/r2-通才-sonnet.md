severity: major

審查對象:`ce5256bd → ea1e0b8a`(第 2 輪修補)。實驗都在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/`。`c2/` 是修後的乾淨 clone,`lumos_before.py` 是修前的 `scripts/lumos`,`lumos_after.py` 是修後的 `scripts/lumos`,`rp/repro.sh` 是 CLI 重現腳本。

先講白話:這一輪把「比對怎麼認身分、怎麼數」改得更精確,效能面修得很有效。但有三處把原本抓得到的作弊放掉了,另有一處效能測試在拿掉修補後仍然綠。

### F1 `ignoreFailures = true` 改成只在「測試區塊」裡才算,測試任務旁的常見寫法全部漏掉
severity: major
blocking: 是 — 違反 S7 條款:S7 寫「建置檔新增 `ignoreFailures = true`」就要列,沒有區塊條件。
引句:「re.compile(r"\bignoreFailures" + _TG_SET + r"true\b")」
file: `scripts/lumos:48761`(`_TG_IN_TEST_BLOCK` 第三項;原本在 `_TG_BUILD_RES`)
失敗場景:AI 為了讓紅燈不擋建置,在建置檔加 `tasks.test.ignoreFailures = true`、Groovy 的 `test.ignoreFailures = true`、`subprojects { test.ignoreFailures = true }`,或把它放在 `tasks.withType<Test> { if (CI) { ignoreFailures = true } }`。判斷「在不在測試區塊」只看最內層區塊的開頭行和同一行的 `{` 前面,這四種都判成不在,候選是 0 條。修前全部會列。
重現:
- `rp/repro.sh <lumos 路徑> ignorefail`
- 修前 `lumos_before.py`:`作弊候選 1 條 [tq/build-config]`,rc=1。
- 修後 `lumos_after.py`:`作弊候選 0 條`,rc=0。
- 四種寫法各自的修前/修後結果在 `e1.py`;另外「`withType<Test> { retry { ignoreFailures = true } }`」(巢狀在 retry 區塊)也從列變成不列。
- 本輪新增的 `detekt { ignoreFailures = true } 不列` 只證明誤報被壓掉,沒有任何一條正向測試涵蓋「不在 `{` 區塊首行的測試任務」寫法,所以 163 條全綠。
歸因:有證據的修復回歸(任務清單點名的 `_TG_BUILD_RES 的 ignoreFailures` 被刪後,新碼沒補回來)。

### F2 CI 的「呼叫測試任務」改成只取第一個 `-x` 之前的字,`-x` 在前的指令就看不到測試任務
severity: major
blocking: 是 — S8「刪掉呼叫 Gradle 測試任務的指令要列」對這種寫法失效;同一處也讓 r1 要修的「改旗標不算拿掉」漏了一條路徑。
引句:「for task in _TG_CI_TEST_TASK.findall(re.split(r"\s(?:-x|--exclude-task)\s+\S+|[|;&]", after)[0] if after else ""):」
file: `scripts/lumos:48875`
失敗場景:
- 漏報:CI 指令是 `./gradlew -x lint test`,AI 改成 `./gradlew -x lint assemble`(整個拿掉測試)。`after` 是 ` -x lint test`,切完 `[0]` 是空字串,改前改後都記不到 `test`,候選 0 條。修前會列。
- 誤報:`./gradlew test` 改成 `./gradlew -x lint test`(只加了排除 lint),新碼列成「拿掉了呼叫測試的 Gradle 指令:test」。r1 測的只有 `--stacktrace` 和 `| tee`。
重現:
- `rp/repro.sh <lumos 路徑> xtest`(修前 rc=1,修後 rc=0)。
- `e3.py`、`e4.py` 有 7 組對照,`-x` 在前的 4 組:
  - `-x lint test → -x lint assemble`:修前列,修後不列。
  - `-x lint testDebugUnitTest → -x lintDebug assembleDebug`:修前列,修後不列。
  - `--no-daemon -x lintDebug test → … build`:修前列,修後不列。
  - `test → -x lint test`:修前列,修後仍列(誤報沒解掉)。
歸因:漏報是有證據的修復回歸;誤報是修補沒涵蓋同族路徑。

### F3 本輪四條新效能測試,有三條在「拿掉修補」後仍然綠,S11 的守不住
severity: major
blocking: 是 — 這四條是 S11「大輸入 30 秒內」新增項的唯一驗證,而 30 秒門檻高於修前的實際耗時。
引句:「check("S11 r1 一行 4000 個中綴斷言 30 秒內", _time.monotonic() - t0 < 30, _time.monotonic() - t0)」
file: `scripts/test_lumos.py:121164`(同族:`:121158`、`:121177`)
失敗場景:改壞實驗(在 c2 clone 做)——把 `_tg_statements` 的 `if ls in done or len(out) >= _TG_MAX_STMTS: continue; done.add(ls)` 整段換成 `pass`,跑 `python3.14 scripts/test_lumos.py -k cli_contract`,結果 `25 passed, 0 failed`。原因是同一份輸入在這台機器上的耗時:

| 樣本 | 修前耗時 | 修後耗時 | 門檻 |
|---|---|---|---|
| 一行 4000 個中綴斷言 | 15.1s(拿掉該修補 16.4s) | 0.26s | 30s |
| 1500 個跳過標記 | 8.8s | 0.29s | 30s |
| 8000 個 CI 放寬鍵 | 6.9s | 3.1s | 30s |
| 1999 條交錯改 | 62s | 0.25s | 30s |

只有最後一條(1999 條交錯改)分得出新舊。另外三條的前置斷言沒有證明「走到慢路徑」,門檻也比修前耗時鬆,屬於 `Systems/測試假綠形態` 的「現場沒鑑別力」。
補充:`_tg_ci_head` 沒改,每個放寬鍵仍向上掃到同層第一行,仍是平方級。`e13.py` 量到 16000 行 4.0s、32000 行 15.8s,`_TG_MAX_LINES` 是 100000 行,且迴圈內沒有看截止時間。這一輪文件說「用堆疊一趟算完,跟行數成正比」,只對 `_tg_ci_blocks` 成立。
重現:`e11.py`(`LUMOS_PATH=lumos_mut_infix.py` 對比 `lumos_after.py`)、`e12.py`(修前修後對比)、`e13.py`。
歸因:新測試缺鑑別力是這一輪造成的;CI 那段平方級是有證據的原有漏查。

### F4 整支測試檔改名或搬套件,類別層級 `@Ignore` 與 `@Before` 裡的 `assumeTrue` 會被列成新增
severity: minor
blocking: 否 — `Systems/test-guard` 的 WHY 已記「測試檔整支改名時類別層級的跳過會被列一次」為代價;但實際範圍比記載的寬。
引句:「who = owner.get(i) or "檔:" + path」
file: `scripts/lumos:48802`
失敗場景:`git mv OldTest.kt NewTest.kt`(內容只改類別名),或搬到別的套件目錄,檔裡有類別層級 `@Ignore("flaky")`,會列 `tq/skip-added`;修前不列。範圍更寬的部分:`@Before fun setUp() { assumeTrue(isCi()) }` 這種不在 `@Test` 函式內的 assume,改名後也被列。WHY 只提到類別層級,沒提到這個。
重現:`rp/repro.sh <lumos 路徑> rename`(修前 0 條 rc=0;修後 1 條 `tq/skip-added`,指紋 57ef3d51…);`e8.py` 另兩組同樣修前不列、修後列。
歸因:有證據的修復回歸(已記代價,但需補上 `@Before` 這一類)。

### F5 新增的 `_tg_class_has_body` 沒有任何測試守,而且對 `@Inject constructor` 與巢狀泛型把類別路徑弄丟
severity: minor
blocking: 否 — 只影響函式鍵的類別前綴,不直接漏報;但這是本輪新改、零測試。
引句:「elif _tg_class_has_body(stripped, m.end(), bmap):」
file: `scripts/lumos:48431`(函式)
失敗場景:
- `class FooTest @Inject constructor(private val a: A) {` 與 `class FooTest<T : List<String>>(val x: T) {` 在修前路徑是 `FooTest`,修後是空字串,函式鍵變成不帶類別前綴。兩個內層類別有同名測試時,鍵改由出現順序決定。
- 把 `elif _tg_class_has_body(...)` 換成 `else:`,`-k tq_guard` 163 條全綠;把 `(?<!::)` 拿掉也全綠。
重現:`e6.py`(修前/修後各七個樣本,`@Inject constructor`、巢狀泛型、`@Suppress("x") constructor` 三個變空)。
歸因:有證據的修復回歸(路徑變空),加上本輪新增邏輯的測試缺口。

### F6 註記改成把宣告行名字前的整段(`public`、`internal`、`private`)也算進去,只改修飾詞就被當成「測試有變」
severity: minor
blocking: 否 — 可放行,但 JUnit 4 轉 5 時會一次冒出一堆。
引句:「pre = klines[decl][:_TG_NAME_RE.search(klines[decl]).start()] if _TG_NAME_RE.search(klines[decl]) else ""」
file: `scripts/lumos:48490`
失敗場景:本體與註記都沒動、只是 Java `public void a()` 改成 `void a()`(JUnit 5 慣例),或 Kotlin `fun a()` 改成 `internal fun a()`,而函式靠自訂輔助(`checkIt(1)`)當斷言。`_tg_fn_cands` 看到 `annot` 變了就重判,列 `tq/no-assertion`。修前不列。
重現:`e2.py`(修前 `[]`,修後 `[('tq/no-assertion','CalcTest.a')]`,`internal fun`、`private fun`、Java 去掉 `public` 三組)。
歸因:有證據的修復回歸(同一個修補也修好了「註記與 fun 同一行」的 expected=,只有後半是副作用)。

### F7 新增測試的鑑別力缺口:三個守衛拿掉仍然綠,一條前置斷言恆真
severity: minor
blocking: 否 — 各自只守新增的細節,單獨不構成條款漏洞。
引句:「check("★前置★ 檢查命令真的有宣告", lv8.get("tools_ran") is not None, lv8.get("status"))」
file: `scripts/test_lumos.py:121402`(`tools_ran` 初值是 `False`,永遠不是 `None`,這條前置永不紅;真正守住的是下一行的 `lv8["ran"]`)
失敗場景:改壞實驗(c2,各自跑對應的 `-k` 子集)全綠:
- 拿掉 `catch` 的 `not re.search(r"\bthrow\b", cb)`(讓 catch 裡重丟的也被列):`-k tq_guard_catch` 8 passed。
- 拿掉 `_TG_CHAIN_FLIP` 的 `isNull/isNotNull`:`-k tq_guard_expected` 24 passed。
- 拿掉 `_tg_tautology` 的 `assertFalse` 分支(`&& false`):`-k tq_guard_assert_weak` 10 passed。
- `_cl_say_lint_ok` 自動放行原因那一行換回 `reason`:`-k lint_new` 71 passed,全 repo 的測試裡找不到「自動放行並記帳」這串字。
對照:`autopass_reason` 在帳本那條(`_codeloop_lint_new_step`)有真測試,拿掉該行 `t_lint_new_test_guard_failure_blocks` 會紅。
歸因:新測試缺口,本輪造成。

### F8 同一行多個中綴斷言去重成一條,刪掉同行的第二個斷言不再被判變弱
severity: minor
blocking: 否 — 要求同行放多個 `shouldBe`,少見。
引句:「if ls in done or len(out) >= _TG_MAX_STMTS:」
file: `scripts/lumos:48534`
失敗場景:`fun a() { x shouldBe 1; y shouldBe 2 }` 改成 `{ x shouldBe 1 }`:修前列 `tq/assert-weakened` 加 `tq/expected-changed`,修後只列 `expected-changed`。去重讓兩側各剩一條敘述,數量沒變。
重現:`e5.py` 最後一組。
歸因:有證據的修復回歸(換效能的代價,但沒測到)。

### F9 測試目錄 `@SdkSuppress`/`@Config(sdk)`/`changeThreshold` 的「值」被改不再列(⚠ 與計劃寫法一致,但行為有變)
severity: minor
blocking: 否 — 計劃第 126 行把 `tq/snapshot-changed` 定義為「命中次數差大於 0」,新碼符合字面,但這不是 r1 當時的行為。
引句:「hits.setdefault(("tq/snapshot-changed", who, m.group(0)), []).append((path, i))」
file: `scripts/lumos:48808`(同行附近的 `skip-added` 身分也不帶參數)
失敗場景:Roborazzi 測試裡把 `changeThreshold = 0.01f` 改成 `0.5f`(放寬比對),或 `@SdkSuppress(minSdkVersion = 21)` 改 34:身分只剩「函式名 + 字樣」,次數沒變,候選 0 條。修前這些都會列。
重現:`e5.py` 前三組(修前列,修後 `[]`)。
歸因:有證據的修復回歸(但屬計劃字面範圍內的設計選擇,需人裁要不要把「值變大」算進)。

## 圖譜鏡頭

沒拿到固定席內容,我自己讀了 `Systems/test-guard` 與 `Systems/測試假綠形態`。
- **已記載的取捨,不列為缺陷**:
  - 跳過標記身分不帶類別、本體與種類,代價是同名測試一拿一加會互抵。
  - 整支檔改名時類別層級跳過會被列一次(F4 只補了範圍較寬的部分)。
  - 比對時間不算進檢查命令預算,「最壞情況整道閘的時間是預算的兩倍」已記為代價。
- **`測試假綠形態` 的 ★INVARIANT★**(還原翻紅釘要配「現場成立」的前置斷言):F3、F7 的缺口屬這一型。F7 的恆真前置斷言是它點名的第④型。
- **F1 與 S7 條款**:S7 條款與計劃表格第 123 行都寫「新增 `ignoreFailures = true`」,沒有區塊條件。圖譜裡沒有決策紀錄允許把它改成只算測試區塊,所以改動與條款衝突,這是筆記對程式的挑戰,不是線索。

## 三問

**①原問題的修復效果有何行為證據?**
- 效能:1999 條交錯改 62s→0.25s;1500 個跳過 8.8s→0.29s;單行 4000 個中綴 15.1s→0.26s;8000 個 CI 鍵 6.9s→3.1s。
- 規則階段超過截止時間:把那段檢查拿掉,`cli_contract` 掛住到 180 秒被測試框架砍掉,算紅。
- 工具檢查時間預算:改回 `tools_deadline = deadline` 後,`t_lint_new_includes_test_guard` 紅(「時間預算剩 28 秒,不足單條保底 30 秒」)。
- 自動放行原因:改壞後 `t_lint_new_test_guard_failure_blocks` 紅。
- 重構後等價,我用修前/修後兩份程式做差分隨機測試,對得上:
  - `_strip_c_comments`:6 萬組輸入乘 8 種旗標,差 0。
  - `_tg_ci_blocks` 對舊的 `_tg_ci_block_has_gradle`:2 萬組,差 0。
  - `_tg_ci_lines`(換用 `_ci_strip_comment`):8 萬組,差 0。
- `-k tq_guard` 在修後 clone 實跑 163 passed。
- 缺口見 F3、F7。

**②修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 呼叫端大致成立:`_waive_origin_tty` 與 `_e2e_waive_cmd` 行為相同,`_cl_say_lint_next` 與 `_cl_say_lint_guard_notes` 沒被弄壞。
- 但有三條相鄰路徑被修補弄壞:
  - 建置檔 `ignoreFailures`(F1)。
  - CI 測試任務計數(F2)。
  - 類別路徑與修飾詞造成的身分變動(F4、F5、F6)。

**③新發現的同一案例,修前、修後各是什麼結果?**

| 案例 | 修前 | 修後 |
|---|---|---|
| `tasks.test.ignoreFailures = true` | 列 | 不列 |
| `-x lint test → -x lint assemble` | 列 | 不列 |
| 整檔改名(類別層級 `@Ignore`) | 不列 | 列 |
| `public void → void`(無斷言輔助測試) | 不列 | 列 |
| `class A @Inject constructor` 類別路徑 | `A` | 空 |
| `changeThreshold 0.01f → 0.5f` | 列 | 不列 |
| 同行第二個 `shouldBe` 被刪 | 列變弱 | 不列變弱 |

證據不足、判不準的是 F9 要不要算缺陷(計劃字面是次數),標記為待人裁。

F1、F2、F3 是三處會讓守衛漏掉作弊或守不住 S11 的缺口,先修這三處再進下一輪。
