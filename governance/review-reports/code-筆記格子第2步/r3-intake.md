# code-筆記格子第2步 r3 收貨(上限輪)

審材:r2 修正差異(r3-snapshot.patch)。席位:正確性-sonnet(3 條,全 minor、blocking 0)、架構對齊-sonnet(2 條,全 minor)。
本輪沒有 major;這是 standard 上限輪,照末輪規矩新 minor 附理由接受、不觸發折返。要做的四項記進 Issues/撤除條件檢查末輪遺留四項,排進第 3 步(同一塊程式、自己有代碼審)。

## 重現表

| id | 現象 | 怎麼重現 | 結果 | 去向 |
|---|---|---|---|---|
| R3C1 | 對續行行號下 drift ack --kind retire 會記實體行、永遠對不上,指令照回成功 | 讀 _drift_ack_text:行號不在 _ns_summary_logical 的鍵裡就退回實體行 | HIT | 接受:擋下時印的是條目第一行、照提示打不會踩到;Issue 第 1 項 |
| R3C2 | 記帳只判不了、hard、nodes、起點非字串、例外兜底沒有斷言 | 席位在臨時 clone 突變實跑仍綠 | HIT | 接受:行為目前正確,只缺斷言;Issue 第 4 項 |
| R3C3 | 印出途中拋例外會記兩筆帳並放行 | 讀 _drift_retire_guarded 與 _drift_retire_report 的順序;找不到現成會拋的輸入 | HIT | 接受:結構在 r2 前就有、觸發不到;Issue 第 2 項 |
| R3A1 | 寫不進帳時沒有 m1 那種快取補記、nodes 上限 20 | 讀 _drift_m1_ledger_miss | HIT | 接受:這支一次推送最多一筆、不帶逐條清單,補記檔是 m1 兩週量測專用;通用寫入器失敗已在 stderr 講;Issue 另段記照留理由 |
| R3A2 | 兜底那筆 handle/listed 記 0,m1 判不了記 null | 讀 _drift_m1_ledger | HIT | 接受:兜底一年碰不到幾次、讀帳以 error 欄分得出;Issue 第 3 項 |
