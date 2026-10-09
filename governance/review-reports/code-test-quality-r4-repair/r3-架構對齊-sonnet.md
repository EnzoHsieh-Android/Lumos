severity: major

## 逐問結果

### 問 1　分層與依賴方向：不完全對齊（ARC-2、ARC-3）
- 新碼的位置沒問題。Semgrep 後端留在 `scripts/test_quality_semgrep.py`，runner 仍在 bundle 核心 `scripts/test_quality.py:68`。
- 但依賴方向變成互相依賴。
  - 既有方向是核心往下呼叫：`scripts/test_quality.py:181` 和 `:342` 惰性 import scan，`:348` import semgrep 的 `PATTERNS`。scan 到 semgrep 也是惰性 import（`scripts/test_quality_scan.py:286`）。
  - 本次 semgrep 在模組頂層反向 import 核心 `from test_quality import run_capture_command`（`scripts/test_quality_semgrep.py:10`）。形成 核心 → scan → semgrep → 核心 的圈。
  - 這個圈沒有真的循環 import，因為上面幾處都是惰性的。
- scan 的 `main()` 在 `scripts/test_quality_scan.py:286` 無條件 import semgrep，連沒開 `--semgrep` 的純 Python 掃描也會被拖進這個依賴。
- 以前 `test_quality_scan.py` 單獨執行時，不需要 `test_quality.py`。現在缺了 `test_quality.py` 就會失敗。
- 配套指紋清單已含 `test_quality.py`（`scripts/lumos` 的 `_TEST_QUALITY_BUNDLE_DIGESTS`），所以 bundle 內補齊了。
- `governance/eval/test_quality_corpus.py` 凍結副本補拷 `test_quality.py` 是這個依賴的後果，不另列。

### 問 2　命名與錯誤處理：結構對，兩處不一致（ARC-2、ARC-5）
- runner 新增的 `cwd=None, env=None` 關鍵字參數，跟鄰居 `model_command(cmd, directory, timeout)` 的做法相容。
- 日誌方式一致：這幾支都沒有日誌，錯誤一律進報告的 `reason`。
- 逾時分類不一致。
  - 專案其他地方都用型別分類：`subprocess.TimeoutExpired` 出現在 `governance/eval/test_quality_handbook.py:163`、`:239`、`:273`，`test_quality_corpus.py:63`，`test_quality_pilot.py:38`，`historical_test_quality.py:64`，`test_quality_evidence.py:106`，`historical_handbook_trial.py:209`。
  - `scripts/test_quality.py:89` 和 `:97` 把逾時包成 `ValueError('timeout; never detected')`，CLI capture（`:262`）只把它當 `reason` 字串。
  - 只有 semgrep 這次改成比對訊息字串，是專案唯一用 `str(exc)` 分類的地方。這個字面值在兩個檔各寫一份，沒有共用常數。
- 新增的測試輔助 `alive` 在兩個測試檔各有一份（ARC-5）。

### 問 3　第二種做法：有（ARC-1 major）
- handbook 的 `model_command` 是第二套手寫的程序群清理，沒有共用 runner，行為也不同（見 ARC-1）。
- 其餘 runner 之外的 `subprocess.run` 啟動點見下方清單。

## 程序啟動點清單（c4982cb1）

| 位置 | 判定 |
|---|---|
| `scripts/test_quality.py:80` `run_capture_command`（`Popen`，`start_new_session=True`） | 共用 runner 本體 |
| `scripts/test_quality.py:246` CLI capture | 走共用 runner |
| `scripts/test_quality_semgrep.py:73` Semgrep 後端 | 本次改走共用 runner |
| `governance/eval/test_quality_handbook.py:235` 到 `:251`（`model_command`，自寫 `Popen` + `killpg`） | 第二種做法（ARC-1） |
| `governance/eval/test_quality_corpus.py:50`（`subprocess.run`，timeout 50，跑凍結 scanner） | 有理由另走：短命的信任測試。但 scanner 內的 Semgrep 現在在獨立 session，corpus 逾時只殺 scanner（ARC-4，⚠） |
| `test_quality_evidence.py:99`、`:131`、`test_quality_pilot.py:35`、`historical_test_quality.py:62`、`historical_handbook_trial.py:205`、`test_quality_handbook.py:156` 等 | 有理由另走：信任夾具或子程序的一次性 `subprocess.run`，都帶 timeout、捕 `TimeoutExpired` |
| `scripts/lumos:152`、`:178`、`:259`、`:1587`、`:5785`、`:6011` | 與測試品質無關（Python 探測、`uv`、`git`）。我只用關鍵字篩選，沒有逐段讀 test-quality 子命令區，這一點不能保證 |

