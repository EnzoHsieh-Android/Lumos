# r1 收貨紀錄(code-對話裡不准跑全套測試)

兩席(審查、架構對齊)全數交回後才寫進卷證;報告從逐字稿取最後一則。架構對齊席初版結尾多一行單獨的 severity,被機器數成第 6 條,退回該席刪掉那一行,存的是重交版。兩份 quote-check 全數錨定。

編號:審查席 R1–R3(minor);架構對齊 A1、A2(minor)、A3(major,家目錄寫檔另起一套)、A4、A5(minor)。

## 先查世界

- PRIOR-ART:A3:本 repo 已有家目錄快取寫入的單一做法(`scripts/lumos` 的 `_mkdir_trusted_under_home`、`_trusted_private_dir`,`_drift_m1_ledger_miss` 用它附加一行);不另寫,把附加一行的部分抽成 `_home_cache_append_line`,原呼叫端與執行器共用。R1:記憶「變異會炸程序」——開子程序的測試要第二道保險,照做。

## 出處清單

- 寫 `~/.cache/lumos` 的位置:`_drift_m1_ledger_miss`(改用新函式)、執行器 `_chat_guard_log`(改用新函式);其餘既有寫入點(派工鏡頭、收工擋停)走同一組信任檢查,不動。
- 讀 `LUMOS_FANOUT_CHILD` 的位置:`_fanout_wanted`(讀常數)、新判斷(改讀常數)。

## 重現(修前紅、修後綠)

| id | 驗法 | 結果 |
|---|---|---|
| R1 | 判斷函式改成永遠不擋 | HIT:修前會開不帶參數的子程序;修後前置檢查先紅、不開子程序 |
| R2 | 拿掉 main 的 `pop("CLAUDECODE")` | HIT:修前測試照綠;修後子程序裡 `t_runner_chat_env_probe` 紅 |
| R3 | 截斷改成 head -3 | HIT:修前沒有案例;修後「超過 10 支」那格紅 |
| A1 | 讀碼 | HIT;改讀 `_FANOUT_CHILD_ENV` |
| A2 | 讀碼 | HIT;`pp_keep_log` 的註解移回緊貼它 |
| A3 | 讀碼 | HIT;改走 `_home_cache_append_line` |
| A4 | 讀碼:`lint-waive` 的理由判法寫在 `cmd_lint_waive` 函式本體裡,沒有可呼叫的函式 | HIT:抽出來要動 lint-waive 指令,這案不做 |
| A5 | 讀碼 | HIT:計劃已寫從頭組環境的理由(不繼承推送前閘與切片標記) |

修後:`-k chat_full_suite` 19、`-k chat_env_probe` 1、`-k red_hint` 6、`-k t_prepush_blocked_last` 5、`-k drift_m1` 252 全綠。
