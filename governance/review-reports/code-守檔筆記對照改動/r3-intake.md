# 代碼審第 3 輪(上限輪)收貨紀錄:守檔筆記對照改動

4 席全收齊後才動程式;審材是第 2 輪修正的差異(94c1e82f..80a8bb90,639 行)。四道機械檢查:4 份都已是正規化格式;quote-check 全數錨定(正確性席交 clean、沒有引句)。架構對齊席 F1 原標 major 但 blocking:否,兩欄矛盾,退回該席自己重判,改成 minor(理由:只重現出兩份判準分歧,舉不出錯行為,照規則自降一級);報告其餘不動。正確性席為讀真實治理帳在主 repo 跑過一次唯讀的 `lumos gov`,自述跑完查過使用帳沒有多寫(違反派工詞「不在主 repo 跑任何指令」的字面,但沒有寫入)。

finding 編號:s=資安-opus、a=架構對齊-sonnet、t=通才-sonnet;正確性席 0 條。

| 編號 | 席 F | 等級 | 處置 | 修法與測試 |
|---|---|---|---|---|
| s1 | 資安 F1 | major | 折 | 讀首行判程式時,路徑帶控制字元一律判不了、算程式;`t_code_loop_bookkeeping_ctrl_char_path_not_exempt` |
| s2 | 資安 F2 | minor | 折 | 簿記資料夾下可執行模式一律算程式;判 `#!` 前去 BOM 與行首空白;`t_code_loop_bookkeeping_exec_mode_and_bom` |
| s3 | 資安 F3 | minor | 折 | `lumos gov` 欄位型別表、不合整行跳過;`t_gov_skips_bad_field_types` |
| a1 | 架構對齊 F1 | minor | 折 | Unicode 類別抽成共用常數(含同族第三份一起併);`t_note_audit_reread_drift_share_special_char_cats` |
| a2 | 架構對齊 F2 | minor | 折 | 改用帶上限的批次讀取、刪除改由檔案模式判;`t_code_loop_bookkeeping_head_read_capped_and_deleted_stamp` ①② |
| t1 | 通才 F1 | minor | 折 | 路徑守衛「跑出 repo」與「建好後再查」兩分支補測試;`t_note_audit_repo_path_guard_outside_and_recheck` |
| t2 | 通才 F2 | minor | 折 | 「目標版刪掉退回讀留痕那版」分支補測試;同上 ③ |

★上限輪★:本輪有 major,照規則全折;折完沒有輪次再派新席。使用者 2026-10-01 裁定「修完直接推」——最後這段修正只經測試與翻紅核對:修正子代理在副本把 11 處修法各自還原全部翻紅;編排者抽查 `-k code_loop_bookkeeping` 25、`-k gov_skips` 17、`-k reread_drift_share` 9、`-k repo_path_guard_outside` 4 全綠。
沒做:共用批次讀檔 `_nodehome_cat_blobs`、`_nodehome_cat_sizes` 對結尾 `\r` 或換行路徑的同族問題(十幾個呼叫端,另案;計劃 REVISIT 2026-11-01);逃逸帳與 hook 事件檔不走 gov 那段讀帳。
重現不到而沒折的:無(refuted-set none)。放行的:無。
