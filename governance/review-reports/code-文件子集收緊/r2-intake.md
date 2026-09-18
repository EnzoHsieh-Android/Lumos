# r2 收貨(2026-09-18;一個全新通才席看 r1 折法)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| F1 | 單reviewer-r2-sonnet | major | HIT:舊版執行器(有 --suite 沒 --graph)配新掛鉤,只改圖譜筆記的推送四片全 argparse 報錯、被判成「測試有紅」擋下 | 折:掛鉤比照 --suite/--shard 讀檔探 "--graph",探不到退全套;假執行器情境(含現場成立前置斷言)|
| F2 | 單reviewer-r2-sonnet | major | HIT:rx_graph 只認 -knowledge,加回 46 支裡 34 支是 x-knowledge/demo-knowledge 假環境(引句 #2 跨 patch 兩行錨不到,原文在 r2-snapshot 第 315–316 行,已機械重現) | 折:只認 lumos 找到的真圖譜目錄名;加回 12 支(合計 75 支、四片 55 秒);斷言加回 <30 支且不含評測 fixture |
| A1 | 架構對齊-r2-sonnet | major | HIT:同 F1(掛鉤沒探 --graph,舊版執行器 rc2 被判紅) | 折:同 F1 |
| A2 | 架構對齊-r2-sonnet | major | HIT:同檔 21479、26510 兩處已用 startswith/split 判「路徑在 docs/*-knowledge」,這批又寫一個 re.match | 折:抽 _vault_slug_of,三處改用;家的檢查、刪除守衛、推送測試範圍三組測試全綠 |

載體:架構對齊-r2-sonnet(引句全錨);單reviewer-r2-sonnet 只記等級與報告(它的引句 #2 跨 patch 兩行錨不到,不當載體)。
