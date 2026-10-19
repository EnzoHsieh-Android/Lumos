severity: major

**圖譜固定席**
- `lumos-cli-read` 的 INVARIANT 管 search 的 superseded 篩選。這份差異沒碰,不影響。
- `design-loop` 的 INVARIANT 管處置閘第五步(審材要是 `.md` 計劃)。沒碰,不影響。
- `guard-kill` 的兩條 INVARIANT 管 rc 優先序與 `--json` 單行輸出。這輪改了 `_kill_method_name`、撞名分支與錯誤訊息文字,verdict 與 rc 的分類沒動,JSON 結構也沒動。
- `測試假綠形態` 的 INVARIANT 要求翻紅釘配前置斷言。新測試 `t_guard_kill_collision_cli` 與 `t_anchor_hint_scans_once` 都有前置條件。不影響。
- `lumos-cli-lifecycle`(sentinel 外位元組不變)與其餘 RISK 節點:這份差異都沒碰到。

**Findings**

1. 撞名判定把「不同檔、不同 describe」的標題拼成假撞名,合法綁定會被擋成 unproven
severity: major
   - blocking: 是
   - 歸因:有證據的修復回歸。這輪新加的 `_name_collisions_across` 造成。
   - 輸入:`e2e/a.spec.ts` 有 `test.describe('login'){ test('form shows') }`,`e2e/b.spec.ts` 有 `test('page loads')` 和 `test('login page loads')`。把 `login page loads` 綁成 Playwright 測試。
   - 走法:`_name_filter_collisions` 把所有檔的 `groups` 和 `tests` 各放進一個平的 list,再用 `_name_collisions_across` 拼。拆在第一個空白,left=`login` 配到 a 檔的 describe,right=`page loads` 配到 b 檔的 test。兩者在不同檔,不可能拼成同一條 titlePath。
   - 預期:`None`。真的 `-g '\slogin page loads(?:\s@\S+)*$'` 只會選中 b 檔自己那支。
   - 實際:
     - 修後 `_name_collision_reason(...)` 回「撞名:篩選會同時選中 2 支(另有:login > page loads)」,而 `login > page loads` 這支不存在。
     - 修前(5f8f8e48)同一組檔案回 `None`。
     - 修後和修前的結果都是用 `_raw_test_titles` 掃真檔案後呼叫 `_name_collision_reason`,不是手造 titles。
   - 影響:推送前合約測試閘(`_run_bound_tests`)與 guard kill 都走這支,誤判會讓該綁定證不出、推送被擋。使用者只能改名,而訊息指的那支根本不存在。
   - 觸發條件:有 describe 結尾等於名字的前綴,且別處有測試標題等於(Playwright)或開頭是(Jest/Dart)名字的後半。標題中間有空白的句子名,拆法一多就更容易撞到。
   - 補測缺口:`t_name_collision_describe_plus_test` 只有「完全沒有 describe」的反例,沒有「describe 與測試在不同檔」的反例。
   - 引句:「g = next((gt for gt, gc in groups if gc.endswith(left) and (not tail or gc == left or gc[-len(left) - 1].isspace())), None)」

2. regex_tail 的「describe 結尾要整字」邊界沒有測試守著
severity: minor
   - blocking: 否
   - 歸因:未判定。這是新程式,沒有修前版本可比。
   - 具體改壞:把 `(not tail or gc == left or gc[-len(left) - 1].isspace())` 換成 `True`。describe `XFoo` 加 test `Bar` 就會對名字 `Foo Bar` 報撞名,但 `-g '\sFoo Bar…$'` 對 `… XFoo Bar` 不會比中。
   - 我在 2e62dcdb 的快照上做了這個改動。`-k name_collision` 9 支全綠、`-k playwright` 21 支全綠,測試抓不到。
   - 同一輪我也做了其他四個改動,測試都會翻紅:
     - 拿掉 lenient 分支 → `t_kill_method_name_prefix_rules` 紅。
     - 拿掉頭尾空白拒收 → `t_titled_names_with_edge_spaces_not_collected` 紅。
     - 快取拿掉 → `t_anchor_hint_scans_once` 紅。
     - 這三條有效。
   - 引句:「g = next((gt for gt, gc in groups if gc.endswith(left) and (not tail or gc == left or gc[-len(left) - 1].isspace())), None)」

