# code-筆記測試綁定要存在 r1 收貨紀錄(2026-10-03,standard:通才-opus+架構對齊-sonnet)

機械:兩份 report-normalize 已正規;quote-check --spec r1-snapshot.patch 全錨定;refcheck 全 ok;seat-check 讀不到派工單材料欄(同上次代碼審派工單形狀),豁免。

編號:g1–g7 = r1-通才-opus.md F1–F7;a1–a4 = r1-架構對齊-sonnet.md F1–F4。共 11 條,全 minor、blocking 0。

| id | 怎麼試 | 結果 |
|---|---|---|
| g1 | 先紅測試 t_note_shape_test_refs_line_attribution ①②:續行新加的名稱帳記 new=False、只改第一行記 True | HIT |
| g2 | 席位突變實驗:拿掉 summary 鍵行判法,59 支照綠;補 ③ 後同一突變翻紅 | HIT |
| g3 | 先紅 t_note_shape_test_refs_scope_consistency ①:正文空 [test-gone:] 被擋 | HIT |
| g4 | 先紅同支 ②③④:合約行佔位字、空方括號、test-gone 說假話與條款行 test-gone 說假話都放行 | HIT |
| g5 | 先紅 t_note_shape_test_refs_undecidable_paths ①:替身讓 ls-tree 回 None → 判成指不到 | HIT |
| g6 | 先紅同支 ②:工作目錄拿掉 test_alive、沒違規時沒有任何提醒 | HIT |
| g7 | 先紅 t_doctor_note_test_refs_output ①:檔名帶 ESC 的筆記,S20 原樣印出 | HIT |
| a1 | 先紅 t_note_shape_test_refs_ledger_check ①②③:帳上沒有 check | HIT |
| a2 | 先紅 t_doctor_note_test_refs_output ②:記憶體 Env 讀不到全文 | HIT |
| a3 / a4 | 讀碼核對 | 採信 |

處置:折 10 條(g1–g7、a1、a2、a4;a4 寫進 _note_shape_eval 說明),放行 a3(名稱切分兩份:設計審已定案摘要條目用 slot_parse,判平台時包回 [test:名] 交既有 resolve_test_refs,沒有重寫平台判定)。修完四個突變實驗(單行 summary 鍵行、保險只在有違規時跑、合約行與條款行整條提早返回、正文空 test-gone 不分區塊)各自讓對應測試翻紅。修前量效能:4000 行 6000 個名稱,抽取 0.1 秒、判定約 18 秒、記憶體高峰 39MB(推送路徑有 20 秒上限)。
