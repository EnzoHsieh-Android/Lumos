# code-殺傷力配方當場試跑 r1 收貨紀錄

機械:兩份 report-normalize 已正規;quote-check --spec r1-code.patch 全數錨定;refcheck 通才 1 條 missing 是報告裡縮寫的路徑 `docs/.../Systems/guard-kill.md`(不是發現依據);seat-check vacuous。

編號:g1 = r1-通才-opus.md F1;a1–a3 = r1-架構對齊-sonnet.md F1–F3。

| id | 怎麼試 | 結果 |
|---|---|---|
| g1 | 照席位 e2.py 的形狀把筆記放 `{"file": 5, …}` 與 `old: null` 兩種配方,`guard kill --id <那條> --json`(寫成 t_guard_kill_only_ids ⑥b 兩格,修前先跑) | HIT:修前兩格都 rc=1、Traceback;修後 rc2、印 kill-rm、標準輸出空 |
| a1 | 工作目錄把筆記改掉不提交、跑 fix-check(t_fix_check_recipe_rerun_note ③b,修前先跑) | HIT:修前照工作目錄那份(沒提醒);修後照提交那份 |
| a2 | 讀碼:`_kill_add_warn` 用「⚠ 提醒:」,`_kill_add_try` 三句沒有(t_guard_kill_add_try ②③ 改斷言前綴,修前紅) | HIT |
| a3 | 帳上同一條配方同 ts 兩筆(先 survived 後 killed),doctor(t_doctor_p2_lists_survived ⑥b,修前紅) | HIT:修前取後者不列;修後取先出現的、跟背書同 |

處置:4 條全折(本輪有 major,一律折)。根因分組:①格式壞判定範圍(g1)②基準不一(a1)③跟鄰居寫法不一(a2、a3)。效能:6 萬筆帳 301 條配方,survived 清單 1.3 秒、峰值 170 MB。
