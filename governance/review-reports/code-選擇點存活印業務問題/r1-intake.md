# code-選擇點存活印業務問題 r1 收貨

- 派兩席(standard:正確性-sonnet、架構對齊-sonnet),審 r1-snapshot.patch(282 行,不拆包)。
- 正確性席第一次交回的總結行寫成「max severity: minor」,report-normalize 轉不了,退回原席重交(只改總結行;重交時內文改成中文,發現與引句不變)。
- 兩份都過 quote-check(全數錨定)與 refcheck(引的檔與行號都存在)。

## 發現與去向

| id | 席 | 等級 | 內容 | 去向 |
|---|---|---|---|---|
| c1 | 正確性-sonnet | minor | choice-points 帳上狀態「存活(合併快篩判)」沒有測試案例,把前綴判斷改成完全等於「存活」測試照綠 | 折:t_choice_survivor_why 補四種狀態的直接案例;改壞成 `== "存活"` 實測翻紅(HIT) |
| a1 | 架構對齊-sonnet | minor | `_choice_points_line` 名字像回一行,實際回清單,跟 `_choice_why_line` 回字串不一致 | 折:改名 `_choice_points_rows` |

重現表:c1 HIT(複本把 startswith 改成 ==,新斷言紅);a1 HIT(讀碼即見,回傳 list)。

## 先查世界

PRIOR-ART: c1 是補測試案例、a1 是改名,兩者都不涉及判讀或防護機制,沒有可借的業界做法;照本 repo 既有寫法(直接呼叫函式的單元案例同 t_choice_kill_verdicts 後段、函式名 `_rows` 回清單同既有 `_kill_*_rows`)。
