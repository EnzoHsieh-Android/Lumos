severity: clean

我站在攻擊者角度逐類看過 r5-pkg-tests.patch(scripts/test_lumos.py 新增約 1300 行)。三類各舉出一條可利用的洞都不成立,所以不開槍。

## ① 提示注入:已看,無

- 測試失敗時 `check()` 的第三個參數會把 `r.stdout + r.stderr`、`adb.log`、`str(d)` 印給讀結果的 AI。這些內容全來自假 adb、假 trace_processor、假 java_heap_dump 和測試自己寫的 stability.json。
- 拿使用者真實日誌、真實裝置輸出或環境變數來印的路徑,我在 diff 裡找不到。
- 帶換行的「偽造的一行」是測試用的固定字串,用來驗證被審程式會把它壓成同一行。它只出現在失敗訊息裡,攻擊者控制不了。
- 這支 patch 沒有 `os.environ` 轉印。

## ② 讀寫與執行越界:已看,無

**暫存以外的寫刪**
- 所有檔案都寫在 `tempfile.TemporaryDirectory(prefix="gctl-ms-")` 底下。我跑完後確認 `$TMPDIR` 沒有殘留的 `gctl-ms-*`。
- 捷徑(symlink)案例的目標 `elsewhere` 也在 td 內。

**`_ms_orphans` 的 pgrep 加 kill(patch 第 1180 到 1186 行)**
- pattern 是 `{fake}/(driver|sleeper)` 或 `{fake}/(adb logcat)`。`fake` 是每次隨機的 `gctl-ms-xxxxxxxx/fake` 全路徑,別的會談或別支測試的程序命令列不可能含它。
- 不是 `pgrep -f driver` 這種裸字串,所以不會比到別人的程序。
- pgrep 不會比到自己。測試程序的命令列也不含 fake 路徑。
- 只送一般 `kill`(SIGTERM),沒有用 `pkill -f` 或萬用字元。
- 實跑 `python3.14 scripts/test_lumos.py -k android_memstab_collect` 得 133 passed、0 failed,約 2 分 22 秒。結束後 `pgrep -fl 'gctl-ms-'` 沒有結果,沒有孤兒。

**SIGHUP / SIGQUIT / SIGINT 會不會打到測試程序自己**
- 測試只對 `sp.Popen` 出來的那個 sh 腳本 pid 用 `p.send_signal(sig)`,沒有 `kill 0`,也沒有對程序群組送訊號。
- 被審腳本自己的群組殺法 `os.killpg(p.pid, SIGKILL)` 搭配 `start_new_session=True`,每個子程序都是獨立群組。file: `scripts/templates/android-stability-collect.sh:59-80`。所以腳本不會殺到測試程序所在的群組。
- 這個檔案不在我手上的 patch 範圍內。我是為了確認測試送的訊號不會外溢才讀它。

**全域設定、HOME、PATH**
- `_ms_collect_env` 設了 `GIT_CONFIG_GLOBAL=os.devnull`、`GIT_CONFIG_NOSYSTEM=1`、`XDG_CONFIG_HOME=<td>/fake/xdg-empty`。
- `ADB`、`TP`、`JAVA_HEAP_DUMP` 每次都指向假工具。所有跑腳本的呼叫都帶這組 env,所以不會打到真裝置。
- 只有 HOME 那條 `~/.config/git/ignore` 案例把 HOME 指到 td 內,而且只讀不寫。
- 假 git 放在 `<td>/gbin`,只有那一次 `sp.run` 的 PATH 前面塞它,不影響測試程序,也不寫入使用者設定。
- 假 adb 只往 td 內的 `FAKE_DIR` 寫 log 和計數檔。

**秘密外洩**
- `SECRET123`、`alice@example.com`、`Bearer` 都是測試假資料,用來斷言「不會落地、不會進失敗原因」。
- 測試沒有讀使用者環境變數去印。

## ③ 非刻意、一步就能繞過的守衛:已看,無

- 前置斷言:每個靠時間或狀態的案例都有獨立的「前置」`check()`,不成立就單獨紅,不會默默變成「測了但其實沒走到」。例子是 `ps_failed` 標記、`p.poll() is None`、`driver.log` 行數、`kill -TERM` 出現在 log。
- 靠時間的部分用 `_ms_wait_for` 輪詢條件,最多 30 秒,再加 `time.sleep(0.5)` 或 1 秒。ps_slow、term_slow、perfetto_slow 都由假 adb 的 flag 檔決定,不是靠偶然對齊。
- Big5 守衛:macOS 有 `zh_TW.Big5`,我實測 `LC_ALL=zh_TW.BIG5` 下 Python 回 `big5`,所以在 macOS 這條真的會跑。沒有該語系的機器(例如 Linux CI)會印出「略過」那行,不是靜默。這條只有警示價值,我不列為 finding。REVISIT 條件不在這批 diff 內,所以我不替它補條件。
- 孤兒檢查不是「紅了才收」。`_ms_orphans` 找到就 kill 並回 pid 清單,`assert not left` 會讓測試紅,同時不留孤兒給別支測試。

## 歸因與圖譜鏡頭

- 沒有 finding,所以不需要「歸因」欄。
- 我沒有跑修前 5fc4e715 的版本。因為沒有 finding,不需要對照兩版。
- 固定席節點判斷:這份測試 diff 只動 `scripts/test_lumos.py`。「測試假綠形態」的 ★INVARIANT★(還原翻紅釘要配前置斷言)在這批新測試裡正是靠「前置」`check()` 遵守的。其餘固定席(lumos-cli-read、guard-kill 等)不受影響,因為這批測試只呼叫 `_mb_run`、`_load_lumos_module` 這些既有輔助函式,沒有改 `scripts/lumos`。
- 殘留合約:派工詞說「算不出來」。我沒讀 residual-index.json,也沒對照問答列,這條無法回答,留給編排者。

最嚴重 severity:clean,blocking 共 0 條。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/code-android-mem-stability/r5-pkg-tests.patch`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/test_lumos.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/templates/android-stability-collect.sh`

我沒有在 `/tmp/lumos-seat-work/...` 建任何東西,所以沒有需要清的暫存。
