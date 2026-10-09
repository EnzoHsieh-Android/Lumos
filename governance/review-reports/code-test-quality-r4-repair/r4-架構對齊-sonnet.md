severity: minor

三個入口(CLI capture、Semgrep backend、handbook 模型命令)確實走同一個 `run_capture_command`,依賴方向也有先例。有兩點跟既有做法不一樣,結構都對,所以判 minor。另有兩點判不準,標 ⚠ 交編排者。

**程序啟動點清單**(a2f30b19)

- 走共用 runner:
  - `scripts/test_quality_semgrep.py:75`(Semgrep backend)。
  - `governance/eval/test_quality_handbook.py:231`(model_command)。
  - CLI capture:本輪沒去追 `scripts/lumos` 裡的呼叫端,只確認 `scripts/test_quality.py` 只有一個 Popen(第 93 行),且 `scripts/test_quality*.py` 沒有別的啟動點。
- 另走 `subprocess.run`,沒有 `start_new_session` 或 killpg:
  - `governance/eval/test_quality_corpus.py:50`,跑凍結 scanner,timeout 50。
  - `governance/eval/test_quality_evidence.py:99` 和 `:131`,timeout 10。
  - `governance/eval/test_quality_pilot.py:35`,timeout 30。
  - `governance/eval/test_quality_handbook.py:159`(run_test),執行模型產生的測試碼,timeout 15。
  - `governance/eval/test_quality_handbook.py:367` 和 `:387`(git init 與 verify wrapper)。
  - `governance/eval/historical_handbook_trial.py:205` 和 `historical_test_quality.py:62`。
- `scripts/lumos` 另有自己的 `start_new_session` + killpg 實作,在 `scripts/lumos:16960`、`27314`、`45717`。這是 lumos 本體的既有做法,和測試品質線無關。

**問 1 分層與依賴方向**

對齊。
- 新例外類別與 runner 都放在 `scripts/test_quality.py`,被 `scripts/test_quality_semgrep.py:10` 與 `governance/eval/test_quality_handbook.py:24` 往下呼叫,沒有跨層直呼。
- 評測腳本用 `sys.path.insert(0, ROOT/'scripts')` 後 import scripts 的做法,跟 `governance/eval/ablation_lumos_first.py:28` 一樣。方向是 eval 指向 scripts,scripts 不 import governance,沒有新的依賴圈。
- `historical_handbook_trial.py:19` 會間接帶進 `scripts/test_quality`,也沒有圈。
- `scripts/` 底下的檔名沒有跟標準庫衝突。
- `scripts/test_quality_scan.py` 把 semgrep 適配器的 import 移到迴圈內。這符合 `docs/lumos-toolchain-knowledge/Systems/test-quality-scan.md:47` 的「選配適配器延後載入」決策。

不對齊有一條,見 ARC4-1。⚠ 見 ARC4-4。

ID: ARC4-1
severity: minor
blocking: false
引句:「from test_quality import CaptureTimeout, run_capture_command」
file: `governance/eval/ablation_lumos_first.py:28`
- 先例在 `sys.path.insert` 後的 import 行寫了 `# noqa: E402`,並用註解說明「單一實作來源」。
- 本檔的 import 行沒有 `# noqa: E402`。
- repo 根目錄沒找到 ruff 設定檔(ruff.toml、pyproject 都沒有),所以不確定專案是否啟用 E402。若啟用,這行會紅燈;全域 ruff 掛鉤(`~/.claude/hooks/prepush-lint.py`)的設定沒查。

⚠ 另有一點:這裡的 `sys.path.insert` 放在模組頂層,而同檔另一個先例 `governance/eval/test_quality_pilot.py:35` 是用 `env PYTHONPATH` 傳給子程序。兩種都有先例,不判錯。

**問 2 命名與錯誤處理**

