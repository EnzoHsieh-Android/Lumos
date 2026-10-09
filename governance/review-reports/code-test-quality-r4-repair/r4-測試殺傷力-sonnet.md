severity: minor

整份最高為 minor。七支目標測試對照修前 7d1975e8 與修後 a2f30b19 實跑過，變異大多被目標斷言抓到。我另外找到五個 minor：一個修補造成的行為退步、一個修補造成的可攜性退步，三個變異存活。

## 修前／修後實驗方法
- 修後 a2f30b19：scan 28 項、handbook 19 項、cli 46 項全綠。
- 修前產品碼配修後測試（產品檔與 `scripts/lumos` 取 7d1975e8，測試取 a2f30b19）：
  - `test_semgrep_backend_outcomes_stop_stream_holding_worker`：success 與 nonzero 兩個子案綠，只有 hang 紅。`BACKEND_TIMEOUT` 在修前不存在，被忽略，實測 40.01 秒大於 6 秒。
  - `test_sigterm_during_semgrep_stops_scan_and_backend`：紅（ERROR）。修前把中斷收成 unavailable 後續掃第二檔，`communicate(timeout=5)` 逾時。
  - `test_python_scan_does_not_need_semgrep_runner_bundle`：紅，`ModuleNotFoundError: No module named 'test_quality'`。
  - `test_exited_model_with_stream_holding_worker_is_not_timeout`：紅（ERROR）。
  - `test_semgrep_report_over_evidence_limit_is_structured_unavailable`、`test_model_timeout_keeps_partial_stream`、`test_failed_capture_stops_worker_that_inherits_streams`：在修前產品碼上也綠。它們是 preserve 或加強型控制，不是還原翻紅釘。
- 修前產品碼上的 `test_failed_capture_stops_worker_that_inherits_streams`：單跑確認綠，修前 runner 本來就處理已退出 launcher 的情況。

## Findings

ID: MUT4-1
severity: minor
blocking: false
引句:「returncode, stdout, stderr = run_capture_command(cmd, timeout, cwd=directory)」
file: `governance/eval/test_quality_handbook.py:231`
`model_command` 改走共用 runner 後，模型輸出超過 10 MiB 會拋出沒人接的 `ValueError("output exceeds 10 MiB")`。修前同樣輸入正常回傳。`run_model` 只接 `TimeoutExpired`，整場評測因此中斷，而不是記成 invalid。
- 修前：fake `claude` 輸出 11 MiB，`model_command` 回 `ok 11534336`。
- 修後：同一輸入，`ev.model_command` 拋 `ValueError output exceeds 10 MiB`。
- 端到端：用 PATH 前置的假 `claude` 呼叫 `run_model`，修前得到 `row valid False rc 0`；修後 `RAISED ValueError output exceeds 10 MiB`。
- 圖譜聲稱「超過 10 MiB 仍回結構化錯誤」，對 `model_command` 不成立。沒有任何測試守超量行為。`r4-behavior-cases.json` 的 preserve 案例也已自承「uncovered」。
- 歸因：有證據的修復回歸。

ID: MUT4-2
severity: minor
blocking: false
引句:「self.assertLess(time.monotonic() - started, 3, "exited model is not a timeout")」
file: `governance/eval/test_test_quality_handbook.py:263`
改寫後的 `model_command` 是否把 `cwd=directory` 傳給 runner，沒有任何測試守。`cwd=directory` 是評測隔離目錄的唯一保證。
- 變異：把 `run_capture_command(cmd, timeout, cwd=directory)` 的 `cwd=` 拿掉。修後 handbook 19 項照綠（rc 0），變異有套上。
- 修前版同樣拿掉 `Popen(cmd, cwd=directory, ...)`，17 項也照綠。
- 新增的兩支 fake claude 控制都沒讓 fake 回報自己的工作目錄。
- 歸因：有證據的原有漏查。重寫函式時沒補上，不是修補造成的。

ID: MUT4-3
severity: minor
blocking: false
引句:「raise CaptureTimeout(bytes(buffers['stdout']), bytes(buffers['stderr'])) from exc」
file: `scripts/test_quality.py:394`（審材 diff 內此行）
runner 第二個逾時出口（兩條管線都 EOF、程序還活著、`proc.wait` 逾時）沒有任何測試走到。
- 變異：把它改回 `raise ValueError('timeout; never detected') from exc`，套在修後版。handbook 19 項、scan 28 項、cli 46 項全綠。
- 後果：Semgrep 在這條路徑會把逾時判成 unavailable，`model_command` 會拋 `ValueError` 而不是 `TimeoutExpired`。
- 另一個變異：這個出口改成 `CaptureTimeout()` 不帶部分輸出，`ModelCommandTests` 也全綠。
- 這條路徑可以到達：子程序關掉 stdout 和 stderr 後繼續睡。
- 歸因：有證據的修復新增路徑缺測，即本輪新增的型別分類在該出口無守衛。

