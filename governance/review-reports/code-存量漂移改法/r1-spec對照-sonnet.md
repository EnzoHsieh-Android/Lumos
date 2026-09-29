severity: major

# 代碼審 r1 spec對照-sonnet 席報告

審材:a patch(scripts/lumos)、b patch(scripts/test_lumos.py)對照 `Projects/存量漂移改法_計劃.md`。
(spec 檔在 clone-ns 底下讀;派工詞給的 repo 根路徑下沒有這份檔。)

## F1 c2 --keep 帶 --dry-run 仍寫表態檔
severity: major
blocking: 是
引句:「`--dry-run` 不拿鎖、不寫檔也不寫帳,但做完判定與前提檢查」
佐證:file: `scripts/lumos:cmd_drift_fix`(a patch 內 `if err is None and kind == "c2" and o.get("keep"): return cmd_drift_ack(...)`,發生在 `o.get("dry_run")` 檢查之前)
1. 屬「縮水」:S9 要 `--dry-run` 不寫檔,實作的 c2 `--keep` 分支在讀 `dry_run` 之前就直接呼叫 `cmd_drift_ack`,dry_run 被忽略。
2. 重現(在 --shared clone 用測試輔助函式 `_df_repo` 建專案,K 是連著已收尾計劃的 open Issue):
   `_df_fix(v,"Issues/K","3","--kind","c2","--keep","--reason","還沒解決等上游","--dry-run")`
   輸出 `0 ✓ 表態記下了(DACK-…)`,`governance/drift-acks.jsonl` 被建立並寫入一筆 c2 表態(含 related、seq)。
3. 後果:使用者要求預覽,卻留下一筆永久表態,這一行之後在 scan 裡顯示已表態、被靜默。
4. 測試沒抓到:S11 的 `t_drift_fix_c2_close_or_keep` 的 `--keep` 只跑不帶 `--dry-run` 的那格;S1 的 ⑨ 用的是 `--close --dry-run`。
5. spec 對 `--keep` 帶 `--dry-run` 沒有單獨寫,但 S9 是無條件句;要嘛 `--dry-run` 印預覽不寫,要嘛回 2 說 `--keep` 不收 `--dry-run`,兩種都比現在符合 spec。

## F2 S2 的「正式行沒綁測試」情況沒有測試在驗
severity: minor
blocking: 否
引句:「家節點沒有綁測試的正式合約行時擋下」
佐證:file: `scripts/test_lumos.py:t_drift_fix_c1_rewrites_with_commit_date`(b patch,⑧ 那格)
1. 屬「縮水」(測試層):⑧ 標題寫「家節點沒有綁測試的正式行」,但 G6 的合約句是「沒轉正的合約」,`_DF_PAY` 裡根本沒有這句,驗到的是「家節點沒有這條合約的行」。
2. 「有正式行但沒綁 [test:]」這一支沒有斷言;`_guard_formal_line(...,None)` 的 `if refs:` 判準被拿掉時,S2 綁的這支測試不會紅。
3. 實作(`_guard_pass_home` 走 `_guard_formal_line(...,None)`)本身是對的,只有測試強度不足。

## 逐條款裁定

- [S1] 已實作。`_drift_fix_args_err`(--kind、參數組合)、`_drift_fix_target`(同名回 2)、`_drift_fix_clean_err`(未追蹤、未提交)、`_drift_fix_load` 內 `load_raw_for_edit`(BOM/CRLF)、`_drift_current_finding`(不是這一種發現)、main 的 drift 三支分派。測試 `t_drift_fix_refuses_wrong_kind` ②–⑨ 都真的驗到,含「工作目錄跟擋之前一樣」。
- [S2] 已實作(測試強度見 F2)。`_guard_settled_date` 順序 --date、已寫日期、`_guard_pass_commit_date`(shallow、也是首次出現就擋、不拿今天);`_guard_pass_home` 前提;`_guard_settle_rewrite` 的 `settle-del` 刪行不疊。`_guard_prose_needs_date` 符合「只在要寫日期時才推」。
- [S3] 已實作。`_guard_settle_pass`(鎖外讀、推日期、拿鎖比 bytes 才寫;沒預告句回 0 印「已轉正」;前提不符回 2)、pending 分支的 `--test` 缺、`--date` 給了回 2、`--test` 改選填、`--date` 新增、IDENT_RE 挪到確定是 pending 之後、成功訊息不印 `[test:]`。測試 `t_guard_settle_pass_completes_prose` 對得上。
- [S4] 已實作。`_DRIFT_C3_STATUSES = _STATUS_ENUM["verification"] - {"pending"}`;`_drift_fm_status` 走 `edit_fm_scalar` + `edit_fm_sync_status_tag`;`_drift_fix_c3` 措辭依狀態分「解決/參考」;`_drift_fix_by` 完整路徑直接查、同名或找不到回 2;`_drift_append_note` 圍欄判斷與空正文。測試對得上。
- [S5] 已實作。證據與範本(`_drift_c4_evidence`、`_drift_c4_print`)、`_drift_c4_text_err`、`_drift_valid_under_hits`(欄位名不算、剛好一次)、重新解析比項數與被換那項、`_handled` 只看被換那項、`template_used`。測試對得上。(乾淨檢查是否套用在「只列證據」上,見 ⚠。)
- [S6] 已實作。`_revisit_lines` 抽出、E5 用 `_ISSUE_CLOSED_STATUSES` 與 `type == issue` 判定並在組行時加註、照樣計數。測試含 spy 驗共用同一支。
- [S7] 已實作。`_issue_close_revisits` 由 main 在 `cmd_set` 成功後呼叫、`drift fix` c2 `--close` 也呼叫;列全部回頭條件、不含程式碼區。測試對得上,行號用寫後內容驗(n == 10)。
- [S8] 已實作。`cmd_drift_ack` 的 c2/c3 先 `_drift_current_finding`(鎖外、新 `Env`)、記 `related`(排序 NFC)與鎖內取的 `seq`;`_drift_split_acked` 只看有 `related` 的、取 seq 最大同號全算、全涵蓋才算、related 非字串清單當沒涵蓋;`prev_ack` 說明由新函式 `_drift_prev_ack_line` 印,沒借 `_drift_old_reason`。測試 ①–⑩ 含同號保守、壞 related、行號移位。
- [S9] 縮水(F1)。其餘已實作:鎖內比指紋才 `atomic_write_verify`、驗證磁碟內容等於算出內容且已處理、不自動還原並指到 `git checkout --`、`--dry-run` 不拿鎖、`_BOOKKEEPING_FILES` 加帳檔、`_drift_ledger_path_err`(逐層符號連結、真實路徑在 repo 內、硬連結數)、`_drift_fix_shape_err`。`LUMOS_DRIFT_FIX_FAULT` 只認 verify|ledger。
- [S10] 已實作。`_drift_fix_hint` 單一產生處;check 擋下、check 只列出、scan、Z 段、計劃收尾(c3 那一項)五處都改用它;c1 一篇一條在 `_drift_print_hints` 去重。測試 ⑤ 用替身函式證明五處走同一支。
- [S11] 已實作(--keep 帶 --dry-run 見 F1)。`_drift_fix_c2_args` 二擇一、結案值取 `_ISSUE_CLOSED_STATUSES`、`_drift_fix_reason_ok`(一行、4–200);`_drift_close_banner` 標題後加橫幅、已有橫幅不加;`--keep` 走 `cmd_drift_ack`、不做乾淨檢查、不寫修復帳。
- [S12] 已實作。`_drift_fix_c5` 從家節點正式行取測試(`_drift_c5_test` 走 `resolve_test_refs`)、多支取第一支並在訊息寫出、`_guard_settle_record_lines` 與 settle 共用、家節點還有預告行回 2、日期用今天、帳記 `test`。測試 ④ 用替身證明共用。

