severity: minor

整份最高為 minor。三個修補群組的行為都有兩版證據，bundle 摘要也對得上；找到兩條 minor。

## Findings

ID: BND4-1
severity: minor
blocking: false
引句:「        os.killpg(proc.pid, signal.SIGKILL)」
file: `scripts/test_quality.py:65`（a2f30b19 的 `terminate_group`）

launcher 剛好在預算邊界附近退出時，macOS 上 `terminate_group` 的 killpg 會丟 `PermissionError`（EPERM）。launcher 已是殭屍、同群無其他成員時就會這樣。例外在 `finally` 裡丟出，蓋掉原本的 `CaptureTimeout`，或蓋掉正常回傳。

後果因呼叫端而異：
- **handbook `model_command`**：只轉 `CaptureTimeout`，所以 `PermissionError` 直接穿出 `run_model`。`main` 沒有 try，整場付費實驗中止，而不是記成 model-timeout。
- **Semgrep backend**：`OSError` 會被收成 `unavailable`，原因文字是 "Operation not permitted"。這點是照程式碼推的，我沒另外跑。

歸因：有證據的原有漏查。修前 7d1975e8 的 runner 與 handbook 自寫版都只接 `ProcessLookupError`。修後 handbook 改走共用 runner，等於繼承同一個洞。修補沒有引入它，也沒有補上它。

兩版同一命令：對 `/usr/bin/true` 連跑 300 次，逾時預算 `0.0005*(i%10)` 秒。
- 修前：ok 209、timeout 70、PermissionError 21。
- 修後：ok 199、CaptureTimeout 86、PermissionError 15。
- 預算 5 秒時兩版都 500 次全 ok，所以只在退出貼著期限那一刻發生。

ID: BND4-2
severity: minor
blocking: false
引句:「大輸出檢查：9 MiB 經共用 runner 與模型命令各約 0.04 秒，20 萬行事件流 0.1 秒，行程記憶體高點約 72 MiB，超過 10 MiB 仍回結構化錯誤。」
file: `governance/eval/test_quality_handbook.py:229`（`model_command`）；呼叫端 `governance/eval/test_quality_handbook.py:392`

`model_command` 改走共用 runner 後，模型輸出（stdout 或 stderr）超過 10 MiB 會丟 `ValueError('output exceeds 10 MiB')`。`run_model` 只接 `TimeoutExpired`，`main` 的 job 迴圈沒有 try。結果是整場實驗以 traceback 中止，這一場已付費的原始事件不會寫進 `events.jsonl`。

驗證筆記說模型命令超限「仍回結構化錯誤」，這句對模型命令不成立。結構化錯誤只在 `lumos test-quality scan` 的 `dispatch` 才有，handbook 沒有。同一份 diff 的 handbook 筆記寫「歷來 61 份事件檔最大 72 KB，共用的 10 MiB 輸出上限不影響既有場次」，那句有量測，不算錯。

歸因：有證據的修復回歸。這是修補新加的行為差異，修前 handbook 自寫版沒有上限。

兩版同一命令：假 `claude` 放 PATH 上，呼叫 `ev.run_model(Path(tmp),'s','p','m',20,False,raw)`。

| 模式 | 修前 | 修後 |
|---|---|---|
| 剛好 10 MiB 的 stdout | 正常回傳（raw 10485760 位元組） | 正常回傳 |
| 10 MiB+1 的 stdout | 正常回傳（raw 10485761 位元組） | `ValueError` 逃出 `run_model` |
| 11 MiB 事件流 | 正常回傳 | `ValueError` 逃出 |
| 只有 stderr 11 MiB | 正常回傳 | `ValueError` 逃出 |

另外三個結果：
- 非 UTF-8 stdout：修前 `UnicodeDecodeError` 中止，修後 `decode(errors='replace')` 正常回傳，這是改善。
- 0 位元組：兩版都正常回傳。
- cwd 不存在：兩版都是 `FileNotFoundError`。

「PATH 找不到 claude」那一項我沒跑成。我把 PATH 縮得太窄，連 python3.14 都找不到，所以腳本沒執行。這項未驗。

已讀，無 finding：
- **巢狀程序群**：外層 runner 逾時或 SIGTERM 時，會 SIGKILL 外層群，scanner 內部 Semgrep 的獨立 session 變孤兒。我實測兩版都會（修前、修後 backend pid 都還活著）。patch 的 PITFALL 寫明「子程序主動 setsid 逃逸不在可攜式保證內」，且 capture 跑的是使用者測試命令而非 scanner，所以不標。
- **版本混裝**：只放 lumos、scanner、adapter、缺 `test_quality.py` 時，`lumos test-quality` 的 `--help`、`scan` 帶或不帶 `--semgrep`，都回結構化「測試品質工具未完整部署…請 lumos update」。直接執行 scanner 帶 `--semgrep` 會是 `ModuleNotFoundError` traceback。決策與 WHY 行都寫了這個代價，修前同樣是 traceback。
- **bundle 摘要**：我自己算了 a2f30b19 三個檔的 sha256，與 `_TEST_QUALITY_BUNDLE_DIGESTS` 逐字一致：semgrep `9d17becd…`、scan `f6796766…`、core `783da623…`。
- **handbook 的 `sys.path.insert(0, scripts)`**：`scripts/` 底下沒有跟 stdlib 同名的檔，沒有遮蔽問題。
- **逾時例外與記憶體**：`CaptureTimeout` 帶部分輸出，上限 10 MiB 加一個 64K 讀塊，兩路合計約 20 MiB 的複本，沒有翻倍失控。

