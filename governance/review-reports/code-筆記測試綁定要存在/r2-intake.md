# code-筆記測試綁定要存在 r2 收貨紀錄(2026-10-03,standard:通才-sonnet+架構對齊-sonnet,只看 r1 修正差異)

機械:兩份 report-normalize 已正規;quote-check --spec r2-snapshot.patch 全錨定;refcheck 全 ok。

編號:g1–g2 = r2-通才-sonnet.md F1–F2;a1–a2 = r2-架構對齊-sonnet.md F1–F2。共 4 條,全 minor、blocking 0。

| id | 怎麼試 | 結果 |
|---|---|---|
| g1 | 先紅 t_note_shape_test_refs_line_attribution ④⑤:t_a 在舊行、t_ab 在新行 → 修前 new 為真;前綴全形冒號同 | HIT |
| g2 | 讀計劃〈做法〉8 與〈名詞〉合約行段、_ns_test_refs_collected 說明 | 採信 |
| a1 | 先紅 t_note_shape_test_refs_git_fail_and_guard ①:ls-tree 回 None 時 st["out"] 沒設 | HIT |
| a2 | 先紅 t_note_shape_test_refs_check_key ④:併帳本欄位要回新字典 | HIT |

處置:4 條全折。修完整字比對的突變(改回子字串)讓 ④ 翻紅;「跑這組」那支複雜度升到 11,抽出 _ns_tr_collect。
