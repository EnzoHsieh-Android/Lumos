# r4 配對案例(修前 f04090128 → 修後 7e2c292e3)

只列待驗範圍,不是「已修好」的證據。需求出處:計劃節點 Projects/情境題答案要引規格出處與回寫循環_計劃(範圍 4、5、天花板 8);中斷兩段式的業界來源見 cap-retro.json 的 world_check。

| 組 | 角色 | 待驗行為 | 來源 | 守它的測試(修後) |
|---|---|---|---|---|
| G1 | repair | 收尾卡住時第二個終止訊號 → 程序立刻結束(殘骸留著、交給清殘骸);第一個訊號時印「再按一次強制結束」 | 天花板 8;業界兩段式 | t_situation_rule_double_signal、t_situation_rule_force_kills_live_group |
| G1 | repair | 等寫入鎖時收到訊號 → 立刻中止、不等 60 秒;中斷不留自己建的殘鎖 | 範圍 4 寫回 | t_situation_rule_write_phase_signals |
| G1 | repair | 計劃已寫、帳沒記時被強制結束 → 先印補記事件再結束 | 範圍 4 寫回 | t_situation_rule_write_phase_signals |
| G1 | preserve | 單一 SIGTERM / Ctrl-C 照舊溫和收尾、rc 2、計劃與帳不寫;離開後處理器還原;nohup 的忽略照留 | 範圍 4 中斷 | t_situation_rule_term_signal、t_situation_rule_interrupt |
| G2 | repair | --plan 大小寫比對改叫 _disk_spelling;NFD 磁碟檔名照收 | 範圍 4 | t_situation_rule_plan_disk_spelling |
| G2 | preserve | Projects 是符號連結、`..`、大小寫不同照拒 | 範圍 4 | t_situation_rule_plan_symlink_and_case、t_situation_rule_plan_path_contained |
| G3 | repair | 同文同測試但帳上事件是別段別列 → 不說完成、照拒並說明;治理帳讀不出來 → 叫人先修帳 | 範圍 4 寫回 | t_situation_rule_already_seg_row |
| G3 | preserve | 同段同列同文同測試且帳已記 → 回 0 完成;帳沒記 → 叫人先刪那條再重跑 | 範圍 4 | t_situation_rule_already_written |
| G4 | repair | --keep-worktree 工作樹沒建起來 → 那個平台一行說沒建成 | guard kill 約定 | t_isolated_worktree_keep_failed_build、t_isolated_worktree_shared |
| G5 | repair | 規格閘印 AI 代跑核可原話時標明是資料 | 天花板 7 | t_spec_gate_ruled_ai_reminder |

修前版本 f04090128 是目前分支 HEAD 的父提交,完整來源在 git 歷史。
