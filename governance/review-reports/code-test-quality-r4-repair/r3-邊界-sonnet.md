severity: minor

ID: BND-1
severity: minor
blocking: false
引句:「except ValueError as exc:」
file: `scripts/test_quality_semgrep.py:88`（審材中 `if str(exc) == 'timeout; never detected'` 同段）
`run_capture_command` 把 SIGTERM 轉成 `ValueError('execution interrupted by signal 15')`。Semgrep 後端現在用 `except ValueError` 把它收成 `status=unavailable`，掃描照常往下做，結束時回 rc=2。修前 SIGTERM 會直接終止掃描器。
- 重現：用 `Test.swift` 和 `Test2.swift`，後端是睡 30 秒不輸出的假 semgrep。啟動 `test_quality_scan.py Test.swift Test2.swift --json --semgrep ./fsleep`，2 秒後送 SIGTERM。
- 修後（c4982cb1）：rc=2。第一個檔回 `unavailable` / `execution interrupted by signal 15`，第二個檔繼續跑到結束，回 `unavailable` / `Expecting value`。終止請求被吞掉，多檔掃描可再拖數十秒。
- 修前（10d40f30）：rc=143，立刻終止。
- 修前在 SIGTERM 時會漏掉 semgrep 程序（pgrep 見殘留，已清掉），修後會清群組；這個副作用是改善。
- 命令：`kill -TERM $P; wait $P; echo rc=$?`
- 歸因：有證據的修復回歸。兩版都實跑過，行為差異在「終止請求被吞掉」。

ID: BND-2
severity: minor
blocking: false
引句:「returncode, stdout, _ = run_capture_command(command, 40, cwd=root, env=env)」
file: `scripts/test_quality_semgrep.py:97`（審材同行）；上限在 `scripts/test_quality.py:65`
Semgrep 的 stdout 或 stderr 超過 10 MiB 現在會拒收，修前不受限。
- 重現：假 semgrep 往 stderr 寫 11 MiB，再印出合法 JSON，其中 `paths.scanned` 含 source。
- 修前：`scanned`。
- 修後：`unavailable` / `output exceeds 10 MiB`。
- 結果仍是結構化的，沒有崩潰或掛住，但屬於新的狀態變化。
- 命令：`python3.14 scripts/test_quality_scan.py Test.swift --json --semgrep ./fgood`
- 歸因：有證據的修復回歸，是共用 runner 的上限帶進後端。實際 Semgrep 加 `--quiet` 時 stderr 很小，影響低。

已讀，無 finding：
- stdout 為空、非 UTF-8、合法 JSON 但形狀錯（`[]`、`{}`）：修前修後都回 `unavailable`，reason 也相同。非 UTF-8 的 reason 是 utf-8 codec 的訊息，空 stdout 是 `Expecting value`，形狀錯是 `invalid Semgrep report shape`。
- 逾時：`ValueError('timeout; never detected')` 的字串比對可靠。其他 ValueError（含 JSON 與 UnicodeDecodeError）不會等於這個字串，不會被誤判成 timeout。
- cwd 與 env：env 是完整複製 `os.environ` 後再加 `SEMGREP_*` 兩項。cwd 是剛建的暫存目錄，source 是絕對路徑，所以相對路徑問題不存在。這兩點與修前 `subprocess.run` 一致。
- CLI 測試的 cwd 改動：`--vault` 那條 `subprocess.run` 新增 `cwd=self.root`，而 `sample.py` 是相對路徑，所以 fixture 會被讀到。另一處移除 `cwd` 的測試給的是絕對路徑 `test_file`，不受影響。
- bundle digest：我自己用 `git show c4982cb1:scripts/<檔> | shasum -a 256` 算過，三個與 `scripts/lumos` 的常數逐位相同。分別是 semgrep 8300fc5d…、scan bb807bd4…、test_quality fb5401e4…。
- 部署載入：`test_quality_scan.py` 以腳本執行，`sys.path[0]` 是同目錄，semgrep 的 `from test_quality import` 會拿到同一份被摘要守住的檔。`_VENDORED_TOOLKIT` 已含這三檔。
- corpus 凍結副本：`governance/eval/test_quality_corpus.py` 已複製 `test_quality.py`。`test_quality.py` 只 import 標準庫，沒有其他遞移相依。凍結 scanner 以腳本執行，`sys.path[0]` 是暫存根目錄，不會 import 到 repo 裡的活檔。實跑 corpus runner 正常輸出，scanner 24 項與 CLI 的 inherits 測試通過。
- PID/PGID：`poll()` 回收 launcher 後才 `killpg`。群組無成員時 `ProcessLookupError` 被吞掉。PGID 被重用必須剛好換成另一個群組長，我沒有構造出可重現的場景。
- PermissionError：我沒有構造出可重現的場景。讀碼可知，若 `killpg` 丟 PermissionError，`group_stopped` 不會被設成 True。`finally` 會再呼叫 `terminate_group` 並再丟一次，同時跳過 `proc.stdout.close()` 和 `proc.stderr.close()`。這個結構在修前（`finally` 無條件 `terminate_group`）已存在，列為未判定。

★INVARIANT★ 兩條：
- 測試假綠形態：新測試 `test_semgrep_backend_stops_worker_after_launcher_exit` 有前置斷言 `pidfile.exists()`，證明 worker 真的被啟動。`test_failed_capture_stops_worker_that_inherits_streams` 的前置是 rc==1 且收到輸出。這個測試沒有直接證明 worker 被殺；沒被殺時，pipe 不關，會因超時丟 ValueError 而紅。我沒有逐一做還原翻紅，這部分未驗。
- lumos-cli-lifecycle：本 diff 在 `scripts/lumos` 只改一行摘要常數，與 sentinel 內外的注入邏輯無關，所以不影響 byte-equal 保留。

三問：
1. 原問題修復效果有行為證據嗎？有。群組清理的前置與測試在 c4982cb1 全綠：scan 測試檔 24 項通過，CLI 的 `-k inherits` 通過。我沒有在 10d40f30 上重跑「worker 殘留」測試，修前紅燈部分未獨立驗證。
2. 修補處的正常、錯誤與相鄰路徑是否成立？大致成立。空、非 UTF-8、形狀錯、timeout 的 status 與 reason 修前修後相同或更結構化。唯二差異是 BND-1 與 BND-2。
3. 新發現同一案例修前修後各是什麼結果？見 BND-1（rc=143 對 rc=2 且續掃）與 BND-2（`scanned` 對 `unavailable`）。

未驗範圍：真 Semgrep 二進位、PGID 重用、PermissionError、Windows。

總結最嚴重 severity: minor；blocking: 0
