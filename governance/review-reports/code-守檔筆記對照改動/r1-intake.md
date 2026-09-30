# 代碼審第 1 輪收貨紀錄:守檔筆記對照改動

8 席全收齊後才動程式。材料拆兩份(程式 1286 行、測試 894 行);通才席審測試,其餘審程式。四道機械檢查:8 份都已是正規化格式;quote-check 全數錨定(規格符合席交 clean、沒有引句);席位都在自己的 clone 做實驗,repo 根 reflog 無異動。外家 finder/否決照 2026-09-30 使用者裁定預設不派。

finding 編號:c=正確性-opus、k=併發-sonnet、b=邊界-sonnet、g=合約圖譜-sonnet、t=通才-sonnet、a=架構對齊-sonnet、s=資安-opus;規格符合席 0 條。

| 編號 | 席 F | 等級 | 處置 | 修法與測試 |
|---|---|---|---|---|
| s1 | 資安 F1 | major | 折 | 共用資料夾守衛:工作目錄任一層是符號連結或解析到 repo 外就不清檔不寫檔、rc2;`t_note_audit_reread_workdir_symlink_refused` |
| s2 | 資安 F2 | minor | 折 | 路徑含控制字元的筆記跳過、印出前過濾;項目檔頭重複欄位整份不收;`t_note_audit_reread_ctrl_char_paths` |
| s3 | 資安 F3 | minor | 折 | 紀錄與判定檔資料夾走同一道守衛;`t_note_audit_reread_verdict_dir_symlink_refused` |
| s4 | 資安 F4 | minor | 折 | 只改留痕有效性:關改名偵測、簿記資料夾下程式副檔名不算簿記、中文檔名照原樣比對;`t_code_loop_bookkeeping_rejects_code_moved_in` |
| k1 | 併發 F1 | minor | 折 | `_nodehome_side` 選配截止時間;`t_nodehome_side_deadline_reread` |
| b1 | 邊界 F1 | minor | 折 | 寫帳前路徑過濾,提醒照常寫帳;`t_note_audit_reread_non_utf8_path_logs` |
| c1 | 正確性 F1 | minor | 折 | prepare 預設略過已對照、`--all` 全產;`t_note_audit_reread_check_reminds` ⑨ |
| g1 | 合約圖譜 F1 | minor | 折 | `_reinject_all` 重注入 CLAUDE.md、AGENTS.md 戳記 v1.2;`t_discipline_block_stamp_matches_version` |
| g2 | 合約圖譜 F2 | minor | 折 | 存量漂移守衛責任欄認領 reread-check 那段;筆記內容審子指令數改成七 |
| a1 | 架構對齊 F1 | minor | 折 | `_note_audit_write_verdict` 加資料夾與前綴參數、reread-record 共用;`t_note_audit_reread_record_shares_verdict_writer` |
| t1 | 通才 F1 | minor | 折 | S7 測試加「頂端已在主線記 none」 |
| t2 | 通才 F2 | minor | 折 | S1 測試加「家筆記在範圍內被刪」 |

翻紅:1–10 的新測試對舊碼跑紅;11、12 守既有行為,改壞對應那行翻紅;修完再把每處修法單獨還原,十二處各自翻紅(修正子代理回報,編排者抽查 `-k reread` 113、`-k code_loop_bookkeeping` 4、`-k nodehome_side_deadline` 3、`-k discipline_block_stamp` 2 全綠)。
順手:skill 與 prepare 印的 codex 派法改成從標準輸入讀項目檔(資安席附帶提的,未列 finding)。
沒做:通用寫帳函式 `_gate_event` 遇非 UTF-8 字串會丟例外的同族問題(只修了 reread 呼叫點,另案)。
重現不到而沒折的:無(refuted-set none)。放行的:無。
