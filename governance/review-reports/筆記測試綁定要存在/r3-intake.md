# 筆記測試綁定要存在 r3 收貨紀錄(2026-10-02,4 席,上限輪)

機械:四份 report-normalize 已正規;quote-check --spec r3-snapshot.md:正確性、整合、架構對齊全錨定,邊界 F8(minor 合併列)一句引句「「類別.方法」」不足 10 字錨不到——內容與正確性 F5 重疊,照正確性那條處理;refcheck 全 ok。

編號:p1–p9 = r3-正確性-opus.md F1–F9;q1–q8 = r3-邊界-sonnet.md F1–F8;s1–s7 = r3-整合-sonnet.md F1–F7;t1–t9 = r3-架構對齊-sonnet.md F1–F9。blocking 16(p 3、q 5、s 4、t 4)。

| id | 怎麼試 | 結果 |
|---|---|---|
| p1 / q1 / s3 / t1 | 三席實測:舊條目補 `[status:superseded]`、測試照留,`_ns_text_key` 前後相等;`_ns_is_old` 回 (True, False) | HIT |
| p2 | 正確性席實測:先在行內提到、後寫在行首的條款編號,「第一次出現」與 clause_bindings 判法不同(本 repo 17 份 38 條) | HIT |
| p3 | 正確性席實測:起點已有 4 個 `[test:待補]`、49 個空的,扣起點集合後永遠擋不到 | HIT |
| q2 | 邊界席實測:平台根是子模組、路徑含 `[ ]` 時第②道對真測試回 grep 不到 | HIT |
| q3 | 邊界席實測:本 repo `test` 欄 1247 個,76 個空值或沒收尾,都是散文講這個標記 | HIT |
| q4 / s4 / p7 / t5 | 讀碼:`_dispositions_check_test` 的 git 逾時拋例外、rc 128 回「無法驗證」 | HIT(讀碼) |
| q5 | 邊界席實測:起點非 UTF-8 筆記 `env_text` 回 None | HIT |
| s1 | 讀碼:名詞段與保險段對「測試寫了沒提交」說法相反 | HIT |
| s2 / t3 / p4 | 整合席實驗:預設 keep_other=False 丟掉單行 summary;`_note_shape_eval` 傳容器就交出 rows | HIT |
| t2 | 讀碼:note-shape 區段不呼叫 `_drift_*` | HIT |
| t4 | 讀碼:格子規則有自己的上線記號 | HIT(計劃改寫明不另設的理由,交下一輪判) |
| 其餘 minor | 讀碼核對 | 採信 |

處置:33 條全折。到上限仍有 major,攤人;Enzo 裁「折入後另開一輪審完整版」——本迴圈到此收,折入後的計劃另開編號 `筆記測試綁定要存在-r4` 派四席審完整版。regression-set:p1、q1、s3、t1(r2 改用 `_ns_text_key` 造成)、p3(r2 改成扣起點集合造成)、t2(r2 改用 `_drift_tree_env` 造成)、t3、s2、p4(r2 寫「自己向 `_notelines_new` 要 rows」造成)。
