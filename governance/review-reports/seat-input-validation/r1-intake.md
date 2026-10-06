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

## 正式六席判讀

| distinct ID / 原始 ID | 重現 | 判準及處置 |
|---|---|---|
| encoding-F1 / logic-F2、integration-F1 | HIT：真 CLI 高／低孤立 surrogate 回1、UnicodeEncodeError；r1-formal-repro.json | 折入：借 os.fsencode 先驗可編碼性，轉索引 rc2；160斷言在原碼66綠94紅 |
| landing-F1 / resources-F1、architecture-F4 | HIT：原CLI read節點僅14原語；既有design-loop已載seat-check收貨三道 | 折入：lands_in改既有Systems/design-loop；保留原等級與不同建議，不新增機制 |
| logic-F1 | HIT：重複名稱解析後 materials=[]、CLI rc0；MISS：違反本案規格的判準 | refuted：新鮮單問題辯方 verdict evidence，原S1／S3允許解析後合法空清單；不擴張唯一鍵政策 |

六席原始報告共5條、blocking3；兩條重複編碼發現與兩條重複落點發現各歸一，存活distinct2，反證排除1，折2、接受0。severity不改寫。正式收貨對每席的平坦派工單與凍結snapshot；逐項檔名提及只是字串觀測，不是真閱讀證明。

第一份雙問題核對報告等級／blocking不一致，整份不用；保留r1-adjudication-raw.md及收據。另派全新、單問題辯方完成協議正確的r1-defense-dupkeys-raw.md，據其客觀引證排除logic-F1。

fold-check回1為project無summary的reverse-omission提醒；正文已有完整理由、碼路徑與卷證，摘要分類規則不允許複寫程式現況。實際鏡像另派乾淨席讀全部本輪卷證與折入diff核對。

首筆記帳嘗試 rc2：目前 CLI 的 refute-verdict 只接受 findings-set 的存活 ID，不接受 refuted-set 的 logic-F1；沒有成功 canary 列，未重記已有成功帳。保留 r1-record-logic-blocked-refute-verdict.json，移除不支援的旗標，反證 verdict 與 file:line 仍保存於原辯方報告和本 intake，refuted-set 理由照實記入。這是編排參數更正，不另開輪次或重設帳本。
