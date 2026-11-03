# r3 待驗案例(code-紅燈版實跑三缺口,修補 r2 的 G1–G4 與 C4)

案例只是待驗範圍,不是作者判定已修好或因果成立的證據。修前 06e101684、修後 e0603d082;測試都在 scripts/test_lumos.py。

| 組 | 角色 | 待驗行為 | 出處 | 案例 | 未覆蓋 |
|---|---|---|---|---|---|
| G1 | repair | 改回單平台時不自己切冒號,只拿現在條款的名字比;本身含冒號、後來不見的測試名不被同名後綴的另一支頂替 | 計劃做法 2「改回單平台」 | t_spec_gate_record_keeps_platform 的單平台兩案(jvm:fee_jvm 照跑綠;gone:fee_jvm 不見了照擋) | 條款名字後綴同時吻合兩個(推得不出寫得出留痕的情境,見 r2-fix-mutation.md P3) |
| G1 | preserve | 多平台照前綴跑;舊留痕裸名照條款補平台;同名綁兩個平台照預設;過期且已完成不補 | 計劃 S3、S4 | t_spec_gate_record_keeps_platform 前半、t_spec_gate_push_bare_name_platform | — |
| G2 | repair | Java 專案(java-junit)沒接裝置判弱證據、寫環境沒跑起來 | 計劃 S6 | t_spec_gate_device_missing_not_red 的 Java 案 | Java 專案推送前那段(只驗了規格閘) |
| G2 | preserve | Kotlin 沒接裝置照判、真的紅照記逃逸 | 計劃 S6 | t_spec_gate_device_missing_not_red 其餘各案 | — |
| G3 | repair | 只差空白版面(拿掉全部空白後相同)只比預期值,沒斷言而有多行字串的既有測試整檔重新縮排不列 | 計劃做法 1 本體簽名 | t_tq_guard_string_comma_args 重新縮排那案 | CRLF 改行尾沒有案例 |
| G3 | preserve | 字串裡空白改了照列改預期值;搬進巢狀類別不列刪測試;本體真的改了照所有規則判 | 計劃 S1;Android測試防竄改檢查 | t_tq_guard_string_comma_args 串接、搬家兩案;-k tq_guard 403 條 | — |
| G4 | repair | 環境樣式表值是具名欄位,存取函式去色碼後比 | 架構對齊席 r2 | t_spec_gate_device_missing_not_red(經存取函式) | 輸出帶色碼的 DeviceException 沒有案例 |
| C4 | repair | 計劃回退節講 `_ENV_MISSING_EVIDENCE` | 文件 | grep 計劃回退節 | — |
