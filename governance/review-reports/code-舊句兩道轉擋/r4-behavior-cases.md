# r4 配對案例(上一輪修補前由編排者列)

修補區間:修前 a4d42fea → 修後 40f871bf。下表是修補前先列的待驗範圍,不是「已修好」的結論;審查席獨立核對、可補案例。


| 組 | repair(原問題要好) | preserve(既有正常行為不能壞) |
|---|---|---|
| 讀端路徑守門 | 上層資料夾(`governance`)是符號連結時,工作目錄紀錄不被讀進來,prepare 與 `drift ack --kind reread` 兩邊都一樣;測試要有「上層是連結」一組 | 資料夾本身是連結、單檔是連結、FIFO、太大、形狀壞照原本略過;正常未提交紀錄照算只差提交(`t_reread_wt_records_guarded`、`t_reread_block_layer1`) |
| 巢狀太深 | 設定檔與判定者報告兩個呼叫端各有一條深層巢狀測試;同一份 `.lumos/config.json` 的兄弟閘讀設定不再丟 RecursionError | 正常設定照讀;讀不成 JSON 的既有訊息與退回預設不變(`-k note_audit_config`、`-k drift_config`、`-k note_shape`) |
| 指令引號 | 給人貼的提交指令走既有 `_sh_quote` | 一般檔名印出來不變 |
| 測試寫法 | 行程內造 RecursionError 改用專案既有的替換寫法,不換 `sys.modules` | 原本「解析不接 RecursionError 就紅」照紅 |
| 帳欄位測試 | skipped、none、covered、undecidable 四種帳的 head_sha 各有斷言;來源欄本機記 hook 有斷言;清略過變數有一條觀察「整族」的斷言(例如子行程裡除了 `LUMOS_SKIP_CLAUDE_PLUGIN` 沒有任何 `LUMOS_SKIP_*`) | 原有 ① 到 ⑦ 斷言照綠 |
| 文件 | 三處文件與真碼一致 | 未改動的段落照舊 |


修補者回報的修後結果(子集全綠、15 種改壞全翻紅)是作者主張,不是證據;請自己跑。
