severity: minor

整份只找到一條 minor：handbook 改走共用 runner 後，模型輸出超過 10 MiB 會讓整場評測崩掉。三個鏡頭的其餘部分我都試著找破口，沒有找到。

ID: REG4-1
severity: minor
blocking: false
引句:「+        returncode, stdout, stderr = run_capture_command(cmd, timeout, cwd=directory)」
file: `governance/eval/test_quality_handbook.py:229-236`（`model_command`）、`governance/eval/test_quality_handbook.py:252-257`（`run_model` 只接 `TimeoutExpired`）

白話：以前模型輸出多大都收得下。現在共用 runner 有 10 MiB 上限，超過就丟 `ValueError('output exceeds 10 MiB')`。`run_model` 與主迴圈都不接這個例外，所以整場評測以 traceback 結束，那次輸出沒落檔，輸出目錄又不能重用（`mkdir(exist_ok=False)`）。`CaptureInterrupted`（SIGTERM）也走同一條路，但修前也是未接的 `ValueError`，那條不算回歸。

歸因：有證據的修復回歸。上限是這次改走共用 runner 才帶進來的。

兩版重現：用 PATH 前置的假 `claude`，印 11,011,000 位元組後退出，呼叫 `ev.run_model(...)`。

| 版本 | 結果 |
|---|---|
| 修前 7d1975e8 | 回傳 row，`valid=False`，raw 長度 11011000，事件檔已寫出 |
| 修後 a2f30b19 | `RAISED ValueError output exceeds 10 MiB`，事件檔不存在 |

直接呼叫 `model_command` 也一樣：修前回 11534337 位元組，修後丟 `ValueError`。

為什麼只算 minor：筆記寫的「61 份事件檔最大 72 KB」我核對屬實（工作樹裡 61 份，最大 72675 位元組）。實際落入上限的機率低。

其餘部分已讀，無 finding：

- **鏡頭 1，例外分類**
  - `CaptureTimeout` 與 `CaptureInterrupted` 的每個呼叫端分類都對：
    - Semgrep 的 `except` 順序正確：中斷先 `raise`，逾時收成 timeout，其餘 `ValueError` 收成 unavailable。
    - CLI capture 的 `except (OSError, ValueError, ...)` 收成 receipt reason，訊息字串不變。
    - `lumos` 入口的 `dispatch` 把 `ValueError` 收成結構化結果。
    - handbook 的 `model_command` 把逾時轉回 `TimeoutExpired`；中斷維持修前行為，往上丟。
  - 兩份 `test_quality_scan.py` 對同一個假 Semgrep（兩檔、每個都 hang、2 秒後送 SIGTERM）的結果：

    | 入口 | 修前 | 修後 |
    |---|---|---|
    | 直接執行 | 約 40 秒後 rc2，輸出完整 JSON | 約 0 秒 rc1，traceback，無 JSON（作者已寫為代價） |
    | 經 `lumos test-quality scan` | 約 40 秒後 rc2，完整 JSON | 約 0.1 秒 rc2，`{"verdict":"not_assessed","complete":false,"reason":"execution interrupted by signal 15"}` |

    兩版的 worker 都已清掉，經 lumos 入口沒有 traceback 外洩。
  - SIGTERM 落在 `terminate_group` 的 `killpg` 與 `wait` 之間：`group_stopped` 仍為 False，`finally` 會再清一次，沒有洞。
  - SIGTERM 落在 `finally` 第一行還原 handler 之後、`killpg` 之前，會留下 backend 群組。這是修前就有的結構，這次 diff 沒碰，我也沒能機械重現，所以不列 finding。

- **鏡頭 2，handbook 改走共用 runner**
  - 非 UTF-8 輸出：`text=True` 的修前版對 `b'\xff\xfe'` 丟 `UnicodeDecodeError`，修後回 `'�� bad'`，是改善。
  - `\r\n`：修前會被 `text=True` 轉成 `\n`，修後原樣保留，對 JSON 行解析無影響。
  - 逾時時的部分輸出：假模型印 200 KB 與 `last` 後睡眠，兩版的 `TimeoutExpired.stdout` 都是 200006 字元且尾端都是 `last\n`，完整性一致。
  - 關於「半寫的檔」：`historical_handbook_trial` 也直接呼叫 `run_model`，所以它與 REG4-1 同源，不另立 finding。
  - 手冊測試 19 項全綠。
  - `process_runner_sha256` 用 `read_text()` 讀檔，與既有 `runner_sha256` 的讀法一致。

