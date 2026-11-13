# r3 配對案例(修前 1d535b07b → 修後 f04090128)

只列待驗範圍,不是「已修好」的證據。需求出處:計劃節點 Projects/情境題答案要引規格出處與回寫循環_計劃(範圍 4、5、天花板 7、8)。

| 組 | 角色 | 待驗行為 | 來源 | 守它的測試(修後) |
|---|---|---|---|---|
| G1 | repair | 殺傷力期間連續兩個終止訊號(SIGTERM×2、SIGTERM→SIGHUP、SIGINT×2)→ 程序群組與工作樹都收乾淨 | 範圍 4 中斷 | t_situation_rule_double_signal |
| G1 | preserve | 單一 SIGTERM / Ctrl-C 照舊收尾、rc 2;離開後處理器還原;nohup(忽略)照留 | 範圍 4 中斷 | t_situation_rule_term_signal、t_situation_rule_interrupt |
| G2 | repair | 寫計劃前、寫後記帳前、記帳當中收到訊號 → 各自走對應出口(不寫/印補記回 1/帳已記回 0) | 範圍 4 寫回 | t_situation_rule_signal_during_write |
| G3 | repair | 「已寫過」分兩種:帳已有對得上的事件 → 說已完成;帳沒有 → 說先刪計劃那一條再重跑 | 範圍 4 寫回 | t_situation_rule_already_written |
| G4 | repair | 舊條款綁兩支測試、--test 其中一支 → 不算已寫過,照插新條款 | 範圍 5 口徑 | t_situation_rule_same_exact_refs |
| G4 | preserve | 同文、綁恰好同一支測試 → 照拒 | 範圍 4 | t_situation_rule_insert_position |
| G5 | repair | 計劃有 BOM、單獨的 CR → 拒絕、計劃不動 | 範圍 4 寫回 | t_situation_rule_read_line_endings |
| G5 | preserve | LF 計劃照常寫回;CRLF 照拒 | 範圍 4 | t_situation_rule_writes_clause、t_situation_rule_crlf_and_encoding |
| G6 | repair | 寫完讀回對不上 → rc 1、訊息說計劃已動 | 範圍 4 rc | t_situation_rule_readback_mismatch |
| G7 | repair | --keep-worktree 但工作樹沒建起來 → 不留保留標記、暫存照收 | guard kill 約定 | t_isolated_worktree_keep_failed_build |
| G7 | preserve | 建起來的保留現場照寫標記、清殘骸跳過 | 範圍 4 sweep_repo | t_isolated_worktree_keep_marker |
| G8 | repair | Projects 本身是符號連結、--plan 大小寫跟實際檔名不同 → 拒絕 | 範圍 4 | t_situation_rule_plan_symlink_and_case |
| G8 | preserve | 正常 Projects/<名> 照收;`..`、中間連結照拒 | 範圍 4 | t_situation_rule_plan_path_contained |
| G9 | repair | 規格閘認到 origin=ai 的人裁條款多印一行提醒、不擋 | 天花板 7 | t_spec_gate_ruled_ai_reminder |
| G9 | preserve | origin=human 不印;認人裁條款的判定不變 | 範圍 5;S13 | t_spec_gate_ruled_clause_as_keeps |

修前版本 1d535b07b 是目前分支 HEAD 的父提交,完整來源在 git 歷史。
