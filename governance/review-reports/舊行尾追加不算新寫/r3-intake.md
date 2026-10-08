# 舊行尾追加不算新寫 r3 收貨(末輪)

審材:r3-snapshot.md(第 3 版,192 行)。席位:正確性 6 條(F1–F6)、邊界可執行 7 條(E1–E7)、整合同步 6 條(I1–I6)、架構對齊 4 條(Z1–Z4);共 23 條,major 9 條(F1、F2、F3、E1、E2、E3、E4、I1、Z1),七個根因。
- 四份都已是正規化格式。引句:正確性那份 F4 的引句不到 10 字被判錨不到——編排者讀 `_note_audit_doctor_lines` 與 `_note_audit_covered` 機械重現成立,照採;其餘全錨。引用:邊界那份的 `scripts/new.py:10` 是情境裡舉例的檔,不是引 repo 檔。
- 前輪修復清單:四席分別驗收,沒到位的都對應到本輪 finding(F1/E2/I2、F2/E1、F3/F4、I1)。
- 到上限(第 3 輪)仍有 major:攤人裁,Enzo 選「折入第三輪後進實作」(實作走高風險代碼審再驗)。本輪 major 一律折,不放行、不派辯方(都有可執行證據且多席獨立一致或編排者讀程式核過)。

## 依根因分組

1. 共用裁法簽名(F1、E2、I2、Z2):`_gate_event_fit` 補 `hard`、`head_sha`、`nodes` 參數與回傳 `nodes`,`then(extra, nodes)` 回傳新 `nodes`;舊句檢查帳逐位元組不變。
2. 作者補救(F2、E1):只剩推送前 `reset --soft` 回範圍起點重提;`amend` 與推上去後改寫或刪括號都整行查,推上去後只能在後面再補一段;S38 與天花板 9 改寫。
3. 判定涵蓋(F3、F4、I4、Z4):fold 改成(編號, tail)、共用的 `_note_audit_class_for` 給六處呼叫端;略過只在適用判定都沒有時算;skip 檢查看任何 tail;doctor 先取最重再照現行只認 CONTEXT/SKIP;S33、S34 補情境。
4. 被刪行比對(E3):兩邊都去尾端空白再比。
5. 放寬帳口徑(E4、I5):暫存表、喚醒後定案,被喚醒的行整行不算;`pairs` 只記有減掉的行。
6. 新分支首推(I1、E6):收窄「本機與 CI 同一個起點」到已存在的分支;既有差異寫進依據與天花板 10;S22 改成兩種範圍各跑一次;新增 S41 釘方向(CI 只會更嚴)。
7. 第二套用到才算(Z1):改成跟 `_NotelinesNet` 同形的小類別 `_NotelinesPairs`。
8. 文件精度(F5、I3、F6、E5、E7、I6、Z3、架構席落點提醒):doctor 改起點那句移到第二層;括號寫成真的全形碼點、零空白算、行內程式碼裡的括號照算;`tail` 不是字串整檔當壞(新增 S40);〈回退〉寫明兩個提交各放什麼;失敗帳 `state` 值域照舊句檢查帳(done/git-failed/error);`lands_in` 加 `Systems/reversibility-governance-ledger`。

## 重現表

| id | 現象 | 怎麼重現 | 結果 | 去向 |
|---|---|---|---|---|
| F1 | 共用裁法簽名做不出舊句檢查帳 | 讀 `_drift_m1_fit` 與 `_drift_m1_ledger` | HIT | 折(第 1 組) |
| F2 | 推上去後改寫括號配不上 | 依配對條件推演(O' 是起點版本整行) | HIT | 折(第 2 組) |
| F3 | tail 判定與略過、skip 合併沒定義 | 讀 `_note_audit_fold`、`cmd_note_audit_skip` | HIT | 折(第 3 組) |
| F4 | doctor「任何判定就算」含 CODE | 讀 `_note_audit_covered`、`_note_audit_doctor_lines`(編排者機械重現) | HIT | 折(第 3 組) |
| F5 | 第一層 doctor 起點說明不符 | 讀第一層 doctor 的掃描上限處理 | HIT | 折(第 8 組) |
| F6 | 全形括號寫成半形 | 編排者在計劃裡找 U+FF08,0 筆 | HIT | 折(第 8 組) |
| E1 | amend 與推上去後改寫都配不上 | 同 F2,另推演提交前起點 | HIT | 折(第 2 組) |
| E2 | 共用裁法簽名 | 同 F1 | HIT | 折(第 1 組) |
| E3 | 被刪行比對有兩種讀法 | 讀計劃 | HIT | 折(第 4 組) |
| E4 | 喚醒的行條數口徑 | 讀 `_note_shape_eval` 喚醒段 | HIT | 折(第 5 組) |
| E5 | 括號字元、零間隔、行內程式碼 | 讀計劃 | HIT | 折(第 8 組) |
| E6 | S22 證明不了起點相同 | 讀計劃 | HIT | 折(第 6 組) |
| E7 | tail 不是字串怎麼辦 | 讀 `_note_audit_parse_verdict` | HIT | 折(第 8 組) |
| I1 | 新分支首推本機與 CI 起點不同 | 讀推送前掛鉤的範圍算法與 CI 的 `$BEFORE` | HIT | 折(第 6 組) |
| I2 | 共用裁法簽名 | 同 F1 | HIT | 折(第 1 組) |
| I3 | doctor 起點說明套錯層 | 同 F5 | HIT | 折(第 8 組) |
| I4 | record 與 skip 的涵蓋沒交代、docstring 漏 | 讀 `cmd_note_audit_record`、`cmd_note_audit_skip` | HIT | 折(第 3 組) |
| I5 | 喚醒的行條數口徑 | 同 E4 | HIT | 折(第 5 組) |
| I6 | 〈回退〉措辭矛盾 | 讀計劃 | HIT | 折(第 8 組) |
| Z1 | 第二套用到才算 | 讀 `_NotelinesNet` | HIT | 折(第 7 組) |
| Z2 | 共用裁法簽名與 then 回呼 | 同 F1 | HIT | 折(第 1 組) |
| Z3 | 失敗帳 state 值域不同 | 讀舊句檢查帳的 state 值 | HIT | 折(第 8 組) |
| Z4 | fold 鍵形狀改了、六處呼叫端 | 讀六處 `fold.get` | HIT | 折(第 3 組) |

## 折入後鏡像核對(便宜 agent,材料含本目錄席報告)

23 條都找得到去向;補了 6 處舊說法殘留:〈做法〉3 的「取得函式」改成 `_NotelinesPairs` 的 `table()`;S18、S23、S26 的 `state` 值改成 done/git-failed/error;同步清單 skill 子檔那句改成只有 `reset --soft` 重提;`_gate_event_fit` 的 `then` 寫明「清單丟光或本來沒有」都會試、照現行「nodes 多於 20 且仍超過」才截(編排者讀 `_drift_m1_fit` 核過:現行不看 rows 在不在)。
