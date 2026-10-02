# code-殺傷力配方當場試跑 r2 收貨紀錄(r1 修正差異)

機械:兩份 report-normalize 已正規;quote-check --spec r2-delta.patch 全數錨定;refcheck 全 ok。通才席說派工尾端沒附固定席筆記,自己跑了 impact --diff 補答。

編號:gr1 = r2-通才-sonnet.md F1;ar1、ar2 = r2-架構對齊-sonnet.md F1、F2。

| id | 怎麼試 | 結果 |
|---|---|---|
| ar1 | 讀碼:`_kill_recipe_judge`/`_kill_judge_file` 判 malformed 的條件跟 r1 另寫的 `_kill_recipe_shape_bad` 不同;寫成 t_guard_kill_only_ids ⑥c 三格(platform 是數字、缺 invariant、原文對不上時 new 是數字),修前先跑 | HIT:修前三格都被擋成格式壞 rc2;修後照跑、不當掉 |
| gr1 | 同 ⑥c「缺 invariant」那格 | HIT(同上) |
| ar2 | t_fix_check_recipe_rerun_note ③c:知識庫在 repo 外,直接呼叫 `_fix_recipe_rerun_notes` | HIT:修前回空;修後一行說明 |

處置:3 條全折(本輪有 major)。根因:①另寫第二套格式判斷(ar1、gr1)→ 拿掉,改用 P2 那支;②靜默跳過(ar2)。ar1 是 r1 修補造成的(regression-set)。
