# 未來每輪修復回歸驗證：原始碼與獨立查證

版本固定：cf53b1ad4aa377c806787b8d5da518a9035c0409。原始碼雜湊見 inventory.json。這不是最新 main 的現況宣告。

查證方式：主控先讀程式，再由乾淨 explorer special_path_home_adjudication 以原始問題盤點，該席另請 bound_python_evidence_scope 唯讀複核。均未改檔、未跑長測試、不是正式審查席、沒有 canary 記帳。

| 能力 | 原始碼入口 | 測試入口 | 界線 |
|---|---|---|---|
| 固定材料與來源 | cmd_canary | t_disposal_snapshot_provenance | 雜湊與引句不等於完整 Git diff 覆蓋證明 |
| 修補對帳 | cmd_loop_fix_check、_fix_dispatch_base、_fix_item_record | t_fix_check_record_complete、t_fix_check_record_template | 檔級對帳；不強制列齊所有 changed，不校驗所有 hunk，正式 record base 不與 dispatch base 再比對 |
| 固定修後版本 | _isolated_worktree、_fix_check_status、_codeloop_record_valid_ex | t_loop_next_fix_check_reminder、t_fix_check_tree_setup | 設定可複製、依賴可連回工作樹、樹外平台不能完全釘住 |
| 修後指定測試 | _classify_test_refs、_spec_gate_judge_items | t_fix_check_test_must_exist、t_fix_check_listed_tests_green | 修後綠；不證修前失敗或正常行為全集保留 |
| 合約測試 | _bound_tests_check | t_fix_check_bound_tests_green | 無綁定可通過且提醒；改名存在舊路徑牽連界線 |
| 先決條件錯誤 | cmd_loop_fix_check | t_fix_check_preflight_record_stops_runners、t_fix_check_preflight_not_run_is_durable | 不跑測試，有 not_run_items；不能把此結果稱動態測試失敗 |
| 同類再發 | _fix_item_repeat | t_fix_check_repeat_category_needs_why | 類別相同需說明，不證同一根因 |
| 回歸標记 | cmd_canary regression_set 分支 | t_canary_regression_set | 編排者判讀；工具驗形狀與集合，不驗機械因果 |
| 相鄰選測 | _affected_test_keys、_testmap_affected_inner | 查 cmd_testmap_affected 與其測試 | 啟發式建議、空值 fail-open，不接成 fix-check 自動來源 |
| mutation | _fix_recipe_rerun_notes、cmd_guard_kill | t_fix_check_recipe_rerun_note | 修正關卡提示而非自動跑配方 |
| 治理判定回放 | cmd_loop_replay | 查該函式相關測試 | 判定與材料漂移，不是產品回歸測試 |

獨立查證與主控一致：現有程式驗修後綠與版本記錄；修補差異的完整性與回歸因果仍不能只靠現有標記保證。

## 本次盤點可重現方式

對 inventory.json 的 source_commit 檢出後，逐行 JSON 讀 docs/.canary-log.jsonl；先按出現順序記各 code- loop 的第一個 round，再取 ts 日期 >= 2026-10-02、含 findings_set 且不是第一輪的載體。分成 regression_set 缺欄、空清單、非空清單三類。輸出 51 筆 = 28 缺欄 + 7 空清單 + 16 非空。每一列都在 inventory.json 保留 loop、round、ts 與標記，便於核對。

這是事件筆數，不是去重後的迴圈數、缺陷數、發生率或因果結果。新流程評估須先定義重記去重與風險分層。
