severity: major

（以下所有實驗都在 `/tmp/lumos-seat-work/code-test-quality-r4-repair/測試殺傷力-sonnet/repo`，用 `python3.14`。每次 mutation 前都先清 `__pycache__`。mutation 改到 bundle 檔時，同步把 `scripts/lumos` 裡該檔的 sha256 改成新值。這樣才不會被「配套版本不一致」的部署檢查誤紅，那種紅不算有效偵測。）

---

ID: MUT-1
severity: major
blocking: true
引句:「rc, out, _ = module.run_capture_command(command, 1)」
file: `scripts/test_test_quality_cli.py:455`（修後新增的 `test_failed_capture_stops_worker_that_inherits_streams`）

敘述：
- 這支測試名稱宣稱「worker 被停掉」，也是本輪唯一讓 worker 持有管線的案例。
- 但它只斷言 `rc == 1` 和 `out == b"launcher-failed"`，沒有 pid，也沒有任何 worker 存活檢查。
- 它只能看出「函式有沒有拖到 timeout」，看不出「worker 有沒有被清掉」。
- 所以如果程式碼變成 launcher 退出就直接返回、但沒清程序群，它照樣全綠。
- 最小重現（對 `scripts/test_quality.py` 做 M3）：把 launcher 退出分支的 `terminate_group(proc)` 換成 `break`，保留 `group_stopped = True`。
  - 實際結果是 worker 洩漏了：mutation 跑完後 `ps` 看到 `python -c import time; time.sleep(60)` 留著，要手動 kill。
  - `test_failed_capture_stops_worker_that_inherits_streams` 在整份 `test_test_quality_cli.py` 裡沒有出現在失敗清單，仍然 OK。
  - 這個 mutation 是被別的測試抓到的：`test_failed_capture_stops_stream_detached_worker`、`test_semgrep_backend_stops_worker_after_launcher_exit` 都紅在 `assertFalse(self.alive(pid))`。
  - 但那兩支的 worker 都是 `stdout=DEVNULL`，沒有持有管線。
- 結果是「launcher 退出且 worker 持有管線」這條路徑，沒有任何測試斷言 worker 真的被清掉。
- 這正好對應鏡頭第 4 點，也違反 ★INVARIANT★「前置斷言證明現場成立」：沒有證明 worker 啟動，也沒有證明 worker 之後死亡。
- 其他 mutation 倒是會被抓到：拿掉 poll 分支（M1）或拿掉 `select` 的 0.1 秒上限（M11），這支都紅，錯誤是 `ValueError: timeout; never detected`。
- 所以它只間接驗證「不 hang」，不驗證「不洩漏」。

歸因：有證據的修復回歸。此測試和對應修補都是本輪新增，修前版沒有這支測試。

兩版命令與結果：
- 修後 `c4982cb1`，套 M3 後跑 `python3.14 scripts/test_test_quality_cli.py`：Ran 46，失敗只有 `test_failed_capture_stops_stream_detached_worker`，inherits 測試通過，worker 洩漏。
- 修前 `10d40f30` 的產品碼搭配修後測試，跑 `-k inherits`：`ValueError: timeout; never detected`。能紅，但那是因為舊版 timeout 上限被打到，不是因為偵測到洩漏。

---

ID: MUT-2
severity: minor
blocking: false
引句:「except ValueError as exc:
        if str(exc) == 'timeout; never detected':」
file: `scripts/test_quality_semgrep.py:86`

敘述：
- Semgrep 後端逾時的分類（改成靠字串比對 `'timeout; never detected'`）完全沒有測試。
- 把比對字串改成 `'timeout'`（M5）後，逾時會被誤歸成 `status=unavailable`、reason 變成原字串，整份 scan 測試和 cli 測試仍全綠（24/24、46/46）。
- 在修前版 `git grep` 找 `backend timed out`、`status.*timeout`、`never detected`，這三個詞在兩個測試檔都沒有命中。
- 所以這是原本就沒測，不是本輪才漏掉的。
- 但本輪改寫了這個 except 結構，正好是逾時分類的高風險改動點。

歸因：有證據的原有漏查（修前同樣沒有測試）。

兩版命令與結果：
- 修前和修後都跑 `git grep`，結果無命中。
- 修後套 M5 並重算 digest，兩份測試檔都 OK。

---

