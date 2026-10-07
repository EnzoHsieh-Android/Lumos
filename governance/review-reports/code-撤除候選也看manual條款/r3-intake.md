# code-撤除候選也看manual條款 r3 收貨

席報告 2 份(正確性 1 條 minor、架構對齊 1 條 major + 1 條 minor),都是沒看過前兩輪的新席。quote-check 兩份全錨。

彙整 id:正確性 c1、架構對齊 a1–a2。載體:架構對齊席。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| a1 | 讀碼:`_ns_tr_manual_clauses` 遇 duplicate/shadowed 把 `lines[no - 1]` 單獨丟回 `clause_bindings`;既有碼對 state 一律原樣採用 | 單行重判丟掉前後文(前面是否定義過) | HIT |
| a2 | 讀碼:`_doctor_test_ref_lines` 每篇經 `_ns_test_ref_lines` 解析一次、`_ns_tr_manual_clauses` 再解析一次 | 兩次 | HIT |
| c1 | 席位探針 B/C/M(重複定義的第二條掛 [manual:] 且下一層寫撤除)修前修後都不列;對照 P([test:] 同形)也不列 | 原有漏查 | HIT |

## 處置

跑滿三輪(standard 上限),最後一輪有 major,攤 Enzo 裁(2026-10-07):拿掉單行重判、重複定義在 [manual:] 這條路一律不列。三條全折(輪內有 major,依規不放行):
- a1:拿掉單行重判,state 一律照 clause_bindings;測試格⑨改成「重複定義、第一條掛 [manual:] → 不列;掛 [test:] → 照列」,並註明兩條路在這個形狀上刻意不同。
- a2:抽 `_ns_clause_rows`,doctor 每篇算一次,`_ns_test_ref_lines(rel, text, rows)` 與 `_ns_tr_manual_clauses(text, rows)` 共用;檢查壞綁定那一段原本自己解析的那次不動(既有)。
- c1:[manual:] 這條路對重複定義一律不列(第一條、第二條都不列),口徑寫進計劃天花板 2;[test:] 那條路第二條漏列是原有行為、不在本案範圍。

翻紅:共用結果改傳空 → S20 14 斷言紅;加回單行重判 → ⑨紅。修補交新編號 code-撤除候選也看manual條款-收尾 派新席審。
