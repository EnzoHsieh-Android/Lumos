severity: clean

這份 diff 沒有能被利用的洞。我只讀了 patch 裡 `scripts/lumos` 的程式部分,並對照 repo 的 `_WIN_CMD_SPECIAL`。測試檔與筆記沒有逐行讀,但全文搜過,沒看到真實憑證、信箱或 shell 拼接。

**特別問題:Gradle 初始化腳本**
1. **路徑能不能被外來輸入影響**:不能。路徑是 `<scratch>/lumos-merge-events.init.gradle`。`scratch` 來自 `_isolated_worktree` 的 `tempfile.mkdtemp(prefix=prefix)`,檔名是常數。事件行、檔名、分支名、筆記內容都進不到路徑。
2. **寫入前後能不能被換掉**:攻擊路徑填不出全四件。
   - 上層資料夾由 `mkdtemp` 建,權限 0700,同機其他使用者放不進符號連結或換檔。
   - 唯一能動它的是被測專案自己的測試程式,它能寫 `../lumos-merge-events.init.gradle`。
   - 但這份測試碼本來就在同一使用者、同一程序樹下由 Gradle 執行,換掉腳本沒有多拿到任何東西。
   - 這一點屬於縱深防禦,標「推論」,不報為 finding。
3. **加引號會不會被路徑內容打破 shell**:不會。
   - POSIX 用 `shlex.quote`。
   - Windows 用 `list2cmdline`,而且 `_choice_merge_init_path` 在路徑含 `&|<>^%"!`(`_WIN_CMD_SPECIAL`)時直接不帶腳本。這 8 個字元就是 cmd.exe 會誤解的那組,所以含 `%` 或 `^` 的使用者名稱走不到 `--init-script`。
   - 路徑插在 `--tests` 段之後,`cmd[shape["e"]:]` 之前,不會切破原字串的引號。
4. **腳本內容**:是固定常數 `_CHOICE_MERGE_INIT`,只開 `testLogging` 事件,沒有字串插值。

**事件行從測試輸出讀進來,能不能讓工具越界**:不能。
- 事件行只經 `_choice_merge_events` 轉成 `failed`、`hung`、`passed` 三份名單。名單的成員只取自 `names`(工具自己算出的 lane 名單),輸出裡的字串不會原樣進入名單。
- 這三份名單只用來排逐支順序。
- 沒有任何事件行文字被印出、寫檔、進派工詞或進 shell。
- 輸出經 `_kill_cap` 截斷,正則是 `fullmatch` 且行首不得空白。
- 被測專案的測試能偽造頂格 `X > y STARTED`,結果只是讓逾時改計 `hang_streak`(15 次才跳開)並改變逐支順序。這不碰讀寫、執行、提示詞,也不是一步就能意外走過的守衛。計劃筆記〈風險〉節已自承這點(刻意偽造,屬範圍外,minor、blocking: 否)。

**三類逐類結論**
1. **提示注入**:已看,無。`merge_init_off` 的值是工具寫死的原因字串(「找不到 JUnit 結果檔」),平台名經 `_kill_esc`。測試輸出文字沒有流入給 AI 的文字或指令。
2. **讀寫與執行越界**:已看,無。
   - 寫檔只有 mkdtemp 私有資料夾裡的一個固定檔名,收尾整個刪掉;`--keep-worktree` 時跟現場一起留下,屬預期。
   - 沒有新增 hook 或安裝腳本,沒有下載來源或環境變數覆蓋。
   - 沒有新寫進程式、範本或公開文件的密鑰與信箱。
   - `scripts/test_lumos.py` 的新測試用 `tempfile.mkdtemp` 加假 Gradle,命令是固定字串。
3. **非刻意、一步就能繞過的守衛**:已看,無。
   - 帶腳本失敗時的重試只在原因是「找不到 JUnit 結果檔」時觸發,重試不帶腳本,不會讓閘提早放行,只是回到原本的不合併路徑。
   - 新欄位 `merge_init_off` 缺欄時讀成空字典,不會讓閘判斷出錯。
   - 這輪沒有新增環境變數開關(`LUMOS_SKIP_*` 之類),也沒有新增讓使用者能意外走過的路徑。

最高 clean,blocking 0 條