## 固定席必答
- **`Systems/測試假綠形態`（★INVARIANT★）**：沒有破壞，而且新增的控制都帶前置斷言。
  - 前置斷言有三個：`worker-holds-stream`（worker 真的寫進同一條管線）、`record.exists()`（第一個 backend 真的啟動）、`core runner really absent`。
  - 我把新測試丟到修前程式碼上跑，修復類案例翻紅，見下一節。
- **`Systems/lumos-cli-lifecycle`（★INVARIANT★）**：不影響。對 `scripts/lumos` 的改動只有 `_TEST_QUALITY_BUNDLE_DIGESTS` 那一行，沒碰 re-inject、sentinel 或 CLAUDE.md 寫入路徑。
- **既有決策「選配適配器延後載入」**：保住，而且更完整。
  - `lumos test-quality` 的 `--help` 在缺 `test_quality.py` 時仍是結構化回應。
  - 純 Python 掃描不需要 `test_quality.py`。這條有控制：`test_python_scan_does_not_need_semgrep_runner_bundle` 在修前紅，修後綠。
  - 修前 `main()` 開頭就 import adapter，順序比 argparse 早；修後移到 `--semgrep` 實際遇到非 Python 檔時才 import。
  - 筆記裡 CaptureTimeout、CaptureInterrupted 的描述與程式一致；SIGTERM 的代價（直接執行以 traceback 非零結束、經 lumos 入口才結構化）我跑了兩條路徑都對。

## 三問與證據

**1. 原問題的修復效果有何行為證據？**

repair 案例：

| 案例 | 輸入 | 預期 | 修前 7d1975e8 | 修後 a2f30b19 | 歸因 |
|---|---|---|---|---|---|
| G1 handbook | 模型正常退出、留下握住 stdout 的子程序 | 立即 rc0，子程序被清掉 | 修後新測試丟到修前碼上：`test_exited_model_with_stream_holding_worker_is_not_timeout` ERROR | 19 項 handbook 控制全綠 | 有證據的修復，行為證據成立 |
| G2 SIGTERM | `lumos test-quality scan A B --semgrep <hang>`，第一個 backend 啟動後送 SIGTERM | 立即非零結束，不續掃下一檔 | 8 秒內沒停，backend 啟動了 2 個 | rc2、1.1 秒、reason 為 `execution interrupted by signal 15`、只啟動 1 個 backend 且已清 | 有證據的修復 |
| G4 延後載入 | 只帶 scan 與 semgrep、不帶 `test_quality.py`，純 Python 掃描 | 掃描完成 | `test_python_scan_does_not_need_semgrep_runner_bundle` FAIL | 綠 | 有證據的修復 |
| G1 Semgrep 三出口 | 成功、非零、逾時，worker 握住管線 | 狀態分別 scanned、error、timeout | 只有 `hang` 子測試紅；success 與 nonzero 在修前碼上本來就綠 | 28 項 scanner 控制全綠 | 見下一段 |

G1 Semgrep 的 `hang` 子測試在修前紅，原因是修前沒有 `BACKEND_TIMEOUT` 常數，測試把它調成 2 秒卻不生效，仍跑滿 40 秒。所以它證明的是常數存在，不是清理邏輯的差異。success 與 nonzero 兩個出口算 preserve 證據，不算 repair 證據。

**2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立？**

- 正常路徑與 preserve 案例都成立：
  - `test_model_timeout_keeps_partial_stream` 在修前碼上也綠，表示逾時仍轉成 `TimeoutExpired` 並帶部分輸出。
  - runner 的剛好 10 MiB 通過；10 MiB 加 1 失敗，訊息不變。
  - CLI capture 的 reason 文字不變。
- 錯誤路徑有兩處新差異或延續：handbook 的超限中止（BND4-2），與 EPERM 蓋掉逾時（BND4-1）。

**3. 新發現的同一案例在修前、修後各是什麼結果？** 已分別列在 BND4-1、BND4-2 的兩版命令與結果。

## 未驗範圍
- 沒用真 `claude` CLI 驗，只用假 `claude` 與假 `semgrep`。
- 未驗 PATH 找不到 `claude`（我把 PATH 縮得太窄，腳本沒跑起來）、真 Semgrep、Windows。
- 沒驗 SIGTERM 落在 `Popen` 回傳與 `proc` 賦值之間的視窗。
- 沒驗 PID/PGID 重用窗口，這個我給不出失敗場景，所以沒標。
- 沒驗直接執行 scanner 時 `--help` 缺 `test_quality.py` 的行為（只驗了 lumos 入口）。
- 實驗檔都在 `/tmp/lumos-seat-work/code-test-quality-r4-repair/邊界資源-sonnet/`，沒動 `/tmp/lumos-readme-oct-audit`。

總結最嚴重 severity: minor；blocking: 0
