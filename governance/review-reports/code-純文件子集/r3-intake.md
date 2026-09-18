# r3 收貨(2026-09-18;上限輪,三個全新席看第二輪折法;外家仍缺席:Codex 額度用盡至 2026-09-19 21:45)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| S1 | 資安-r3-sonnet | major | HIT:只改 governance/anchor-baseline.json → suite=docs,--suite docs 不含 t_anchor* | 折:_DOCS_ONLY_NEVER(基準線、governance/code-loop/)碰到就 full;案例⑦b/⑦c |
| S2 | 資安-r3-sonnet | minor(推論) | HIT:同上形狀 | 折:同 S1 |
| S3 | 資安-r3-sonnet | minor | 席位自述「已看,無」,不是發現(報告格式把每段都掛了 severity 行) | 放行:非發現,無可折 |
| S4 | 資安-r3-sonnet | minor | 同 S3 | 放行:非發現 |
| S5 | 資安-r3-sonnet | minor | 同 S3 | 放行:非發現 |
| S6 | 資安-r3-sonnet | minor | 同 S3 | 放行:非發現 |
| S7 | 資安-r3-sonnet | minor | 同 S3 | 放行:非發現 |
| A1 | 架構對齊-r3-sonnet | major | HIT:`--shard 3/2` 先被「片號要在片數內」擋成 rc2,沒走到「這片沒分到」 | 折:改 2000/2000,斷言 rc1 且訊息「一支測試都沒分到」 |
| A2 | 架構對齊-r3-sonnet | minor | HIT(引句在 patch 外、機械重現 21723 行):cochange upto 同語意舊寫法 | 折:改 _range_base(root, diff_range) or "HEAD" |

★r3 是上限輪:這輪折入(三處)之後沒有下一輪新席再看;REVISIT 記在計劃節點。