範圍節中不在 [SN] 的規格:
- 五種 c1–c5 寫入順序:已實作。乾淨檢查、讀檔拒 BOM/CRLF、鎖外新建 Env 判定、前提、自由文字先過形狀擋、dry-run、鎖內比指紋、驗證、寫帳。讀檔與乾淨檢查的先後與 spec 相反(spec 先乾淨檢查再讀),兩者都在寫入前、結果相同,不算偏離。
- 參數與種類組合表、`--date` 格式與未來日期回 2、`--reason` 4–200 一行:已實作於 `_drift_fix_args_err`。
- 錯誤回 2 的情況(probe、非 c1–c5、同名、未追蹤、不乾淨、BOM/CRLF、判定不符、git 逾時/shallow、寫入 OSError、驗證失敗、帳寫不進去):已實作。
- 修復帳欄位(id、seq、date、path、line、kind、changed、after_sha256、template_used、test):已實作;`after_sha256` 是算出的內容雜湊而非重讀磁碟,但第 6 步先驗磁碟內容等於它,等價。
- 事件沿用閘名 `drift-check`、種類 `fix`,並印「修復帳要跟筆記一起提交」:已實作。
- HELP_WHEN 的 drift、drift ack、drift fix、settle 與 argparse help:已補。
- `_STATUS_ENUM` 抽成模組常數、`_plan_first_commit` 加逾時:已實作。
- guard 區段不呼叫 drift 區段:確認(guard 那批函式只呼叫 guard 與底層 git、Env 函式)。
- 兩支既有測試的調整:`t_guard_settle_recovers_half_done` 已改;`t_guard_settle_rewrites_planned_prose` 沒動(該測試沒有手補段場景,合理)。
- 回退相關與同步的筆記、指令文件:屬 c patch(圖譜與 skills 文件),不在本席審材範圍。

## 四類清單

縮水:
- F1(S9 的 `--dry-run` 不寫檔,c2 `--keep` 例外寫表態檔)。
- F2(S2 的「有正式行但沒綁測試」沒有測試驗,測試層)。

未實作:(空)

多做:(空)。有兩處是收得比 spec 列舉更嚴,認定在「會改變 YAML 結構的字元」的範圍內,不算多做:`_drift_c4_text_err` 另擋 `--new` 結尾的冒號與 ` #`,以及 `--old` 不能跨行。

⚠ 交編排者:
1. c4「不帶改寫參數只列證據」在實作裡仍先過乾淨檢查(`_drift_fix_load` 只在 `dry_run` 時跳過)。spec 第 5 節寫「c4 不帶改寫參數(`--dry-run` 同):列證據與範本,回 0 不寫」,第 1 節只說 `--dry-run` 不做乾淨檢查;髒的驗證紀錄上想看證據會被回 2。spec 字面兩讀,我判不準,不計入 finding。
2. 第 8 節「上線時:工具鏈 2026-09-29 那 17 筆 c2 表態…逐筆比對」屬實作收尾的資料動作,不在 a/b patch;請確認 c patch 或後續提交有沒有做。
3. doctor Z 段每種只印一條「改法例」(第一筆),c1 沒有「每篇一條」;scan 與 check 有做到。spec S10 的「c1 每篇一條」對 Z 段是否也適用,措辭上不明。

縮水+未實作共 2 條
最高等級:major
