severity: minor

## Finding CON7-01
severity: minor
blocking: 否
引句:「fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o666)」
file: `scripts/scenario_probe.py:98`

- 具體輸入:輸出位置是自己擁有、單一名字、權限 0600 的既有結果檔,umask 為 022,資料量超過 128 KiB。
- 走到哪一段:暫存檔以 0o666 去掉 umask 建立,所以是 0644。接著 `tmp.write(data)`(第 104 行)先寫入,最後才 `os.fchmod(..., keep_mode)`(第 106 行)。
- 壞在哪:使用者刻意設成 0600 的檔,內容會先寫進一個全域可讀的暫存檔,之後才收窄權限。其他本機使用者只要在這段空窗開啟暫存檔,收窄權限後仍留著已開的讀取權。暫存檔名含 pid 與 4 位元組隨機數,但同目錄可列出。
- 重現:用 `os.fchmod` 的 spy 在呼叫當下讀暫存檔的狀態,umask 022,既有檔 0600:

```
n=200000   fix:    at fchmod: tmp mode=644 size=200000
n=200000   before: at fchmod: tmp mode=600 size=200000
n=2000000  fix:    at fchmod: tmp mode=644 size=2000000
n=2000000  before: at fchmod: tmp mode=600 size=2000000
```

- 資料量 20000 時,fchmod 當下 size=0,資料還在緩衝區,但暫存檔仍是 0644,只剩可讀開啟的空窗。
- 修法方向:建立後、寫入前先 `fchmod`。
- 歸因:有證據的修復回歸。修前用 `NamedTemporaryFile`,暫存檔恆為 0600(`before` 的輸出如上),修後改為 0o666 建立。

## Finding CON7-02
severity: minor
blocking: 否
引句:「if stat.S_ISCHR(st.st_mode):」
file: `scripts/scenario_probe.py:47`

- 具體輸入:`--out /dev/rdisk0`,這是目前使用者沒有寫入權限的字元裝置。
- 走到哪一段:開跑前檢查碰到字元裝置就直接 `return None`,不看 `os.access`。同檔對普通檔有檢查(第 50 行),對字元裝置沒有。
- 壞在哪:該函式的 docstring 宣稱「跟 `_atomic_write_bytes` 一一對應」、「跑模型之前先看輸出位置寫不寫得出去」,但沒寫入權限的裝置照樣放行。整批跑完後,第 82 行才丟出 `PermissionError`,結果全丟。這正是第五輪想消除的「整批跑完才報權限錯」。
- 重現:

```
modA precheck -> None | os.access W: False
  write -> PermissionError [Errno 1] Operation not permitted: '/dev/rdisk0'
```

- 追加模式的 `--history` 同路徑(第 47–48 行對兩種模式都直接放行)。
- 歸因:有證據的原有漏查。`before` 版同一輸入結果相同(precheck 回 None、寫入丟 PermissionError)。
- 這條只會在批次結束時丟 PermissionError,沒有寫入或危害,所以只給 minor。

## Finding CON7-03
severity: minor
blocking: 否
引句:「old_alarm = signal.signal(signal.SIGALRM, _hang); signal.alarm(5)」
file: `scripts/test_lumos.py:43364`

- 具體輸入:任何用 `run_with_timeout` 跑 `t_probe_boundary_fifth_round_output_edges` 的情況。
- 走到哪一段:測試執行器(`scripts/test_lumos.py:35292-35306`)用 `SIGALRM` 加 `signal.alarm(180)` 當每支測試的逾時。新增的 FIFO 段在 `finally` 裡 `signal.alarm(0)`,只還原了處理器,沒有還原鬧鐘。
- 壞在哪:這段之後(歷史檔 FIFO 與唯讀目錄的 `main()` 呼叫、換成連結的追加、消融腳本載入)不再有逾時保護。若這些地方卡住,整套測試無限期停住,不會拋 `TestTimeout`。
- 重現:用同樣的寫法包在 `run_with_timeout(test, 2)` 裡。FIFO 段結束後,`getitimer` 回 0.0;接著睡 3 秒,沒有 `TestTimeout`。
- 歸因:有證據的修復回歸。FIFO 段由 3e149721 新增,`483df9fe` 的這支測試沒有 signal。repo 裡另有 13076 與 69602 兩處同寫法,是既有慣例,但此處是新增。
- 本機實跑 `-k t_probe_boundary_fifth_round_output_edges` 為 25 passed、0 failed,耗時 2.1 秒,沒有殘骸。

