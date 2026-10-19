severity: major

核對的是修後版本 5f8f8e48,修前版本 960cd3e6。兩版都用 `git show` 取出,載入成模組後在同一份夾具上跑。Playwright 用的是 order-web 的 1.64.1,也就是這輪實測所用的版本。

## Findings

1. Playwright 的結尾錨定讓帶 tag 的測試必紅
severity: major
   - blocking: 是
   - 歸因:有證據的修復回歸
   - 位置:`_name_filter_escape` 新增的 `regex_tail`,即 `(?:^|\s)<名>$`。
   - 問題:Playwright 比對 `-g` 的字串是 `_grepTitleWithTags()`。`file: node_modules/playwright/lib/common/index.js:2851` 把 `test._tags` 接在標題後面,`_tags` 也包含 describe 繼承來的 tag。所以 `test('login', { tag: '@smoke' }, fn)` 的比對字串是 `a.spec.js login @smoke`,結尾不是 `login`。`PLAYWRIGHT_TEST_RE` 因為標題後面有逗號,會收下這支測試,讓它能被綁定。
   - 具體例:夾具 `test('login', {tag:'@smoke'}, …)`,綁定名 `login`。
     - 直接跑 `playwright test -g '(?:^|\s)login$'` 得到 `Error: No tests found`。
     - 經 `_run_bound_tests`:修前 `('green','')`,修後 `('red','rc=1 Error: No tests found')`。
     - 同夾具的不帶 tag 測試 `pay`,修前修後都是綠,所以不是環境問題。
   - 影響:用 tag 的 Playwright 專案,綁了這種測試的推送會被擋。文件和計劃都沒提 tag。
   - 引句:「+    return r"(?:^|\s)" + esc + "$" if name_filter == "regex_tail" else esc」
   - 未涵蓋:`test.describe('x', {tag}, …)` 底下的測試沒另外跑。這一條是讀原始碼推的,依據是 `_tags` 含繼承的 tag。

2. 撞名判定把「自己」讓給 describe,真測試被算成撞名(誤擋)
severity: major
   - blocking: 是
   - 歸因:有證據的修復回歸
   - 位置:`_name_filter_collisions` 的 `own` 旗標,搭配 `_raw_test_titles` 把 describe 也收進來。
   - 問題:`own` 被第一個「文字相同」的標題用掉,不看種類。檔案順序是 describe 在前、測試在後時,describe 被當成自己,真測試接著被當成「別的標題」。`regex_tail` 的比對條件是 `kind == "test"`,所以這支測試會命中自己。
   - 具體例:`test.describe('checkout', () => { test('checkout', …); test('pay', …) })`,綁定名 `checkout`。
     - 真跑 `-g '(?:^|\s)checkout$'` 只選到 1 支(`a.spec.js:5:3 › checkout › checkout`)。
     - `_run_bound_tests`:修前 `green`,修後 `unproven`,訊息為「撞名:篩選會同時選中 2 支(另有:checkout)」。「另有」指的就是它自己。
     - `_name_collision_reason("pay")` 回 None,所以只有與 describe 同名的測試被誤擋。
   - 影響:describe 與測試同名是常見寫法。guard kill 也共用這支判定,會把配方記成 error。
   - 引句:「+        if text == n and not own:」

3. `guard kill` 共用撞名判定這一條,測試守不住
severity: major
   - blocking: 是
   - 歸因:有證據的修復缺口(測試端)
   - 問題:`t_guard_kill_shares_collision_check` 只直接測 `_name_collision_reason`,再用 `inspect.getsource` 確認原始碼含這個字串,沒有走過 `cmd_guard_kill`。
   - 改壞重現:在 `cmd_guard_kill` 把 `if _coll:` 改成 `if False and _coll:`。
     - `python3.14 scripts/test_lumos.py -k guard_kill_shares_collision`:3 passed, 0 failed。
     - `-k collision`:23 passed,全綠。
   - 影響:guard kill 路徑「撞名就不跑」是這輪修補宣稱的行為,現在關掉也沒有測試會紅。
   - 引句:「+    check("③guard kill 呼叫這一支(結構檢查,補 ①②)", "_name_collision_reason(" in src, "")」

