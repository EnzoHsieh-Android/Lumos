# code-審查跑滿回顧 r4 收貨紀錄(2026-10-06)

第 4 輪(到上限後 Enzo 裁 extra-round 的破例輪):全新 7 席(不讀前三輪席報告與 cap-retro.json),審第三輪修正與跑滿提示缺口修正的差異 `r4-snapshot.patch`(15774a0d..a93d8376,排除帳本與卷證,2006 行,sha256 121709ac…;超過 1800 行未拆,派工詞要求主程式段必讀、測試與筆記當查證材料)。第三輪修正關卡 `loop fix-check --round r3` 通過(ec0afdab)。

## 收貨三道
- 七份報告 `quote-check` 對 `r4-snapshot.patch`:全數錨定;`report-normalize`:全部正規。
- 收件前 `git reflog -1` 只有編排者自己的提交。

## 編排者重現(佐證通道)
| id | 依據 | 結果 |
|---|---|---|
| A2/G1/C1/K4 | 四席各自實跑 `loop next` 到 cap-reached 印兩行記人裁指令;編排者讀碼確認 `_cap_retro_next_lines` 與 `_cap_hint_lines` 各印一次 | HIT(多席+讀碼) |
| A1/G3/B2/K1 | 四席造只用 \r 行尾的治理帳,`_retro_gov_events` 與 `_drift_jsonl_iter` 系讀者筆數不同;編排者讀碼確認 `_drift_jsonl_iter` 說明寫「只在 \n 切行」 | HIT(多席+讀碼) |
| P1 | 併發席實跑黏行;編排者讀碼確認 `_codeloop_gov_log`、`_codeloop_dispositions_gov_log` 直接 `open(path, "a")`,兩支在本分支之前就存在(`git log -S` 最早 da5f9636),本分支沒改 | HIT(單席+讀碼) |
| S2 | 資安席實跑帳換成指向 /dev/zero 的捷徑,`loop list --all` 記憶體持續成長(腳本 /private/tmp/claude-501/r4/) | HIT(單席,可執行證據) |
| S1 | 資安席實跑輪次帶 ESC/C1,`[cap-hint]` 與處置閘橫幅原樣輸出 | HIT(單席,可執行證據) |

## 逐條去向(25 條;使用者 2026-10-06 裁:修本次改動範圍內的,既有程式的缺口開 Issue,記 accept-risk 後推送)
本輪有 major 放行,處置閘依 code 迴圈規則不會過;放行由人裁 accept-risk 承擔(見治理帳 loop-retro cap-decision)。

| id | 席 | 嚴重度 | 一句 | 去向 |
|---|---|---|---|---|
| A2 | 架構 F2 | major | 記人裁指令在 loop next 印兩次(修補引起) | 折:單一來源 |
| G1 | 通才 F1 | minor | 同 A2 | 折:單一來源 |
| C1 | 正確性 F1 | minor | 同 A2 | 折:單一來源 |
| K4 | 合約 F4 | minor | 同 A2,記完人裁後兩句矛盾 | 折:單一來源 |
| G4 | 通才 F4 | minor | 治理帳壞時 cap-hint 仍叫人記人裁 | 折:單一來源 |
| C2 | 正確性 F2 | minor | 同 G4 | 折:單一來源 |
| A3 | 架構 F3 | minor | 治理帳壞時統計多出假迴圈(修補引起) | 折 |
| G2 | 通才 F2 | minor | 同 A3 | 折 |
| C3 | 正確性 F3 | minor | 同 A3 | 折 |
| B4 | 邊界 F4 | minor | 同 A3 | 折 |
| K2 | 合約 F2 | minor | 同 A3 | 折 |
| S1 | 資安 F1 | major | 跑滿提示與處置閘橫幅原樣印輪次編號 | 折 |
| P3 | 併發 F3 | minor | 治理帳權限打不開時出口提示只叫人換檔(修補引起) | 折 |
| B3 | 邊界 F3 | minor | 同 P3 | 折 |
| B1 | 邊界 F1 | minor | `_append_governance_log` 一筆無法編碼就整批靜默丟(修補引起) | 折 |
| K3 | 合約 F3 | minor | 計劃與筆記沒跟上 gov-bad 第五種狀態與 S17 例外(修補引起) | 折 |
| A1 | 架構 F1 | major | `_drift_jsonl_iter` 系讀者只認 \n,與 `_ledger_lines` 兩套 | 放行:既有讀者、本分支沒改;把「所有讀者」的錯誤說法更正,統一切行開 Issue |
| G3 | 通才 F3 | minor | 同 A1 | 放行:同 A1 |
| B2 | 邊界 F2 | minor | 同 A1 | 放行:同 A1 |
| K1 | 合約 F1 | minor | 同 A1 | 放行:同 A1 |
| S2 | 資安 F2 | major | 約 20 處讀帳不判一般檔、不限大小 | 放行:既有讀者、本分支沒改;開 Issue |
| P1 | 併發 F1 | major | code-loop 兩支治理帳寫入器沒補換行、沒接編碼例外 | 放行:既有寫入器、本分支沒改;更正「兩支寫入器」說法,開 Issue |
| P2 | 併發 F2 | minor | 審查帳寫入器 `_jsonl_append_verified` 沒補換行 | 放行:既有寫入器;開 Issue |
| A4 | 架構 F4 | minor | fix-check 紀錄樣板原樣輸出帳上 C1 | 放行:既有功能;開 Issue |
| S3 | 資安 F3 | minor | `_gate_event` 仍經捷徑寫到 repo 外 | 放行:計劃〈誠實界線〉已記,REVISIT 2026-11-06 |

修補引起(regression-set):A2、G1、C1、K4、A3、G2、C3、B4、K2、P3、B3、B1、K3。