ID: MUT4-4
severity: minor
blocking: false
引句:「raise CaptureInterrupted('execution interrupted by signal ' + str(signum))」
file: `scripts/test_quality.py:369`（審材 diff 內此行）
中斷訊息「execution interrupted by signal N」沒有測試守。
- 圖譜聲稱「CLI capture 的 receipt reason 不變」。`r4-behavior-cases.json` 的 preserve 案例引 `test_cancelled_capture_stops_child` 為證，但該測試沒有斷言訊息。
- 變異：把訊息改成 `'interrupted'`，cli 46 項與 scan `sigterm` 皆綠。
- 逾時訊息有 `test_timeout_not_detection` 守住：變異成 `'timed out'` 時它紅。
- 我另外實跑 `scripts/lumos test-quality scan A.swift B.swift --semgrep <fake hang>` 並送 SIGTERM：
  - 修後：rc 2、輸出結構化 `{"complete": false, "reason": "execution interrupted by signal 15"}`，backend 只被呼叫 1 次，0 秒結束。
  - 修前：rc 2，第二檔也被呼叫（calls=2），耗時 40 秒，輸出是 unavailable 的完整 report。
- 產品行為正確，缺的只是訊息斷言與經 lumos 入口的測試。
- 歸因：有證據的原有漏查。

ID: MUT4-5
severity: minor
blocking: false
引句:「loader.exec_module(module)」
file: `scripts/test_test_quality_scan.py:601`（審材 diff 內此處）
`semgrep_module()` 拿掉 `sys.path.insert(0, SEMGREP_TOOL.parent)` 後，測試只有在 `scripts/` 是 `sys.path[0]` 時才跑得起來。
- 命令：從 repo 根目錄 `python3.14 -m unittest scripts/test_test_quality_scan.py`。
- 修前：24 項 OK。
- 修後：28 項 FAILED（errors=4），`ModuleNotFoundError: No module named 'test_quality'`。
- 推送前的閘用 `python scripts/test_test_quality_scan.py` 跑，不受影響。
- 歸因：有證據的修復回歸（測試可攜性）。

已讀，無 finding：
- 時間門檻：success 與 nonzero 實測約 0.55 秒（門檻 1.5 秒），hang 用 `BACKEND_TIMEOUT=2` 對 6 秒，keeps_partial 的 1 秒逾時，exited 的 3 秒。
- 壓力測試：同時開 80 個 busy 程序，連跑 `keeps_partial` 與 `exited` 15 次、cli inherits 10 次、outcomes 3 次，全綠。
- 唯一的 flake 出現在 30 個 busy 程序下，是舊測試 `test_model_timeout_stops_worker_without_paid_call` 的「worker launched」斷言，不在本輪 diff。
- 閘的 60 秒上限：scan 約 13 秒、handbook 約 11 秒、cli 約 29 到 30 秒，餘裕夠。
- 失敗路徑的衛生：`sigterm` 與 `exited` 兩支測試在變異紅時，worker 的 `addCleanup` 還沒註冊，會留下約 60 秒自行過期的 `sleep(60)`。實測有殘留，會自己結束，不構成 finding。

## 前置斷言與 oracle
- worker 握住管線：CLI 與 handbook 兩支用 `worker-holds-stream` 出現在被捕獲的輸出來證明。outcomes 與 sigterm 靠 `[call] = self.calls(record)` 證明 backend 真的被呼叫恰好 1 次，sigterm 另靠 `record.exists()` 證明送信號前 backend 已啟動。這些前置都成立。
- 核心檔真的不在：`assertFalse((root/'test_quality.py').exists())`。
- expected 來自需求（狀態字串、returncode 3、metrics `off`），不是重抄實作。
- worker 啟動靠固定 `sleep(0.3)`，沒有握手。壓力測試下沒出事，所以不標 finding。