## Findings

ID: ARC-1
severity: major
blocking: true
引句:「CLI capture 與 handbook model runner 都建立獨立 POSIX 程序群，必須採同一項返回前清理政策」
file: `governance/eval/test_quality_handbook.py:226`（對照 `scripts/test_quality.py:68`、`:49`）
這份修補宣稱「維持一套程序群清理政策」，實際上是兩份實作。
- `model_command` 用 `Popen` 加 `communicate()` 加 `os.killpg` 自己清群（`:235`、`:241`、`:251`）。
- 共用 runner 用 selector 輪詢加 `proc.poll()` 偵測 launcher 退出，再 `terminate_group`。
- 本次新補的缺口是「worker 繼承 stdout/stderr 時，已退出的 launcher 被誤判逾時」。`model_command` 的 `communicate()` 要等管線 EOF，worker 握著管線時就會拖到逾時。
- 本次 diff 把這個缺口只補在共用 runner 這邊，`model_command` 沒動，而 PITFALL 文字寫兩者「同一項」。
- 之後接手的人要在兩套程序群語意之間猜。
- 若 handbook 屬 `governance/eval`、不隨 bundle 發布因此不能 import `scripts/test_quality.py`，那是正當理由，但筆記沒寫。我的判法是 major。想當成可接受分歧，請在筆記寫明理由與回頭條件。

ID: ARC-2
severity: minor
blocking: false
引句:「if str(exc) == 'timeout; never detected':」
file: `scripts/test_quality_semgrep.py:89`（對照 `scripts/test_quality.py:89`）
這是專案唯一用例外訊息字串分類的地方。其他啟動點都用 `subprocess.TimeoutExpired` 型別。runner 的訊息一改，semgrep 的 `timeout` 狀態就悄悄變成 `unavailable`。結構上沒有第二套流程，所以列 minor。

ID: ARC-3
severity: minor
blocking: false
引句:「from test_quality import run_capture_command」
file: `scripts/test_quality_semgrep.py:10`（對照 `scripts/test_quality_scan.py:286`、`scripts/test_quality.py:348`）
適配器反向依賴 CLI 核心，形成互相依賴，細節見問 1。scan 單獨執行不再自足。⚠ 交編排者：bundle 內有多個模組、沒有既有的「共用底層模組」慣例可對，我不確定這算跨層還是可接受的同 bundle 依賴，暫列 minor。

ID: ARC-4
severity: minor
blocking: false
引句:「(root/'test_quality.py').write_bytes((ROOT/'scripts/test_quality.py').read_bytes())」
file: `governance/eval/test_quality_corpus.py:50`
corpus 用普通 `subprocess.run(..., timeout=50)` 啟動 scanner。scanner 內的 Semgrep 現在在獨立 session，corpus 逾時殺掉 scanner 時，那個群不會被清。⚠ CLI capture 路徑本來就有同樣性質（逾時走 `SIGKILL`，runner 的 `SIGTERM` 處理不會觸發），專案沒有既有做法可對，交編排者。

ID: ARC-5
severity: minor
blocking: false
引句:「return run.returncode == 0 and bool(run.stdout.strip()) and not run.stdout.strip().startswith('Z')」
file: `scripts/test_test_quality_scan.py:19`（對照 `scripts/test_test_quality_cli.py:364`）
測試輔助 `alive` 逐字複製了一份，並額外在 `semgrep_module()` 用 `sys.path.insert` 繞開 import（`scripts/test_test_quality_scan.py` 約 `:30`）。鄰居 cli 測試沒有這種做法。

不對齊共 5 條，其中 major 1 條
總結最嚴重 severity: major；blocking: 1
