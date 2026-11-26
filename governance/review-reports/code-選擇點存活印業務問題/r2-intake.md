# code-選擇點存活印業務問題 r2 收貨

- 派兩席全新(正確性-sonnet、架構對齊-sonnet),審 r2-snapshot.patch(288 行);正確性席另附 r2-repair.patch(r1 兩條修補的差異)。
- 兩席第一次交回都卡格式:正確性席總結句提到上一輪的「minor」字樣,架構對齊席兩條等級寫成列表項;都退回原席重交,只改格式,內容不變。
- 兩份都過 report-normalize;架構對齊席引句全數錨定;正確性席判 clean、零條發現。

## 發現與去向

| id | 席 | 等級 | 內容 | 去向 |
|---|---|---|---|---|
| a2 | 架構對齊-sonnet | minor | `_choice_points_rows` 回要印的字串清單,本 repo 回字串行的慣例是 `_lines` 後綴(`_rows` 是資料列) | 折:改名 `_choice_points_lines`(r1 a1 那次改名選錯後綴,這次照鄰居 `_doctor_metric_lines`) |
| a3 | 架構對齊-sonnet | minor | choice-points 用顯示字串前綴「存活」判斷要不要印,鄰居是用判定鍵產生顯示字串 | 放行:`_choice_ledger_status` 只交出顯示字串,改成看判定鍵要改它的回傳介面,比這次改動大;帳上所有存活字樣都以「存活」開頭,t_choice_survivor_why 已直接釘住四種狀態 |

重現表:a2 HIT(讀碼:回傳 list、鄰居 `_lines` 後綴回字串行);a3 HIT(讀碼:`st.startswith("存活")`)。

## 先查世界

PRIOR-ART: a2 是改名,照本 repo 既有命名慣例(回字串行用 `_lines`,例 `_doctor_metric_lines`);不涉及判讀或防護機制,沒有業界做法可查。
