severity: minor

只讀 diff、跑兩版實驗；沒改被審 repo。實驗在 `/tmp/lumos-seat-work/code-test-quality-r4-repair/回歸正確性-sonnet/repo`（shared clone）。

ID: REG-1
severity: minor
blocking: false
引句:「returncode, stdout, _ = run_capture_command(command, 40, cwd=root, env=env)」
file: `scripts/test_quality_semgrep.py:73`
敘述：Semgrep 後端原本用 `subprocess.run(capture_output=True)`，輸出沒有上限。改走共用 runner 後繼承了 10 MiB 上限（`read_ready_output` 的 `raise ValueError('output exceeds 10 MiB')`）。合法的大 JSON 報告原本掃得完，現在變成 `unavailable`。
- 失敗場景：假 backend 印出約 11 MiB 的合法 Semgrep JSON，`results` 為空、`paths.scanned` 正確。
- 這是 fail-closed，不是誤判綠。但它是修前沒有的行為改變，且本輪的文件和測試都沒提。
- stderr 也有同一改變：原本 `text=True` 遇到非 UTF-8 stderr 會拋 `UnicodeDecodeError` 而 unavailable，現在 stderr 被丟掉不解碼。這個方向無害。
歸因：有證據的修復回歸（修前 `subprocess.run` 無上限，修後有）。
命令（兩版都用上述假 backend 與 `Test.swift`，執行 `test_quality_scan.py w/Test.swift --json --semgrep w/semgrep`）：
- 10d40f30：`scanned None`
- c4982cb1：`unavailable output exceeds 10 MiB`

已讀，無 finding 的部分：
- 鏡頭 1(a)：launcher 退出、worker 繼承管線。迴圈每 0.1 秒 `poll()`，一偵測到退出就殺群，不再被誤判 timeout。launcher 已寫進管線的資料殺群後仍可讀，不會被截斷。
- 鏡頭 1(b)：worker 關閉管線。launcher 退出後管線 EOF，迴圈正常結束，`finally` 殺群。
- 鏡頭 2：`group_stopped` 配 `finally` 時，各出口不會重複殺，也不會漏清。
  - 例外、SIGTERM（handler 在 `terminate_group` 中途丟 ValueError）、輸出上限、timeout 這幾個出口，`finally` 最多再殺一次。
  - `ProcessLookupError` 被吞，已 reap 後 `proc.wait()` 直接回傳。
  - 壓力測試 300 次：launcher 同時產生 8 個瞬死 worker 並輸出 100 KB，全部正常 rc0、輸出 100001 bytes，沒有 `PermissionError`（macOS 殭屍群 EPERM 沒打中）。
  - PGID 重用窗口在修前修後都存在，修補沒有放大。
- 鏡頭 3：
  - JSONDecodeError、`UnicodeDecodeError`、SIGTERM 中斷、「invalid finding location」現在都走 `except ValueError`，分到 `unavailable` 且 reason 為 `str(exc)`，與修前同類。
  - 真 timeout 仍是 `timeout`。
  - 非零退出仍是 `error` 加 `returncode`。
  - CLI `capture` 對 `(OSError, ValueError, ET.ParseError)` 的處理沒變。
- 鏡頭 4：寫一半被 kill 時，report 由 `read()` 讀入、receipt 後寫，重跑 `args.out.mkdir(exist_ok=False)` 會擋，沒有新的非冪等路徑。
- 固定席：兩條 ★INVARIANT★ 都不受影響。
  - 測試假綠形態：新增的 `inherits_streams` 和 `worker` 測試都有前置斷言（rc 與 out 內容、`pidfile.exists()`、`status == 'scanned'`）。
  - lumos-cli-lifecycle：`scripts/lumos` 只改一行 bundle 摘要常數，沒碰 sentinel 注入邏輯。

三問：
1. 原問題修復效果有行為證據嗎？有。
   - claim：launcher 退出而 worker 繼承管線時，不再誤報 timeout。
   - input：`-k inherits`。
   - expected：rc1、out 為 `launcher-failed`。
   - before：10d40f30 該測試不存在，CLI `-k inherits` 回 NO TESTS RAN。
   - after：c4982cb1 通過（1 test OK）。
   - comparison：拿掉迴圈內的 `poll/terminate_group` 後，同一測試紅，錯誤是 `ValueError: timeout; never detected`。
   - attribution：修補造成的改善，有證據。
2. 修補處的正常、錯誤與相鄰路徑是否仍成立？成立。
   - 正常路徑：scanner 套件在 10d40f30 為 22 項、c4982cb1 為 24 項，都 OK。
   - 相鄰路徑：`global_vault` 控制兩版都綠。
   - 逾時路徑：Semgrep 後端的真逾時（40 秒）和非零退出殘留 worker 沒有專屬測試，我也沒跑，這部分未驗；只靠 `finally` 的程式碼推理。
3. 新發現的同一案例，修前修後各是什麼？只有 REG-1，修前 `scanned`，修後 `unavailable`（見上）。

未驗範圍：
- 真實 Semgrep 二進位沒裝，全用假 backend。
- launcher 自己 daemonize、讓 worker 在 launcher 退出後才寫結果的情況：修前會等管線 EOF，修後在 launcher 退出後被殺群而截斷。這是設計取捨，我沒有找到實際會踩到的呼叫者，所以沒列 finding。
- `-k global_vault` 的刪 fixture 對照、`--check-helper` 移除 cwd 後是否改測到另一條路徑，我只確認了兩版皆綠，沒做 fixture 刪除對照。

實驗殘留的 `time.sleep(60)` 背景程序已用 `pkill` 清掉。被審 repo 沒動；shared clone 最後停在 c4982cb1，`scripts/test_quality.py` 已從備份還原。

總結最嚴重 severity: minor；blocking: 0
