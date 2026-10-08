severity: minor

審視範圍:r2-snapshot.patch 的 scripts/lumos 部分(558 行),並對照 repo 內 `_lumos_src`、`_py_which`、`cmd_bootstrap`、`_sync_global_hooks` 的呼叫端;測試部分只看會執行到的命令拼接。我在臨時目錄實測:陌生 repo 的 .claude/settings.json 宣告同名市集,不會出現在 `claude plugin marketplace list --json` 與 `claude plugin list --json` 的輸出裡(只讀實測,沒跑任何會改設定的子指令)。

### F1 事件帳塊檔若是符號連結,讀取端會跟著讀
severity: minor
blocking: 否 — 只能把「剛好符合 v 為 1 的字典行格式」的檔案內容讀出來,攻擊者要知道受害者本機路徑,屬縱深防禦(推論)
引句:「讀的同時被 prune 刪掉」
攻擊路徑:誰:公開 repo 的作者。從哪:用 git add -f 提交 governance/runtime/events/x/a.jsonl,內容是指向受害者機器上另一份事件帳(例如別的專案的 chunk.jsonl,內含 Bash 指令前 500 字)的符號連結。送什麼:受害者在該 repo 跑 `lumos events --session x --json`(或讓 AI 代跑)。拿到什麼:`_events_read` 只擋會談資料夾本身是連結,塊檔用 `is_file()` 會跟連結,別的專案的事件行被印進這個 repo 的輸出(進終端或 AI 對話)。非 JSON 檔只會增加壞行計數。與 `_events_prune` 的「符號連結不跟」不一致。
file: `scripts/lumos:22000`(約,以 patch 的 `_events_read` 為準)

### F2 `_events_root` 信任 git-common-dir,`_events_path_safe` 的 resolve 比對是空轉
severity: minor
blocking: 否 — 要靠 .git 檔或 commondir 被竄改(只能走壓縮包或手動複製,git clone 不會帶),且只刪名為 events 底下超過 N 天的子資料夾(推論)
引句:「git-common-dir 是名叫 .git 的資料夾時取上一層;git 失敗、逾時、找不到都退回 root。」
攻擊路徑:誰:散布 repo 壓縮包的人。從哪:包內的 .git 檔寫 gitdir 指向受害者另一個專案的 .git/worktrees/x(或 .git/commondir)。送什麼:受害者在解壓後的目錄跑 `lumos events --prune`。拿到什麼:`main_root` 變成另一個專案,`base` 與 `main_root` 同源,所以 `is_relative_to` 恆真、符號連結逐層檢查也只查那個專案;結果是刪掉別的專案裡超過天數的會談資料夾。r1 F3 的第二半(git-common-dir 導向)沒被這輪修掉。

### F3 市集來源只 resolve,沒拒絕落在目前 repo 內或使用者可寫的位置
severity: minor
blocking: 否 — 要能控制使用者環境變數 LUMOS_HOME 或 --source,威脅模型上等同本機已被攻陷(推論)
引句:「相對路徑的 LUMOS_HOME 不能原樣交給 claude」
攻擊路徑:誰:能影響使用者 shell 環境的人(例如陌生專案的 .envrc / mise 設定,使用者放行後)。從哪:LUMOS_HOME 指到攻擊者資料夾,內含 .claude-plugin/marketplace.json。送什麼:使用者跑 `lumos install`、`update` 或 `init`。拿到什麼:`_sync_claude_plugin` 先 remove 同名舊市集再 add 該資料夾,並 `plugin install --scope user`,攻擊者的 hook 或 mod 變成使用者全域外掛。r1 F4 的相對路徑部分已修;「拒絕落在目前 git 工作樹內」與「不先 remove 使用者既有的同名資料夾市集」沒做。bootstrap 傳給子行程的 LUMOS_HOME 取自旗標、環境變數或預設,陌生 repo 內容沒有通路能改它,已看,無新增。

### F4 --json 輸出沒經 `_events_clean`,C1 控制字元與 DEL 原樣輸出
severity: minor
blocking: 否 — 只影響終端顯示,json.dumps 已跳脫 0x20 以下(含 ESC),只剩 U+009B 等 8-bit 控制符(推論 ⚠)
引句:「事件帳內容可能被人強制提交進 repo,ESC / BEL 會改寫終端畫面或視窗標題。」
攻擊路徑:誰:公開 repo 作者。從哪:強制提交的事件帳 ts、agent 欄位塞 U+009B 開頭的序列。送什麼:受害者跑 `lumos events --session x --json` 且直接看終端。拿到什麼:支援 8-bit CSI 的終端可能解讀成控制序列(改標題或畫面);不能執行碼。另外 `{base}` 路徑與 `claude` stderr 第一行也未剝控制字元,風險同級。

逐類:
1. 不可信輸入流到危險操作:路徑注入見 F1、F2;`--session` 已改正規式(首字元英數,擋 `..`、絕對路徑、空字串、換行),已看,無穿越;命令與 shell 已看,無(全為 list 形式,無 shell=True);反序列化只有 json.loads,已看,無。
2. 登入與權限:已看,無。
3. 密鑰與個資:本 diff 無新增 log 秘密;錯誤訊息只取 claude 輸出第一行;事件帳內容讀取端原樣輸出屬 F1;寫入端(mods)不在本 diff,⚠ 未審。
4. 加密與傳輸:已看,無。
5. 執行邊界:hook 與 enforcement 新增段只做 git rev-parse 與 stat,不執行 repo 內檔案、不呼叫 claude;外掛來源是 `_lumos_src()` 而非 vendored 或 cwd 路徑;`_py_which` 仍拒相對 PATH 項,Windows 擋 cwd;陌生 repo 的專案設定經實測進不了市集或外掛列表,不會影響同名判斷;`_sync_claude_plugin` 在同名市集來源不是本機資料夾時拒動(fail closed);測試端有全域假 HOME 隔離(`scripts/test_lumos.py:430` 的自檢),不會寫真機;LUMOS_HOME 見 F3。
6. 行動端:已看,無。
新增依賴:無。

前輪修復驗收(r1 資安席):
- F1 終端跳脫序列注入:文字輸出路徑已修(`_events_clean` 剝 C0、DEL、C1);--json 與路徑類輸出未涵蓋,見本輪 F4。
- F2 --session 路徑穿越:已修,正規式加上 `fullmatch` 與 `is_symlink` 檢查,實讀確認 `..`、絕對路徑、尾端換行都擋得住。
- F3 --prune 上層連結:部分已修,新增 `_events_path_safe` 逐層檢查符號連結;git-common-dir 導向未擋,見本輪 F2。
- F4 市集信任錨:部分已修,已 resolve、同名非本機市集拒動、失敗有提示與手動指令;未拒絕 repo 內來源,見本輪 F3。

總結:最嚴重 minor,blocking 0 條
