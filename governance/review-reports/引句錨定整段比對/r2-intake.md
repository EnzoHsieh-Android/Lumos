# r2 收貨紀錄(6 席全新)

## 引句錨定狀況

quote-check:接手的人、最壞時序、回滾三席全數錨定(載體選接手的人);正確性 7/14、邊界 5/14、架構對齊 1/5 句錨不到。錨不到的原因同 r1:被審計劃含巢狀引號(舊抽取器截在內層),席位報告裡的示範輸入含「引句:「…」」字樣也被當成引句去比。

## 機械重現表

| 群 | 涵蓋 finding | 重現命令/查證 | 結果 |
|---|---|---|---|
| 「標籤」邊界未定義、可繞 | C1 B2 | 讀 r2-snapshot.md 抽取規則 3、4 只寫「下一個標籤」;以 scan4 同型實作對 `引句:「真的原文真的原文真的」這是引句：編造後半」` 依兩種讀法各跑 | HIT:兩讀法結果相反,其一放過 |
| 引句內含標籤產生幽靈條目 | C2 B3 | 讀 r2-snapshot 規則 6「標籤數就是結果條數」與規則 3 邊界;構造外層引句內含「引句:「…」」 | HIT |
| 章的值域與讀章 | B1 T4 | grep `scripts/lumos` 的 `_GOV_FIELD_TYPES` 無 quote_rule;r2-snapshot 只定義有值/缺/不認得 | HIT |
| 舊版讀新章、無章靜默 | T1 T2 C7 | 讀 `scripts/lumos` `_REPLAY_ENGINE_REV` 與 `cmd_loop_replay` 的 engine_rev 判斷;處置閘通過時只印「全數錨定」不印判準 | HIT |
| 隔離閥缺、回退不成立 | R1 R2 R3 | 讀處置閘引句步驟 try 只接 OSError/UnicodeDecodeError;凍結只擋 rc2;現有 golden 有 5 個 rc1 | HIT |
| 擋下事件與 gov 統計 | R4 A2 T6 B7 H7 | 回滾席在暫存 repo 實寫兩筆 canary/blocked 跑 `gov --stats`,新事件落進「缺 refuted-set」;同檔既有擋下 note 帶 id= | HIT(回滾席實測,本表照其命令與輸出) |
| compare-rules 參數與容錯 | B4 B5 B6 H2 A4 R5 | `scripts/lumos` quote-check parser 的 qc_report 必填、--spec required;`gov --since` 為整數天數 | HIT |
| 量測不可重現 | H1 C4 | 用 r2-snapshot 寫的口徑重算總組數 3273(讀不到 20、零引句 221),與稿中 2631 不符;交叉表加總 2676 > 2631 | HIT(稿中 2631 為編排者抄錯) |
| 測試缺口 | C5 T3 R6 A1 | 讀 `scripts/test_lumos.py` t_quote_full_span_*:只有一輪一列;無回放、無停用;S6 讀 v.parent 的治理帳(實際落 root/docs) | HIT |
| 同步清單與驗證步驟 | H3 H4 H5 H6 C3 C6 A3 A5 | 05 檔第 14 行是 quote-check 指令列、無「收貨三道」;templates §1 括號為全形;基線「自己比自己」;回放單個約 0.8 秒 | HIT |

## 處置

- 折入 40 條(全部):見計劃審計修正紀錄 r2 那行;測試照第三版條款重寫(S1–S7,實作前全紅)。
- 放行:無。refuted:無。
