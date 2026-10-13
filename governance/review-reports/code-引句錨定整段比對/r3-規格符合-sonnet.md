severity: minor

規格〈做法〉〈驗收條款 S1–S8〉〈兩階段上線〉〈量測與留痕〉〈同步改的地方·第一階段〉我逐條對過程式與測試,只找到 1 條字面出入,沒有 blocking。

我讀了 patch 和 repo 現檔,沒有跑測試,所以測試是否為綠沒有驗到。

**1. 處置閘印的判準行多了 `[disposal] ` 前綴,跟規格字面不同**
severity: minor
blocking: 否
引句:「print(f"[disposal] 引句判準:{_qlabel}")」
file: `scripts/lumos:26516`
- 規格〈判準版本蓋在帳上〉寫「第一行印『引句判準:<版本>』(沒章時印『引句判準:legacy(帳上無章)』)」。
- 程式印出來的是 `[disposal] 引句判準:...`,前面多了處置閘各行共用的前綴。
- 我判斷這是刻意跟同一閘的其他行對齊。測試只用「字串包含」判斷,所以不會紅,實際上也不會誤導任何讀者。
- 要嘛規格補一句「帶 `[disposal]` 前綴」,要嘛維持現狀。手動 `quote-check` 的第一行是逐字的「引句判準:<版本>」,與規格一致。⚠ 判不準規格要不要嚴格到前綴。

**規格有寫、程式也做到的部分**
- 抽取規則六步:預先配對、標籤處理、被後面的閉引號補閉合時整段錨不到、各條尾段自己數落單收尾引號、unclosed 取到行尾且最多 200 字、只有格式不合的列截斷。
- `_quote_rows` 的必填 `rule` 與 `ValueError`,以及四個呼叫點加比較模式都明確傳 rule。
- 舊判準一字未改:我拿 `_quote_rows_legacy` 跟 base 的 `_quote_rows` 逐行 diff,只差函式名那一行。
- 寫側:常數 `_QUOTE_WRITE_RULE` 是 `legacy`,通過時載體列蓋 `quote_rule`,被擋時不寫帳,主檢查丟例外照原樣往外傳。
- 章的讀法:沒有章用 legacy,章值不認得判失敗並印規格那句訊息,不印診斷指令。
- 處置閘:判準丟例外判失敗並印型別,四種失敗都另印診斷指令,路徑用 `_sh_quote` 並把開頭是 `-` 的補成 `./`,`MemoryError` 照常往外丟,錨不到那行另標格式不合條數。
- 擋下事件:note 欄位順序與規格一致(`quote=` 排在最後),kind 取值與 `unknown` / `err` 都對得上。
- `gov --stats` 四格互斥,輸出字串逐字相符。
- 比較模式:五行交叉表與「略過:…」一行逐字相符。
- 比較模式的參數與帳本檢查:報告、`--spec`、`--rule`、`--json` 同時帶時擋下並回 rc2,帳本不存在時回 rc2,帳上路徑與檔案大小有檢查,同一組(報告, 快照)只算一次,快照用完即丟。
- 手動 `quote-check`:第一行印判準,`--rule` 有 choices,`--json` 多 `rule` 欄,格式不合列帶標註,缺報告或 `--spec` 手動擋下,零引句的常見原因已補兩項。
- 第一階段範圍:`seat-check` 用常數,兩個測試替身改收 `**kw` 並加 `_QUOTE_WRITE_RULE`,`t_no_adhoc_normalizer_in_review_reports` 沒動。
- 第一階段只動了規格准許的文件:`lumos-design-loop` 的 `SKILL.md`、`templates.md`,`Systems/loop-convergence-recording` 新增一節,兩篇 Issue,以及驗證紀錄。第二階段的文件(`_CODEX_AGENT_INSTRUCTIONS`、`05-設計審查迴圈.md` 等)都沒碰。
- S1–S8 對應的 8 支測試都存在(`t_quote_full_span_*`),測試內容涵蓋各條款的字面案例。

**程式做了、規格沒寫的**
沒有實質項目。新增的 `_quote_anchor_row` 只是兩版共用的比對輔助,`_QUOTE_LABEL_RE` 是為了不動舊判準而複製的標籤規則,兩者規格都隱含了。

我建的實驗目錄已刪除;repo 內沒有任何寫入。

總結:最高等級 minor,blocking 共 0 條
