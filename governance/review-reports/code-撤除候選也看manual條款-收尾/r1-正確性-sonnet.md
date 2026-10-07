severity: minor

背景測試已跑完,補上先前未判定的子集結果:`-k note_shape` 為 279 passed, 0 failed,`-k note_test_ref` 為 2 passed, 0 failed。其餘結論不變。解析丟例外那一條仍是靠讀碼,沒有注入例外去實測。

## F1 同一條款行用全形冒號或空白寫 `[test：…]` 時會被列兩次
severity: minor
blocking: 否
引句:「for no in _ns_tr_manual_clauses(text, rows):」
佐證:`scripts/lumos:32286`(`_ns_test_ref_lines` 以 slot_parse 判 `[test:]`),`scripts/lumos:7218`(clause_bindings 的 refs 來自 `invariant_test_refs(seg)`)。
失敗場景:條款行 `- [S1] 當 x 時應 y [manual:開頁面目測一次] [test：test_alive]`,下一層寫「裁定:撤除」。
- slot_parse 認全形冒號與 `[ test : x ]`,`invariant_test_refs` 不認。
- clause_bindings 因此判這行 state=manual,`_ns_tr_manual_clauses` 回這一行。
- [test:] 路因 `_test_names_of(sp)` 有名稱也列這一行。
- 同一行同一個條款出現兩筆候選。測試 ⑧ 只釘 ASCII 的 `[test:]` 加 `[manual:]`,沒蓋到這兩種寫法。
歸因:有證據的原有漏查(不是修復回歸)。修前 4b5f283 與修後 81646602 輸出相同,都是 `:8 … [test:]` 加 `:8 … [manual:]` 兩筆。命令是在 `/tmp/lumos-seat-work/code-撤除候選也看manual條款-收尾/正確性-sonnet/` 下,對 a(修後)與 b(修前)兩個 clone 各跑 `python3.14 probe3.py`。

## F2 [manual:] 路沒有「只看正文」的限制,frontmatter 摘要裡長得像條款的行也會被列
severity: minor
blocking: 否
引句:「rows = _ns_clause_rows(_note_from_text(rel, text), text)   # 同一篇只解析一次,[test:] 與 [manual:] 兩條路共用」
佐證:`scripts/lumos:32003`([test:] 路取 clause 行號後,`_ns_test_ref_lines` 另限 `regions[no - 1] == "body"`);`_ns_tr_manual_clauses` 直接吃 rows 的行號,沒有 region 判斷。
失敗場景:計劃的 frontmatter summary 續行寫成 `  - [S1] a [manual:開頁面目測一次]`,下一行縮排更深寫「裁定:撤除」。
- 輸出 `P_計劃.md:6  條款仍掛 [manual:]`,但第 6 行在 frontmatter 內,不是驗收條款。
- 同樣的行掛 `[test:]` 時,[test:] 路因 region 不是 body 而略過,兩條路不一致。
- 這個形狀少見,所以只算 minor。
歸因:有證據的原有漏查。修前與修後輸出相同(`probe2.py` 的 `fm continuation` 與 `fm summary dash` 兩例,兩版都列第 6 行),不是這次修補造成的。

## 修復與保持不變的結果,分開報
**repair(⑨ 同編號定義兩次)**
- `probe4.py` 的 `dup manual` 案例,兩行都寫 `[S1]`,第一條掛 `[manual:開頁面目測一次]` 且下一層寫撤除。
  - 修前列 1 筆 `[manual:]`。
  - 修後不列。這與維護者裁定一致。
- `dup test`(第一條掛 `[test:test_alive]`)兩版都列 `[test:]`,沒變。
- 重複的第二條才寫撤除(`dup second retire manual`)兩版都不列,這是 `[manual:]` 路已知的刻意限制。
- 相鄰狀態 shadowed(`[S1]` 之後又出現「  [S1] 見這個 `x`」這種認不得的清單行):修前列、修後不列。
  - 判定依據:此行 state=shadowed,不是 manual。
  - 這比裁定文字(只提 duplicate)多涵蓋一種狀態,但邏輯一致。
  - 天花板第 2 點沒有寫 shadowed,筆記範圍略窄於實際行為。

**preserve**
- `_ns_test_ref_lines` 的三個呼叫點:`scripts/lumos:32089`、`32286` 不帶 rows,走 `rows is None` 自己算,與原本 try/except 加空集合等價;`32404` 帶 rows。
- 解析出錯、非 project、`type` 寫成清單、沒有 `[S`:`_ns_clause_rows` 回 [],`probe2.py` 四例都沒有候選也沒有例外,兩版輸出一致。
- `rows=[]` 與 `rows=None` 的差別:[] 是「已算過、沒有條款行」,不會重算;doctor 傳入的 [] 與重算結果相同,沒有行為差。
- ①–⑧ 與 `t_doctor_s20*` 全綠(`-k t_doctor_s20`:38 passed, 0 failed)。
- CRLF、已標作廢、`[manual:已撤除,…]`、圍欄內、同篇另一條掛 `[test:]`:兩版結果一致,都符合預期。

**圖譜鏡頭**:固定席的合約是「修 bug 的還原翻紅釘須配前置斷言證明現場成立」。新測試的「不列」格(③④⑤⑦⑨)沒有各自的前置斷言。路徑壞掉時這些格會靠 ①②⑥ 與 ⑨ 的 `[test:]` 對照組翻紅,所以還原翻紅有間接保護,我判不會破壞合約。

**角色鏡頭**:`be-api-compat` 與 `be-authz` 不適用,這是純 CLI 診斷輸出,沒有對外 API 或授權端點。

## 三問
1. **原問題修復效果**:有行為證據。`python3.14 probe4.py` 的同編號定義兩次 `[manual:]` 案例,修前列 1 筆、修後 `{}`。`-k t_doctor_s20` 為 38 passed, 0 failed。
2. **相鄰呼叫路徑**:不帶 rows 的三個呼叫點、非計劃、`type` 為清單、沒有 `[S` 都成立(`probe2.py`,兩版輸出一致)。`-k note_shape` 279 passed、`-k note_test_ref` 2 passed,皆 0 failed。解析丟例外時,`_ns_clause_rows` 以 `except Exception` 回 [],這點靠讀碼,未實測。
3. **新發現同一案例修前、修後**:F1 兩版都列 2 筆(`probe3.py`)。F2 兩版都列第 6 行(`probe2.py`)。兩者都不是修復回歸。

總結：最高等級 minor,兩條 finding 都是修前就存在的原有漏查,修補本身(⑨)行為正確且沒有造成回歸。
