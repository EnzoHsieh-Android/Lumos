severity: clean

已看,無可利用的洞。逐類結果如下。

1. 測試執行面:已看,無。
   - 符號連結與硬連結都建在 `mkvault()` 的暫存目錄內(`sym.symlink_to(real.name)`、`_os.link(real, hard)`、`clog.symlink_to(target.name)`、`external`/`broken`),沒有指向測試目錄外。
   - 被換掉的全域狀態都放在 `finally` 還原:`builtins.open`、`sys.argv`、`Path.read_bytes`、`lm._vault_write_lock`。
   - 持鎖子程序用 `subprocess.Popen([sys.executable, "-c", helper, ...])`,是參數陣列、沒有 `shell=True`,路徑以 argv 傳入、沒有拼進指令字串。helper 自己 `sleep(.4)` 就結束,測試最後 `proc.wait(timeout=5)` 收掉。
   - 可補強但不構成洞(推論,影響有限):`run(...)` 若在 `wait` 之前丟例外,子程序不會被主動收掉,但它 0.4 秒後會自己退出。
   - 這輪反而拿掉了把 `git show HEAD:scripts/lumos` 寫成檔再 `exec_module` 的舊做法,少了一條動態載入路徑。
   - `_QFM_UNICODE16_DICP_RANGES_TEXT` 是用 `int(…,16)` 解析的固定常數,沒有 `eval`、反序列化或 `yaml.load`。
2. 筆記是否誘導代理做危險動作或藏看不見字元:已看,無。
   - 對 patch 掃了零寬、雙向控制、BOM、軟連字號等字元,只在第 44 行的刪除行命中,內容是 `❤️‍🔥` 的合法 ZWJ 說明。
   - 三篇筆記的新增行都是設計規則與回顧紀錄,沒有叫代理執行指令、改設定或外送資料的句子。
3. 密鑰與個資:已看,無。
   - 只有 `evil\x1b[2J` 這種明顯的假資料。
   - 測試產物裡沒有 token 或密碼。
4. 執行邊界:已看,無。
   - 沒有 `expanduser`、`Path.home`、`~/.cache` 或 `~/.claude` 的寫入。
   - 寫入都落在 `mkvault()` 與 `_mk_spec_gate_repo` 的暫存目錄。
   - 唯一讀 repo 的是 `(repo / "docs").rglob("*.md")` 的唯讀掃描,沒有寫入。
   - 第 921 行的 `_fc_git(root, "add", …)` 的 `root` 是測試自建的暫存 repo。
5. 其他:已看,無。
   - 第 783 行附近用 lambda 取代 `builtins.open`,只比對 `plog`,其餘轉給 `real_open`,而且只在測試行程內有效。
   - 這輪沒有新依賴。

總結:這份 patch 的測試檔與三篇筆記都沒有能被利用的洞,全部暫存與全域狀態的處理都在合理範圍內。
