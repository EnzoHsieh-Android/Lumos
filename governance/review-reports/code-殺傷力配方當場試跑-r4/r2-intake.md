# code-殺傷力配方當場試跑-r4 r2 收貨紀錄(r1 修正差異)

機械:兩份 report-normalize 已正規;quote-check --spec r2-delta.patch 兩份全數錨定;refcheck 通才 1 條 missing 是報告裡的縮寫路徑(不是發現依據)。

編號:p1 = r2-通才-opus.md F1;q1、q2 = r2-架構對齊-sonnet.md F1、F2。

| id | 怎麼試 | 結果 |
|---|---|---|
| q1 | t_guard_kill_only_ids ⑥h「invariant 帶雙向控制字元」--json,修前先跑 | HIT:修前 U+202E 原樣印出;修後經 `_kill_esc` 印成 ‮、中文照舊 |
| p1 | ⑥h「invariant / note 帶替身字元」--json,修前先跑 | HIT:修前寫 kill-log 時 UnicodeEncodeError rc1;修後恰一行合法 JSON |
| q2 | 讀碼:`_kill_old_bad`/`_kill_new_bad` 回說明字串、鄰居 `_kill_path_issue` 叫 issue;三支防怪型別小函式散在 `cmd_guard_kill` 之後、covers 是行內三元 | HIT(讀碼) |

處置:3 條全折(本輪有 major)。根因:①另寫第二份跳脫(q1)與寫 kill-log 漏跳脫(p1)同一件事 → 兩處都經既有 `_kill_esc`;②命名、位置、形狀不一(q2)→ 改名 `_issue`、搬到 `_kill_new_issue` 旁、covers 抽小函式。翻紅:兩處 `_kill_esc` 各拿掉,⑥h 對應格子紅。
