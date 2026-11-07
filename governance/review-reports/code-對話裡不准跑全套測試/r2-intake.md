# r2 收貨紀錄(code-對話裡不准跑全套測試)

兩席新席(審查二、架構對齊二)全數交回後才寫進卷證;quote-check 全數錨定。審查二留在 `/tmp/lumos-seat-work/code-對話裡不准跑全套測試/` 的暫存,收貨後由編排者刪除。

編號:審查二 T1(major,守衛測試翻紅)、T2(minor,計數寫法沒有測試);架構對齊二 B1(minor,新函式位置與參數形狀)、B2(minor,開檔確認那段跟 `_regular_own_fd` 重複)。

歸因:T1 有證據的修復回歸(r1 把信任檢查搬進新函式,守衛測試按函式名盯的是舊函式);T2 修復宣稱沒測試守;B1、B2 搬位置時沿用了舊寫法。

## 先查世界

- PRIOR-ART:T1:同一支守衛測試已有先例(2026-09-30 `_lens_cache_write` 抽成 `_home_cache_write` 時,改盯共用那支、另驗原函式轉呼叫),照同一做法改。B2:`scripts/lumos` 已有 `_regular_own_fd`(擋捷徑、管線、別人的檔),新函式改用它。

## 出處清單

- 守衛測試 `t_private_dir_trust_shared_across_four_sites` 盯的寫入點清單:`_drift_m1_ledger_miss` 換成 `_home_cache_append_line`,另驗 `_drift_m1_ledger_miss` 與執行器 `_chat_guard_log` 都轉呼叫它。
- 開檔確認一般檔的寫法:`_regular_own_fd`(既有單一來源),`_home_cache_append_line` 改用它,不再手寫 fstat。

## 重現(修前紅、修後綠)

| id | 驗法 | 結果 |
|---|---|---|
| T1 | `-k t_private_dir` | HIT:修前 17 passed 1 failed;修後 20 passed |
| T2 | 真子程序案例:`~/.cache/lumos` 換成連結 | HIT:修後照樣擋下、連結指到的地方沒有被寫;計數改回直接開檔時這格紅(審查二實跑:會寫到連結指到的地方) |
| B1 | 讀碼 | HIT;新函式搬到 `_home_cache_write` 後面 |
| B2 | 讀碼 | HIT;改用 `_regular_own_fd` |

修後:`-k t_private_dir` 20、`-k chat_full_suite` 20、`-k chat_env_probe` 1、`-k red_hint` 6、`-k t_prepush_blocked_last` 5、`-k drift_m1` 全綠。
