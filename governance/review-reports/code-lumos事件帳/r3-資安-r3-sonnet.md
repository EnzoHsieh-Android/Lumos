severity: minor

審視範圍:r3-snapshot.patch 的 `scripts/lumos` 部分(646 行),對照 repo 內 `_lumos_src`、`_py_which`、`_lens_git`、`_esc_clean`、`_PATH_SPECIAL_CATS`。測試檔與文件只看會被執行的部分。
我在臨時目錄做了一個唯讀實驗:`.git/commondir` 指向別的 repo 時,`lumos events --prune` 會擋下,什麼都沒刪。
沒有跑任何 `claude plugin` 子指令,也沒有改 repo 任何檔。

### F1 讀取端沒走 `_events_path_safe`,上層符號連結會被跟著讀
severity: minor
blocking: 否 — 讀到的是受害者自己的資料、只顯示給受害者本人,攻擊者拿不到輸出,屬縱深防禦(推論)
引句:「if not d.is_dir() or d.is_symlink():」
攻擊路徑:誰:公開 repo 的作者。從哪:用 git 提交 `governance/runtime/events` 當成符號連結,指向受害者機器上別專案的事件帳。送什麼:受害者在該 repo 跑 `lumos events`、`--session x` 或 `--json`(或讓 AI 代跑)。拿到什麼:`_events_read` 與 `_events_sessions` 只檢查會談資料夾與塊檔是不是連結,`base` 上層的連結會被跟著走。別專案的會談編號、時間、工具名,以及 `--json` 模式下整行事件欄位,會印進終端或 AI 對話。攻擊者本人看不到輸出,所以只是誤導或把別處資料帶進受害者的對話。`governance/runtime/` 在 `.gitignore:34`,攻擊者得用 `git add -f` 才能提交。`--prune` 路徑已有 `_events_path_safe`,讀取端沒有同一道。
file: `scripts/lumos` 的 `_events_read`、`_events_sessions` 與 `cmd_events` 讀取分支(patch 第 347–400 行附近)

### F2 `{base}` 路徑在兩處文字輸出沒經 `_events_clean`
severity: minor
blocking: 否 — 要靠壓縮包內的資料夾名帶控制字元,且受害者自己的終端本來就會顯示那個路徑,只影響顯示(推論)
引句:「print(f"沒有事件帳:{base} 不存在或是空的。")」
攻擊路徑:誰:散布 repo 壓縮包的人。從哪:包內資料夾名含 ESC 或 U+009B 序列,或用 `.git/commondir` 把主 checkout 導到這種名字的資料夾。送什麼:受害者在該目錄跑 `lumos events`。拿到什麼:`沒有事件帳:{base}` 與 `最近 N 個會談(事件帳在 {base})` 兩行把路徑原樣印出,控制序列可改寫終端標題或畫面,不能執行程式。r2 F4 提到的 `{base}` 沒清這一點,在這兩行仍未修;`--prune` 擋下訊息已經有清。
引句:「print(f"最近 {len(rows)} 個會談(事件帳在 {base}):")」

## 逐類
1. 不可信輸入流到危險操作:
   - `--session` 用 `fullmatch` 的正規式,首字元必須是英數,加上 `is_symlink` 檢查,路徑穿越已看,無。
   - `--days` 只收 ASCII 數字、上限 36500、不收前導零,已看,無。
   - `shutil.rmtree` 只對 `base` 的直接子資料夾,連結一律跳過;`rmtree` 本身不跟連結。
   - 所有子行程都是 list 形式,無 `shell=True`;反序列化只有 `json.loads`,並接住 `RecursionError`。已看,無。
   - 讀取端見 F1。
2. 登入與權限:已看,無。`uninstall` 與 `teardown` 只動 `--scope user`;專案範圍那份不碰。
3. 密鑰與個資:
   - 讀取端的文字輸出只印 `ts`、`agent`、`tool`、`reason`、`origin`、`agent_type`,且經過清理。
   - `--json` 會原樣輸出整行事件;事件內容由寫入端 mod 決定,mod 不在本 diff,⚠ 未審。
   - 事件帳目錄在 `.gitignore:34`,預設不入庫。
   - 外掛錯誤訊息只取 `claude` 輸出的第一行,並經 `_events_clean`。已看,無新增洩漏。
4. 加密與傳輸:已看,無。
5. 執行邊界:
   - `_events_main_trusted` 能不能被偽造的 gitdir 檔騙過:
     - 騙不過導向受害者的情況。實驗中 `.git/commondir` 指向別的 repo,因為受害者的 `.git/worktrees` 沒登記攻擊者的目錄,所以擋下。
     - 偽造要成功,必須同時控制「主 checkout」與它底下的 `worktrees/*/gitdir`。這樣導到的是攻擊者自己的目錄樹,刪不到受害者資料。
     - `root == main_root` 的短路是同一個目錄,安全。
   - `_events_path_safe` 的最後一行 `resolve().is_relative_to` 對 `base = main_root/_EVENTS_REL` 恆真,只剩逐層連結檢查有效。這是冗餘,不是洞。
   - hook 與 enforcement 新增段只做 `git rev-parse`(3 秒逾時)與 `stat`,不執行 repo 內檔案。
   - 外掛路徑:
     - `_py_which` 拒相對路徑項。
     - 市集來源是 `_lumos_src().resolve()`,來源不是預設位置時會印出;同名非本機市集 fail closed。
     - r2 F3 提的「拒絕落在使用者可寫位置或 repo 內」仍未做,威脅模型仍需能控制 `LUMOS_HOME` 或 `--source`,等同本機已被控制,不重報。
     - `_sync_global_hooks(src_repo, ...)` 呼叫 `_sync_claude_plugin()` 時沒傳 `src_repo`,外掛市集來源與 hook 來源可能不同(取自 `LUMOS_HOME` 或預設),但攻擊者沒有路徑去改這兩者,無可利用路徑。
   - `bootstrap` 傳給子行程的 `LUMOS_HOME=str(home)` 是自己 clone 的目錄,已看,無。
6. 行動端:已看,無。
新增依賴:無。

## 前輪修復驗收(r2 資安席)
- F1 塊檔符號連結:已修,塊檔現在 `is_file() and not is_symlink()`,與 prune 一致;但事件帳上層連結的讀取端仍沒擋,見本輪 F1。
- F2 git-common-dir 導向:已修,新增 `_events_main_trusted`,實驗確認偽造 commondir 導向別的 repo 時整個擋下、零刪除。
- F3 市集來源信任:部分修,來源不是預設位置時會印出,仍未拒絕可寫或 repo 內位置,威脅模型屬本機已被控制,維持不報。
- F4 `--json` 與路徑輸出的控制字元:`--json` 一律 ASCII 已修;`{base}` 路徑在兩處文字輸出仍未清,見本輪 F2。

總結:最嚴重 minor,blocking 0 條
