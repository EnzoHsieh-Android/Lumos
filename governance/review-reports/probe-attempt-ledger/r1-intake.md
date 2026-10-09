preflight-4: ran

獨立前掃原稿 r1-preflight-original.md。語意澄清：明列兩個真runner與父派工器、時間欄位及五小時邊界、fatal傳遞、傳遞原始窗口上限、不把首次limit呼叫與被拒重試混為一談。核心裁定（SQLite、launch-intent、首五小時保守初始化）未在前掃自行變更，交正式席。prose-lint的一處「必要時」已改為明列事件與判準。

## 正式收貨與折入

四席原稿與純格式重發俱保留，重發只补文件級與每條finding的獨立宣告，未重跑或更改觀察。八條去重為LD1–LD6，全部folded，不用新代碼／執行器補設計因果故事。

- LD1：明確零值完全停用帳；受管域不包含零值／舊版／其他工具，補S5切換驗收。
- LD2：明確本機額度拒絕的例外、失敗結果列、limit_hit=false、fatal/inconclusive、rc3及父程序保留原候選停止，補S6。
- LD3：明列先停舊版與未受管探針、確認無在途的人工切換前提；不宣稱五小時自動阻止舊版。
- LD4：初始化與claim均存REAL epoch秒，不取整；同一now計數，<=now-18000已過期。
- LD5：父程序先建pending與log再查帳；查詢异常寫正式事故、設stop；候選不存在不捏造，S3補父故障驗收。
- LD6：sleep前檢查兩種剩餘額度；已滿零sleep；清楚限定檢查後的並行race仍可能等待但不多啟動。
