severity: minor

審查對象:`r3-repair-lumos.patch`,修前 `5f8f8e48`、修後 `2e62dcdb`。我把兩版 `scripts/lumos` 各取出來載入,用同一批輸入跑過。一個 blocker 或 major 都沒找到,以下三條都是 minor。

## Findings

**1. Windows 引號層沒跟著改,`-g` 的 Windows 防護是空的**
severity: minor
- blocking: 否
- 歸因:有證據的原有漏查。修前修後都一樣,不是這次修補造成的。
- 位置:`_name_filter_escape` 與 `_run_cmd_expand`。
- 問題:修補把 `|`、`^`、`<` 從 `-g` 正規式拿掉,理由是 cmd.exe 會誤解。但 `{method}` 一律走 `shlex.quote`,在 Windows 上也一樣。cmd.exe 不認單引號,所以引號層一直是壞的,正規式內容再乾淨也沒用。
- 具體例:輸入 `\slogin(?:\s@\S+)*$`,`shlex.quote` 輸出 `'\slogin(?:\s@\S+)*$'`(含單引號,與平台無關)。cmd.exe 會把單引號當成參數的字面字元,`-g` 收到的 pattern 開頭是 `'`,永遠比不到。`{python}` 在 Windows 已改用 `_sp.list2cmdline`,`{method}` 卻沒有。
- 佐證:`t_playwright_tail_tags_and_own` 的②只檢查展開字串裡沒有特殊字元,沒有檢查 Windows 的引號形狀。
- ⚠ 未能在 Windows 重現,只重現了 `shlex.quote` 的輸出。
- 引句:「不用 | ^ <(Windows cmd.exe 會當管線、跳脫、轉向);」

**2. 新增的 `"""`、`'''`、`@"` 三個分支,在大字串上吃的記憶體比修前多,現有記憶體測試沒量到**
severity: minor
- blocking: 否
- 歸因:有證據的修復回歸。
- 位置:`_C_STRIP_RE` 的 `(?:"(?!"")[^"]*)*` 這種「群組加星號」寫法,每遇到一個引號就多推一格狀態。
- 具體例:一個 8MB 的 Kotlin 原始 JSON 字串(`val s = """` 後接重複的 `{"k":"v"}\n`),常駐記憶體增加量修前約 153MB,修後約 404MB。
- 更極端的例子:`"""` 後接 400 萬組 `a"`,或 `@"` 後接大量 `""`,增加量約 250 到 505MB。
- 現有測試的問題:`t_comment_strip_big_string_memory` 只餵 8MB 的 `'A'`,走的是單引號分支。它還把門檻從 200MB 放寬到 300MB,但這個輸入修前修後都是 0MB 增加,所以新分支沒有被量到。
- 引句:「應抓到的錯:_C_STRIP_RE 改回群組加星號的寫法 → ①紅。」

**3. `regex_tail` 的撞名判斷只剝比對對象的 tag,沒剝被綁的名字,和 `-g` 實際行為不一致**
severity: minor
- blocking: 否
- 歸因:有證據的修復回歸。
- 原因:修補把 `-g` 放寬成 `(?:\s@\S+)*$`,但撞名判斷是先剝標題尾端的 `@tag`,再拿去比被綁的名字。
- 具體例:綁定名 `login @smoke`,另有測試 `login @smoke @fast`。
  - 實際選取:`\slogin @smoke(?:\s@\S+)*$` 會選中 `login @smoke @fast`。
  - 判斷結果:`_name_filter_collisions("login @smoke", [("test","login @smoke"),("test","login @smoke @fast")], "regex_tail")` 回 `[]`,漏報。
  - 修前:兩邊一致,都不會選到。
- 範圍有限:只有「被綁的名字本身以 `@詞` 結尾」才會發生。
- 引句:「regex_tail 比之前先拿掉標題尾巴的 @tag(Playwright 把 tag 接在標題後面比,2026-10-15 實跑)。」

