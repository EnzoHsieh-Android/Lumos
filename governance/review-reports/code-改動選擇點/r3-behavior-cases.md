# code-改動選擇點 r3 待驗行為(修補鏡頭配對案例)

只列待驗範圍,不是「已修好」的證據。修前 f1be3141cc5d9c46df7794dc84c007b49d05ecbb(第二輪派工單 base_commit,與 4dd1ed800c 之間只差第二輪卷證)、修後 8e521300bb3ca14d838f58ff5da1543ce298a46c。來源:計劃 docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md 的條款與〈用詞〉。

| 組 | 角色 | 待驗行為(輸入 → 預期) | 出處 | 相關測試(修後) |
|---|---|---|---|---|
| H1 | repair | 計劃筆記在 docs/、測試在 feature/src/test/(排在 docs 後);只改筆記 → 守的測試雜湊不變;只補強測試內容 → 雜湊變、那行重跑 | S11、〈範圍〉2 | t_choice_kill_test_files_in_test_paths |
| H1 | repair | 測試名是正式碼裡另一個字的子字串 → 正式碼改動不影響雜湊 | S11 | t_choice_kill_test_files_in_test_paths |
| H1 | repair | 兩平台同名測試各改一支 → 各自的雜湊各自變 | S8、S11 | t_choice_kill_test_files_in_test_paths |
| H1 | repair | 查詢逾時或測試路徑裡找不到 → 記成不明標記,上次存活的行一律重跑;推送端不拿不明的比「另一組守的測試」 | S11 | t_choice_kill_test_files_in_test_paths |
| H1 | preserve | 測試名與內容都沒變的 survived → 不重跑;no_result → 重跑;新增綁條款的測試 → 重跑 | S11 | t_choice_kill_rerun_rules、t_choice_kill_incremental |
| H2 | repair | 放行檔有一筆 AI 放的 choice: → 推送前小結印選擇點那一行;lint-waive 提示句說明會出現在哪 | 〈存活的處置〉 | t_lint_waive_choice_ai_summary |
| H2 | preserve | lint 與情境段的 AI 放行行照舊;doctor 放行計數不含 choice: | S22 | t_gov_stats_choice_dedup |
| H3 | repair | 1400 支各 4 行的小檔在推送前那一圈判得到(不是全部算不出來);掃描與挑壞法各自計時 | S19、〈範圍〉4 | t_choice_scan_batch_budget |
| H3 | preserve | 一支會讓 ast-grep 失敗的檔加一支小檔 → 整批失敗退逐檔,小檔照判、壞檔單獨標算不出來 | S19 | t_choice_scan_per_file |
| H4 | repair(文件) | 計劃〈範圍〉1 寫明有檔算不出來 choice-points 回 3;〈範圍〉2 寫明 choice-kill 有檔沒跑回 2 | — | 文件 |

未覆蓋:真 Android 專案的端到端耗時(S26 手動驗收);整批輸出超過 64MB 退逐檔時,約 450 支以上的大檔改動會超出推送前時限(只提醒不擋,修補報告實測 300 支各 200 行約 24 秒)。
