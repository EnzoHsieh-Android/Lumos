severity: clean

我對照的是 `scripts/lumos` 裡修正差異的改動(第 81120–81174 行一帶)和同層鄰居。結論是這次修法沒有引入跟既有做法不一樣的地方。

**1. 分層與依賴方向**
- 修法沒有另寫一套認條款的判法。`_choice_plan_view` 把自己已經呼叫過的 `clause_bindings(...)` 結果(`rows`)取出 `r["line"]`,當成 `clause_lines` 傳給 `_choice_plan_sections`。對照:`scripts/lumos:81169` 本來就用同一份 `rows` 建 `clauses`、`bound`,第 81174 行只是多取同一份資料的行號。
- `_choice_plan_sections` 自己不呼叫 `clause_bindings`,依賴方向維持「視圖層算好、分段層吃參數」。對照:`scripts/lumos:81111`。`_choice_reader_lines` 同樣只吃 `text`,並且用 `_h2_section_lines` 判段落,沒有第二套找節邏輯。
- 函式裡的 `taken = _choice_reader_lines(text) | set(clause_lines)` 是把兩種來源的行號併成一個「扣掉的行」集合,沿用原本 `taken` 的用法。

**2. 命名與錯誤處理**
- 新參數 `clause_lines=()` 的預設值寫法,跟同檔鄰居一致。對照:`scripts/lumos:14300`(`_door_keyword_hits(text, skip=())`)、`scripts/lumos:41456`(`exclude=frozenset()`)。呼叫端傳 set、函式內再 `set(...)` 轉一次,可接受任何可迭代物。
- 名稱用 `clause_lines`,跟 `_choice_reader_lines`、`_h2_section_lines` 的 `spans`(行號區間)用字一致,都是「行號」語意。`heads`/`spans` 是由函式往外附加結果的輸出參數,`clause_lines` 是輸入,兩者方向不同,沒有混用。
- 這次沒有新增任何錯誤處理分支。

**3. 第二種做法**
- 沒有。`clause_bindings` 的其他呼叫端(`scripts/lumos:14561`、`77012`、`79878` 等)都是用同一個函式認條款定義行,新修法也是。
- 「從條款讀取結果推行號」沒有重新實作,是直接吃 `rows`。
- 要扣的行號集合在 `_choice_plan_view` 內只算一次,沒有在兩處各自重算。

不對齊共 0 條,其中 major 0 條
