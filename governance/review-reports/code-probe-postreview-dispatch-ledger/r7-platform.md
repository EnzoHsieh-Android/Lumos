severity: minor

## Finding PLT7-01
severity: minor
blocking: 否
引句:「fd = os.open(path, os.O_WRONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))」
file: `scripts/scenario_probe.py:82`
- 輸入:`--out` 指到 tty 或 pty slave(例如 `/dev/ttys018`),而探針本身是 session leader(例如 `start_new_session=True` 起的)。
- 路徑:`_atomic_write_bytes` 的字元裝置分支用 `O_NONBLOCK|O_NOFOLLOW` 開檔,沒帶 `O_NOCTTY`。`--history` 的 `os.open`(`scripts/scenario_probe.py:1389`)也一樣沒帶。
- 壞處:session leader 開 tty 會把它收成控制終端。同一次合併裡,主線已在 `_confirm_tty` 補了 `O_NOCTTY`(`scripts/lumos:23908`,註解寫「session leader 開測試 pty 時不可把它收作控制終端」)。第五輪驗證筆記也記了拿掉 `O_NOCTTY` 後子程序收到掛斷。這一處是同族漏網。
- 重現:macOS 上子程序用 `start_new_session` 起,父程序先建 pty,子程序對 slave 路徑各做一次寫入,事後用 `O_NOCTTY` 開 `/dev/tty` 探測有沒有控制終端。
  - 對照組(自己帶 `O_NOCTTY` 開):`[False, False]`,rc 0,正常退出。
  - 67b1dea2 的 `_atomic_write_bytes`:`[False, True]`,控制終端被收走。子程序 15 秒沒退出,我用 SIGKILL 收掉。
  - 修前 483df9fe 的結果完全相同。
- 歸因:有證據的原有漏查。第五輪就沒帶,第六輪改開檔旗標時沒補。
- 未判定:子程序不退出的確切原因(疑似關 tty 時被擋),我沒追到。

## Finding PLT7-02
severity: minor
blocking: 否
引句:「規則跟 _atomic_write_bytes 與歷史檔追加一一對應:取代模式下,字元裝置直接寫、其他非目錄的東西」
file: `scripts/scenario_probe.py:47`
- 輸入:`--out /dev/tty`,環境沒有控制終端(CI、容器、背景批次都是)。
- 路徑:開跑前檢查對字元裝置一律 `return None`,沒查能不能開、能不能寫。批次跑完後 `_atomic_write_text` 才開檔,得到 ENXIO,是沒有說明的 `OSError`。這個寫入在 `scripts/scenario_probe.py:1381`,先於 `--history`,所以結果和歷史都沒寫出來,額度已花掉。
- 重現(macOS,無 ctty):
  - `_output_target_problem('/dev/tty', True)` 回 `None`。
  - `_atomic_write_bytes('/dev/tty', ...)` 拋 `OSError [Errno 6] Device not configured: '/dev/tty'`。
  - 修前與修後輸出相同。
- 第六輪的註解宣稱檢查與寫入規則「一一對應」,對字元裝置不成立。
- 歸因:有證據的原有漏查。
- 附帶確認:O_NONBLOCK 對 `/dev/null`、pty slave 都正常。
  - `/dev/null` 與 pty slave:寫入成功,master 讀到資料。
  - 管線(`/dev/fd/1` 指到管線):lstat 是 FIFO,開跑前檢查 rc2,訊息是「/dev/fd 不可寫」。
  - `/dev/stdout`:是符號連結,同樣 rc2。
  - 這些都沒有 traceback。

## Finding PLT7-03
severity: minor
blocking: 否
引句:「old_alarm = signal.signal(signal.SIGALRM, _hang); signal.alarm(5)」
file: `scripts/test_lumos.py:43364`
- 輸入:CI 或本機跑 `t_probe_boundary_fifth_round_output_edges`。測試框架 `run_with_timeout`(`scripts/test_lumos.py:35291`)用 `signal.alarm(180)` 守每支測試。
- 路徑:新測試自己 `alarm(5)`,`finally` 裡 `alarm(0)`,只還原 handler,沒還原剩餘秒數。框架那支 180 秒計時被取消。
- 壞處:FIFO 區塊之後的整段(多次 `mod.main()`、歷史檔被換成連結的案例)沒有逾時保護。這一段如果卡住,套件不會拋 `TestTimeout`,CI 會卡到 job 逾時。
- 沒有造成假綠假紅,handler 有還原,mkfifo 的暫存檔也有被清掉(測試自己斷言「寫完不留暫存檔」)。
- 同樣寫法在 `scripts/test_lumos.py:13076` 與 `:69602` 已有先例。
- 歸因:第六輪新增這一處,屬同型舊慣例,未判定為修補回歸。
- 目前我沒找到這一段會卡住的反例。

