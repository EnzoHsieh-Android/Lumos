# r1 收貨紀錄

## 機械驗證

- 單reviewer-sonnet:quote-check 5 句有 1 句錨不到(F4 引的是計劃第 417 行原文,那一行這次沒改,不在凍結差異裡);report-normalize 只把檔尾總結句的等級搬成獨立行。
- 架構對齊-sonnet:quote-check 全數錨定;格式不用改。

## 重現表

| id | 席 | 怎麼重現 | 結果 |
|---|---|---|---|
| r-F1 | 單reviewer | 在綁定比對迴圈對 expires_on=null 的項跳過,跑 t_secev_s68_review_no_expiry | HIT:修前照綠(②接受兩種代碼);修後同一改壞讓 ① ② 翻紅 |
| r-F2 | 單reviewer | 把 _SECAPR_NO_EXPIRY_TYPES 加上 gate_setting,跑 t_secev_s68_review_no_expiry | HIT:修前照綠(④只測 exception);修後逐型別測,同一改壞翻紅 |
| r-F3 | 單reviewer | 兩把金鑰,null 人審由 key0 簽,key1 撤銷 key0,判定 | HIT:修前人審照 ok、review qualified;修後判 approval_signer_revoked |
| r-F4 | 單reviewer | grep 計劃第 417、726、755 行與 d10 原文 | HIT:三處只寫日期、d10 仍寫人審 90 天(引句錨不到是因為那幾行不在差異裡,原文以 grep 核對) |
| r-F5 | 單reviewer | 讀舊版 _secev_ip_review 與 _secapr_entry_shape | HIT:舊版遇 null 判整塊看不懂,只多擋不漏放 |
| a-F1 | 架構對齊 | 讀 _secev_stage_judge 的 considerations 讀法對照 _seccell_compute | HIT:旁路沒驗形狀與核可;修後改用 _seccell_compute 的 pending,沒核可的格子不算(S69 ③ 新增對照) |
| a-F2 | 架構對齊 | grep 三處「允許 null」條件 | HIT:三處各寫一份;修後收成 _sec_no_expiry |

## 處置

全部折入,沒有放行、沒有駁回。
