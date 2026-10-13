severity: minor

## 發現

### 1. `_bt_kill_proc` 的 `poll()` 檢查和 `killpg(getpgid(pid))` 之間有一個極窄的 pid 重用競態(推論)
severity: minor
blocking: 否
引句:「os.killpg(os.getpgid(proc.pid), _signal.SIGKILL)」

1. 誰:能在同一台機器、同一使用者下以高頻率 fork 的本機程序(或碰巧在跑的其他工作)。
2. 從哪裡:主流程在 `_settle_and_reap` / `reap()` 裡呼叫 `_bt_kill_proc`,工作執行緒同時在 `_kill_run` 裡 `communicate()` 收屍。
3. 送什麼:時序是主流程 `proc.poll()` 回 None(子程序還沒被收)之後、`getpgid` 之前,工作執行緒剛好 `wait()` 收掉它,pid 立刻被新程序重用。
4. 拿到什麼:`getpgid(pid)` 會取到新程序的群組,SIGKILL 打到不相干的程序群組。
5. 為什麼只標推論:
   - `killpg` 繞過 Popen 內部的 waitpid 鎖。
   - 子程序在被收之前是殭屍,pid 不會被重用。窗口只有 `poll()` 到 `getpgid` 之間「剛好被另一條執行緒收屍、同一瞬間 pid 被重用」,macOS 的 pid 遞增配置下實務上近乎不可能。
   - 攻擊者無法控制 pid 配置時序。
   - 打到的也只是同一使用者的程序,沒有跨權限效果。
6. 沒有重現,這條是理論上的縱深防禦。
7. 歸因:未判定。`_kill_run` 逾時路徑原本就有同樣的 `killpg(getpgid(proc.pid))`,只是少了 `poll()` 前置;這一輪新增了第二個呼叫點。
8. 縱深做法:改成 `os.killpg(proc.pid, SIGKILL)`。`start_new_session=True` 讓 pgid 等於 pid,不需要再查 `getpgid`。群組內只要還有成員,這個 pgid 就不會被重用。

## 逐類檢查

1. **不可信輸入流到危險操作**:已看。
   - `parallel` 只接受整數 2 到 16,其他值一律當 1。
   - 提醒訊息用 `{v!r}` / `{bt!r}` 印設定值,repr 會跳脫控制字元和 ANSI 序列,沒有終端逃逸注入。
   - `run_cmd` 組 shell 的路徑(`_run_cmd_expand`、`shell=True`)這份 diff 沒改。測試方法名與平台 root 的信任邊界和修補前一樣,屬於專案自宣告指令(同 CI 信任邊界)。
   - 這一輪沒有新增注入面。
2. **登入與權限**:已看,無。
3. **密鑰與個資**:已看,無。治理帳只新增 `secs_kind: "wall"`,提醒訊息只印 `parallel` / `bound_tests` 的值。
4. **加密與傳輸**:已看,無。
5. **執行邊界**:
   - **killpg 與 pid 重用**:見發現 1。
   - **測試檔用 pid 檔殺程序**:
     - `pids/` 在 `tempfile.mkdtemp`(0700)底下,由假測試自己寫入。另一個使用者無法放入檔名,檔名只用 `os.getpid()`。
     - `_bt_kill_pids` 對「`os.kill(pid, 0)` 還活著」的 pid 直接 SIGKILL。假測試結束後 pid 檔還留著,若 pid 被別的程序重用,會誤殺同一使用者的程序,不是攻擊路徑。
     - 窗口只有測試期間加最多 2 秒,macOS 的 pid 空間大,風險可忽略。S5 的迴圈每輪先清空 `pids/` 再開跑,進一步縮小窗口。
     - 無可利用路徑,不另列發現。
   - **打開陌生 repo**:
     - 惡意 repo 的 `.lumos/config.json` 能把平行數拉到 16,但這個 repo 已能寫任意 `run_cmd` 讓推送閘執行,沒有新的權限。
     - 計劃筆記和手冊都已明講這點。
     - 並行開 16 支屬於資源耗盡,依規定不報。
   - 工作執行緒是 daemon,中斷時由 `_BtProcs.reap` 收掉整個群組,沒有新增持久化的執行面。
6. **行動端**:已看,無。
7. **新加依賴**:已看,無。`queue`、`threading`、`time` 都是標準函式庫,測試用的 `unittest.mock` 也是標準函式庫。

## 附註

- 測試檔會被 CI 執行的命令已審。`run.py` 由測試自己生成,`sys.executable` 加 `GRAPHCTL` 路徑,沒有外部可控字串進 shell。
- 我只看了 diff 本身,沒有跑重現,也沒有開臨時 repo,所以沒有需要清理的暫存。

總結:最高等級 minor
