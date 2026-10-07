# code-撤除候選也看manual條款-收尾 r1 收貨

前一個編號跑滿三輪後 Enzo 裁定改法,本編號審那次改動。席報告 2 份(正確性 2 條 minor、架構對齊 1 條 minor),都是新席。quote-check 兩份全錨。

彙整 id:正確性 c1–c2、架構對齊 a1。載體:正確性席。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c1 | 測試格⑩:同一行 `[manual:開頁面目測一次]` 加 `[test：test_alive]`(全形冒號)或 `[ test : test_alive ]`、下一層寫撤除 | 修前列兩行(一行 [test:]、一行 [manual:]) | HIT |
| c2 | 測試格⑪:開頭欄位摘要續行 `  - [S1] a [manual:開頁面目測一次]`、下一行更深寫撤除 | 修前列第 6 行 | HIT |
| a1 | 讀碼:doctor 為呼叫 `_ns_clause_rows` 先 `_note_from_text` 一次,`_ns_test_ref_lines` 內又一次 | 兩次;改動前 `_ns_test_ref_lines` 與 `_ns_tr_manual_clauses` 也各讀一次 | HIT |

## 處置

- c1、c2 折:`_ns_tr_manual_clauses` 只看正文(`_notelines_regions`,同 [test:] 那條路),同行 slot_parse 認得測試名就讓 [test:] 那條路列;測試格⑩⑪ 修前紅、修後綠。
- a1 放行(輪內最高 minor):開頭欄位解析很便宜,改動前同一篇也讀兩次,沒有變多;不為省一次解析把 `_ns_test_ref_lines` 的參數再改一次形狀。
- 計劃天花板 2 補上被遮(shadowed)狀態(正確性席「修復結果」段提到範圍窄於實際行為)。
