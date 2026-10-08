# code-殺傷力配方當場試跑-r4 r1 收貨紀錄(前一迴圈第 3 輪修正差異)

機械:兩份 report-normalize 已正規;quote-check --spec r1-snapshot.patch 兩份全數錨定;refcheck 全 ok。

編號:o1–o4 = r1-通才-opus.md F1–F4;s1、s2 = r1-架構對齊-sonnet.md F1、F2。

| id | 怎麼試 | 結果 |
|---|---|---|
| o1 / s1 | t_guard_kill_only_ids ⑥d 加兩形狀(`./empty.py` 空檔沒寫 old、`./prod.py` new 帶替身字元)×(帶/不帶 --id),修前先跑 | HIT:修前四格 rc1(KeyError、UnicodeEncodeError);修後 rc2、--json 恰一行、那條 error |
| o2 | 對照通才席網格結果改寫 Issue 清單 | HIT(文件) |
| o3 | ⑥f covers 是數字、detail 是數字,修前先跑 | HIT:修前 rc1 當掉;修後照跑一筆 |
| o4 | ⑥f invariant 是清單帶合約片段,修前先跑 | HIT:修前(r3 版)判沒有配方可跑 rc2;修後照跑,跟 r3 之前一樣 |
| s2 | ⑥g 把判法換成會丟例外的,呼叫 `_guard_kill_pick`,修前先跑 | HIT:修前不印;修後印一行判斷時出錯、照跑 |

處置:6 條全折(本輪有 major)。根因:①判法與原地擋各寫一份(o1、s1)→ 抽 `_kill_old_bad`/`_kill_new_bad` 共用;②配方多餘欄位型別怪會崩(o3)與 `--json` 遇替身字元崩(⑥d 修後浮出,同屬 guard kill 碰到怪欄位)→ 讀前驗型別、輸出跳脫;③r3 片段過濾改變了既有行為(o4)→ 改回 in 比對、只擋丟例外;④兜底靜默(s2);⑤文件(o2)。翻紅:六處逐一改回,對應格子都紅。
