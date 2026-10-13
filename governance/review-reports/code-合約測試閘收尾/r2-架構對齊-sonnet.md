severity: clean

沒有 major 以上的不對齊。這份 diff 的寫法都能對到同一支檔裡既有的做法。我只讀了 diff 和既有程式碼對照,沒有跑測試,也沒有改任何東西。

## 鏡頭逐條判定

1. 共用小函式的位置與命名:對齊。
   - 新的 `_kill_proc_group` 放在 `_kill_run` 正上方(file: `scripts/lumos:17175`、`scripts/lumos:17189`)。
   - 它沿用 `_kill_*` 前綴,同一族還有 `_kill_cap`、`_kill_attribute`。
   - 三處各自手寫的 `killpg(getpgid(pid))` 收成一個函式,是在移除第二種做法,不是新增。
   - `_lint_run_and_parse` 改呼叫它,也一併拿掉區域 `import signal`。

2. 函式內 import 慣例:對齊。
   - `_kill_proc_group` 裡的 `import signal`、`_BtProcs.__init__` 裡的 `import threading as _threading`,都延續這支檔裡「函式內 import」和 `_` 別名的寫法(file: `scripts/lumos:48344`)。
   - `reap` 裡的 `import time as _time_mod` 是搬自舊 `_run_bound_tests` 的別名。檔頭已有 `import time`(file: `scripts/lumos:61`),但 `_kill_run` 也在函式內 import time,所以這是既有慣例,不是新做法。

3. 例外類別:對齊。
   - `_BtStopped(Exception)` 附 docstring,形狀同 `_NoteRereadStop`、`_DriftM1Stop`(file: `scripts/lumos:34667`、`scripts/lumos:39975`)。
   - 命名是 `*Stopped` 而不是 `*Stop`,屬風格偏好,不列。

4. 子程序開法與收尾:對齊。
   - 仍是 `start_new_session=True`,逾時路徑照舊走「殺群組、`proc.wait()`」。
   - `_kill_run` 對 `started` 參數改成經 `launch()` 開程序,不給時走原本的 `_popen()`。其他呼叫端都沒傳 `started`,沒有新增第二種開法。
   - 唯一的小改變是 `started` 從 list 變成 `_BtProcs`,而 `_BtProcs` 不再繼承 `list`。唯一傳入它的呼叫點是 `_one`(file: `scripts/lumos:48241`),已一併改過,沒有殘留的 `.append` 用法。

5. 執行緒與鎖:對齊。
   - 沿用 `threading` 加 daemon 執行緒的做法,`Condition` 取代 `Lock` 加輪詢。
   - 檔內沒有別的 `Condition` 用法可對照,所以這是新增一個原語,不是第二種做法。
   - `_worker` 裡本來為了輪詢才有的 `tally` 和 `_time_mod`,已隨輪詢一起拿掉。

6. 測試檔的子程序探針與清理:對齊。
   - 新增的 `_bt_spawn_probe` 是把原本散在 S5、S7 的兩份內嵌探針收成一份。
   - `_bt_groups_alive`、`_bt_kill_groups` 的形狀、命名、位置,都和既有的 `_bt_alive_pids`、`_bt_kill_pids` 平行(file: `scripts/test_lumos.py:50061`、`scripts/test_lumos.py:50075`)。
   - 暫存目錄一樣用 `tempfile.mkdtemp(prefix="gctl-btpar-")`,並在 `finally` 裡 `rmtree`。
   - 新測試都以 `t_` 開頭,會被 `names = {k for k in globals() if k.startswith("t_")}` 收到(file: `scripts/test_lumos.py:1786`)。
   - 子程序裡用子類別包住 `subprocess.Popen`,和檔內其他地方的 `mock.patch("subprocess.Popen")` 寫法不同。但探針跑在獨立的子程序,mock 到不了那裡,所以不算第二種做法。

7. 跨層直呼:未發現。`_BtProcs` 和 `_kill_proc_group` 都只被 `_kill_run` 和 `_run_bound_tests` 一帶用到,沒有新的跨層依賴。

## 三問(只回答和架構對齊有關的部分)

① 原問題的修復效果:我沒有跑測試,所以沒有行為證據。結構上,舊的「登記後才收、最多輪詢 2 秒」已改成「先數正在開、再用 `Condition` 等」,不再有兩套並存的收尾機制。

② 修補處的相鄰呼叫路徑:`_kill_run` 逾時、lint 逾時、合約測試閘收尾這三處,現在都經由 `_kill_proc_group` 這一條,相鄰路徑一致。
- 它直接用 `proc.pid` 當群組編號,不再先查 `getpgid`。這前提靠所有呼叫端都用 `start_new_session=True` 開程序。
- 目前三處呼叫端都符合這個前提。我沒有 finding 要列。

③ 同一案例的修前修後:本席沒有新發現,所以不適用。

總結:最高等級 clean
