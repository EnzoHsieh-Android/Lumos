severity: major

我是以修後版 5f8f8e48(`git show` 取出的 `lumos_after.py`)對照修前版 960cd3e6(`lumos_before.py`)實跑。實驗檔都在 `/tmp/lumos-seat-work/code-測試名收自由字串/邊界-sonnet/`,沒有動 repo。

## Findings

**1. c-style 剝註解改成認得字串後,多行原始字串裡單獨一個 `/*` 會把後面所有測試吞掉(Kotlin、Swift、C#)**
severity: major
blocking: 是
- 位置:`_C_STRIP_RE` 與 `_strip_test_comments` 的 c-style 分支。結尾的 `(?:\*+/)?` 讓沒有收尾的 `/*` 一路刪到檔尾。
- 為什麼會發生:修補前,Kotlin、Swift、C# 走兩段式,沒收尾的 `/*` 原樣留著,所以後面的測試還在。修補後這三家全走新引擎。多行字串(`"""`、`#"""`、`@"` 跨行)在新引擎裡每行各自配對引號,引號配不起來的那一行裡的 `/*` 就被當成真註解。
- 具體例,Kotlin:
  ```
  val s = """
  a /* b
  """
  @Test fun after4() {}
  ```
  `_strip_test_comments(s, "c-style")` 的結果:修前版留下 `after4`,修後版整段刪光。
- 其他同類輸入的結果:
  - Kotlin 的 `glob: src/** /* lone`:修前版留下 `after2`、`after3`,修後版全沒了。
  - Swift 的 `#"""\n body /* open\n """#`:修前版留下 `testAfter6`,修後版沒了。
  - C# 的 `@"line1\n /* open\n line3";`:修前版留下 `After8`,修後版沒了。
- 後果:這幾個測試在 `discover_test_methods` 裡消失,綁定判成懸空,且沒有任何提示。
- 測試漏洞:S55 的 `t_comment_strip_keeps_strings_all_c_style` 只測單行字串 `"GET /api/*"`,把引擎退回兩段式才會紅,但多行字串這個新弱點它抓不到。
- 歸因:有證據的修復回歸。兩版對同一輸入跑出不同結果。
- 引句:「r"|//[^\n]*|/\*[^*]*(?:\*+[^*/][^*]*)*(?:\*+/)?", re.S)」
- 同一段 docstring 只把「JS 正規式字面」列為已知限制,沒寫多行字串這個洞。

**2. `_clause_visible` 在大量沒收尾的 `[test:` 上是平方級**
severity: minor
blocking: 否
- 位置:`_clause_visible` 對每個 `[test:` 各呼叫一次 `_slot_value_end`(沒有 `]` 時每次掃到行尾),再對 `hidden` 做 `any(...)` 線性掃描。
- 實測輸入:`"[S1] " + "[test:x " * n`。

  | 長度 | 耗時 |
  |---|---|
  | 4 萬字 | 4.5 秒 |
  | 16 萬字 | 76 秒 |
  | 32 萬字 | 291 秒 |

- 同類:`` `[test:x` `` 重複,20 萬字 8.5 秒。正常有收尾的 `[test:x]` 重複 36 萬字只要 0.03 秒。
- 對照:修前版用的 `_strip_inline_markup` 是線性的。`_clause_visible` 每條條款行、規格閘、待決問題都會走,大型異常筆記一行就能卡住。
- 歸因:有證據的修復回歸。修前版沒有這個函式。
- 引句:「end = _slot_value_end(line, m.end())」

**3. Playwright 的 `-g` 包裝式一定帶 `|` 與 `^`,Windows 的 cmd.exe 會當管線,S64 的守衛沒涵蓋它**
severity: minor
(⚠ 沒有 Windows 機器,只驗了展開字串,未能重現實際行為,所以自降一級)
blocking: 否
- 實測展開:`_run_cmd_expand('npx playwright test -g {method}','login',name_filter='regex_tail')` 得到 `npx playwright test -g '(?:^|\s)login$'`。
- 問題:`_WIN_CMD_SPECIAL` 只檢查「名稱」,沒檢查包裝後的字串。cmd.exe 不認單引號,所以 `|` 會變成管線。名稱再乾淨,Windows 上每個 Playwright 綁定都會被切碎。S64 要擋的正是這類注入,守衛卻守不住它自己新加的包裝。
- 歸因:修前的 `regex` 對乾淨名稱不產生 `|` 與 `^`,所以這是修復引入的行為。Windows 端行為未判定。
- 引句:「return r"(?:^|\s)" + esc + "$" if name_filter == "regex_tail" else esc」

**4. 撞名偵測看不到「describe 標題 + 測試標題」接起來的完整標題**
severity: minor
blocking: 否
- 實驗檔:
  ```
  test.describe('login', () => { test('flow', ...) });
  test('login flow', ...);
  ```
