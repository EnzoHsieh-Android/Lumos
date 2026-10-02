# 筆記測試綁定要存在-r4 r1 收貨紀錄(2026-10-02,4 席;前一迴圈三輪到頂後另開)

機械:四份 report-normalize 已正規;quote-check --spec r1-snapshot.md:正確性、整合全錨定;邊界 F6(minor)一句引句跟快照差幾個字錨不到、架構對齊 F3 一句引句不足 10 字——兩條內容都有他席或讀碼佐證,照常處理;refcheck 全 ok。

編號:w1–w8 = r1-正確性-opus.md F1–F8;x1–x8 = r1-邊界-sonnet.md F1–F8;y1–y11 = r1-整合-sonnet.md F1–F11;z1–z8 = r1-架構對齊-sonnet.md F1–F8。blocking 21(w 6、x 5、y 6、z 4)。

| id | 怎麼試 | 結果 |
|---|---|---|
| w1 / y3 / x3 / z1 / w2 | 席位實驗:借 `_ns_slots_old_lines` 不帶 texts2 時新行比對到自己(推送時 1c 與佔位字全放行);`_ns_slot_key` 對條款行回 None | HIT |
| w3 / x1 / y2 / z5 | 三席實測:逐篇 `_nodehome_reader` 讀整庫一版 13.8–17 秒;`_nodehome_cat_blobs` 0.16–0.24 秒 | HIT |
| w4 / x2 / y1 / z2 | 整合席 CI 形狀 clone 重現:`_mainline_ref` 預設在 CI 等於終點 | HIT |
| w5 / x5 / y5 | 實測:`_dispositions_check_test` 對 rc 128 回 (False, …)、子模組 rc 1 | HIT |
| w6 / y6 | 實測:hay_for 掃整個 repo,`main`、`_git` 被判「設定認不到」放行 | HIT |
| x4 | 讀碼:1c 只看「這次才標作廢」,已作廢條目新掛活測試放行 | HIT |
| z3 / z4 / 其餘 minor | 讀碼核對 | 採信 |

處置:35 條全折。問題集中在「只擋新加的」要分新舊的接點(四輪都在這裡找到新錯),攤人;Enzo 裁換方向「碰到的筆記整篇要乾淨」——不分新舊、不讀起點與主線、不用舊行判定,上面 w1–w4、x1–x4、y1–y4、z1、z2、z5 這些接點整類消失;判存在第①道改 `_classify_test_refs`、第②道抽 `_test_in_tree` 回三態(w5、x5、y5);拿掉 def 判法(w6、y6);程式預設 warn、本 repo 開 block(z4);`_note_shape_eval` 加 `rows_out`(w7、y7);其餘 minor 照補。條款重編 S1–S25。
