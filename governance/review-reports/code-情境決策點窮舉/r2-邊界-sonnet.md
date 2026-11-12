severity: minor

整份 diff 逐 hunk 讀完。我在 `/tmp/lumos-seat-work/code-情境決策點窮舉/邊界-sonnet/` 用 importlib 載入修後版 `check.py`,餵自造輸入。沒有修前版的實跑結果,只能讀 patch 刪除的行比對;下面三條都因此只寫「修前依 patch 讀碼」,沒有實跑對照。找到三條輕微問題,都是失敗時偏向多報或漏報一個小角落,沒有重大等級的問題。

1. `_visible_lines(keep_fenced=True)` 遇到沒關的圍欄會丟掉最後一行內文
severity: minor
blocking: 否
引句:「hidden.update({a, end} if keep_fenced else range(a, end + 1))」
file: `scripts/lumos` 的 `_visible_lines`(keep_fenced 版);新舊對照見 `configs/ast-grep/kotlin-android/check.py` 的 `_fence_body`
失敗場景:圍欄沒關(`b is None`)時,`end = len(lines)-1` 是最後一行內文,不是圍欄標記。`keep_fenced` 把它當標記藏掉,內文少一行。
- 實測輸入:`"```kotlin\nval a = 1\nval last = 2".splitlines()`。
- check.py 版回 `[(2,'val a = 1')]`,少了 `val last = 2`。
- `scripts/lumos` 的 `_visible_lines(keep_fenced=True)` 回 `[(2,'val a = 1'),(3,'val last = 2')]`。
- docstring 寫「同 scripts/lumos 的 keep_fenced」,實際不同。
- 修前的 `_fence_body` 用 `range(x+1, len(lines))`,最後一行有算。
- 後果:範本檔最後一組以未關圍欄收尾時,片段只落在那最後一行,範本路徑會誤報「不在範本」。這種誤報是多報,不是漏放。
歸因:有證據的修復回歸(修後實測見上;修前依 patch 刪除的 `fenced.update(range(x + 1, (y if y is not None else len(lines))))` 讀碼,沒有實跑修前)。

2. `_bad_lines` 的原始行與去註解行用兩種換行規則切,遇到 `\x0c` 等字元會對錯行
severity: minor
blocking: 否
引句:「code = lumos._strip_c_comments(text, blank_strings=True, keep_newlines=True, kotlin=True).split("\n")」
file: `configs/ast-grep/kotlin-android/check.py`(`_bad_lines`,`raw = text.splitlines()` 與上面這行共用 `no` 當索引)
失敗場景:`raw` 用 `splitlines()`,`\x0c`、`\u2028`、`\x85` 都會斷行。`code` 只用 `"\n"` 斷,兩邊行數差一,`code[no-1]` 取到下一行。
- 實測輸入:`b"a\x0c\nfoo() // BAD\nbar()\n"`。
- 結果:回 `(行3,'bar()')`,正確應是 `(行2,'foo()')`。
- 後果:壞例檔含這類字元時,// BAD 標的是別行,片段比對與起訖行涵蓋判斷都對到錯的行。
- 範圍:`\x0c` 在 Kotlin 樣本裡罕見,所以只標 minor。
歸因:有證據的修復回歸(修前依 patch 刪除的 `lines = f.read_text(...).splitlines()` 讀碼,同一份 list 同時給標記判斷與取行,沒有兩套切法;沒有實跑修前)。

3. `_unreach_table` 片段格尾巴的雜字被默默丟掉
severity: minor
blocking: 否
引句:「rows.append((c[0], c[1], sn[0] if len(sn) == 1 and c[2].startswith("`") else c[2], c[3], c[4]))」
file: `configs/ast-grep/kotlin-android/check.py`(`_unreach_table`)
失敗場景:`startswith("`")` 加 `len(sn)==1` 只要求開頭是反引號、剛好一個片段,後面接什麼都放行。
- 實測輸入:格子 `` `a` 垃圾 ``。
- 結果:回 `'a'`,「垃圾」不見。
- 後果:手改型錄時尾巴留的字不會被擋,片段會直接對上反查單位 `a`。
- 修前:從頭到尾必須被反引號包住才取內文,否則整格原文照用,對不上單位會被報成「不是反查單位」。
歸因:有證據的修復回歸(修後實測見上;修前依 patch 刪除的 `snip = c[2][1:-1] if ... c[2][0] == c[2][-1] == "`"` 讀碼,沒有實跑修前)。

三問回答:
- ①原問題的修復效果:
  - `// BAD` 整字認:同一份 `_bad_lines`,輸入 `//BAD` 會認、`// BADGE` 不認、`// BAD-NEXT` 認。
  - 字串裡的 `//` 不截:`"http://x/y".let { go(it) }` 整行保留。
  - 單獨一行標記:跳過註記行,標到下一個語句。
  - `.` 續行併進同一語句:`repo.x()` 加 `.y()`,CRLF 檔也成立。
  - 非 UTF-8 檔回「讀不了」,不崩。
  - 多行字串裡的 `//` 不當標記;字串裡的 `// BAD` 不被當成註解。
  - 片段只有 `…`:`_parts_in_order` 回 False。
  - `_snippets` 對 `\|` 還原,維持原行為。
  - 以上都是修後實測;修前沒跑,這些主張沒有同一案例的修前對照。
- ②修補處的正常、錯誤與相鄰路徑:
  - 全形冒號與頓號:`_norm` 取代 `_norm_colon` 後,全形冒號仍正確換成半形,頓號本來就不在轉換範圍。
  - D-n 前導零(`D-04`)、全形數字(`D-４`)被 `_API_ITEM_RE` 拒絕,結果正確。
  - 停用列守衛:`DATA-68` 只被停用的 D-38 引用。若把 `_referenced_checks` 的停用過濾拿掉,守衛測試會紅,所以它不是空轉。
  - 例外:上面三條是相鄰路徑的缺口。
- ③新發現同一案例的修前修後結果:三條都沒有跑修前版,只有讀碼推斷,結果見各條歸因行。

未驗範圍:
- 本機沒跑 `--sg` 完整模式,沒驗新增的「S7 改壞」案例實際會紅。
- 沒在副本改壞各守衛逐一確認測試翻紅,只做了停用列那一道。
- 沒驗 `.api` 母體多一行、缺錨點的邊界。

總結:最高等級 minor,共 3 條
