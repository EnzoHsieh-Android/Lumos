# code-筆記格子第2步 r1 收貨

席位:正確性-sonnet(4 條,major 1)、架構對齊-sonnet(6 條,全 minor)。兩份都已正規化、引句全數錨定、refcheck 無壞引用。
本輪有 major → 依代碼審規則 accepted 必空,10 條全折。

## 重現表

| id | 現象 | 怎麼重現 | 結果 | 去向 |
|---|---|---|---|---|
| C1 | 欄位寫在續行的 RULE,drift ack 記的實體行與判定給的接回整條對不上,表態永遠無效 | 新測試 t_slots_retire_followups ①:續行 RULE 推送擋下 → drift ack 該行 → 再推;改回給整條原文時 ① 兩條斷言紅 | HIT | 折:_retire_lines 原文改給第一個實體行,判定照整條解析 |
| C2 | gate=warn 的專案 retire 沒寫仍預設 block | 測試 ③:gate=warn、retire 不寫 → 修前 rc1、修後 rc0 且照樣提醒;預設寫死 block 時 ③ 紅 | HIT | 折:retire 沒寫照總開關;doctor 加一行(retire 比總開關鬆或寫錯時講) |
| C3 | 核心判定用光時間時撤除條件一條都沒判,且逾時訊息寫成回頭條件 | 測試 ②b:_DRIFT_BUDGET_SEC=-1 時撤除條件照樣判出成立;改回吃核心剩下的時間 ②b 紅 | HIT | 折:自己一個 20 秒截止時間;_drift_probe_check 的逾時訊息依 kind 寫撤除條件 |
| C5 | ⑦ 只驗呼叫順序、ack / 續行 / 預算用完 / gate=warn 都沒測 | 讀測試 | HIT | 折:新測試 t_slots_retire_followups 補 ①②②b③④⑤,每項翻紅已驗 |
| A1 | 同一份設定在一次呼叫裡解析兩遍 | 讀 cmd_drift_check | HIT | 折:改成解析一次,各開關從同一份取 |
| A2 | retire 壞值提醒少了 JSON 壞、drift_check 不是物件兩支 | 讀 _drift_retire_config 對照 _drift_old_sentence_config | HIT | 折:兩支都講一句;測試 ④ 驗 doctor 對壞值講「沒讀懂」 |
| A3 | 治理帳只在成立時記、不帶頂端 | 測試 ⑤:沒成立的推送找不到 check=retire 的帳;只在成立時記 ⑤ 紅 | HIT | 折:每次跑都記(passed / warned / blocked),帶成立與判不了的條數、head_sha、base_sha |
| A4 | 「判不了只列出不擋」是既有「判不了算要處理」的例外,docstring 沒寫 | 讀 cmd_drift_check docstring | HIT | 折:docstring 明寫唯一例外與理由 |
| A5 | 沒印既有的「不改就留著並表態」固定段 | 讀 _drift_report_must | HIT | 折:照同一句型印;測試 ① 驗有這段 |
| A6 | 預算註解說「同舊句檢查的先例」但配法不同 | 讀註解 | HIT | 折:跟 C3 一起改成真的同舊句檢查(獨立截止時間),註解照實寫 |

## 設計文字跟著改

C2、C3 動到計劃裡寫定的設計(預算來源、子開關預設),計劃筆記的設計段與效能段已改、審計修正紀錄補一行「實作期」;存量漂移守衛那條 WHY 同步。
