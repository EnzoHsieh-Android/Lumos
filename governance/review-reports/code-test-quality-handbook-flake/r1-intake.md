# r1 intake

preflight-4: ran

單席（架構對齊，Claude sonnet，light 分級）。收貨時三句引句把全形標點抄成半形錨不到，退回該席只修引句後重收，全數錨定。四條皆由編排者核對程式成立。

| id | source | severity | reproduce | disposal | evidence |
|---|---|---|---|---|---|
| FLK-1 | 架構對齊 | minor | HIT | folded | 筆記的防回歸欄改指具體測試名，與同篇其他 PITFALL 一致 |
| FLK-2 | 架構對齊 | minor | HIT | folded | 刪掉與筆記重複的行內註解，理由只留在 PITFALL，與鄰近逾時控制寫法一致 |
| FLK-3 | 架構對齊 | minor | HIT | folded | 同形的手冊「逾時保留部分輸出」控制預算也放寬到 5 秒；手冊 20 項綠 |
| FLK-4 | 架構對齊 | minor | HIT | folded | 同根因的收證「串流關閉後逾時保留部分輸出」控制放寬到 5 秒；該測試綠 |

regression_set：none。同族偶發紅一次掃完，避免只修被點名的那一支。
