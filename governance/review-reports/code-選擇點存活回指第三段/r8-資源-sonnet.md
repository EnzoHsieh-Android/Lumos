severity: clean

這輪沒有發現 blocking 級問題。我讀了程式碼,沒有實際執行測試。

**成本**
- `_choice_plan_view` 傳給 `_choice_plan_sections` 的 `{r["line"] for r in rows}`,是在 `clause_bindings` 已經跑完的 `rows` 上多建一個整數集合。
- 分段迴圈裡的 `no not in taken` 是 O(1) 查找。每份計劃讀取器行號只算一次(`_choice_reader_lines`)。
- 大計劃、很多條款時是線性成本,沒有新的重複掃描或二次方路徑。`_ChoiceLayerCtx.view` 又按計劃快取,所以每份計劃每次呼叫只算一次。
- `scripts/lumos:81163`、`scripts/lumos:81174`

**對旁檔外移與份大小的影響**
- 分段結果只會變小:原本在正文裡重複出現的條款定義行現在被扣掉。
- 旁檔外移與切份用的位元組數,都來自 `_choice_layer_plan_md` 輸出的同一份 `v["sections"]`,所以大小判斷跟著結果一致。方向只會是更少外移、更少份,不會變多。
- 標題行不受 `taken` 影響,段名與同名編號 `#2` 不會因此漂移。
- `_choice_plan_view` 內 `clauses` 取原文與 `sections` 用的是同一個 `_note_lines(text)` 行號,沒有對不齊的風險。
- `scripts/lumos:81530-81575`

**修補三問**
- 修到沒:修到了。新測試 `t_choice_plan_view_body_drops_clause_lines` 同時涵蓋自造的「驗收條款帶說明」計劃和 repo 裡真實的計劃,斷言條款原文不在正文、說明句仍留在正文。
- 有沒有引入新問題:沒看到。
- 同類位置還有沒有:`sections` 的使用處只有三個,即旁檔外移的材料、基礎段落的引用,以及 `v["sections"]` 的段名列舉。它們都吃同一份分段結果,沒有另一條路徑還在用沒扣條款行的正文。
- `scripts/lumos:81251`、`scripts/lumos:81539`、`scripts/lumos:81749`

總結:最高等級是 clean
