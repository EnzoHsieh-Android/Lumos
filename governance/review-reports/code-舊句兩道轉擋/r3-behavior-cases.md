# r3 配對案例(上一輪修補前由編排者列)

修補區間:修前 88322e46 → 修後 59f8f92b。下表是修補前先列的待驗範圍,不是「已修好」的結論;審查席獨立核對、可補案例。

| 組 | repair(原問題要好) | preserve(既有正常行為不能壞) |
|---|---|---|
| 帳長度 | 30 條規則類條目、條目長度 ×1 與測試原本 ×N 各一案,寫出的整行 ≤4096 位元組(含 commit 與 head_sha) | 舊句檢查帳、筆記形狀擋放寬帳照原樣截(`-k gate_event`、`-k m1`) |
| 索引長度 | `t_command_index_complete` 轉綠 | 索引仍提到 `--kind reread`(`t_command_index_complete` 其他 13 條) |
| 紀錄讀取守門 | 未提交紀錄是深層巢狀 JSON、符號連結、太大、形狀壞,prepare 不崩、不算 wip;`drift ack --kind reread` 碰到同樣的檔照原本處理 | 正常未提交且 provenance_ok 為真的紀錄照算 wip(`t_reread_block_layer1` ⑥⑦) |
| 訊息 | 上限加 1 位元組時訊息不再自相矛盾;多列超限時提示講到列數 | 剛好等於上限照寫(`t_reread_record_refuses_unreadable_size` 對照組) |
| 測試 | 清變數測試同時觀察第二個同族變數;`.git/hooks` 預設路徑有行為測試 | 原本「拿掉清變數那行就紅」照紅 |
| 帳欄位 | warn 下判不了的 skipped 帳也記 state | block 下判不了的 blocked 帳照記 state |
| 文件 | 筆記、計劃、README、CHANGELOG 對超長行判準、帳來源、「還沒提交」口徑、提交提示、名稱範圍的描述與真碼一致 | 未改動的段落照舊 |

修補者回報的修後結果(子集測試全綠、17 種改壞全翻紅)是作者主張,不是證據;請自己跑。
