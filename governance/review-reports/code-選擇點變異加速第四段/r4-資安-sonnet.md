severity: minor

我只對這份凍結 patch 的程式與測試段(`scripts/lumos`、`scripts/test_lumos.py`)逐行查過,並對照 HEAD `c5be145a2` 的 `_run_cmd_expand`、`_isolated_worktree`、`_WIN_CMD_SPECIAL`。三類都沒有可利用的洞,只有一條縱深防禦類的提醒。

**本輪特別想的問題:「含 {method} 的那一段緊接殼層元字元就判形狀不支援」**
- 這一步只會讓工具更保守。它在 `_choice_merge_shape` 裡多一個回 `None` 的條件,回 `None` 就是不合併、照舊逐支跑。
- 沒有任何寫法因此更容易被殼層插值。合併指令的組法沒變:每支測試名仍經 `_run_cmd_expand` 的 `_cmd_arg_quote`(POSIX 用 `shlex.quote`,Windows 用 `list2cmdline`,並先擋掉 cmd.exe 特殊字元)。
- 本輪新抽出的 `_cmd_arg_quote` 是把原本兩處內嵌的引號寫法原樣搬過來,沒有改變行為。

severity: minor
blocking: 否
引句:「if any(ch in seg for ch in "&;|<>"):   # 含 {method} 的那一段緊接殼層元字元」
這條是縱深防禦,攻擊路徑寫不完整,標「推論」。
- 這份擋字清單只列 `&;|<>`,沒有 `` ` ``、`$(`、`(`、`)`、`\`、`^`、`%`。形如 `--tests={method}$(cmd)` 的一段仍會被判成可合併。
- 合併時該段會對每支測試名各重複一次,`$(cmd)` 就被執行 N 次。
- 誰=寫 `run_cmd` 的人,也就是專案設定檔作者;從哪=專案設定檔;送什麼=帶命令替換的 `run_cmd`;拿到什麼=原本就拿得到的殼層執行,只是次數變多。
- 缺「拿到新權限」這一件:逐支路徑本來就用 `sh -c` 執行同一個 `run_cmd`,所以沒有跨過新的邊界。
- 若要順手收緊,可以改成白名單(只允許 `[A-Za-z0-9_.=-]` 加 `{method}`)。不改也沒有新增風險。
file: `scripts/lumos:28806`

**① 提示注入:已看,無。**
- 新增的事件行解析(`_choice_merge_event_line`、`_choice_merge_events`)吃 Gradle 輸出,結果只拿去重排逐支順序,不判任何事。
- 解析出的名字必須對得上 `lane`(守衛測試名單)才會進 `merge_failed` 和 `merge_back`,輸出裡的自由文字不會進派工詞或 hook 附加段。
- `merge_init_off`、`unclean` 寫進治理帳的值都是程式內的固定字串常數(`_CHOICE_MERGE_NO_RESULTS_WHY`、`_CHOICE_MERGE_HANG_WHY` 等),沒有外來文字。
- 印到終端的訊息仍經 `_kill_esc`。

**② 讀寫與執行越界:已看,無。**
- 事件初始化腳本寫在 `tempfile.mkdtemp` 建的 0700 暫存目錄(`scratch`)裡,檔名固定(`lumos-merge-events.init.gradle`),不在 repo 內、不跟隨外來路徑。
- 腳本內容是程式內常數(`_CHOICE_MERGE_INIT`),沒有插值外來字串。
- `--init-script <路徑>` 經 `_cmd_arg_quote` 加引號;Windows 路徑若含 `_WIN_CMD_SPECIAL`(`&|<>^%"!`)就放棄,不帶腳本。
- 新增程式沒有下載、沒有環境變數覆蓋來源、沒有密鑰或信箱。
- 測試檔段我也掃過,沒有真能用的憑證,也沒有新的外部輸入命令拼接。

**③ 非刻意的一步繞過:已看,無。**
- 沒有新增任何 `LUMOS_SKIP_*` 或環境變數入口。
- 新增的跳開與恢復邏輯(`_kill_merge_note_unclean`、`_kill_merge_trip`、`hang_streak`)只影響快篩要不要啟用,不會讓任何壞法被記成「存活」而繞過守衛。
- 重試路徑(帶腳本不通過時不帶腳本重跑)只在原因恰為「找不到 JUnit 結果檔」時觸發,通過後仍走同一套 classify,不會因此放寬判定。
- 治理帳新增的 `merge_init_off` 已加進 `_GOV_FIELD_TYPES` 的型別檢查。

最高 minor,blocking 0 條
