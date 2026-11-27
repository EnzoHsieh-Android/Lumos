severity: clean

我走過上一輪修補,沒找到會做錯事的輸入。

- **修到沒**:修到了。`_choice_plan_sections` 現在把 `_choice_reader_lines` 回報的行號從正文扣掉,讀取器的範圍就是 `_h2_section_lines`(`scripts/lumos:13973`)。
- **隨機輸入**:我用 6000 組隨機文件驗證「正文」與「讀取器行」恰好一邊,零違規。標題用了這些變體:`## 驗收條款 ##`、`##<tab>驗收條款`、`#### 驗收條款`、縮排與引用塊標題、全形空白、`## 預期值表(x)`、圍欄、`# 一級`。
- **審計紀錄節**:它是正文與讀取器之外的第三類,兩邊都不收,這是設計本意。
- **新問題**:沒引入。唯一的呼叫端是 `_choice_plan_view`(`scripts/lumos:81149` 起)。預期值表的 `exp` 與 `sections` 取自同一份文字,第 2 層、`deps_sha`、材料三個讀者拿的是同一份段落。
- **同類位置**:`_choice_layer_not_body` 現在只判審計紀錄,沒有別處再用標題字面判這兩節。
- **已跑測試**:`-k t_choice_plan` 12 個全綠,含 `t_choice_plan_sections_reader_complement`。`-k t_choice_layer` 在背景跑,我沒等到結果。

總結:最高等級是 clean
