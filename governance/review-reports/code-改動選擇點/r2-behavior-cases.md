# code-改動選擇點 r2 待驗行為(修補鏡頭配對案例)

只列待驗範圍,不是「已修好」的證據。修前 7826895c162915abba4d1ab892ce4b3216ad65b0、修後 4dd1ed800c58b62a724c550f3edd3dd54f979705。來源:計劃 docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md 的條款與〈用詞〉。

| 組 | 角色 | 待驗行為(輸入 → 預期) | 出處 | 相關測試(修後) |
|---|---|---|---|---|
| G1 | repair | 20 行曾存活、上限 14,放行抽中的行後再推 → 抽中集合不變、沒抽中的 6 行仍不要求;提醒印的曾存活數是 20 | 〈用詞〉回報上限、S16 | t_choice_push_cap_waive_stable |
| G1 | preserve | 用 killed 處置抽中的行 → 沒抽中的仍不要求;新存活行出現 → 重抽 | S16 | t_spec_gate_push_choice_cap |
| G2 | repair | 第一支測試紅但帶弱證據 → 同組下一支照跑;只有弱證據的 survived → 記 no_result | S9、〈用詞〉殺掉判定 | t_choice_kill_weak_evidence |
| G2 | preserve | 強 killed → 同組停跑;都強 survived → survived | S7、S8 | t_choice_kill_batch、t_choice_kill_no_result |
| G3 | repair | 測試名不變、測試內容補強後重跑 → 那一行重跑;no_result 的行重跑 → 重跑 | S11、〈範圍〉2 | t_choice_kill_rerun_rules |
| G3 | preserve | 測試名與內容都沒變的 survived → 不重跑;新增綁條款的測試 → 重跑 | S11 | t_choice_kill_incremental |
| G4 | repair | `name + ": " + id`、`f1 + id + "/"` → 鏈上每個 + 都不產生算術壞法 | S2 | t_choice_points_str_concat_chain |
| G4 | preserve | `a + b`(兩邊都不是字串字面值)→ 照常產生 | S2 | t_choice_points_operands |
| G5 | repair | 一支 1500 行呼叫清單函式加一支小檔 → 小檔照判、大檔單獨標算不出來 | S19、〈範圍〉4 | t_choice_scan_per_file |
| G5 | preserve | 一般大小檔掃描結果與修前相同;乾節點照略過 | S3、S4 | t_choice_points_arid、t_choice_points_stable |
| G6 | repair | 種子改常數、拿掉洗牌、節點排序改壞、排除後 continue 改 break → 測試要紅 | 論文 4.1 Listing 2;〈用詞〉一行一個壞法 | t_choice_points_pick_order |
| G6 | repair | cmd_guard_kill 不傳新參數 → 輸出與 rc 完全不變;skipped 不進 rc | Systems/guard-kill 兩條合約 | t_choice_guard_kill_new_params |
| G7 | repair | 連續 5 行相同 → 標不唯一、不跑;guard kill、situation-rule 同樣判法 | S3 | t_choice_unique_overlapping |
| G8 | repair | 兩平台同名測試 → 各自有結果、不判缺結果 | S8 | t_choice_kill_same_name_two_platforms |
| G9 | repair | 遠端名 `my/fork`、在主線 trunk 上不帶 --diff → 擋下要帶 --diff | 〈範圍〉1 | t_choice_range_mainline_slash_remote |
| G11 | repair | 帳裡重複列 → 統計去重;人裁寫回的第一筆不算第一次跑;doctor 放行計數不含 choice: | S22 | t_gov_stats_choice_dedup |
| G12 | repair | aborted 很長 → 事件不超過位元組上限;check.py --catalog-only 帶 --sg 用它 | S20 | t_choice_ledger_write_semantics |
| G10 | repair(文件) | 計劃與 lumos-code-loop SKILL:lint-waive 與 choice-kill 在 code-loop pass 之前 | — | 文件 |

未覆蓋:真 Android 專案的端到端耗時(S26 手動驗收)。
