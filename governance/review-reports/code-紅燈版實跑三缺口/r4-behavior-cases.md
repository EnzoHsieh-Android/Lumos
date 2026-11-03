# r4 待驗案例(code-紅燈版實跑三缺口,人裁換形狀後的修補:r3 的 G1–G3 與 D3)

案例只是待驗範圍,不是作者判定已修好或因果成立的證據。修前 e0603d082、修後 374e77519;測試都在 scripts/test_lumos.py。

| 組 | 角色 | 待驗行為 | 出處 | 案例 | 未覆蓋 |
|---|---|---|---|---|---|
| G1 | repair | 單平台時帶冒號、在測試索引找不到的留痕名字照擋並講明設定改了,不跑、不記逃逸;被刪的含冒號測試不被同名後綴的另一支頂替 | 計劃做法 2「改回單平台」(r3 人裁) | t_spec_gate_record_keeps_platform 單平台三案(jvm:fee_jvm、gone:fee_jvm 單條款、兩條款) | 已完成計劃的降成提醒那條路 |
| G1 | preserve | 單平台本身含冒號、測試還在的名字照跑;多平台照前綴跑;舊留痕裸名照條款補平台 | 計劃 S3、S4 | t_spec_gate_record_keeps_platform 前置(gone:fee_jvm 判紅留痕)、前半、t_spec_gate_push_bare_name_platform | — |
| G2 | repair | 抽斷言文字只壓字串外空白,字串裡多一格空白要列改預期值 | 代碼審 r3 D2 | t_tq_guard_string_comma_args「字串裡多一格空白」 | tab 換空白沒有獨立案例 |
| G2 | preserve | 字串外排版不同(重新縮排、換行)不列;其他斷言規則照舊 | Android測試防竄改檢查 | -k tq_guard 405 條 | — |
| G3 | repair | 推送前判「沒過的全是環境沒跑起來」看原因是不是表裡任一格的 why | 架構對齊席 r3 E2 | t_spec_gate_device_missing_not_red | 表裡只有一種 why,多種 why 沒有案例 |
| D3 | repair | 計劃 S3 條款與做法 2 一致 | 文件 | 讀計劃 S3 | — |