## 固定席逐條判定
- 測試假綠形態(★INVARIANT★ 還原翻紅釘要配前置斷言):沒有破壞。
  - 新增的硬連結案例與歷史檔被換成連結的案例都有「現場成立」斷言。
  - FIFO 不卡住的案例沒有先斷言它是 FIFO,但 `mkfifo` 成功就必然是 FIFO。我實測修前版 `_atomic_write_bytes` 會卡住(4 秒後 HANG),修後版換成普通檔。還原會翻紅,所以不構成假綠。
- `codex-harness`:新 PITFALL 與 WHY 跟程式一致。取代模式只有字元裝置直接寫,FIFO、socket、連結換成普通檔,對照 `scripts/scenario_probe.py:73` 的說明相符。
  - 合併段的 `verified_by` 兩邊清單都在,第六輪驗證筆記存在且被連結。
  - 註:PLT7-01 的 tty 控制終端問題,筆記沒提。
- `lumos-cli-lifecycle`、`lumos-cli-read`、`bound-tests-gate`、`design-loop`、`canary-audit`、`autonomous-iteration-loop`:
  - 這份審材只動 `scenario_probe`、消融腳本、`test_lumos.py` 與筆記。
  - 沒碰 re-inject、search 預設排除、bound-tests 閘、處置閘第五步、canary 落盤這些行為。
  - 合併帶進的 `scripts/lumos` 與主線逐位元組相同,我沒看到行為被破壞。
  - 它們各自綁定的測試我沒跑。
- 其餘只列名的節點:沒有逐篇判定。

## 合併段(鏡頭 3)
- `scripts/lumos` 在 67b1dea2、6467401a 兩版逐位元組相同。三版的 `_confirm_tty` 都是 `os.O_RDWR | getattr(os, "O_NOCTTY", 0)`。
  - 本分支相對 merge-base 2db51cc4,在這支檔上只加了這一行(主線同一處也加,所以合併不會讓主線丟東西)。行為相同。
- 主線兩支測試在 67b1dea2 版的武裝範圍:
  - `t_codex_s1_lens_arm_claim` 與 `t_codex_s1_r1_fixes` 都用 `_lens_smallest_commit(repo, ml)`,取主線近 30 個非合併提交裡改動行數最少的那個。
  - 範圍是 `<它的~1>..<它>`,不是分支範圍。我只讀了測試碼,沒跑,「不再逾時」未驗。

## 修補三問
- 原問題的修復效果:
  - FIFO 不卡住:修前 483df9fe 對沒人讀的 FIFO 卡住(HANG),修後換成普通檔,類型是 0o100000。
  - umask 不碰程序全域:`umask 077` 下新檔 0600,在兩版都一致。
  - 歷史檔 `O_APPEND|O_NONBLOCK` 對普通檔無副作用:兩次追加內容正確,權限 0644。
- 修補處的相鄰路徑:
  - 檢查後才冒出 FIFO,我用 patch `lstat` 模擬字元裝置被換成 FIFO:
    - 無讀者:`OSError` ENXIO,沒卡住,是無說明的 `OSError`,只在競態下發生。
    - 有讀者:EINVAL,訊息為「輸出位置在檢查後被換掉」。
  - `--history` 被換成 FIFO:無讀者得 ENXIO;有讀者時會成功追加一個位元組進 FIFO,沒有報錯。程式註解寫「換成連結或 FIFO 時報錯」,對有讀者的 FIFO 不成立,但沒有傷害。
- 同一案例修前與修後:PLT7-01 與 PLT7-02 兩版結果相同,屬原有漏查,不是修補回歸。

## 未驗範圍
- Linux 實機沒跑,以下兩點只讀程式碼:
  - `/proc/self/fd/*` 與 `/dev/stdout` 在 Linux 是符號連結。非 root 時開跑前檢查擋下(rc2)。
  - 我沒驗 root 且 `/dev` 可寫時(典型是容器)會怎樣。程式碼上,`_atomic_write_bytes` 會用普通檔取代 `/dev/stdout` 這個連結本身。這是第五輪起「取代連結」的既有設計,不是第六輪造成的,但後果值得有人在容器裡確認。
- root 分支的測試只讀碼,沒在 root 下跑。
- 沒跑全套與 CI,實驗目錄已 `rm -rf`。

總結:最高嚴重度 minor
