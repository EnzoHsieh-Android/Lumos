# code-改動選擇點 r4 待驗行為(修補鏡頭配對案例)

只列待驗範圍,不是「已修好」的證據。修前 dbdc038622a33ea32d32dba7ac7e8f923c73442e(第三輪派工單 base_commit)、修後 24ec789661392ddf59b5a8774a4856d173ddab61。來源:計劃 docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md 的條款與〈用詞〉。本輪是人裁破例加開的第 4 輪(cap-decision extra-round)。

| 組 | 角色 | 待驗行為(輸入 → 預期) | 出處 | 相關測試(修後) |
|---|---|---|---|---|
| J1 | repair | 測試檔 app/src/test/java/FooTest.kt 含 fun bar(),綁名 FooTest.bar → 找得到所在檔(不是不明標記);改該測試內容 → 雜湊變 | S11 | t_choice_kill_test_files_in_test_paths |
| J1 | repair | 測試路徑裡含測試名、副檔名不屬於該平台的檔(feature/src/test/resources/cases.md)改了 → 雜湊不變 | S11 | t_choice_kill_test_files_in_test_paths |
| J1 | preserve | 一般名、反引號名、兩平台同名、子字串名、只改計劃筆記 → 結果與第三輪相同 | S8、S11 | t_choice_kill_test_files_in_test_paths、t_choice_kill_rerun_rules |
| J2 | repair | 暫存目錄落在 .gitignore 寫 *.kt 的 git repo 底下,兩支檔各一個比較運算 → 整批各 1 個命中(不是 0) | S19 | t_choice_scan_* (修補新增) |
| J2 | repair | 整批卡住、逐檔立刻回,掃描時限 8 秒 → 所有檔掃到 | 〈範圍〉4 | t_choice_scan_batch_share |
| J2 | preserve | 1400 支小檔整批判得到;一支壞檔加一支小檔 → 小檔照判 | S19 | t_choice_scan_batch_budget、t_choice_scan_per_file |
| J3 | repair | 拿掉推送前多算的碰到計劃時限底線 → 推送前判定結果不變 | — | t_spec_gate_push_choice* |
| J4 | repair | choice-kill 有一支檔算不出選擇點 → rc 2、stderr 警告;doctor 新增告警放行條數不含選擇點 | 〈範圍〉2、S22 | 修補新增測試 |

未覆蓋:真 Android 專案的端到端耗時(S26 手動驗收);整批輸出超過 64MB 退逐檔時,約 450 支以上的大檔改動會超出推送前時限(只提醒不擋);拿掉時限底線後,若日後 `_choice_requirement` 的流程改成不先算過計劃,推送前建圖譜那一步沒有時限。