- **鏡頭 3，adapter 延後 import**
  - 只有 `scan` 與 `lumos` 兩個檔，沒有 `test_quality.py` 和 adapter：修前 `--help` 直接 traceback，修後正常印出 usage，與 WHY 行「遞移缺檔不應使 help 失效」一致。
  - 缺 adapter 時，經 lumos 入口的結構化回報兩版相同。
  - 帶 `--semgrep` 的多檔掃描：adapter 現在在第一個非 Python 檔才載入。import 失敗時，經 lumos 入口仍是結構化結果；直接執行仍是 traceback，與修前相同。

- **新測試能不能抓回歸**：變異一個、單測一個，都紅在目標斷言。
  - 把 import 搬回頂層：`test_python_scan_does_not_need_semgrep_runner_bundle` 紅。
  - 拿掉 `except CaptureInterrupted: raise`：`test_sigterm_during_semgrep_stops_scan_and_backend` 紅。
  - 拿掉 `except CaptureTimeout`：`test_semgrep_backend_outcomes_stop_stream_holding_worker` 的 hang 子案例紅。
  - 把逾時的部分輸出清空：`test_model_timeout_keeps_partial_stream` 紅。

兩條 ★INVARIANT★ 與既有 WHY：

- **測試假綠形態**：新測試都有前置斷言，包含 `'core runner really absent'`、`'worker really shared the model stream'`、`'first backend really started before the signal'`，上面的變異也證實它們不會假綠。
- **lumos-cli-lifecycle**：diff 在 `scripts/lumos` 只改了 `_TEST_QUALITY_BUNDLE_DIGESTS` 一行，沒碰 sentinel 或 `CLAUDE.md` 注入，不影響。
- **test-quality-scan 的 WHY**：不但沒破壞，standalone `--help` 反而修好了。
- 改到的四個家的 WHY／PITFALL 行與實際行為一致。小瑕疵：scan 那條寫「帶 `--semgrep` 時仍要整組 bundle」，實際只掃 Python 檔時不載入 adapter，這不算 finding。

三問：

1. **原問題修復效果**
   - claim：已退出的模型留下握管線子程序，不再被誤判逾時。
   - input：`test_exited_model_with_stream_holding_worker_is_not_timeout`，並用變異驗證。
   - expected：rc0 且約 0.3 秒內回傳。
   - before：作者筆記說修前約 3 秒後被判逾時。我沒有重跑修前，標未判定。
   - after：19 項全綠。
   - comparison：行為與預期一致。
   - attribution：有證據的修復。

2. **正常、錯誤與相鄰路徑**
   - claim：CLI capture、Semgrep、handbook 的逾時與中斷分類都正確。
   - input：見鏡頭 1 與 REG4-1。
   - expected：逾時／中斷各自走自己的分類，且不洩漏 traceback。
   - before / after：見上表，只有 REG4-1 是新的差異。
   - comparison：REG4-1 是修後新增的失敗模式。
   - attribution：有證據的修復回歸。

3. **新發現案例的修前修後**
   - claim：輸出超過 10 MiB。
   - input：假 `claude` 印 11,011,000 位元組。
   - expected：該場被記成無效，評測繼續。
   - before：`valid=False`，繼續。
   - after：`ValueError`，整場中止，事件檔不存在。
   - comparison：行為變差。
   - attribution：有證據的修復回歸。

未驗範圍：

- 修前「3 秒逾時」的原始紅燈沒有重跑。
- 首次執行 `test_test_quality_scan.py` 曾有 1 項失敗；之後在同一份修後檔案上連跑 6 次、加 CPU 負載再跑 3 次，都是 OK，沒有找到失敗原因，也沒有可重現的場景，所以不列 finding。
- `finally` 第一行之後、`killpg` 之前的 SIGTERM 時序窗口，無法機械重現。
- 完整 `test_lumos.py` 全套沒有跑，Windows 不在範圍。

我的實驗檔都放在 `/tmp/lumos-seat-work/code-test-quality-r4-repair/回歸正確性-sonnet/`，變異副本已刪。

總結最嚴重 severity: minor；blocking: 0
