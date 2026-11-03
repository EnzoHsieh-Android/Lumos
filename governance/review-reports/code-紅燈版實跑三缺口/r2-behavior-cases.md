# r2 待驗案例(code-紅燈版實跑三缺口,修補 r1 的 G1–G7)

案例只是待驗範圍,不是作者判定已修好或因果成立的證據。修前版本 bcd9a1703、修後 06e101684;測試都在 scripts/test_lumos.py。

| 組 | 角色 | 待驗行為 | 出處 | 案例(測試/斷言) | 未覆蓋 |
|---|---|---|---|---|---|
| G1 | repair | 治理帳忽略判法只有一支、放帳檔區,比對工具、規格閘、doctor 三處都叫它 | 計劃做法 4 | t_tq_guard_redbase_ledger_ignored、t_spec_gate_redbase_ledger_ignored、t_doctor_gov_ledger_ignored | 程式位置本身沒有行為測試 |
| G1 | preserve | 否定規則、已追蹤、git 判不了時照舊措辭 | 計劃 S7 | t_tq_guard_redbase_ledger_ignored 的三個「照舊措辭」斷言 | — |
| G2 | repair | 沒接裝置(DeviceException)判弱證據、不記逃逸 | 計劃 S6 | t_spec_gate_device_missing_not_red | java-junit 只靠同一張表,沒有獨立案例 |
| G2 | preserve | Kotlin 真的紅照樣是紅、照存紅燈版、照記逃逸 | 計劃 S6、規格閘紅燈版 S1 | t_spec_gate_device_missing_not_red 最後一案、t_spec_gate_redbase_written_on_red | — |
| G3 | repair | doctor 段 fail-open 接所有例外;平台前綴沒定義接專屬型別;規格閘那行走錯誤輸出 | 架構對齊席 A2–A4 | t_spec_gate_push_unknown_platform、t_spec_gate_redbase_ledger_ignored | doctor 段丟例外的路徑沒有測試 |
| G3 | preserve | 平台不在設定裡:還在做擋、已完成提醒 | 計劃 S5 | t_spec_gate_push_unknown_platform | — |
| G4 | repair | 剝過文字那條路只給 angle=False;沒有字串時兩條切法逐字相同 | 架構對齊席 A6 | t_tq_guard_string_split_fallback 的隨機 300 段與 angle=True 斷言 | 隨機字串只含 ab、空白、逗號、三種括號 |
| G4 | preserve | Room 守衛切 Migration 參數不變 | Systems/room-guard | -k room(168 條)、-k t_rg_(33 條) | — |
| G5 | repair | 搬進巢狀類別、本體有多行字串不列刪測試 | 單審席 R1 | t_tq_guard_string_comma_args 搬家那案 | CRLF 改行尾沒有案例 |
| G5 | preserve | 字串裡空白改了照列改預期值;重新縮排不列 | 計劃 S1;Android測試防竄改檢查 S1 | t_tq_guard_string_comma_args 串接那案、t_tq_guard_skip_added 整檔重新縮排 | — |
| G6 | repair | 多平台寫的 平台:名字,改回單平台照去掉前綴的名字跑、不記逃逸 | 單審席 R2 | t_spec_gate_record_keeps_platform 單平台那案 | 單平台而名字本身含冒號、去掉前綴後碰巧撞到另一支測試 |
| G6 | preserve | 多平台照前綴跑;舊留痕裸名補平台 | 計劃 S3、S4 | t_spec_gate_record_keeps_platform 前半、t_spec_gate_push_bare_name_platform | — |
| G7 | repair | 還沒提交那句自帶改法與自查指令 | 單審席 R3 | t_tq_guard_redbase_ledger_ignored「自帶改法」斷言 | — |
| G7 | preserve | 治理帳沒被忽略時還沒提交那句照舊 | 規格閘紅燈測試快照 S10 | t_tq_guard_redbase_reads_tip「只提醒紅燈版還沒提交」 | — |