4. `t_playwright_name_filter_anchored` 的夾具蓋不到第 2 條
severity: minor
   - blocking: 否
   - 歸因:有證據的修復缺口(測試端)
   - 問題:`titles` 把 `("test","login")` 排在 `("group","login")` 前面,測試先吃掉 `own`,所以抓不到 describe 在前的順序。同一個測試也沒有 tag 案例,第 1 條同樣漏掉。
   - 引句:「+    titles = [("test", "login"), ("test", "logout works"), ("test", "relogin"), ("group", "login"), ("test", "a (b) LOGIN")]」

5. 「describe 加測試」拼出來的標題,撞名漏判
severity: minor
   - blocking: 否
   - 歸因:有證據的原有漏查。修前用 `methods` 集合加子字串判定,同樣漏掉。
   - 具體例:`test('Foo Bar')` 加 `describe('Foo'){test('Bar')}`。綁定名 `Foo Bar` 時,真跑 `-g` 選到 2 支都通過,`_name_collision_reason` 回 None。原因是只比單一標題的結尾,不比 describe 串起來的路徑。
   - 引句:「+            hit = kind == "test" and (cmp == nl or (cmp.endswith(nl) and cmp[-len(nl) - 1].isspace()))」

6. `_anchor_migration_hint` 每條懸空綁定都重掃整個 repo
severity: minor
   - blocking: 否
   - 歸因:有證據的修復新增,未判定是否構成回歸。
   - 問題:它用 `file_name_match=None` 走整個 repo 所有 `.ts/.js`(含應用程式碼),doctor 對每條懸空或偽證據的綁定各呼叫一次。實測 22MB 的 800 個 `.ts` 檔,一次呼叫 0.63 秒,100 條懸空約一分鐘。
   - 引句:「+    loose = {**prof, "file_name_match": None}」

## 逐項已驗,未見問題

- **Kotlin/Swift/C# 換成新剝註解法**:前後版本跑同一批夾具(字串內 `//`、`/*`、單引號字元字面、註解裡的撇號、Kotlin 反引號名)。
  - 結果更好:`` `visits http://x` `` 修前被截成 `after`,修後找得到。
  - 其餘案例前後一致,沒有退化。
  - Kotlin 原始字串 `"""` 內的 `fake` 前後都會被收,是既有行為。
- **`_clause_visible`**:反引號包住的 `[test:範例]` 仍隱藏。值內的反引號照字面留下,未閉合反引號的 `truncated` 旗標與舊版一致。
- **`_split_test_ref` 新呼叫端**(doctor Check T、`_dispositions_split_test`、`_bind_name_problem`、`_kill_method_name`):走過 `android:Foo`、`API: x`、未定義但長得像平台名、全形冒號,都符合文件所述。
- **PLAYWRIGHT_TEST_RE 逗號限定**:可收 `test('x', {tag}, fn)`,不收 `test.skip('原因')`。
- **`_raw_test_titles`**:`.step` 已排除,測試用的 `test.skip('原因')` 會被當成標題收進去。只有名字剛好是某個測試標題結尾時才會誤報,沒找到實際誤報案例。

## 三問

1. **原問題的修復效果**
   - 撞名改看 `_raw_test_titles`:`t_name_collision_sees_skipped_titles` 的案例有行為證據(修前集合看不到跳過的標題)。這輪沒有自己重跑原始 r1 的紅綠。
   - 剝註解:字串內 `//`、`/*` 的截斷已修好,證據見上。
   - 結尾錨定:對沒有 tag、沒有 describe 同名的測試有效(`pay` 綠)。
2. **修補處的正常、錯誤與相鄰路徑**
   - 發現 1 和 2:兩個正常路徑在修前是綠、修後變紅或證不出,屬於修補引入。
   - 其餘相鄰路徑(`_kill_method_name`、`_bind_name_problem`、`_clause_visible`)的正常與錯誤輸入成立。
3. **同案例前後結果**:見發現 1 和 2 的修前修後數據。

未驗範圍:Windows 的 `_WIN_CMD_SPECIAL` 路徑、`_test_in_tree` 的 git grep 多 `-e` 跳脫變體(只讀程式)、`.each` 跨行表格造成的標題漏收。

最嚴重:major,blocking 共 3 條(發現 1、2、3)。
