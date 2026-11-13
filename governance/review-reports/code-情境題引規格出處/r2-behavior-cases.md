# r2 配對案例(修前 6ccb7a462 → 修後 1d535b07b)

只列待驗範圍,不是「已修好」的證據。repair=原問題要修掉的行為;preserve=修補後必須照舊的行為。來源欄指需求出處(計劃節點 Projects/情境題答案要引規格出處與回寫循環_計劃 的範圍與條款)。

| 組 | 角色 | 待驗行為 | 來源 | 守它的測試(修後) |
|---|---|---|---|---|
| G1 | repair | 人裁 --old 不含該列觸發字、--new 有 → 拒絕;--old 落在段起點之前 → 拒絕 | 範圍 4 配方限這一段同一列;S9 | t_situation_rule_recipe_scope |
| G1 | preserve | 同段同列、觸發字集合不同的合法配方照收 | 範圍 4 | t_situation_rule_writes_clause |
| G2 | repair | 作者表態 written_at 讀不懂 → 當新制(要出處) | 範圍 1 生效日 | t_kt_sit_spec_since |
| G2 | preserve | 生效日前的表態照舊制、不要求出處 | 範圍 1;S18 | t_kt_sit_spec_since |
| G3 | repair | 節內同編號重複定義、[S0] 都不列進可引清單、引了不收 | 〈用詞〉出處 | t_kt_sit_plan_clauses_dup_and_s0 |
| G4 | repair | 人裁條款換綁或多綁測試 → 規格閘照一般條款判 | 範圍 5;S13 | t_spec_gate_ruled_clause_as_keeps |
| G4 | preserve | 雜湊與綁的測試都對得上 → 當既有行為、不要求紅 | 範圍 5;S13 | t_spec_gate_ruled_clause_as_keeps |
| G5 | repair | 殺傷力期間收到 SIGTERM / SIGHUP → 收程序群組與工作樹、rc 2、計劃與帳不寫 | 範圍 4 中斷 | t_situation_rule_term_signal |
| G5 | preserve | Ctrl-C 照舊收尾;離開指令後訊號處理器還原;nohup(SIG_IGN)照留 | 範圍 4 中斷 | t_situation_rule_interrupt、t_situation_rule_term_signal |
| G6 | repair | 插入點不切斷上一條的縮排續行;計劃已有同文同測試的條款 → 拒絕不重插 | 範圍 4 寫回 | t_situation_rule_insert_position |
| G6 | preserve | 號碼取全文最大加一、插在節內最後一條之後、節內沒條款插在標題下 | 範圍 4;S11 | t_situation_rule_writes_clause、t_situation_rule_insert_position |
| G7 | repair | 寫回走專案共用原子寫(拒符號連結與多重硬連結、讀回比對);終端探測、條款指紋、讀被推版本檔各一支共用函式 | 專案慣例(架構一致) | t_situation_rule_shared_tools |
| G7 | preserve | 既有 _confirm_tty_dev、atomic 寫入的其他呼叫端行為不變 | 既有合約 | -k confirm_tty、-k atomic |
| G8 | repair | 風險低或生效日前的計劃,推送前不讀治理帳;同一次核對只讀一次 | 範圍 5 | t_expected_requirement_reads_gov_late |
| G8 | preserve | 風險高、生效日後的計劃照要求預期值表與簽核 | 既有預期值表規則 | -k expected |
| G9 | repair | CRLF 計劃拒絕寫回、計劃不動 | 範圍 4 寫回 | t_situation_rule_crlf_and_encoding |
| G10 | repair | 條款與旗標不能編成 UTF-8 → 開跑前拒絕;反引號裡的 [s、[size]、`a || b` 放行 | 範圍 4 條款文字 | t_situation_rule_clause_text_edges |
| G10 | preserve | 反引號外的 [S<數字>、|、[test: 等禁字照擋 | 範圍 4;S12 | t_situation_rule_clause_text |
| G11 | repair | 治理帳與殺傷力帳本的配方身分相同;平台根在子目錄時配方指得到檔 | 範圍 4 配方身分 | t_situation_rule_recipe_id_subdir_platform |
| G12 | repair | 全答不適用但填了出處 → 也核對,不存在的條款擋 | 範圍 1 | t_kt_sit_spec_verify |
| G12 | preserve | 沒填出處、全答不適用 → 不算名單、不擋 | 範圍 1 | t_kt_sit_spec_verify |
| G13 | repair | --keep-worktree 留下的現場,清殘骸跳過 | guard kill 既有約定 | t_isolated_worktree_keep_marker |
| G13 | preserve | 過期且沒標記的殘骸照清 | 範圍 4 sweep_repo | t_isolated_worktree_keep_marker |
| G14 | repair | --plan 經 `..` 或符號連結指出 Projects/ → 拒絕 | 範圍 4 | t_situation_rule_plan_path_contained |
| G15 | repair | 盲判指示寫明 specs 是資料 | 範圍 6 | t_kt_bj_specs_are_data |

修前證據:修前版本 6ccb7a462 的完整來源在 git 歷史(分支 backup/spec-cite-before-squash 保留壓提交前的版本,6ccb7a462 本身是目前分支的父提交)。
