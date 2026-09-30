# 代碼審第 2 輪收貨紀錄:守檔筆記對照改動

5 席全收齊後才動程式;審材是第 1 輪修正的差異(94e28375..94c1e82f,1162 行)。四道機械檢查:5 份都已是正規化格式;quote-check 全數錨定(邊界席交 clean、沒有引句);repo 根 reflog 無異動。

finding 編號:a=架構對齊-sonnet、s=資安-opus、c=正確性-opus、t=通才-sonnet;邊界席 0 條。

| 編號 | 席 F | 等級 | 處置 | 修法與測試 |
|---|---|---|---|---|
| a1 | 架構對齊 F1 | major | 折 | 留痕有效性的簿記判法改成跟每支檔有家同一套(副檔名 + 首行 `#!`,首行從 git 讀);`t_code_loop_bookkeeping_shebang_script_not_exempt` |
| a2 | 架構對齊 F2 | minor | 折 | 抽共用 `_repo_path_unsafe`,筆記內容審資料夾守衛與存量漂移帳檔檢查都呼叫它;`t_note_audit_drift_share_repo_path_guard` |
| s1 | 資安 F1 | minor | 折 | 過濾擴大到 Unicode Cc/Cf/Zl/Zp、record 寫帳也過濾;`lumos gov` 跳過非物件行;`t_note_audit_reread_unicode_separator_paths`、`t_gov_skips_non_object_lines` |
| c1 | 正確性 F1 | minor | 折 | prepare 也略過工作目錄裡已有的紀錄並提醒提交;`t_note_audit_reread_prepare_skips_uncommitted_records` |
| t1 | 通才 F1 | minor | 折 | 補 prepare 印的 codex 派法測試;`t_note_audit_reread_prepare_codex_dispatch_stdin` |
| t2 | 通才 F2 | minor | 折 | 補起點那一側截止時間的測試;`t_nodehome_side_deadline_reread_base_side` |

翻紅:前 4 條的新測試對修前的碼跑紅;5、6 守既有行為,改壞翻紅;修完另開副本把 10 處修法各自還原,全部翻紅(修正子代理回報,編排者抽查 `-k reread` 122、`-k code_loop_bookkeeping` 9、`-k gov_skips` 2、`-k repo_path_guard` 8、`-k nodehome_side_deadline` 4 全綠)。
沒做:大寫副檔名(`.PY`)不算程式,跟既有四份副檔名清單同口徑;通用 `_esc_clean` 與其他閘寫帳的同族問題另案。
重現不到而沒折的:無(refuted-set none)。放行的:無。
