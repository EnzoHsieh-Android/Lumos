# code-資安護欄唯讀盤點 r3 收貨與處置

## 修補鏡頭配對案例(待驗範圍,不是已修好的證據)

r2 修補(aadf6b07→84a58aee)每組的原問題與守護測試;preserve 修前證據未判定,新席可自行在臨時副本跑。

| 組 | findings | repair | 修補處與守護測試 |
|---|---|---|---|
| R1 | 安1,邊1,架2,正1,通6,外3,通5 | 輸出一律走同一個顯示出口:選圖譜失敗的 stderr 原樣印路徑、顯示函式沒跳看不見的字、id 等欄位沒上限、文字覆蓋區漏列 invalid | _secinv_show→t_seclist_r2_output_escape; cmd_security_list→t_seclist_r2_output_escape; _secinv_render_coverage→t_seclist_r2_text_json_parity |
| R2 | 安2,外1 | docs 這層(或 repo 根到圖譜之間任一層)是捷徑時,自動找圖譜與 --vault 都會讀到 repo 外 | _secinv_vault_problem→t_seclist_r2_docs_symlink; _secinv_repo_root→t_seclist_r2_docs_symlink; _secinv_select_vault→t_seclist_r2_docs_symlink,t_seclist_g4_read_guards |
| R3 | 外2 | 證據引用指到非 Verification 節點只記提示,references_valid 仍為 true、入口照算已映射 | _secinv_evidence→t_seclist_r2_nonverif_evidence |
| R4 | 資1,資2,正2,資3 | 錯誤清單無上限(8MB 輸入 279 萬筆、5GB)、inventory 查重用 list、決策每條重解析 | _SecinvErrors→t_seclist_r2_error_cap; _secinv_check_row→t_seclist_r2_error_cap,t_seclist_g3_gaps_not_hidden; _secinv_inv_items→t_seclist_r2_inventory_dup_scale; _secinv_decision_problem→t_seclist_r2_decision_cache_scale |
| R5 | 通1,通2,通3,通4,通7,通8,邊3 | 測試缺口:新輔助函式蓋掉既有同名 _sl_vault、not_utf8 與各讀取類錯誤沒有斷言、unknown_evidence_statu | t_test_file_no_duplicate_defs→t_test_file_no_duplicate_defs,t_summary_line_replace; t_seclist_r2_not_utf8→t_seclist_r2_not_utf8; t_seclist_r2_read_kinds→t_seclist_r2_read_kinds; t_seclist_r2_unknown_status_refs→t_seclist_r2_unknown_status_refs; t_seclist_integration_gaps→t_seclist_integration_gaps;  |
| R6 | 架1,架3 | 讀圖譜仍是第二套(只改名搬家)、沒共用既有有界讀、沒提到既有 dirfd 決定;_secinv_collect 直接讀私有欄位 | _read_fd_capped→t_seclist_g8_read_request_bound,t_seclist_s10_size_caps; _retro_read_bytes→t_seclist_g8_read_request_bound; _vault_safe_read_rel→t_seclist_g8_read_request_bound,t_seclist_s10_size_caps; _secinv_collect→t_seclist_s01_concern_sections |
| R7 | 整1,整2,整3,整4,正3 | 文件與小項:子計劃缺 50000 與新上限、輸出契約新增項沒照實寫、Verification 舊段落沒標取代、母計劃過期句與 updated | _vault_safe_recheck→t_seclist_r2_changed_dedupe; 資源與效能→t_seclist_r2_entries_boundary; 代碼審 r2 修正→t_seclist_r2_error_cap; 解 Q1–Q3→t_seclist_integration_gaps |

## r3 收貨

同門七席加外家 Codex 一席全部交回後一次存檔;這輪共用派工詞在,格式由 report-normalize 補檔級行即合格。整合席唯一引句引自 diff 外的母計劃既有行(該席自己註明),不影響其發現。共 15 條(正1–2、邊1、資1、整1、通1–3、架1–3、安1–3、外1)。

多席獨立一致:--vault 帶 .. 經捷徑可繞過檢查(安2、邊1、通2)。

## r3 根因分組與處置(末輪,全部折入、不放行)

| id | 組 | 處置 | 一句 |
|---|---|---|---|
| 安1 | T1 | folded | tags 原文含 flag/security-relevant 但解析不到就記錯並列入未登記 |
| 通1 | T2 | folded | 加全庫錯誤總上限,超出併一筆 |
| 外1 | T3 | folded | 重複 ID 等登記錯誤涉及的控制項不算入口映射 |
| 安2 | T4 | folded | --vault 檢查與開檔用同一條正規化路徑 |
| 邊1 | T4 | folded | 同安2 |
| 通2 | T4 | folded | 同安2 |
| 正1 | T5 | folded | 補超過每篇上限時 references_valid 與入口斷言 |
| 正2 | T5 | folded | 補 valid: False 大小寫斷言 |
| 通3 | T5 | folded | 整合⑤′、② fixture 分出差異或照實改名 |
| 架1 | T6 | folded | _read_fd_capped 搬到 _regular_own_fd 附近 |
| 架2 | T6 | folded | 決策快取共用 nodes 格 |
| 架3 | T6 | folded | .git 判定統一一種寫法 |
| 資1 | T7 | folded | 顯示函式先整串快篩 |
| 整1 | T8 | folded | 母計劃 Q3、Q4 text 標明已依決策決定 |
| 安3 | T9 | folded | 其他區塊的自由文字也套資料框 |
