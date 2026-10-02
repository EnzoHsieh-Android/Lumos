# code-筆記格子第2步 r2 收貨

審材:r1 修正差異(r2-snapshot.patch)。席位:正確性-sonnet(3 條,major 1)、架構對齊-sonnet(3 條,全 minor)。
本輪有 major → accepted 必空,6 條全折。

## 重現表

| id | 現象 | 怎麼重現 | 結果 | 去向 |
|---|---|---|---|---|
| R2C1 | 表態只比 RULE 第一個實體行:續行條件不同的兩條互相放行;表態後改續行條件舊表態照樣有效 | t_slots_retire_followups ①b(改續行條件後再推)、①c(第一行相同的兩條只表態一條);ack 改回只記實體行時兩項都紅 | HIT | 折:判定與 drift ack --kind retire 都用接回續行的整條(新函式 _drift_ack_text);r1 C1 的「給實體行」改法撤回 |
| R2C2 | 每次跑都記 passed,跟 drift-check 閘「放行不寫帳」的既有規矩衝突;治理帳寫入者清單沒補 | 讀 Systems/reversibility-governance-ledger 那條 WHY 與 Issues/治理帳多個寫入者都沒上鎖;測試 ⑤:沒成立時不該有帳,改回每次記 ⑤紅 | HIT | 折:只在有成立或判不了時記;起點不是 sha 記空字串;Issue 補一句新寫入者 |
| R2C3 | 測試沒釘住:壞值+gate=warn、gate=off+retire=block、推送印提醒、逾時訊息分 kind、固定段指令行 | 席位在臨時 clone 拿掉判斷實跑仍綠 | HIT | 折:測試補 ②c、③b、③c 與固定段指令行斷言,每項翻紅已驗 |
| R2A1 | 帳的欄位詞跟 m1 兩套(must/unknown 對 handle/listed),nodes 截 50 沒有 m1 的尺寸保護 | 讀 _drift_m1_ledger | HIT | 折:改用 handle/listed;nodes 截到 20(m1 尺寸保護丟光 rows 後的同一個上限;這支不帶 rows) |
| R2A2 | 例外兜底只印一行、不記帳,跟 m1 兜底不同 | 讀 _drift_retire_guarded 對照 _drift_m1_guarded | HIT | 折:兜底也記一筆 warned(帶 error);判不了不擋是計劃寫明的例外,不改 |
| R2A3 | 測試內聯解析治理帳、ack 不走共用寫法 | 讀測試 | HIT | 折:抽出 _rt_events(用既有 _ns_gov)、_rt_ack、_rt_line、_rt_inproc 共用小工具;ack 用 cwd 是因為 drift ack 不收 --repo(r1 實跑時擋下「不認得這幾個參數」) |