3. regex_tail 比對時,標題的尾端 tag 被剝掉,名字端卻沒剝
severity: minor
   - blocking: 否
   - 歸因:有證據的修復回歸,漏洞形狀是這輪才有。
   - 輸入:綁定名 `login @smoke`,另一支測試標題 `x login @smoke`。
   - 走法:`cmp` 先過 `_PW_TAG_TAIL_RE.sub` 變成 `x login`,`nl` 仍是 `login @smoke`,`endswith` 為假。實際 `-g '\slogin @smoke(?:\s@\S+)*$'` 會選中它,撞名被漏判。
   - 預期:報撞名。實際:不報。
   - 影響面:只有名字本身以 `@tag` 結尾時才發生,罕見。
   - 引句:「cmp = _PW_TAG_TAIL_RE.sub("", cmp)」

**三問**
- **①原問題的修復效果**
  - 剝註解:Kotlin `"""`、C# `@"`(含 `$@"`、`""` 跳脫)、Dart `'''` 內單獨的 `/*` 都不再吞掉後面的測試。
    - 我用 `_strip_test_comments` 對照修前版本確認。
    - Kotlin 多行字串修前輸出只剩 `val s = """\n`,修後完整保留。
    - 空字串相鄰、`'x@"y'`、`@Foo("x")`、`'''' ` 這幾種形狀兩版輸出一致,沒誤傷。
  - `\s…(?:\s@\S+)*$`:對 `login`、`login @smoke @x`、`x login` 都比中,`login2` 與整串只有 `login` 比不中。
  - 頭尾空白標題拒收:修前、修後行為和測試都對得上。
  - 殺傷力配方的 lenient 剝前綴:拿掉會翻紅。
- **②修補處的正常與相鄰路徑**
  - `_kill_method_name` 與修前版本在 `android:Foo`、`API: x` 這類輸入上等價。
  - `_bind_name_problem` 的全形冒號與已定義前綴放行,和讀取端 `_split_test_ref_ex` 判得一致。
  - `_clause_visible` 改走 `_strip_inline_markup(keep_test_fields=True)`:
    - 半形、巢狀 `[test:` 以外的輸入與修前相同。
    - 我用 30 萬筆隨機行比對,差異只在三種怪形狀,都不是真實條款行:
      - 全形冒號 `[test：` 的欄位現在也保留反引號。
      - 大小寫的 `[Test:` 現在也保留。
      - 巢狀 `[test:[test:` 內層的行為不同。
    - 全形冒號與大小寫這兩項是改動方向,不是缺陷。
  - 相鄰路徑破了一個,就是 Finding 1。
- **③新發現在修前、修後各是什麼**
  - Finding 1:修前 `None`,修後撞名。
  - Finding 3:修前沒有 tag 剝除,不存在此形狀。

**未驗範圍**
- 沒有真的跑 Playwright,`\s` 與 tag 位置只用 Python `re` 對字串模擬。
- 沒跑全套測試。
- `shlex.quote` 在 Windows `cmd.exe` 的行為沒驗,修前就是這樣。
- 沒做大型輸入的效能量測。`_C_STRIP_RE` 的新分支只用小輸入驗過功能,沒有量記憶體或時間。
- 只讀了差異裡的程式碼,沒讀 `Projects/測試名收自由字串_計劃.md`。

暫存:我的實驗目錄已用字面路徑刪掉。

最嚴重 severity:major。blocking 共 1 條(Finding 1)。