部分不對齊。
- repo 其餘 `.py` 與 `scripts/lumos` 搜不到任何自訂例外類別(`class …(…Error|ValueError|Exception…)`)。`CaptureTimeout` 和 `CaptureInterrupted` 是專案第一次出現的自訂例外。
- 跟既有「ValueError 加訊息字串」的做法不同,但它繼承 ValueError、保留原訊息,既有的 `except ValueError` 呼叫端不會壞。這算是把字串比對的做法換成型別分類,方向是收斂,結構對。
- 把分類改成型別以後,`CaptureTimeout` 的建構子簽章帶 `stdout/stderr`,跟內建例外慣例有差,但夠用。

ID: ARC4-2
severity: minor
blocking: false
引句:「raise CaptureInterrupted('execution interrupted by signal ' + str(signum))」
file: `scripts/test_quality.py:83`
- 專案原本沒有自訂例外,兩個新類別是第一批。
- 命名沒有套用 `*Error` 後綴;例外類別慣例是 `*Error`,但 repo 沒有先例可比,所以只列 minor。
- 讓 `CaptureInterrupted` 繼承 ValueError,意味著 `except ValueError` 仍會吞掉它。Semgrep 端用先 `except CaptureInterrupted: raise` 擋掉(`scripts/test_quality_semgrep.py` 的 except 區塊)。其他呼叫端沒做同樣處理,見 ARC4-3。

ID: ARC4-3
severity: minor
blocking: false
引句:「raise subprocess.TimeoutExpired(cmd, timeout, output=exc.stdout.decode(errors='replace'),」
file: `governance/eval/test_quality_handbook.py:233`
- 把 `CaptureTimeout` 轉回 `subprocess.TimeoutExpired`,讓下游 `run_model` 的 `except subprocess.TimeoutExpired`(`:254`)不用改。這是適配層,合理。
- `CaptureInterrupted` 沒有同樣的轉換,直接穿出 `model_command`。
- 舊實作丟的是 `ValueError('model interrupted by signal …')`,錯誤型別因此改變。
- 我沒有追 `model_command` 的呼叫端是否有 `except ValueError`,所以只列 minor。

**問 3 第二種做法**

沒有新增「第二種做法」。diff 反而把 `model_command` 裡自抄的 Popen、killpg 區塊刪掉,併進共用 runner。但還有兩處沒統一。

ID: ARC4-4
severity: minor
blocking: false
引句:「proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child'],」
file: `governance/eval/test_quality_handbook.py:159`
- 同一檔裡的 `run_test` 執行的是模型產生的測試碼,仍是 `subprocess.run` 加 timeout,沒有獨立程序群,逾時只殺直接子程序。
- 這跟同檔 `model_command` 剛統一的「獨立 POSIX 程序群清理」是同一族風險。
- 筆記說有意收斂的是「CLI capture 與 handbook model runner」,所以 `run_test` 不在宣稱範圍內。
- ⚠ 它跑的是 AST 限制過的固定 fixture,風險比模型命令低,算不算「應統一卻沒統一」我判不準,交編排者。

ID: ARC4-5
severity: minor
blocking: false
引句:「run = subprocess.run(command, capture_output=True, text=True, timeout=50)」
file: `governance/eval/test_quality_corpus.py:50`
- 這處跑的是凍結 scanner,而 scanner 內部會用共用 runner 起 Semgrep。
- corpus 的 `subprocess.run` 逾時只殺 scanner 本身,不殺 scanner 另起的 Semgrep 程序群。
- 這是巢狀的兩層逾時,第二層(50 秒)沒有 killpg。結構上是另一種做法,但屬既有,本輪沒改。

⚠ 還有一條:semgrep import 搬進迴圈內的位置,讓缺檔的 ImportError 改在掃描中途才出現,而不是 `main` 一開頭。
- 舊決策的原因是「遞移缺檔不應使既有 CLI 的 help 失效,測試品質命令則須明確回不完整及更新指引」。
- 新位置會不會讓缺檔訊息不再是「明確回不完整」,我判不準。
- 引句:「from test_quality_semgrep import scan as semgrep_scan」
- file: `scripts/test_quality_scan.py:293`(a2f30b19 的行號未逐行核對,引句取自審材)
- 這不是 major,交編排者判。

**不對齊共 5 條,其中 major 0 條**
總結最嚴重 severity: minor；blocking: 0