- 結果:綁 `login flow` 時 `_name_filter_collisions` 回 `[]`。但 Playwright 的 `-g` 比對的是整串,巢狀那支的完整標題 "login flow" 同樣吻合 `(?:^|\s)login flow$`,兩支會一起被選中。
- 同類:`outer > inner > deep` 與頂層的 `inner deep` 也漏掉。
- 設計取捨:S51 文字寫「describe 標題不算」,所以這是照設計走;但設計沒考慮「describe + 測試」接起來等於另一支名字的情形。
- 歸因:有證據的原有漏查。修前版 `regex` 模式對這組輸入同樣回 `[]`。
- 引句:「hit = kind == "test" and (cmp == nl or (cmp.endswith(nl) and cmp[-len(nl) - 1].isspace()))」

**5. 標題前後帶空白的 Playwright 測試,宣告看得到但跑不到**
severity: minor
blocking: 否
- 成因:`discover` 取名時 `_unwrap_backticks` 會 strip,`test('trail ', …)` 被收成 `trail`。展開的 `-g (?:^|\s)trail$` 要貼著字尾,對不到標題 "trail "。
- 實測:我的實驗檔裡 `discover_test_methods` 確實收了 `trail`,`_name_filter_collisions('trail', …)` 回 `[]`(不撞名,會照常去跑)。
- ⚠ 未能確認:Playwright 實際是否 trim 標題,以及 `-g` 對不到時是不是 "No tests found" rc 1,我沒有 playwright 可以跑。
- 歸因:未判定,是否為修復回歸要等實跑確認。修前的 `-g trail` 是子字串比對,不受影響。
- 引句:「r"(?:^|\s)" + esc + "$"」(該行是 `_name_filter_escape` 的錨式回傳)

## 三問的回答

- **原問題的修復效果(已驗到行為)**
  - 撞名看全部標題:`it.skip`、樣板、`.each` 這類掃描不收的標題現在算進去。
  - Playwright 結尾錨定:`login` 與 `a login` 現在判撞名,`alogin`、describe、`relogin` 不算。
  - `test.skip('why')` 在修前版被收成宣告 `why`,修後版不收。
  - 標題內含 `//`、`/*` 的測試(`has // slash and /* star`、其後的 `after star`)保留。
  - 單行的 `$`、`\` 標題都能正確跳脫:`a$b`、`a\b`、`a/b`、`a(b` 展開的 regex 都正確,且 `_test_name_ok` 均為合法。
  - 不合法的:`a[b`、純空白、全形空白。
  - Windows 的 `& % " ! ^` 在 `_IS_WIN=True` 時被擋;非 Windows 上全放行(符合 S64 設計,POSIX 靠 shell 引號)。
- **修補處的正常、錯誤與相鄰路徑**
  - 單行字串與反引號 Kotlin 方法名在新引擎下更穩。
  - 多行原始字串這條相鄰路徑回歸(Finding 1)。
  - `_clause_visible`:`[test:uses `foo` flag works]` 與 `[test:`整串反引號`]` 都能照字面綁,反引號包住的整段 `[test:範例]` 仍不算。但遇到大量未收尾 `[test:` 會平方級變慢(Finding 2)。
  - `_split_test_ref` 三處切法一致:`[test:Foo bar: baz]` 在多平台下修前是「未定義平台」報錯,修後整串歸預設平台。
  - `_bind_name_problem` 與 guard bind 的冒號規則和修前相同,全形冒號名仍被一律擋(修前就如此,不算新問題)。
- **同一案例的修前與修後結果**:都已列在各 finding 的「歸因」。Finding 1 兩版輸出不同(修後回歸);Finding 4 兩版相同(原有);Finding 3、5 未判定,原因是缺 Windows 與 Playwright 環境。

## 未驗範圍

- 沒有 Windows 或 playwright 環境,Finding 3 與 5 只驗了展開字串與邏輯。
- 沒有跑 `test_lumos.py`,沒有驗 `_test_in_tree` 的 git grep 路徑。
- 沒有驗 Java text block:java 走 c-style+strings,修補沒有改它,所以不在這次差異內。
- 沒有看圖譜固定席的合約實際綁定的測試能否仍通過。
- 固定席的判斷:這份修補只動 `scripts/lumos` 與測試檔。固定席各節點(lumos-cli-read、guard-kill 等)宣稱的行為,我沒找到被這份差異直接破壞的。`guard-kill` 的 rc 優先序與 `--json` 純度沒有被動到,只是 `guard kill` 新增了「撞名 → error」的結果,在已有的 `error` 分支內。

臨時目錄 `/tmp/lumos-seat-work/code-測試名收自由字串/邊界-sonnet/` 留給編排者收貨後刪。

最嚴重 severity:major。blocking 共 1 條(Finding 1)。
