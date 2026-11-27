severity: minor

審查範圍:只看資安三類。`scripts/lumos` 新增的 `_KillCompile` 等合批編譯段、跳過集合(`_choice_skip_read`、`_choice_invalid_live`)、`on_invalid` 與 `audit_done` 寫帳段,以及測試與文件的新增處都讀過。實驗未另跑,結論來自讀 diff 加讀 repo 現況。

**①提示注入:已看,無。**
- 編譯器輸出只被 `_CHOICE_COMPILE_ERR_RE` 抽成(路徑、行號)去比對,不原文回顯。
- 印出的訊息裡的 `loc`、`row`、`plat`、例外類名都有包 `_kill_esc`。
- `_kill_run` 回傳的輸出另有截斷標記,被截斷時 `_choice_compile_errors` 回 None,一律不記無效。
- 帳事件欄位(`file`、`fp`、`new_sha`、`row`、`blob`)只當 dict 鍵與集合比對,不進派工詞或 hook 附加段。`row` 只在 `on_invalid` 印出時經 `_kill_esc`。

**②讀寫與執行越界:無可直接利用的洞,有一條縱深防禦。**
- 編譯指令的組法:`run_cmd` 本來就以 `shell=True` 執行,而且來自 repo 內的 `.lumos/config.json`。`_choice_compile_cmd` 只做三件事:
  - 把任務名換成 `compile<變體>UnitTestKotlin`,變體只吃 `[A-Z][A-Za-z0-9]*`。
  - 模組名走 `re.escape`。
  - 其餘字串照搬原文。
  - 沒有新增 shell 插值面。
- 編譯錯誤路徑:路徑只拿去做 `os.path.realpath` 與 `startswith(wt_real + os.sep)`,再轉成相對路徑放進集合,沒有拿去開檔或寫檔。越界路徑只增加 `stray` 計數。`file://` 的 `%2e%2e` 之類先 `unquote` 再 `realpath`,也不會跑到樹外。
- 套壞法與還原寫檔:寫入目標 `target` 取 `realpath` 並要求在 `wt_real` 之內,還原用 `git checkout -- :(literal)<相對路徑>`。
- 殘留一條縱深防禦(推論):`wt_real` 之內的目標若是指向 `.git/` 內檔案的捷徑,`startswith` 擋不住。這要 repo 作者自己刻意放捷徑,又要讓壞法的 `old` 文字剛好對上,屬於範圍外的刻意多步偽造。

severity: minor
blocking: 否
引句:「target = os.path.realpath(os.path.join(self.c.wt, r.get("file", "")))」
這一句之後只檢查 `startswith(self.c.wt_real + os.sep)`,沒檢查目標是不是落進工作樹自己的 `.git/`。攻擊路徑是推論:誰=repo 作者本人;從哪=在受審檔放一個指向 `.git/hooks/*` 或 `.git/config` 的捷徑;送什麼=讓壞法 `old` 對上目標內文;拿到什麼=合批編譯寫檔時改到版控設定。前提是隔離樹是完整 clone,不是 linked worktree。我沒有確認隔離樹實際怎麼建,所以只標縱深防禦。建議的補強是在 `units()` 加一條「真實路徑不在 `.git` 底下」。

**③非刻意、一步就能繞過的守衛:已看,無可直接利用的洞,有一條推論。**
- 誰=使用者或照常操作的 AI;從哪=推送前閘或 `choice-points`;送什麼=帳上已有的 invalid 事件;拿到什麼=該存活行被判 `exhausted`(不擋、不跑)。
- 偽陽性無效判定要同時成立:原樹先編綠、這一批編紅、錯誤落在壞法改的行範圍內、單獨再編仍紅。環境不穩造成的紅,在原樹對照組那一步就被擋成 `env`。
- 逾時、輸出被截斷、單獨編綠都不記無效。這幾條都是失效開放,但屬於預期的保守方向。
- 殘留的間隙:跳過集合只比對「該檔的 blob」。別支檔改了而使舊無效候選其實能編了,推送閘仍照帳跳過它,要等下一次 `choice-kill` 的探針才補償。若同一行候選全在集合裡,該行就變 `exhausted`,推送閘不擋。這是計劃明載的設計(失效開放,檔改了重驗),觸發要先有真的無效事件。我把它標成推論、minor。

severity: minor
blocking: 否
引句:「live = {ns: e for ns, e in last.items() if not e.get("cleared")}」
攻擊路徑是推論:誰=使用者;從哪=只改別支檔(例如修正 API 簽章)再推送;送什麼=帳上同一 blob 的舊 invalid 事件;拿到什麼=該行在推送閘被判「沒有可用壞法」而不被要求處置,直到有人再跑 `choice-kill`。

**未發現問題的其他項**
- 密鑰與信箱:未新增。
- 安裝腳本與下載來源:這次未動。
- 環境變數:新增的 `CK_COMPILE` 與 `CK_MARK` 只在測試的假 gradle 裡,不是產品碼路徑。
- 新增的 `LUMOS_SKIP_*`:無。

總結:最高等級是 minor(兩條,均為推論性縱深防禦)
