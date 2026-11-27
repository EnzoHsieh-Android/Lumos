severity: clean

這次修補沒有引入跟既有做法不一致的地方。三問依序如下。

**1. 分層與依賴方向**

新增的 `_choice_reader_lines`(`scripts/lumos` 約 81103–81105 行)是往下依賴既有的共用找節器 `_h2_section_lines`(`scripts/lumos:13973`),沒有自己再寫一套找節邏輯。
- 它配的兩條正則 `_KT_SIT_ACCEPT_H2_RE`、`_EXPECTED_H2_RE`,跟既有呼叫端一樣:`scripts/lumos:77951`(驗收條款)、`scripts/lumos:14713`(預期值表)、`scripts/lumos:81160`(`_choice_plan_view` 讀預期值表)。
- 沒有繞過 `_visible_lines`(圍欄判斷)和 `_note_lines`(切行),行號口徑跟 `_choice_plan_sections` 本身用的 `_note_lines(text)` 是同一個,所以「扣掉讀走的行」的行號能對上。
- 依賴方向跟 `_choice_plan_view` 同層(`_choice_*` 輔助呼叫共用底座),沒有跨層直呼。
- `_choice_layer_not_body` 現在只判審計修正紀錄,跟 `_FOLD_AUDIT_RECORD_RE` 的「只管審計紀錄」分工一致。

**2. 命名與錯誤處理**

- 命名跟鄰居一致:`_choice_plan_view`、`_choice_plan_sections`、`_choice_layer_not_body` 的 `_choice_` 前綴,新函式沿用。
- 對沒有該節(回 `None`)的處理寫成 `or []`,跟 `scripts/lumos:81160`、`scripts/lumos:12821`、`scripts/lumos:14135` 的既有寫法相同,沒有另外寫例外處理。
- 沒有傳 `heads` 參數,跟 `scripts/lumos:81160` 一樣。要判「節出現幾次」的 `scripts/lumos:14713`、`scripts/lumos:77951` 才需要 `heads`,這裡不需要。
- docstring 與註解沿用「找節邏輯不准長出第三套」的既有措辭,出處標註也與鄰居同格式。

**3. 第二種做法**

- 沒有第二種找節做法。r4 那個拿標題重組再判的第二種做法,在這次修補中被拿掉了,改成直接用共用讀取器讀走的行。
- 正文切段裡的 `_CHOICE_HEAD_RE` 是修補前就有的切段用標題判法。它管的是切段,不是找「驗收條款」「預期值表」兩節,這次沒有新增或擴大。
- 測試端用 `m._h2_section_lines(...)` 重算讀走的行,是用共用讀取器當對照組,不是另寫判法。
- 筆記端(計劃、規格閘、PITFALL 的修法敘述)的措辭與 r5 換形狀的內容一致,沒有看到新的不同寫法。

不對齊共 0 條,其中 major 0 條
