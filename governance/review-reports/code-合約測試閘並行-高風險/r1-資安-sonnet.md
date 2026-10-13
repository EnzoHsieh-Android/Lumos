severity: minor

我站在攻擊者角度看過整份 diff。能被利用的洞沒有找到,下面只有一條縱深防禦類的 finding。

1. 惡意 repo 的設定檔可自行放大並行度(縱深防禦,推論)
severity: minor
blocking: 否
引句:「if isinstance(v, int) and not isinstance(v, bool) and 2 <= v <= 16:」
file: `scripts/lumos:48150-48250`(新增 `_bound_tests_parallel` 與 `_run_bound_tests` 的並行段,位置取自 diff 的 hunk)
1. 誰:提供惡意 repo 的人。
2. 入口:陌生 repo 裡被提交的 `.lumos/config.json`。
3. 送什麼:`"bound_tests": {"parallel": 16}`。
4. 拿到什麼:推送閘最多同時開 16 支測試程序。這只是放大已有的行為,沒有新的執行能力。
5. 為什麼只算 minor:同一份設定檔裡的 `platforms.*.run_cmd` 本來就會被 `_kill_run` 當指令執行(`cmd = _run_cmd_expand(run_cmd, …)`,diff 的上下文可見)。能寫設定檔的人原本就有任意碼執行,`parallel` 沒有加出新的攻擊面。
6. 沒有能當場翻紅的重現,所以是推論。

各類逐項判定
1. 命令、路徑、模板注入與反序列化:已看,無。
   - `parallel` 只經過 `isinstance(int)` 且在 2 到 16 之間的檢查,不會進入任何指令字串。
   - 並行改動沒有改 `cmd` 與 `root` 的組法,仍是原有的 `_run_cmd_expand` 加 `_kill_run`,去重鍵 `(root, cmd)` 也沒變。沒有新增 shell 插值。
   - 序列化原本保護的東西:每支測試仍有各自的程序群組與暫存輸出檔,diff 沒有引入共用的可寫狀態。`seen` 與 `errs` 都在鎖裡寫。
   - 兩個同 `root` 的測試同時跑,可能互相踩該目錄下的產物。這是正確性問題,不是權限問題,歸其他席。
2. 登入與權限:已看,無。
3. 密鑰與個資:已看,無。新的 stderr 提醒會把設定值原樣印出,但用的是 `{v!r}` 和 `{bt!r}`。repr 會把 `\x1b` 之類的控制字元轉成跳脫序列,所以惡意 repo 無法靠這個往終端注入 ANSI 序列或偽造輸出。印出的內容只有 `parallel` 與 `bound_tests` 這兩個欄位本身,不含密鑰。
4. 加密與傳輸:已看,無。
5. 執行邊界:已看,無新增。
   - 打開陌生 repo 時,該 repo 的 `.lumos/config.json` 透過 `parallel` 只能調並行度(上限 16),不能繞過任何檢查。判紅綠、逾時、跑過證據和去重在 diff 中都沒動。
   - 錯誤路徑上,例外會往外丟,是偏嚴(fail-closed)。並行段只在 `workers > 1` 時走,出錯時 `raise errs[0]`,不會變成假綠。
   - `_bound_tests_parallel` 讀設定失敗時回 1,等於循序,不會放寬任何檢查。
   - 閘的決定沒有用到 `secs_kind` 或牆上時間,所以 secs 改成牆上時間不會讓某道檢查被繞過。
   - 測試檔裡真的會被 CI 執行的部分:都用 `tempfile.mkdtemp` 搭配固定的 `sys.executable` 與測試腳本。沒有把外部輸入拼進 shell 命令,`_sp.run` 都是 list 形式。
6. 行動端:已看,無。

新依賴:無。用的是標準函式庫 `threading` 和 `queue`,沒有新增依賴。

總結:最高等級 minor
