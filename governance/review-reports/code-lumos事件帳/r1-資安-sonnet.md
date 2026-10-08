severity: minor

審視範圍:r1-snapshot.patch 的 scripts/lumos 部分(測試檔與 skills 文件只掃過,未見命令拼接或外部輸入流入)。外掛本體(mods/claude/lumos-ledger、.claude-plugin/marketplace.json)不在此 diff,這個 worktree 裡也不存在,所以「外掛寫入端記了什麼」未審,標 ⚠。

### F1 事件帳內容原樣印到終端(跳脫序列注入)
severity: minor
blocking: 否 — 只能影響終端顯示,沒有執行或外洩,屬縱深防禦
引句:「print(f"  {e.get('ts', '?')}  {who}{e.get('ev')}  {detail}{ok}")」
攻擊路徑:攻擊者在公開 repo 用 git add -f 提交 governance/runtime/events/x/a.jsonl,v 欄位寫 1,agent、tool、ts 欄位塞 ANSI/OSC 跳脫序列。受害者 clone 後在該 repo 跑 `lumos events --session x`,或會談資料夾名本身含跳脫字元,會被 `_events_sessions` 的 `print` 原樣印出。拿到:偽造或覆蓋終端輸出、改視窗標題,不能執行碼。init 只在新建 governance/.gitignore 時才寫 runtime/,既有 repo 不保證有忽略,但強制提交不受 .gitignore 影響。
file: `scripts/lumos:18213`

### F2 --session 未限制為單層資料夾名(路徑穿越讀取)
severity: minor
blocking: 否 — 只讀、只列 .jsonl 中 v 為 1 的 dict 行,攻擊者必須能控制使用者給的參數(推論,屬縱深防禦)
引句:「d = base / session」
攻擊路徑:推論:被提示注入的 AI 或腳本替使用者跑 `lumos events --session ../../../some/dir --json`(絕對路徑會直接取代 base),會讀任意目錄下的 *.jsonl 並印出。`_events_read` 內也是 `_events_root(root) / _EVENTS_REL / session`,同樣沒擋。拿到:讀取任意目錄的 jsonl 事件行;如果記到的 Bash 前 500 字含密鑰,這支指令的 --json 會原樣吐出(R16 縱深)。建議 session 只接受 `^[\w.-]+$` 且不含 `/`、`..`。

### F3 --prune 只檢查最後一層是否為符號連結
severity: minor
blocking: 否 — 要使用者在陌生 repo 主動下 --prune,且目標路徑需剛好吻合,條件苛刻(推論)
引句:「if not base.is_dir() or base.is_symlink():」
攻擊路徑:推論:陌生 repo 把 `governance` 或 `governance/runtime` 做成指向受害者其他目錄的符號連結(連結本身是 git 允許的內容),使 base 這個最後一層是真資料夾,而上層被導走。受害者在該 repo 跑 `lumos events --prune`,`shutil.rmtree` 會刪掉那個目錄下超過 30 天的子資料夾。另外 `_events_root` 信 `git rev-parse --git-common-dir` 的結果,陌生 repo 的 .git 檔可把它導到別的 repo。拿到:刪除受害者另一個目錄裡名為 events 之下的舊子資料夾,範圍受限。建議對 base 先 resolve 後確認落在 repo 根之下再刪。
file: `scripts/lumos:20277`(`_events_prune` 在 diff 內約 20430 行附近,以 patch 為準)

### F4 uninstall 與 sync 會移除使用者自己加的同名本機市集
severity: minor
blocking: 否 — 只動名為 lumos-toolchain 的 directory 型市集,沒有跨界或提權,屬資料完整性縱深
引句:「_claude_do(claude, ["plugin", "marketplace", "remove", _LEDGER_MARKET, "--scope", "user"])」
攻擊路徑:推論:使用者已有名叫 lumos-toolchain、指向另一個資料夾(例如自己的 worktree)的 directory 市集。`lumos install` 發現路徑與 `_lumos_src()` 不同就先 remove 再 add,等於用 LUMOS_HOME 所指的來源取代它,並連帶使從舊市集裝的外掛失效。攻擊者能控制 LUMOS_HOME 環境變數時,可把使用者全域市集換成攻擊者資料夾,然後 `claude plugin install` 就把該資料夾的 hook 或 mod 登記成使用者全域外掛。LUMOS_HOME 屬使用者環境,威脅模型上等同本機已被攻陷,故不升級;但這是新增的「寫進全域設定的信任錨」,也沒有對來源路徑做檢查,例如要求為絕對路徑、不在目前 repo 之內。順帶:LUMOS_HOME 若設成相對路徑,`str(src)` 會以相對路徑傳給 `marketplace add`,由 claude 以目前目錄解讀,在陌生 repo 內跑 install 可能解成該 repo 內的資料夾。建議對 src 做 resolve,並拒絕落在目前 git repo 工作樹內的來源。
file: `scripts/lumos:17631`

逐類結論:
1. 不可信輸入流到危險操作:路徑注入見 F2、F3,終端輸出見 F1。命令與 shell 已看,無:所有 subprocess 呼叫都是 list 形式,無 shell=True,`claude` 回傳的 JSON 只用於比對 name、source、path、id,path 只做 realpath 比較,不拿來執行或寫入。反序列化已看,無:只有 json.loads,沒有 pickle 或 yaml.load。
2. 登入與權限:已看,無。
3. 密鑰與個資:事件帳記 Bash 指令前 500 字,可能含密鑰。寫入端不在本 diff,⚠ 無法確認有無遮蔽。讀取端 `--json` 會原樣印出整個事件。init 只在新建 governance/.gitignore 時加入 runtime/,既有 repo 已有 gitignore 者不會補,可能被提交,建議加補寫規則。錯誤訊息只取 claude stderr 第一行,沒帶秘密。
4. 加密與傳輸:已看,無。
5. 執行邊界:`_sync_claude_plugin` 的來源用 `_lumos_src()`(固定為 `LUMOS_HOME` 或 `~/harness/lumos-toolchain`,不是專案 vendored 的路徑,所以陌生 repo 的 scripts/lumos 登記不到自己的資料夾),且 `source` 參數目前沒有呼叫端傳入。`_py_which` 已拒絕相對路徑 PATH 項,假 `claude` 要先控制 PATH,屬本機攻陷。打開陌生 repo 時,hook 或 enforcement 只呼叫 `_events_root` 的 `git rev-parse` 與 stat,不執行 repo 內檔案,也不呼叫 `claude`,可接受。`enforcement_status` 新增段落只讀 mtime。授權範圍:新增 `--scope user` 的全域登記,見 F4。
6. 行動端:已看,無。
新增依賴:無。

總結:最高 severity 為 minor,blocking 條數 0(共 4 條,全為縱深防禦)。
