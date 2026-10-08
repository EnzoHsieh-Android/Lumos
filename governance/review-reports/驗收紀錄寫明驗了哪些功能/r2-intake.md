# 驗收紀錄寫明驗了哪些功能 r2 收貨紀錄(2026-10-03,4 席)

機械:四份 report-normalize(架構對齊席兩行「severity: minor ⚠」用 --write 純格式拆成兩行,不改等級);quote-check --spec r2-snapshot.md:正確性、整合、架構對齊全錨定,邊界席 #4 一句(「用 lumos append <新紀錄> system_refs "無 <理由>"」)錨不到;refcheck 四份全 ok。

編號:c1–c7 = r2-正確性-opus.md F1–F7;b1–b7 = r2-邊界-sonnet.md F1–F7;i1–i8 = r2-整合-sonnet.md F1–F8;a1–a6 = r2-架構對齊-sonnet.md F1–F6。共 28 條,blocking 5(c1、b1、b2、i1、a1)。

| id | 怎麼試 | 結果 |
|---|---|---|
| a1 / b3 / b7 / c3 / i8 | 讀碼:build_typed_index 已定義單項規則(整值單一連結、路徑不退回檔名、同名多候選報不明確);本案自訂規則跟它不同 | HIT(四席指向同一處) |
| b1 | 席位實驗:system_refs:、[]、沒縮排的 - 項,parse_frontmatter 都解成 [] | HIT |
| c1 | 席位實驗:只寫 `無` 的紀錄沒有筆記連進來,doctor --ci 回 1(1/4 孤兒);1/4 建議掛上、3/4 又叫拔 | HIT |
| b2 / c2 | 讀碼與推演:`無` 的分隔、字數、`無 [[Systems/A]]`、`無障礙…` 純文字 | HIT |
| b4 | 引句錨不到;內容(append 不擋 無 混用)隨 `無` 拿掉一起消失 | 改法消掉 |
| i1 / c5 | 讀碼:孤兒清單只排 superseded,stale/fail 的孤兒拿到 None 會崩 | HIT |
| a3 / c6 / i7 | 讀碼:E1 與孤兒清單另有一份狀態判斷、沒轉小寫 | HIT |
| c4 | 席位實驗:macOS 上 --systems systems/A 照樣建檔 | HIT |
| c7 | 席位實驗:裸名登記照抄 remove 回 2;紀錄寫壞時正確登記被唸多掛 | HIT |
| i3 | 讀碼:sync 只剩寫壞項時在 if not planned 先印無漏寫 | HIT |
| i6 | 編排者查 slim/FROZEN.md:2026-08-20 起凍結 | HIT |
| b5 / b6 / i2 / i4 / i5 / a2 / a4 / a5 / a6 | 讀碼核對 | 採信 |
| 全庫 status | 編排者 grep:全部小寫,沒有 Fail/Stale 寫法 | 已驗 |

處置:28 條全折。同一類(怎麼判一項)第二輪,換形狀:單項判法直接借 build_typed_index 的既有規則(抽成共用),拿掉 `無 <理由>`。其餘照補,詳見計劃審計修正紀錄 r2。
