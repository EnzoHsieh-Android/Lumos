# r3b 收貨(2026-09-18;=r3 換編號重記:r3 那筆把資安席五段「已看,無」記成 accepted,而 code 迴圈輪內有 major 時 accepted 必空,閘擋;帳不能撤銷只能換編號。上限輪,三個全新席看第二輪折法;外家仍缺席:Codex 額度用盡至 2026-09-19 21:45)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| S1 | 資安-r3-sonnet | major | HIT:只改 governance/anchor-baseline.json → suite=docs,--suite docs 不含 t_anchor* | 折:_DOCS_ONLY_NEVER(基準線、governance/code-loop/)碰到就 full;案例⑦b/⑦c |
| S2 | 資安-r3-sonnet | minor(推論) | HIT:同上形狀 | 折:同 S1 |
| S3 | 資安-r3-sonnet | minor | 席位自述「已看,無」,不是發現(報告格式把每段都掛了 severity 行) | 折:非發現,無可折,視為已處置(不得 accepted:輪內有 major) |
| S4 | 資安-r3-sonnet | minor | 同 S3 | 折:非發現,同 S3 |
| S5 | 資安-r3-sonnet | minor | 同 S3 | 折:非發現,同 S3 |
| S6 | 資安-r3-sonnet | minor | 同 S3 | 折:非發現,同 S3 |
| S7 | 資安-r3-sonnet | minor | 同 S3 | 折:非發現,同 S3 |
| A1 | 架構對齊-r3-sonnet | major | HIT:`--shard 3/2` 先被「片號要在片數內」擋成 rc2,沒走到「這片沒分到」 | 折:改 2000/2000,斷言 rc1 且訊息「一支測試都沒分到」 |
| A2 | 架構對齊-r3-sonnet | minor | HIT(引句在 patch 外、機械重現 21723 行):cochange upto 同語意舊寫法 | 折:改 _range_base(root, diff_range) or "HEAD" |

★r3 是上限輪:這輪折入(三處)之後沒有下一輪新席再看;REVISIT 記在計劃節點。
