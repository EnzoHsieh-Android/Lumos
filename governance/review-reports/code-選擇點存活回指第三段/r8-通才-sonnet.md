severity: clean

這輪修補我讀完了,沒有 blocking 發現。

**修到沒?** 修到了。`_choice_plan_sections` 在 `/Users/enzo/harness/lumos-reach3/scripts/lumos:81127` 把「讀取器節行號」和 `clause_lines` 合併成 `taken`,正文因此不再收條款定義行。標題帶說明、讀取器讀不到那一節時,條款原文就不會同時出現在條款與正文兩邊。

**跨檔追蹤**
- `_choice_plan_sections` 在 `scripts/lumos` 裡只有一個正式呼叫端:`_choice_plan_view`(`scripts/lumos:81174`),已傳入 `{r["line"] for r in rows}`。
- 其餘 `scripts/test_lumos.py` 裡的舊測試是直接呼叫、沒傳條款行,預設值 `()` 讓行為跟修補前一樣。
- 其他讀 `v["sections"]` 的地方(`scripts/lumos:81539`、`81546`、`81749`)和 `v["all"]`、`v["block"]` 都出自同一份視圖,所以第 2 層驗證、`deps_sha`、材料三個讀者拿到的是同一份段落,不會分叉。
- `clause_bindings` 的定義行是 `defined[cid] = (no, seg)`,只有第一筆。重複編號的後續行(`dup_lines`)不在 `rows` 的 `line` 裡,會留在正文。這跟 `clauses` 字典只存第一筆的口徑一致,不算新問題。

**新測試能不能抓到改壞?** 能。我在複製出的目錄裡把 `| set(clause_lines)` 拿掉,`t_choice_plan_view_body_drops_clause_lines` 兩條斷言都紅,真計劃那條抓出 S1、S2、S3 漏進正文。還原後原本是 2 passed。

**唯一弱點(不擋):** 真計劃 `/Users/enzo/harness/lumos-reach3/docs/lumos-toolchain-knowledge/Projects/逃逸自動記_計劃.md` 的標題要是日後改成純「## 驗收條款」,那條斷言會變成永遠綠、不再驗證修補。自造語料那條仍然釘著修補,所以保護沒有消失,也不會出現假紅。

**清理:** 我跑測試留下的 `gctl-run-2dvmzixo` 暫存現場與複製出的實驗目錄都已刪除。

總結:最高等級是 clean
