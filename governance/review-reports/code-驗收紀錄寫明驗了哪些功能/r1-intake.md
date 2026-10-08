# code-驗收紀錄寫明驗了哪些功能 r1 收貨紀錄(2026-10-03,standard:通才-opus+架構對齊-sonnet)

機械:兩份 report-normalize 已正規;quote-check --spec r1-snapshot.patch 全錨定;refcheck 全 ok。

編號:g1–g5 = r1-通才-opus.md F1–F5;a1–a3 = r1-架構對齊-sonnet.md F1–F3。共 8 條,blocking 1(g1)。

| id | 怎麼試 | 結果 |
|---|---|---|
| g1 | 先紅 t_doctor_check3_extra_hint_shell_quoted:登記藏 $(touch PWNED) 照貼會執行;檔名有空白切成兩個參數 | HIT |
| g2 | 先紅 t_doctor_orphan_suggest_declared_all:5 項宣告、換 4 個雜湊種子順序不同,只印 3 項 | HIT |
| g3 | 先紅 bad_entry 補 null、~、只有註解:原因寫「不是單一連結」 | HIT |
| g4 | 讀碼:append 的 help 沒列 system_refs | 採信 |
| g5 | 補 bad_entry 沒縮排、一行多連結案例;lint 斷言改直接寫檔單獨驗 | HIT(測試缺口) |
| a3 | 讀碼:1/4 在推薦外又解析一次 | 採信 |
| a1 / a2 | 讀碼 | 採信、放行 |

處置:折 6(g1–g5、a3),放行 2(a1:狀態判斷只改四處是計劃定的範圍,其他讀 status 的照舊、lint 提交時擋非小寫;a2:封頂後補問題數照 1/4 孤兒段直接調 issues 的先例,封頂是設計審 r2 定的)。突變:改法拿掉 _drift_sh → shell_quoted 兩條紅;推薦拿掉排序 → declared_all 紅。