## Mutation 表
| 測試 | 變異 | 修後結果 | 變異結果 | 紅在哪 | 有效偵測 |
|---|---|---|---|---|---|
| keeps_partial | CaptureTimeout 第一出口不帶輸出 | 綠 | 紅 | `assertIn init` | 是 |
| keeps_partial | stdout 與 stderr 交換 | 綠 | 紅 | 同上 | 是 |
| keeps_partial | 第二出口不帶輸出 | 綠 | 綠 | 無 | 否（MUT4-3） |
| 全部 | 第二出口改回普通 ValueError | 綠 | 三套件皆綠 | 無 | 否（MUT4-3） |
| model_timeout 兩支 | `model_command` 逾時改直接拋 ValueError | 綠 | 紅（ERROR） | `ValueError: timeout` | 是 |
| python_scan | scanner 頂層 import | 綠 | 紅 | rc 1，`ModuleNotFoundError` | 是 |
| sigterm | 拿掉 `except CaptureInterrupted: raise` | 綠 | 紅（ERROR） | `communicate` 5 秒逾時 | 是 |
| sigterm | handler 改丟普通 ValueError | 綠 | 紅 | 同上 | 是 |
| sigterm | 中斷訊息改字 | 綠 | 綠 | 無 | 否（MUT4-4） |
| outcomes | `BACKEND_TIMEOUT` 寫死 40 | 綠 | 紅（hang） | 40.02 不小於 6 | 是 |
| outcomes | 拿掉 `CaptureTimeout` 分支 | 綠 | 紅（hang） | `'unavailable' != 'timeout'` | 是 |
| outcomes | 拿掉 `cwd=root` | 綠 | 三案皆紅 | `cwd_has_rules` | 是 |
| outcomes | 拿掉 `SEMGREP_SEND_METRICS` | 綠 | 三案皆紅 | `None != 'off'` | 是 |
| outcomes、exited、cli inherits | 拿掉 launcher 退出後清群 | 綠 | outcomes 的 success 與 nonzero 紅，cli inherits 與 exited 紅（ERROR） | 狀態為 timeout | 是 |
| sigterm、outcomes、handbook timeout | 拿掉 finally 清群 | 綠 | 三者紅 | `True is not false`（worker 仍活） | 是 |
| cli inherits、exited | 同上（拿掉 finally 清群） | 綠 | 綠 | 無 | 否，這兩支只走 launcher 退出路徑，該變異由前述三者代守 |
| over_evidence | stderr 不計入上限 | 綠 | 紅 | `0 != 2` | 是 |
| handbook 全部 | 拿掉 `model_command` 的 `cwd=` | 綠 | 綠 | 無 | 否（MUT4-2） |
| cli | 逾時訊息改字 | 綠 | cli 紅，scan 與 handbook 綠 | `test_timeout_not_detection` | 是 |
| `process_runner_sha256` | 拿掉 manifest 欄位 | 無對應測試 | 全 repo `git grep` 只有圖譜與產品行 | 無 | 否，無測試讀它 |

## 三問
1. 原問題的修復效果有何行為證據？
   - claim：握管線 worker、SIGTERM、純 Python 掃描三條修補都有行為證據。
   - input：修前產品碼配修後測試。
   - expected：目標測試紅，修後綠。
   - before：outcomes 的 hang 紅（40 秒）；sigterm 紅；python_scan 紅；exited 紅。
   - after：全綠。
   - comparison：紅點都落在目標斷言，沒有被別的斷言代打。
   - attribution：有證據的修復效果。
   - 例外：`over_evidence`、`keeps_partial`、`failed_capture inherits` 在修前也綠，是 preserve 或加強，不是修復證據。
2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立？
   - claim：多數仍成立，但有兩處退步。
   - input：`model_command` 輸出 11 MiB；從根目錄用 `python -m unittest` 跑 scan 測試。
   - expected：與修前相同。
   - before：回傳 `ok 11534336`；24 項 OK。
   - after：拋 `ValueError`（MUT4-1）；4 個 errors（MUT4-5）。
   - attribution：有證據的修復回歸。
   - 相鄰路徑：經 lumos 入口送 SIGTERM，修後 rc 2 且為結構化輸出，成立。
3. 同一案例修前、修後各是什麼結果？
   - 兩份 Semgrep SIGTERM 掃描，修前續掃第二檔、耗時 40 秒；修後 0 秒、只呼叫一次 backend。
   - 握管線 worker 的 model 命令，修前 5 秒逾時；修後 rc 0、輸出完整。

固定席必答：
- 兩條 ★INVARIANT★ 都不受影響。
  - `lumos-cli-lifecycle`：diff 在 `scripts/lumos` 只動 `_TEST_QUALITY_BUNDLE_DIGESTS` 一行，沒碰 sentinel 與 CLAUDE.md 注入邏輯。
  - 測試假綠形態：新增還原翻紅釘各有前置，見上方「前置斷言與 oracle」一節；`over_evidence` 在修前也綠，不是釘。
- 既有決策「選配適配器延後載入」：本輪是加強。`python_scan` 測試證明只缺 `test_quality.py` 時純 Python 掃描仍完成。經 lumos 入口缺檔仍走 `dispatch` 的 `ImportError` 結構化錯誤。

未驗範圍：
- Windows。
- 真 `claude` CLI。
- 安裝後部署位置。
- 完整 `scripts/test_lumos.py` 閘。
- 直接執行 scanner 收 SIGTERM 時 traceback 非零結束，圖譜已宣告為代價，我只確認 rc 非 0。

總結最嚴重 severity: minor；blocking: 0
