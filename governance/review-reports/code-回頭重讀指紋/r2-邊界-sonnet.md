severity: major

severity: major
blocking: 是 — 上輪資安席的 major(同一段改動搬到前後三行相同的另一個函式,指紋不變)在 Kotlin、Java、箭頭函式這幾種寫法上沒有修掉
引句:「名字取 def/class/function/func/fn 後面那個」
問題:`_note_reread_hunk_tags` 只認 `def/class/function/func/fn` 當定義關鍵字。找不到關鍵字就退回「取第一個識別字」,而第一個識別字常常只是修飾字或型別。這些寫法的不同函式會得到同一個名字,等於整個拿掉段落標頭,回到上輪被點名的洞。我用 `_note_reread_hunk_tags` 直接餵內容實測:
- Kotlin 頂層:`fun top1()` 與 `fun top2()` 的 hunk 都得到 `fun`。
- Kotlin 或 Java 類別裡:縮排的 `    fun a()` 與 `    public void a()` 認不出是方法,兩個方法的 hunk 都只得到 `A`,沒有 `A/a`、`A/b` 的區分。
- JS、TS 箭頭函式:`const a = () =>` 與 `const b = () =>` 都得到 `const`。
- Go:`func (r *T) Name` 與 `func (r *U) Name` 都得到 `Name`,方法接收者被跳過,同名方法在不同型別之間分不開。
- Swift 的 `func` 有收,但 `final class`、`struct`、`extension`、`enum` 等會被當成第一個識別字。
- Rust 的 `impl Foo {` 頂格行得到 `impl`,不同 impl 區塊裡的同名方法也撞名。
具體失敗情境:作者把 `-check(user)` 改成 `+allow(user)`,原本在 Kotlin 類別的 `fun publicList()`。本鏈提交後把同一段改動搬到 `fun adminList()`,兩個函式前後三行一樣。兩版 hunk 的名字都是 `A`,指紋相同,「資安席看過」的紀錄會套到新位置。這個專案的主要使用者做 Android 與 Kotlin,所以不是冷門路徑。
修法建議:定義關鍵字加上 `fun`、`func`、`impl`、`interface`、`struct`、`enum`、`extension`、`object`、`void` 型別行(例如行尾含 `(` 且帶 `{` 的縮排行)。或者改成「名字找不到就用整行去掉參數括號後的文字」,不要退回單一字。
佐證:``scripts/lumos: `_NOTE_REREAD_DEF_RE`、`_note_reread_hunk_tags`(patch 約 36413 行起新增段)``;測試 `t_reread_fp_hunk_ident_rule` 與 `t_reread_fp_hunk_moved_between_functions` 只用 Python 與單一 Go 範例,沒有 Kotlin、Java、JS 的反例。

severity: minor
blocking: 否 — 邊緣寫法,輸出仍是確定性的,只是區分力變弱
引句:「頂格行照 git 預設段落標頭的規則(第一個字是英文字母、底線或 $)」
問題:
- `pub(crate) fn foo` 的括號不被修飾字正規式接受,整行得到 `pub`。
- 非 ASCII 函式名(例如 `def 中文():`)的識別字正規式比不上,退回第一個識別字 `def`,所有中文函式名共用同一個名字。
- 非 UTF-8 的名字會在第一個壞位元組處截斷,例如 `def f\xff\xfe` 得到 `f`,與真的 `def f` 撞名。
- 縮排的字串內容像 `    class of problems` 會被當成方法 `of`。
- 頂格的 docstring 或多行字串內容以字母開頭,會被當成頂格行。這點與 git 原本行為相同,但新增了一個與簽出無關的錯誤來源。
這幾項都不會崩潰,也不會因名字含代理字元而讓雜湊編碼失敗,只是區分力下降。
佐證:``scripts/lumos: `_NOTE_REREAD_IDENT_RE`、`_NOTE_REREAD_DEF_RE` 附近``

已讀,無 finding:
- CRLF:行尾的 `\r` 不影響取名,`def foo` 和 `def bar` 分得開。
- tab 縮排:`A/a` 與 `A/b` 分得開。
- 只有註解的頂格行:`#` 與 `//` 不算頂格,正確跳過。
- `d==0`(純刪除)與新增檔(hunk 起點為 0):邊界取行正確,不越界。
- 刪檔、子模組、二進位:`noid` 為全零或 mode 為 160000 時回傳空名字,不讀內容。
- 裸庫模式:在 git 2.39.2 實測,把 cwd 設成 git 目錄加 `--git-dir` 與 `--bare`,工作樹裡的 `.gitattributes` 設 `f.txt -diff` 不再影響輸出,對 `git worktree` 的 git 目錄也成立。簽出什麼,指紋都一樣。
- `attr.tree` 設定:2.39 不認得會被忽略,不報錯。
- 查大小失敗退回 v1:`_note_reread_fp_oids` 排除全零編號與子模組,缺物件時記「查大小失敗」,邏輯一致。
- 測試破壞檢查:我只跑了 `-k reread_fp_hunk`,6 支全綠。`d==0` 的 `(3,0)` 期望 `check_a` 能抓到起點算錯。「翻紅釘」只讀了描述,沒有逐條改壞再跑。

最高等級 major,blocking 共 1 條。
