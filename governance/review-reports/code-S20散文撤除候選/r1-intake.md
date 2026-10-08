# code-S20散文撤除候選 r1 收貨紀錄(2026-10-03,standard:通才-sonnet+架構對齊-sonnet)

機械:兩份 report-normalize 已正規;quote-check --spec r1-snapshot.patch 全錨定;refcheck 全 ok。

編號:g1–g4 = r1-通才-sonnet.md F1–F4;a1–a2 = r1-架構對齊-sonnet.md F1–F2。共 6 條,全 minor、blocking 0。

| id | 怎麼試 | 結果 |
|---|---|---|
| g1 | 先紅 t_doctor_s20_prose_retire_by_verdict_verb ⑤:裁定到冒號超過 20 字 → 誤列 | HIT |
| g2 | 先紅同支 ⑥:一行兩個裁定、第二個撤除 → 漏列 | HIT |
| g3 | 先紅同支 ⑦:裁定:改為、裁定:「改寫」→ 誤列 | HIT |
| g4 | 補同支 ⑧ 兩行說明、空行之後(程式本來就對,補釘) | 採信 |
| a1 / a2 | 讀碼:常數與輔助函式放在使用端之後;_ns_tr_prose_retire 跟 _ns_tr_retired 只差一字 | 採信 |

處置:6 條全折。每個裁定各切一段判、前綴放寬到 60 字、動作詞加改為與改成並去掉開頭引號;常數移到同組常數區、函式移到使用端之前並改名 _ns_tr_says_retire、_ns_tr_sub_says_retire。突變「只看第一個裁定」讓 ⑥ 翻紅;rtb 真實計劃再驗:清前 15、清後 0。
