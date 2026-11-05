severity: minor

### F1 coroutines 規則只補一層括號加法,`+ (job)` 與兩層巢狀仍誤報
severity: minor
blocking: 否
引句:「括號裡再包一層加法:CoroutineScope(…) + (x + job);$J 是內層加法的直接運算元(代碼審 r4 通才席 Finding 2)」
file: `configs/ast-grep/kotlin-android/rules/coroutines.yml:135-152`
場景:我用 ast-grep 0.51.1(pip 裝)、sgconfig.yml 掃臨時檔,類別內有 `private val job = SupervisorJob()`。以下兩種寫法的 scope 都用了 `job`,規則仍報 `kt-long-lived-scope-plain-job`:
- `CoroutineScope(Dispatchers.Main) + (job)`
- `CoroutineScope(Dispatchers.Main) + (CoroutineName("x") + (other + job))`

原因:新分支只認 `parenthesized_expression` 的直接子節點是加法、且 `$J` 是那個加法的直接運算元。`(job)` 沒有加法。兩層巢狀時 `job` 在第二層加法裡。
這兩種是修補前就有的誤報,修補沒有宣稱修它們。Issue 第 5 項寫的是「認括號裡再包一層加法」,一層寫法確實修到了。實測 `(other + job)` 與 `(CoroutineName("x") + other + job)` 都不報,Holder3 的好例也不報。壞例 S3 確實命中。

### F2 Systems/kotlin規則包 的樣本排除範圍描述沒跟著更新
severity: minor
blocking: 否
引句:「規則包樣本目錄 `configs/ast-grep/<包>/samples/` 跟審計證物同理,風險分級、棧別題、新增告警閘(含測試防竄改比對)與 Room 守衛都不當產品碼掃」
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:39`
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:43`
場景:diff 沒動 kotlin規則包 這篇。第 39 行仍寫「風險分級、棧別題與每支檔有家都不把它們當產品碼」。第 43 行仍寫「`_RULEPACK_SAMPLE_RE` 與 `node_home.ignore` 兩處同一個範圍」。這次已讓測試防竄改比對(`_tg_kind`)與 Room 守衛三處(`_rg_grep`、`_rg_hunks`、`_rg_triggered`)也套用同一個正規式。照這篇讀的人會以為作弊比對與 Room 守衛還會掃樣本,而這正是這次修掉的問題。後果是認知落差,不會做出錯誤動作。

## 實測證據(測試對改壞的反應)
在複本上改壞,跑 `python3.14 scripts/test_lumos.py -k <關鍵字>`:
- `_tg_kind` 略過條件改成 `if True`:`t_tq_guard_skips_rulepack_samples` 的 ★對照★ 紅。
- 拿掉 `_rg_grep` 的過濾:「樣本裡的測試不充當真 DAO 的測試」紅。
- 拿掉 `_rg_triggered` 的過濾:「改到樣本不觸發(不記帳)」紅。
- 拿掉 `_rg_hunks` 的過濾:「有真升級觸發時…」紅。
- 正規式拿掉開頭錨點:`t_room_guard_skips_rulepack_samples` 與 `t_tq_guard_skips_rulepack_samples` 兩支新測試仍全綠。能抓到的是既有的 `t_rulepack_sample_dir_skips_risk_scan`(「別的 samples 目錄照掃」)。改壞的是共用的 `_RULEPACK_SAMPLE_RE`,所以略過條件寫太寬這個改壞有被守住,只是不在新測試裡。
- 新測試的對照組(同形的一般路徑照擋、照列)獨立有效。
- 本機沒有 ast-grep 時 `t_kotlin_rulepack_samples` 只跑靜態那半。我另裝 0.51.1,設 `LUMOS_AST_GREP` 跑完整測試:23 條全過。
- 「非 JSON」那條測試用假 sg(輸出 `not json`、結束碼 1)。拿掉 try/except 會丟 ValueError,被測試的 except 接住後判紅。這個測試能抓到錯。
- 非 JSON 處理:`scan` 回 None,`check` 加「跑不起來」並以非零結束。這是大聲失敗,不會讓自檢假綠。

## 逐項走過、沒找到問題的邊界
- `_strip_yaml_comment`:引號狀態每行重置。引號內的 `#` 不剝。`#` 前面不是空白也不剝。整行註解變空行。後面的程式碼只用得到 files 區塊。
- 全形逗號:`[、,，]` 拆分正確,`(無)，foo` 會報。
- `_RULEPACK_SAMPLE_RE.match` 以字串開頭為準,只認 repo 根的 `configs/ast-grep/<包>/samples/**/*.kt(s)`。路徑裡別處剛好有 `samples`、別的規則包層級、Windows 分隔符都不誤略過。`_tg_kind` 先把反斜線換成斜線。git 輸出本來就是斜線。
- `_RULEPACK_SAMPLE_RE` 在 `scripts/lumos:61551` 定義,晚於使用處。它是模組層全域,呼叫時才解析,沒問題。
- 範圍:樣本只有 `.kt`,`.java` 與其他副檔名照掃。這是原有的設計。

## 圖譜鏡頭
- Systems/kotlin規則包:有不一致,見 F2。其他合約不受影響:自檢解析的修補與規則的修補都往更嚴、更準的方向,沒有放寬任何 `RULE:`、INVARIANT 或測試綁定。
- Systems/test-guard:新增那行 WHY 與 `_tg_kind` 行為一致,`[test:t_tq_guard_skips_rulepack_samples]` 綁得到,而且是真的會紅的測試。對該篇既有行為(紅燈版比對、`_tg_functions` 等)沒有影響,因為只有樣本路徑回 None。
- Systems/room-guard:新增那行 WHY 與三處過濾一致。「git grep 找資料庫與測試、DAO 差異、觸發判斷」三處都有各自的紅測試。`_rg_grep` 也給 `Migration` 與 `MigrationTestHelper` 的搜尋用,樣本因此不會充當真升級或真測試。這是合理的副作用,沒破壞合約。
- Systems/pitfalls-code-loop:WHY 補了「含測試防竄改比對、Room 守衛」,與程式一致。原本 `[test:t_rulepack_sample_dir_skips_risk_scan]` 仍綁風險分級那半,新兩條測試只在 test-guard 與 room-guard 兩篇綁,沒有破壞。
- Issues/Kotlin規則包代碼審放行的小問題:
  - 第 1、2、3 項確實修到,測試 `t_kotlin_rulepack_samples` 與 `t_kotlin_catalog_rows_wired` 能抓到對應改壞。
  - 第 4 項:型錄兩條理由已分開,字句與實際規則註解(try/runCatching 終端操作列舉不完)一致。
  - 第 5 項:只修到一層括號,見 F1。
  - 第 7 項:修到。
  - 第 6 項:改成 REVISIT 分流,記錄明確。

## pitfalls 相關命中
kt-pitfalls.txt 裡跟這次新增行有關的只有兩條:`check.py:129 catalog_problems` 與 `check.py:301 check` 的複雜度警告。兩支函式本來就複雜,這次沒改它們的結構(`check` 只把迴圈變數改成 `_d`),屬於既有警告。`scripts/test_lumos.py` 的 ruff 命中(125658 等行)都不在這次新增行。對新增測試與程式沒有命中。

最高嚴重度:minor
