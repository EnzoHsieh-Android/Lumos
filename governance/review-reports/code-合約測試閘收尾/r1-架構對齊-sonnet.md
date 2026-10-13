severity: minor

## 1. S7 測試仍留著一份內嵌探針,與新抽出的 `_bt_spawn_probe()` 並存
severity: minor
blocking: 否
引句:「return ("import signal; signal.signal(signal.SIGINT, signal.default_int_handler)\n"」
file: `scripts/test_lumos.py:50260`
file: `scripts/test_lumos.py:50291`
- 既有寫法:`t_bound_tests_parallel_interrupt_stops_dispatch` 在 50260 行一帶自己內嵌 SIGINT 探針。
- 這份 diff 的寫法:把 `t_bound_tests_parallel_error_stops_fast` 改用新的共用 `_bt_spawn_probe()`,另外兩支新測試也用它,S7 沒改。
- 差在哪:同一組並行測試現在有兩份「子程序裡載入 lumos 並跑 `_run_bound_tests`」的探針,各自獨立維護。
- 沒做的比對:我沒逐行比 S7 的探針與 `_bt_spawn_probe` 差多少。
- 為什麼只算 minor:只是重複,沒引入新機制,也看不到現有測試因此失準。

## 2. 沒有不對齊的地方
以下逐項對照,結論都是對齊。

- **殺程序群組**
  - 既有:`scripts/lumos` 裡只有舊的 `_kill_run` 逾時、lint 指令逾時、`_bt_kill_proc` 三處各寫一份 `killpg(getpgid)`。
  - 這份 diff:三處都收斂成 `_kill_proc_group`,`scripts/lumos:17175`,放在 `_kill_run` 正上方,函式內 `import signal`,也沒有留下第二種做法。
  - 判定:這是減少分歧,方向對齊。
- **子程序開法**
  - 既有:`subprocess.Popen(..., shell=True, start_new_session=True, ...)` 加 `communicate(timeout)` 加逾時收尾,都沿用 lint 的先例(`scripts/lumos:27752` 一帶)。
  - 這份 diff:`_kill_run` 只把 Popen 包進 `_popen()`,交給 `started.launch`,不給 `started` 時行為不變。
  - 判定:對齊。
- **執行緒與鎖**
  - 既有:同一個函式內用 `threading.Lock()` 和 `queue.Queue`,在函式內 import,工作者是 daemon 執行緒(`scripts/lumos:48251`)。
  - 這份 diff:`_BtProcs.__init__` 用 `threading.Condition()`,同樣在函式內 import(`scripts/lumos:48344`)。
  - 判定:`scripts/lumos` 裡這是第一個 `Condition`,沒有既有用法可對照。它與 `Lock` 同屬標準庫、用法同層,而且「等正在開的都開完」確實需要等待與通知,所以不算第二種做法。
- **例外類別**
  - 既有:`_NoteRereadStop`(`scripts/lumos:34667`)、`_DriftM1Stop`(`scripts/lumos:39975`)都是簡單的 `Exception` 子類加 docstring。
  - 這份 diff:`_BtStopped(Exception)` 只有 docstring,沒有 `__init__`。
  - 判定:對齊;它不帶資料,所以不需要 `__init__`。
- **共用小函式的命名與位置**
  - 既有:`_kill_*` 與 `_bt_*` 這類以功能領域當前綴的私有小函式,放在使用處旁邊。
  - 這份 diff:`_kill_proc_group` 放在 `_kill_run` 旁(`scripts/lumos:17175`),`_BtProcs` 與 `_BtStopped` 仍在 `_run_bound_tests` 後面。
  - 判定:對齊。
- **`_BtProcs` 不再是 `list` 子類**
  - 引用已清掉:舊的 `len(procs)` 與 `tally` 簽帳整組移除,現在只剩 `procs.reap()` 與 `started.launch`。
  - 判定:沒有殘留的跨層直呼。
- **測試暫存與清理**
  - 既有:`tempfile.mkdtemp(prefix="gctl-btpar-")`,在 `finally` 裡 `_bt_kill_pids` 加 `shutil.rmtree`,與 `scripts/test_lumos.py:50061` 一帶相同。
  - 這份 diff:新測試沿用同樣的前綴與清理,另外加了 `_bt_groups_alive` 和 `_bt_kill_groups`(這兩個是新增的並行輔助函式)。
  - 判定:兩套輔助函式分工不同(`pids/` 逐 pid 對 `spawned/` 逐群組),命名風格也一致,不列問題。

總結:最高等級 minor
