severity: clean

沒有可利用的洞。以下是 1197 行快照全部看過後的結論,凍結 patch 裡的程式、測試、筆記都含在內。

**①提示注入:已看,無。**
- 被測專案輸出的事件行,經 `_choice_merge_event_line` 與 `_choice_merge_events` 解析後,只會回傳「呼叫端自己傳進去的 `names` 裡的名字」。
- 這些名字只拿去排逐支順序(`merge_failed`、`merge_back`),不進派工詞、hook 附加段或指令。
- 帳上新欄位 `merge_init_off` 的值來自程式常數(「找不到 JUnit 結果檔」),不含外來文字。
- 印出的平台名都先過 `_kill_esc`。
- 守檔筆記新增的 PITFALL 行有 `[repro:_choice_merge_events("x.V > foo (bar) FAILED", ...)]`。我 grep 過 `scripts/lumos`,`repro` 只出現在提示字串與格式檢查裡,沒有任何地方會把它當指令執行,所以只是文字。

**②讀寫與執行越界:已看,無。**
- **初始化腳本的路徑與內容**:
  - 內容是常數 `_CHOICE_MERGE_INIT`,寫的位置是 `<scratch>/lumos-merge-events.init.gradle`。
  - `scratch` 是 `_isolated_worktree` 用 `tempfile.mkdtemp` 建的上層資料夾,權限預設 0700,檔名固定且在自己剛建的資料夾內。
  - 沒有「照著外來路徑寫檔」或「捷徑跟過去」的入口。
  - 就算被測專案的測試能改這個檔,它本來就以同一使用者身分執行任意碼,沒有新增權限。
- **`_cmd_arg_quote` 的引號**:
  - POSIX 用 `shlex.quote`,安全。
  - Windows 用 `subprocess.list2cmdline`,跟舊版 `_run_cmd_expand` 對 `{python}`、`{method}` 的寫法一致,只是抽成共用函式。
  - `list2cmdline` 本身擋不住 cmd.exe 的特殊字元,但 `_choice_merge_init_path` 在 Windows 上先用 `_WIN_CMD_SPECIAL`(`&|<>^%"!`)把含這些字元的路徑擋掉、改成不帶腳本。該常數我在 `scripts/lumos:6507` 查過。
  - `--init-script` 只插在 `--tests` 段之後、原字串其餘部分之前,不改變既有的 shell 邊界。
- **密鑰與信箱**:新增內容裡沒有。測試檔的假 Gradle 與暫存資料夾都在自己的 `mkdtemp` 底下。
- **下載來源與環境變數覆蓋**:沒有安裝腳本或下載。PRIOR-ART 的網址只出現在筆記文字裡。

**③非刻意、一步就能繞過的守衛:已看,無。**
- 腳本被 Gradle 拒收時,會不帶腳本重試一次,並照剩餘總時限重算上限,只在「找不到 JUnit 結果檔」這一種失敗才重試。
- 這是退化到原本的合併行為,不是放寬任何守衛。
- 事件行只影響排序,不影響判定。判殺掉、存活仍由逐支或合併結果檔決定。
- 偽造事件行最多改變斷路器是「另外數 15 次」還是「照舊數 5 次」。製造這種輸出的是被測專案自己的測試,它本來就能執行任意碼,不構成越界。
- 沒看到會被 `LUMOS_SKIP_*`、`PYTHONPATH`、Ctrl-C 或合併提交這類非刻意狀態意外走過的新守衛。訊號與時限的處理(`_KillHalt`、`mg.interrupted`)沿用既有寫法,新程式只是沿用。

最高 clean,blocking 0 條