ID: MUT-3
severity: minor
blocking: false
引句:「returncode, stdout, _ = run_capture_command(command, 40, cwd=root, env=env)」
file: `scripts/test_quality_semgrep.py:73`

敘述：
- 本輪給 `run_capture_command` 新增了 `cwd` 和 `env` 參數，對應的測試沒有任何一支驗證 `cwd` 或 `env` 有傳進去。
- 兩支新 Semgrep 測試用的假 semgrep 只印 JSON，不讀 cwd，也不讀 `SEMGREP_*` 環境變數。
- M7（拿掉 `cwd=root`）和把 `env=env` 弄壞，都在 scan 24/24、cli 46/46 全綠。
- 而 `cwd` 和 `env` 正是「不載入來源專案設定」這個防護的載體。
- 修前版是 `subprocess.run(..., cwd=root, env=env)`，同樣沒有測試守這兩個參數。

歸因：有證據的原有漏查。

兩版命令與結果：
- 修後套 M7 並重算 digest，兩份測試檔都 OK。
- 修前沒有對應測試。

---

ID: MUT-4
severity: minor
blocking: false
引句:「self.assertEqual(out['inputs'][0]['status'], 'scanned')」
file: `scripts/test_test_quality_scan.py:213`

敘述：
- 缺的案例：Semgrep 後端「非零退出」或「逾時」時留下 worker，沒有任何測試。
- 這支 worker 測試的假 semgrep 退出碼是 0，而且 worker 是 `stdout/stderr=DEVNULL`，不持有管線。
- 所以它沒測到新程式碼的主要路徑：launcher 退出時 worker 還持有管線。
- 它能紅，純粹是因為舊版 `subprocess.run` 沒清程序群。
- 這支測試也無法偵測 M10（拿掉 finally 的 `terminate_group`）：整份 scan 測試仍是 OK。
- M10 只被 `test_cancelled_capture_stops_child` 抓到，那是 CLI 測試，不是本席要驗的目標測試。

歸因：未判定。修前同樣沒有這個案例，但本輪新增了這條路徑，不能全歸給原有漏查。

---

已讀，無 finding：
- `test_semgrep_out_of_range_is_structured_unavailable`
  - 修前和修後都綠（修前版跑 `-k out_of_range` 為 OK），所以它是行為保存測試，不是修復偵測器。
  - 它的 `99` 行號超出範圍，是獨立於實作的輸入。
  - 它斷言 `status=unavailable`、`complete=False`，沒有重抄實作的字串。
- corpus 案例 `test_corpus_runner_reports_unavailable_languages`
  - 修前版也綠，因為舊 semgrep 不 import `test_quality`，所以它不能證明修復。
  - 但守住新的遞移相依：M6（corpus 少拷 `test_quality.py`）會紅在 `assertEqual` 的集合差異（`Items in the first set but not the second`），是有效偵測。
- global `--vault` 的 `cwd=self.root` 改動
  - 該測試在修前、修後都綠，是 cwd 修正。
  - 沒有行為上的問題。
- `scan` 標準對照案例移除 `cwd=self.root`
  - 修前、修後都綠，被測腳本用絕對路徑執行，所以沒有影響。

---

Mutation 表：

