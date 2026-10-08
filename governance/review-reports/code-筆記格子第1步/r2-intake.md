# r2 收貨與處置(code-筆記格子第1步,修正差異,high 七席)

七席收齊才動碼。正確性、通才兩份 severity 寫在列表項裡,`report-normalize --write` 做純格式搬移。通才 R2U2 第一句引句是它自己的概括(報告裡寫明),第二句錨定;下表重現。併發資源、資安兩席 clean。

## 重現

| id | 做法 | 結果 |
|---|---|---|
| R2G1/R2C1/R2B3 | 舊 `DEP:[[甲]]` 改成 `DEP:[[甲改名]]` 跑 --staged --slots | HIT:被擋,與計劃「改了連結也算舊行」矛盾;改計劃成「只認補連結,換、刪連結算新寫」,範本改給 SEE;⑪翻紅驗過 |
| R2U1 | 舊 `WHY:舊的一句話` 後接續行 | HIT:修前 rc0;只改續行時回頭查整條、第一行對上只給實體行來源;⑦翻紅驗過(兩處各自翻紅) |
| R2B1 | 舊 `WHY:a bc`、新 `WHY:ab c`;舊 `WHY:不能和平共處`、新 `WHY:不能平共處` | HIT:文字鍵改成空白只在中日韓字旁去掉、英文壓成一格,「和與及見」不當分隔;⑩翻紅驗過 |
| R2B2 | 舊 `DEP:[[甲|說明]]` 補 `[confirmed:]` | HIT:鍵改用從寬的連結正規式(含別名段落);⑨ |
| R2C2 | 開擋前多行、開擋後重排成一行,推送 | HIT:窄窗口,寫進計劃天花板 10 |
| R2B4 | 檔名含引號、tab、ESC 的筆記 | HIT(既有):寫進計劃天花板 11 |
| R2B5 | 讀 `_vault_in` | HIT:說明改正 |
| R2G2 | 對照計劃〈擋〉治理帳與 doctor 兩句 | HIT:計劃改寫(check、格名、--ci 不唸) |
| R2G3/R2G4/R2U3 | 拿掉修法跑 slots 子集 | HIT:補 t_slots_fail_open_and_output_hygiene(批次讀失敗、選圖譜、合併、清控制字元)與推送說明斷言,逐項翻紅驗過 |
| R2G5/R2U2 | 推送側多行條目、pre2 改名 | HIT:補 ⑧;兩道保護的分工寫進 `_ns_slot_line_problems` docstring |
| R2A1 | 舊違規印路徑、doctor 那行 | HIT:兩處也過 `_esc_clean` |
| R2A2 | 比對鍵靠長度分、None 鍵 | HIT:鍵第一格標 text/ptr,舊行集合改成 text/ptr/phys 三個明確欄位 |
| R2A3 | 混合違規的帳 | HIT:check 記成 shape+slots |
| R2A4 | doctor 依 ci 分流 | HIT:理由寫在註解與計劃〈擋〉 |

## 處置

全部折入:R2C1 R2C2 R2B1 R2B2 R2B3 R2B4 R2B5 R2G1 R2G2 R2G3 R2G4 R2G5 R2U1 R2U2 R2U3 R2A1 R2A2 R2A3 R2A4。無放行。