## 固定席逐條判定
- `codex-harness.md`(家):本審材改它的筆記。新舊 PITFALL、WHY 各只出現一次,所有 `[[…]]` 連結都存在於 67b1dea2。筆記宣稱「FIFO、socket、連結換成普通檔;追加只收普通檔與字元裝置」,與程式一致。只有 CON7-02 與筆記「開跑前檢查一一對應」的說法有落差。
- `測試假綠形態.md`(★INVARIANT★):不受影響。新測試有現場成立的前置斷言(`linked.st_nlink == 2`、`swap_hist.is_symlink()`、`hung`)。例外是 CON7-03 的逾時鬧鐘。
- `autonomous-iteration-loop.md`(★RISK★):本審材只動它牽連的 `test_autonomous_loop.py` 的相關脈絡,未見行為變更。未深查。
- `lumos-cli-lifecycle.md`(★INVARIANT★ re-inject):不受影響。合併段只動 TTY 與外掛筆記。
- `lumos-cli-read.md`、`design-loop.md`、`bound-tests-gate.md`、`canary-audit.md`:不受影響。審材沒有碰其合約對應的行為。`t_slim_uninstall_manifest_parent_cleanup_is_best_effort`、`t_canary_record_persist` 等綁定測試沒有被改。
- 其餘「超出上限只列名」的節點:未逐條審。

## 合併鏡頭
- 筆記兩邊內容都在,沒有重複行,也沒有死連結。已把 6 篇合併後的筆記的所有 `[[…]]` 對 67b1dea2 的檔案清單核對。
- `scripts/lumos` 的 `O_NOCTTY` 只剩一處,在 23908。
- `SKILL.md` 步驟 5 與 6 採主線版。branch 的試行說明在第 16 與第 48 行各有一條,與 binding 的「一行」不符,但兩條互補、不矛盾。
- `t_dart_profile_discovery` 在 `6467401a`、`3e149721`、`67b1dea2` 都定義兩次,是主線與分支本來就有,不是合併造成的。

## 修補三問
- ①原問題的修復效果:
  - FIFO 不卡住:在 `t_probe_boundary_fifth_round_output_edges` 的 25 個斷言中通過。
  - 跑的期間歷史檔被換成連結時 `ELOOP`:在同一個測試中通過。
  - 報表標記:靜態讀碼,`visible` 對 `⟦` 本身也轉寫,輸出唯一可還原。
  - 硬連結:通過(「有多個名字的檔不沿用權限」)。
- ②正常、錯誤與相鄰路徑:
  - 字元裝置 TOCTOU:被換成 FIFO(有讀者)、普通檔、目錄、連結時,`open` 或 `fstat` 檢查擋下,不寫。
  - 沒有讀者的 FIFO:`ENXIO` 立即報錯,不會卡住。
  - 歷史檔換成有讀者的 FIFO:會寫到讀者,沒有型別確認,但無實害。
  - 暫存檔 `O_EXCL` 迴圈:撞名只會換隨機後綴重試。
  - `BaseException` 清理:涵蓋 KeyboardInterrupt。SIGKILL 與 SIGTERM 的殘留仍沒人收,與修前相同。
- ③新發現同一案例,修前與修後:

| 發現 | 修前 483df9fe | 修後 3e149721 / 67b1dea2 |
|---|---|---|
| CON7-01 | 暫存檔恆為 0600 | 暫存檔先以 0644 寫入 |
| CON7-02 | 預檢放行、寫入報 `PermissionError` | 同左 |
| CON7-03 | 沒有 signal | 新增 FIFO 段後鬧鐘被取消 |

## 未驗範圍
- ctty 取得:在 macOS 用新 session 加 pty slave 路徑試了兩次,`/dev/tty` 的 `has_ctty` 為 False,沒有重現,所以不報。第一次嘗試有一次子程序卡在退出狀態,我自己的測試程序已經殺掉並確認清理。
- 歷史檔 `O_APPEND|O_NONBLOCK` 多程序交錯:紀錄約 300 位元組,小於 128 KiB 緩衝,在普通檔上是單次 `write`,未實測多程序競爭。
- 歷史檔指向字元裝置(例如終端)時 `O_NONBLOCK` 沒有改回阻塞,滿緩衝可能 `BlockingIOError`。沒有具體重現情境,不報。
- 程序群與孫程序:審材沒有新增子程序、`setsid` 或 `killpg`,不適用。
- 沒有跑全套測試,也沒有跑修前版本的測試;兩版本的 `_atomic_write_bytes` 與 `_output_target_problem` 行為差異是直接各自 import 比較。

實驗目錄 `/tmp/lumos-seat-work/code-probe-postreview-dispatch-ledger/併發資源7-sonnet/` 已刪除,沒有留下我自己的背景程序。

總結:最高嚴重度 minor