| 測試名 | mutation | 修後結果 | 套 mutation 結果 | 紅在哪個斷言 | 是否有效偵測 |
|---|---|---|---|---|---|
| `test_semgrep_backend_stops_worker_after_launcher_exit` | 還原產品碼到 `10d40f30`（subprocess.run） | 綠 | 紅 | `assertFalse(self.alive(pid))` | 有效 |
| `test_semgrep_backend_stops_worker_after_launcher_exit` | M3：launcher 退出分支改 `break`、不殺群 | 綠 | 紅 | `assertFalse(self.alive(pid))` | 有效 |
| `test_semgrep_backend_stops_worker_after_launcher_exit` | M1：拿掉 poll 殺群分支 | 綠 | 綠 | 無 | 無法偵測。行為等價，因為 finally 仍會殺 |
| `test_failed_capture_stops_worker_that_inherits_streams` | 還原產品碼到 `10d40f30` | 綠 | 紅 | `ValueError: timeout; never detected`（逾時代打） | 弱。只是 timeout 錯誤，不是目標斷言 |
| 同上 | M1：拿掉 poll 殺群分支 | 綠 | 紅 | 同上 `ValueError`（逾時代打） | 弱 |
| 同上 | M11：拿掉 `select` 的 0.1 秒上限 | 綠 | 紅 | 同上 `ValueError`（逾時代打） | 弱 |
| 同上 | M3：launcher 退出改 `break`、不殺群（洩漏） | 綠 | 綠，worker 洩漏 | 無 | **無效（MUT-1）** |
| `test_semgrep_out_of_range_is_structured_unavailable` | 還原產品碼到 `10d40f30` | 綠 | 綠 | 無 | 預期內，行為保存測試 |
| corpus 案例 | 還原產品碼到 `10d40f30` | 綠 | 綠 | 無 | 預期內，行為保存測試 |
| corpus 案例 | M6：少拷 `test_quality.py` | 綠 | 紅 | `assertEqual` 集合差異 | 有效 |
| global `--vault` 案例 | 還原產品碼到 `10d40f30` | 綠 | 綠 | 無 | 預期內，cwd 改動非修復偵測 |
| 整份 scan 測試 | M5：逾時比對字串 | 全綠 | 全綠 | 無 | 無效（MUT-2） |
| 整份 scan 測試 | M7：拿掉 semgrep 的 `cwd=root` | 全綠 | 全綠 | 無 | 無效（MUT-3） |
| 整份 scan 與 cli 測試 | M10：拿掉 finally 的 `terminate_group` | scan 綠 | scan 仍綠，cli 紅在 `test_cancelled_capture_stops_child` | `assertFalse(self.alive(pid))` | 只有 cancel 測試抓到（MUT-4） |

---

三問與證據：

**① 原問題的修復效果有何行為證據？**
- claim：Semgrep 後端在 launcher 退出後會清理 worker。
- input：假 semgrep 啟動一個 `sleep 60` 的 worker 並寫 pid，之後輸出 JSON 並退出。
- expected：scan 回報 `scanned`，且 worker 在 2 秒內消失。
- before（`10d40f30` 產品碼）：`-k worker` 紅，`AssertionError: True is not false`。
- after（`c4982cb1`）：同測試綠。
- comparison：前紅後綠，修復有行為證據。
- 但 worker 是 `DEVNULL`，只證明「沒持有管線」這一條路徑。
- 持有管線的路徑只有 MUT-1 那支弱測試，它在洩漏版會綠。
- attribution：修復有證據；管線持有路徑的證明不足。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立？**
- 正常路徑：scan 24/24、cli 46/46 在修後版（`c4982cb1`）全綠。
- 超出範圍行號（結構化 unavailable）：修前、修後都綠，未退化。
- 逾時路徑：行為上有保留（同一個 `ValueError` 被改成字串分類），但沒有任何測試守它（MUT-2）。
- 未驗範圍：Semgrep 非零退出、輸出超過 10 MiB、SIGTERM 中斷時 Semgrep 路徑的 worker 清理，沒有對應測試。
- attribution：修前同樣無測試。

**③ 新發現的同一案例在修前、修後各是什麼結果？**
- MUT-1：修前沒有這支測試，所以「同一案例」的修前結果是 N/A，只能說修前產品碼在逾時處報錯。
- MUT-2 / MUT-3：修前、修後都沒有守衛，結果一致，都是 mutation 全綠。
- MUT-4：修前也沒有對應案例。

**固定席必答（兩條 ★INVARIANT★）：**
- `Systems/測試假綠形態`：這份 diff 沒有破壞它，但 MUT-1 顯示本輪新增的 inherits 測試沒完全滿足它。它沒有前置斷言證明 worker 啟動，也沒有斷言 worker 死亡。
- `Systems/lumos-cli-lifecycle`：沒有破壞。diff 只改 `scripts/lumos` 裡一行 bundle 摘要常數，沒碰 re-inject 的 sentinel 邏輯，也沒碰 CLAUDE.md 寫入路徑。

**未驗範圍：**
- Windows。
- 真實 Semgrep 二進位。
- 全套 3700 案例。
- 圖譜筆記（`.md`）的準確性。

清理狀況：實驗期間洩漏的兩個 `sleep 60` 程序都已手動 kill，最後 `ps` 檢查為 0 筆。審查 repo（`/tmp/lumos-readme-oct-audit`）沒有改動。

總結最嚴重 severity: major；blocking: 1
