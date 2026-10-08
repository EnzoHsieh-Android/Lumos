severity: major

# 第一輪彙整與處置

四個獨立席全收齊、原稿及原席純格式重發均保留；八條觀察去重為六組，全部折入設計。沒有執行產品或真模型，不把設計閉合當實作通過。

## LD1

severity: major
blocking: 是
引句:「`--max-per-window 0` 仍明示不設限制」

處置：明確零值完全停用帳；受管域不包含零值／舊版／其他工具，補S5切換驗收。

## LD2

severity: major
blocking: 是
引句:「已達限不插入且rollback，未達限插入並commit；commit成功才啟動模型」

處置：明確本機額度拒絕的例外、失敗結果列、limit_hit=false、fatal/inconclusive、rc3及父程序保留原候選停止，補S6。

## LD3

severity: major
blocking: 是
引句:「新建帳自動從 initialized_at 保守封住首五小時，使新工具上線前或遺失帳後的舊呼叫先過期」

處置：明列先停舊版與未受管探針、確認無在途的人工切換前提；不宣稱五小時自動阻止舊版。

## LD4

severity: minor
blocking: 否
引句:「恰滿五小時的紀錄已過期」

處置：初始化與claim均存REAL epoch秒，不取整；同一now計數，<=now-18000已過期。

## LD5

severity: major
blocking: 是
引句:「初始化、時計與鎖錯誤使用專用 fatal 例外」

處置：父程序先建pending與log再查帳；查詢异常寫正式事故、設stop；候選不存在不捏造，S3補父故障驗收。

## LD6

severity: major
blocking: 是
引句:「其後被本機額度拒絕的重試應零新增 launch-intent，且不再先等待300秒」

處置：sleep前檢查兩種剩餘額度；已滿零sleep；清楚限定檢查後的並行race仍可能等待但不多啟動。
