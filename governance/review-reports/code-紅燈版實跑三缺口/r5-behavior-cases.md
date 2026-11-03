# r5 待驗案例(code-紅燈版實跑三缺口,r4 修補 G1–G4 與 H3)

案例只是待驗範圍,不是作者判定已修好或因果成立的證據。修前 374e77519、修後 04de0941c;測試都在 scripts/test_lumos.py。

| 組 | 角色 | 待驗行為 | 出處 | 案例 | 未覆蓋 |
|---|---|---|---|---|---|
| G1 | repair | 改回單平台的擋下訊息講實作還沒綠時重跑、實作已綠時換回空殼補跑或改走設計審 | 計劃做法 2 | t_spec_gate_record_keeps_platform「擋下訊息講…補法」 | 照訊息實際走一遍補跑流程沒有自動案例 |
| G1 | preserve | 改回單平台照擋、不跑、不記逃逸;已完成降成提醒 | 計劃 S3 | t_spec_gate_record_keeps_platform 單平台各案 | — |
| G2 | repair | 只壓字串外空白共用 _tg_ident 的掃描迴圈 | 架構對齊席 r4 | -k tq_guard(行為不變) | 無行為差可測(重構) |
| G2 | preserve | _tg_ident 預設行為(字串外標點兩側空白拿掉)不變 | 既有 | -k tq_guard 408 條 | — |
| G3 | repair | 判字串常值的樣式認得三引號跨行字串:多行字串裡的 assertEquals 字樣不算強斷言 | 計劃做法 1 | t_tq_guard_string_comma_args「多行字串裡的 assertEquals」 | 判訊息參數、判容差、判恆真條件三處用三引號字串沒有獨立案例 |
| G3 | preserve | 單行字串、字元常值的判法不變 | 既有 | -k tq_guard | — |
| G4 | repair | 中綴斷言字串裡多一格空白要列;改回單平台已完成降成提醒 | 單審席 r4 F4、F5 | t_tq_guard_string_comma_args 中綴案、t_spec_gate_record_keeps_platform 已完成案 | — |
| H3 | repair | trimIndent 字串重新縮排多報寫成已知限制、附 REVISIT | 計劃做法 1 | 讀計劃 | — |
