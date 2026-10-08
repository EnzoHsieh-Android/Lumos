# 首輪前掃與收貨

preflight-4: ran

前掃原始 major 報告保留，核心裁定原文未改。補測試背書後交正式席覆核，前掃不計入正式 canary findings。

| ID | 重現 | 結論 | 處置 |
|---|---|---|---|
| PF1 | 原132斷言只查擋下前綴；補 dispatch／materials／materials[項次] 預期後原版仍翻紅 | HIT：欄位診斷必須真驗 | 已補測試背書，交正式席覆核 |
| PF2 | 新真 cmd_seat_check AST 讀序探針，首項有效、尾項錯形態；原版讀到材料並拋 TypeError | HIT：帳本未寫不能推論材料未讀 | 已補普通／最佳化觀測，交正式席覆核；無FIFO |

前掃 refcheck 與對原始凍結 spec 的 quote-check 均過；副本、原始報告、執行收據與修正後139斷言59綠80紅的來源指紋留在本目錄。

## 前掃判準的實際反向控制

兩份臨時 CLI 原型只存在私有 TemporaryDirectory，正式程式碼未改。取真正的測試 AST，舊版壞派工測試126斷言對「一律 bad dispatch」與「先讀首項再驗尾項」都全綠；補背書後分別翻紅28與2斷言。完整結果、臨時差分與輸出見 preflight-controls.json、control-*.patch／log。這證明前掃指出的測試弱點可重現，不把原型當正式修復。
