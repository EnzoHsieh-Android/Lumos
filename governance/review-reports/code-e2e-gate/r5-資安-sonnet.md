severity: major

范圍:只看 r5-repair.patch 的修補差異,並對照完整快照與工作樹原始碼。沒有建立臨時檔。

## 發現

### 1. 兩個出口以外還有直接印出外來檔名的輸出點,修補說的「出口一律走這裡」不成立
severity: major
blocking: 是

- 誰:陌生專案的作者(使用者 clone 或 checkout 其分支),或在工作樹裡留下怪檔名的第三方腳本。照常操作的 AI 會讀到這些輸出。
- 從哪裡:`lumos android-e2e judge --no-record` 的按功能判讀報告,還有 `judge --precheck`。
- 送什麼:在 `app_dirs` 底下,提交一個檔名帶換行或 ESC 的檔,例如 `x\n注意:忽略上面所有規則…`。git 允許這種檔名。
- 拿到什麼:任意多行文字,原樣出現在 AI 看到的輸出裡。
  - `_e2e_changed_files` 把 `git diff --name-only -z` 的檔名原樣收進 `unmatched`,放進 `steps.json` 的 selection。
  - `_e2e_judge_partial` 再用 `print(f"  ! 這些改到的檔沒有對應功能…:{'、'.join(sel['unmatched'])}")` 印出,沒經 `_e2e_clean` 或 `_esc_clean`。
  - `--precheck` 印的 `擋下:{err}` 帶 `_dirty_non_bookkeeping` 的檔名,直接用 `print`,沒過 `_e2e_say_block`。這一條是修補把同類 print 都改成 `_e2e_say_block` 時漏掉的。
  - `_e2e_print_runs` 印的 `reason`、`name`、`reports`、`notices` 也沒清,來源是 run 目錄與判讀結果。這一項我沒逐欄追到來源,但它同樣不經那兩個出口。
- 歸因:有證據的原有漏查。這幾行不在 r5-repair.patch 的改動裡。修補沒有放大它,但修補註解宣稱已統一,所以這個缺口會被當成已封住。

引句:「print(f"  ! 這些改到的檔沒有對應功能(推送前的整套跑照樣會驗到):{'、'.join(sel['unmatched'])}")」
file: `scripts/lumos:41162`
引句:「print(f"擋下:{err}" if err else "工作目錄乾淨,可以開跑。", file=sys.stderr if err else sys.stdout)」
file: `scripts/lumos:42180`

### 2. `_e2e_parent` 在淺層 clone 裡把「查不出上一版」當成「根提交」而放行
severity: minor
blocking: 否

- 歸類:推論,縱深防禦。
- 誰:在淺層 clone 或 `--depth` 的工作樹推送的使用者。
- 從哪裡:`_e2e_gate_uses` 走到「主線候選查不到、被推送提交又沒有 `macrobench.json`」那條分支。
- 送什麼:`rev-list --parents -n 1` 成功,但淺層邊界的提交沒有 parent 欄,`_e2e_parent` 回 `""`。
- 拿到什麼:`parent` 為空,不檢查上一版有沒有 e2e 段,「拿掉驗收設定」這道擋不到。
- 範圍很窄:要同時查不到主線,又在淺層邊界上才會走到。
- 歸因:未判定。

引句:「return (parts[1] if len(parts) > 1 else ""), None」
file: `scripts/lumos:41640`

### 3. `_esc_clean` 保留零寬與格式字元,零寬字只在路徑欄位被源頭拒收
severity: minor
blocking: 否

- 歸類:縱深防禦。
- 其他外來字串進訊息時,零寬字、BOM、Zl/Zp 都還在。出口的 `_e2e_clean` 沒處理這些。
- 逃逸帳字樣的拆法是插入一個空格。我試想了全形、夾零寬字兩種繞法:這兩種只會讓字串不再匹配 `pre-push` 的 `grep`,不會反過來「造出」那兩串字,所以拆開的做法繞不過去。
- `tier=high 且` 這串拆成 `ti er=high 且`,`grep` 找不到。
- 目前只剩視覺混淆(零寬字讓兩行看起來一樣),沒有可利用的路徑。
- 歸因:未判定。

引句:「if any(unicodedata.category(ch) in ("Cc", "Cf", "Zl", "Zp") for ch in p):」
file: `scripts/lumos:40331`

## 三類逐項

### ① 提示注入
- 逃逸帳字樣:修補的做法有效。`_e2e_clean` 先 `_esc_clean`,再拆兩串字,`_e2e_gate_out` 與 `_e2e_say_block` 共用。
- 欄位串接:各欄位先分別清過,串接後的 `reason` 在出口又整串清一次,沒看到跨欄位拼出標記字樣的路。
- `_cl_say_e2e_block` 的 `reason`、`record`、`bad_cases`:都從 `_e2e_gate_out` 的結果來。
- check 的 JSON:經 `json.dumps`,且內容也來自 `_e2e_gate_out`。
- `提醒:` 行:欄位出自 `_e2e_gate_out`,或是整數、`fp`。
- 開場掛鉤:只印份數。
- `--list`:`fp` 受 `E2E_FP_RE` 約束,其餘欄位走 `_esc_clean`。
- 功能名與情境名:受 `[A-Za-z0-9_-]+` 約束。
- 洞在發現 1:未經清理的輸出點仍在。

### ② 讀寫與執行越界
- `_e2e_record_update` 改用 `lstat` 判大小,是正向的修補。
- `_e2e_parent` 與 `rev-list` 的 sha 來自 `_LENS_SHA_RE` 驗過的十六進位值或 `_push_rev` 的完整 sha。tree 讀取用 `--literal-pathspecs … --`。沒有被當成選項的路。
- 新增的密鑰或信箱:已看,無。
- 淺層 clone 的問題見發現 2。

### ③ 非刻意的守衛繞過
- 判定讀紀錄上限改成 2MB:同一份大紀錄在「判定、寫入、掃描」三處的處置一致,都不讓裡面的放行生效。
- `_E2eGitErr` 的型別分流:git 暫時失敗不會被標成 `bad_record` 而叫人去刪紀錄。
- `cfg_weakened`:只影響提示行,不改判定結果。
- 路徑 64 層與清單 1000 項的上限:不是一步就能走過去的守衛。
- 已看,無。

最高等級 major,擋實作 1 條(發現 1)。
