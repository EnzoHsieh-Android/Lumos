severity: minor

1. 程序群組收尾寫法多一份,而且與既有兩處不完全相同
severity: minor
blocking: 否
引句:「os.killpg(os.getpgid(proc.pid), _signal.SIGKILL)」
file: `scripts/lumos:17196`(`_kill_run` 逾時段:killpg,失敗後退 proc.kill)
file: `scripts/lumos:27719`(lint 那處:只有 killpg,沒有退路)
- 新的 `_bt_kill_proc` 是專案裡第三份「killpg 加 proc.kill 退路」。既有 `_kill_run` 逾時段已有同樣的寫法,但收尾邏輯沒有共用。
- 兩份的 `except` 元組一樣,都是 `(ProcessLookupError, OSError, AttributeError)`。
- `_bt_kill_proc` 多了 `proc.poll() is not None` 的前置判斷。`_kill_run` 的逾時段沒有這一步,它後面直接 `proc.wait()`。
- `_bt_kill_proc` 在函式內用 `import signal as _signal`,模組層的 `os` 則直接用。`_kill_run` 是函式內 `import signal`,沒加別名。專案的慣例是函式內 import,別名則不常見。
- 這是兩份獨立的複本,不是第二種做法。若有人以後改逾時收尾(例如加 `proc.wait`),`_bt_kill_proc` 不會跟著變。

2. 繼承 list 的類別在專案裡沒有先例
severity: minor
blocking: 否
引句:「class _BtProcs(list):」
file: `scripts/lumos:48309`(`_BtProcs` 在檔案中段的 bound-tests 區塊)
file: `scripts/lumos:39941`(既有 `_DriftM1Run` 等 `_Xxx` 類別都是普通類別,沒有繼承內建容器)
- Grep 查 `^class .*\(list\|dict\|set\)`,整支 `scripts/lumos` 只有 `_BtProcs` 一個。
- 命名前綴 `_Bt` 與 `_Drift…`、`_Notelines…` 的慣例一致,放置位置也是在家區塊附近,這兩點對齊。
- 不對齊的是它覆寫 `append`,讓 list 的行為依內部狀態變化。
- `_kill_run(started=procs)` 的呼叫端把它當純 list 用。這種「交出內部物件」的參數,專案裡既有的例子是 `sink=`(`scripts/lumos:30737`、`:32471`)和 `out=`(`:27436`),都是 dict 或 slots,不是帶副作用的 list 子類。
- `started` 這個名字也沒有先例。要不要改,判不準,標 ⚠。

3. 並行的工具選擇有書面說明,對齊
severity: minor
blocking: 否
引句:「它的工作者不是 daemon,程式結束時會 join,出錯或 Ctrl-C 也得等」
file: `scripts/lumos:48200`
- 專案裡沒有其他 `threading.Thread` 的用法。Grep `threading\.Thread` 只有診斷題庫的字串樣式和這一處。
- 自建 daemon 執行緒加 queue 是專案第一個並行,沒有既有做法可比。但註解已寫明不用 `ThreadPoolExecutor` 的理由。
- 這條只記錄「專案第一個並行」。判不準它算不算新慣例,標 ⚠。除此之外,與既有做法沒有衝突。

三問

1. 分層與依賴方向
   - `_bt_kill_proc` 和 `_BtProcs` 放在 `_run_bound_tests` 下方,同一個 bound-tests 區塊,與 `_bt_parallel_warn`、`_bound_tests_parallel` 放在一起。這樣放對齊。
   - `_kill_run`(`scripts/lumos:17175`)是低層 helper。它只多一個選用參數 `started`,沒有反向依賴 bound-tests 的類別,呼叫端傳入的 list 子類只當 list 用。依賴方向沒有問題。
   - 沒有發現跨層直呼。

2. 命名與錯誤處理
   - 私有前綴 `_bt_`、`_Bt` 一致,測試命名 `t_bound_tests_parallel_*` 與既有 `t_bound_tests_*` 一致。
   - 錯誤處理的 `except` 元組與 `_kill_run` 一致,收尾「盡力而為」也與註解一致。
   - 警告用 `print(..., file=sys.stderr)`,與專案裡 871 處同類寫法一致。
   - 與既有寫法的差異只有 finding 1 提到的 `poll()` 前置判斷和 `_signal` 別名。

3. 第二種做法(Grep 實查)
   - 程序群組收尾:`os.killpg` 出現在 `scripts/lumos:17196`、`:27719`、`:48301`。其中 `:17196` 與 `:48301` 的 killpg 加 `proc.kill` 退路是同一個形狀的複本(finding 1)。
   - 並行:無先例,見 finding 3。
   - 繼承內建容器的類別:無先例,見 finding 2。
   - 「交出內部物件給呼叫端」的參數:既有慣例是 `sink=`、`out=`,新加的是 `started=`,命名不同但形狀相近。
   - 專案裡沒有引入新依賴。

不對齊共 3 條,其中 major 0 條