## 逐項核對的輸入

這些都沒問題:
- **Playwright 錨**
  - 標題 `a login` 對 `login`:修前修後都判撞名。
  - 標題含 `$`、`\`、`/`、`(`、`[`、`.`、`*`:escape 後的 `\s…(?:\s@\S+)*$` 在 JS 風格比對下,對有 tag 和沒 tag 的字串都成立。
- **撞名邏輯**
  - describe 與測試同名:describe 不再搶「自己那支」。
  - describe 加測試拼名(`Foo > Bar`):在 regex 和 regex_tail 兩種模式都抓到。
  - 巢狀兩層(`A Foo Bar`)抓不到,這是文件寫明的限制。
  - 拼名只看標題文字、不核對真實巢狀,所以會多報,這是「寧可多數」的設計取向,我不算它是缺陷。
  - 效能:40 個空白、2 萬支測試的名字,每次約 0.03 秒。
- **頭尾空白標題**:`'  lead'`、`'trail '`、全形空白、帶尾空白的 describe,修後都回 None,修前會收成修剪後的名字。
- **剝註解**:Kotlin `"""…//…/*…"""`、C# `@"…""…"`、跨行 `@"`、Swift `#"…"#` 後面的 `test("keep…")` 都保留。修前 Kotlin 的 `"""` 案例會把後面的測試吃掉。沒收尾的 `/*` 仍刪到檔尾,維持舊行為。
- **條款行**:`_clause_visible` 改走 `keep_test_fields` 後,我拿 10 條含 `[test:…]`、反引號、未收尾反引號、`[test : …]`、`[manual:…]` 的行,修前修後輸出逐字相同。1 萬欄位、2 萬個隱藏區段都不到 0.02 秒。
- **平台前綴**:`_kill_method_name` 對 15 種輸入修前修後完全一致,包括 `android:Foo`、`android: Foo`、`API: …`、`x：y`、`Foo:Bar:Baz` 和空值。`_bind_name_problem` 現在放行已定義前綴和全形冒號,擋 `API: x`,和讀取端一致。
- **檔名錨快取**:`_ANCHOR_MAP_CACHE` 的 key 帶 `profile_name`,實際 `pentry` 都有這個欄位,不會互相覆蓋。

## 三個問題的回答

1. **原問題的修復效果**:
   - 已有行為證據,我用兩版 `scripts/lumos` 實跑比對:tag 容許、describe 同名不搶、頭尾空白不收、多行字串不吞後面的測試。
   - 條款行平方級的問題改成一趟走完,輸出與修前相同。
2. **修補處的正常、錯誤與相鄰路徑**:
   - 正常路徑和相鄰路徑都沒壞。
   - 錯誤路徑上有兩處新缺口,就是 finding 2 和 3。
   - Windows 那條(finding 1)是修補沒碰到的既有缺口。
3. **新發現在修前、修後的結果**:
   - finding 2:修前約 153MB,修後約 404MB。
   - finding 3:修前一致,修後漏報。
   - finding 1:修前修後相同。

## 未驗範圍
- 沒有在 Windows 實跑,沒有跑真的 Playwright 或 Jest,`-g` 行為是用 Python `re` 模擬 JS 正規式。
- 沒有跑 `test_lumos.py` 的全套,也沒有做拿掉實作看測試會不會紅的破壞測試。
- Java 文字區塊走的是舊的兩段式剝註解(`c-style+strings`),這次沒動,我也沒深查。
- 我取的是 `git show 2e62dcdb:scripts/lumos`,沒讀工作樹當前的 HEAD(`85de72e4`)。

最嚴重 severity:minor。blocking 共 0 條。

我的臨時目錄 `/private/tmp/lumos-seat-work/code-測試名收自由字串/邊界-sonnet` 已刪。上一層迴圈目錄因為還有別席的內容,沒有刪。
