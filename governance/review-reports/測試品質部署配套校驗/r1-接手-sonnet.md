severity: major

我讀了 spec、圖譜三篇 Systems 筆記和 lands_in、`scripts/lumos` 的配套檢查，以及安裝與更新流程和兩支掛鉤。另外在 `/tmp/lumos-seat-work/測試品質部署配套校驗/接手-sonnet/s/` 用 `scripts/` 的副本實跑了反例。對照 repo 沒動。

ID: HND-1
severity: major
blocking: 是
引句:「每支先讀最多 10 MiB 的 bytes，全部對上才從同一批 bytes 載入。」
審材外佐證 file: `scripts/test_quality_semgrep.py:10`
審材外佐證 file: `scripts/lumos:49445`
審材外佐證 file: `scripts/lumos:49471`
問題與判準:「全部從同一批已驗 bytes 載入」這句在 Semgrep 轉接器上不成立。
- `scripts/lumos:49445` 的指紋表順序是 semgrep、scan、test_quality，載入迴圈照這個順序 exec。
- `scripts/test_quality_semgrep.py:10` 在模組頂層寫了 `from test_quality import CaptureInterrupted, CaptureTimeout, run_capture_command`。
- semgrep 被 exec 的時候，`sys.modules` 裡的 `test_quality` 還沒登記成已驗版本。於是這行 import 走標準 import 機制，吃磁碟上的 `test_quality.py`，也就是可能帶舊 bytecode 的那份。
- 實測一：載入後 `sys.modules["test_quality_semgrep"].run_capture_command is sys.modules["test_quality"].run_capture_command` 為 False。兩個模組各自帶著不同的 `test_quality` 物件。
- 實測二（重現 spec 的反例）：我把來源改成同大小同時間戳、編出舊 pyc，再還原正確來源。`_test_quality_load_bundle()` 回 None（判定合格），已驗的 `test_quality` 沒有舊內容，但 semgrep 轉接器拿到的 `run_capture_command` 帶舊內容。
- 所以 spec 要消滅的「時間戳與大小相同的舊 bytecode 回到舊判讀」，在 `scan --semgrep` 路徑還在。
- S2 的現有測試 `scripts/test_test_quality_cli.py:760` 只跑 capture，沒有任何控制走 semgrep 路徑，所以這個洞綠燈通過。
- 修法要在 spec 寫明。可以先登記好全部空模組再 exec。也可以把載入順序改成依賴序（`test_quality` 先）。另外 S2 要補一條 semgrep 路徑的驗收。

ID: HND-2
severity: minor
blocking: 否
引句:「CLI 綁定三支 sidecar 的內容指紋」
審材外佐證 file: `scripts/lumos:49445`
審材外佐證 file: `scripts/lumos:49450`
審材外佐證 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:66`
問題與判準:三個月後接手的人，從 spec 看不出改 sidecar 或新增 sidecar 要同步哪幾處。
- 指紋表 `_TEST_QUALITY_BUNDLE_DIGESTS` 是寫死在 `scripts/lumos:49445` 的常數。
- spec 和 `test-quality-scan.md`、`test-quality-multilang.md`、`test-quality-cli.md` 都沒寫常數名，也沒寫怎麼重算。
- `test-quality-cli.md:66` 只列四道守衛：頂層指令數、`--help`、指令總目錄字數、兩支掛鉤豁免清單。這份清單漏了第五處，也就是這張指紋表。
- 漏改的結果是失敗但看不出原因：該 sidecar 改完沒改常數，`test-quality` 全面拒絕，訊息只有「配套版本不一致:檔名」。能抓到的只有 `t_test_quality_cli`，它在 `scripts/test_lumos.py:78622`。
- 新增 sidecar 有兩個靜默陷阱，spec 都沒寫：
  - `_test_quality_bundle_sources` 只把檔名以 `test_quality` 開頭的 vendored 檔當必備（`scripts/lumos:49450`）。不照這個前綴命名的新 sidecar 不被要求，也不被校驗，會走標準 import。
  - 載入順序有依賴，HND-1 就是這個問題的實例。
- 這一項 fail-closed，不會假綠，所以是 minor。

ID: HND-3
severity: minor
blocking: 否
引句:「正式 argparse 解析後只對 test-quality 回結構化錯誤；其他指令照既有流程。」
審材外佐證 file: `scripts/lumos:49486`
審材外佐證 file: `scripts/lumos:49475`
審材外佐證 file: `scripts/lumos:50518`
問題與判準:實作跟 spec 描述的隔離範圍不一致，另有一條死分支。
- 載入發生在 `main()` 第一行（`scripts/lumos:49486`），早於 parser 建立，而且所有指令都會 exec 三支 sidecar。spec 寫的「parser 建立期」「其他指令照既有流程」描述不準。
- 例外只接 `(OSError, ValueError, ImportError, SyntaxError)`（`scripts/lumos:49475`）。我把 sidecar 末尾加一行 `raise RuntimeError`，同步改指紋後，`lumos python-path` 和 `lumos --version` 都直接噴 traceback。
- 這表示一次指紋合格但 import 期出錯的 sidecar 發版，會讓整個 lumos 掛掉，包含 pre-push。這違反 S3 的「不妨礙既有 --help、--version 入口」。
- `scripts/lumos:50518` 還留著 `ModuleNotFoundError` 退路，印非 JSON 的 stderr 並回 2，違反 S1 的 JSON 契約。目前走不到，因為已載入時 import 命中 `sys.modules`，但它是誤導接手者的死碼。
- spec 應註明這兩點，或把例外面收成 `Exception`。

ID: HND-4
severity: minor
blocking: 否
引句:「安裝入口改用不可變版本配套且執行固定內容，混裝與 stale-bytecode 反例均確認不會假綠時」
審材外佐證 file: `scripts/lumos:22726`
審材外佐證 file: `scripts/lumos:22361`
問題與判準:RETIRE-IF 的條件不可觀測。
- 沒有指令、檔案、符號或狀態可以檢查「安裝入口已改用不可變版本配套」。現在的安裝入口是 `_vendor_toolchain`（`scripts/lumos:22726`）逐檔 `copy2`。
- 專案的機器式撤除條件格式有 `when-file`、`when-symbol`、`when-gone`、`人裁` 等。這條既沒用這些格式，也沒寫成人裁加 `[until:]`。
- 「均確認不會假綠」沒說誰確認、用什麼確認。三個月後沒人能判定該不該撤。
- 應改成可觀測的條件，例如某個安裝入口檔或符號出現後由人裁，並附回頭看的日期。

ID: HND-5
severity: minor
blocking: 否
引句:「[manual:實際建立舊快取後還原來源，與正常及五棧既有卷證配對核對]」
審材外佐證 file: `scripts/test_test_quality_cli.py:760`
審材外佐證 file: `scripts/test_test_quality_cli.py:837`
審材外佐證 file: `scripts/test_test_quality_cli.py:306`
問題與判準:S1 到 S3 的 [manual:] 驗法，接手者照字面做不能重現。
- S2：沒給指令。同大小、同時間戳這個條件要靠補空白或同長度替換字串，再用 `os.utime` 還原，只有測試檔裡有做法。
- S2：「五棧既有卷證」沒指名是哪五棧。圖譜只有 Node 與 Laravel、C# 與 Android 與 iOS 兩篇 Verification，spec 沒連結，也沒給路徑。
- S3：「兩種正式 argparse 排列」沒列舉。我實測 `lumos test-quality --vault x scan` 在不完整配套下回的是非結構化的「不認得 --vault」，回 2，而 `lumos --vault x test-quality scan` 才是結構化 JSON。接手者不知道哪一種算合法排列。
- S1：「來源不可讀」和超過 10 MiB 的情況沒有任何測試，我也沒找到手動做法。現有測試只涵蓋缺檔（`:306`）、混裝（`:609`）、舊快取（`:760`）、`--vault`（`:837`）。
- spec 應連到這些既有測試，或補上具體的手動步驟。

ID: HND-6
severity: minor
blocking: 否
引句:「PRIOR-ART: 沿既有工具檔指紋函式」
審材外佐證 file: `scripts/lumos:22331`
審材外佐證 file: `scripts/lumos:22361`
審材外佐證 file: `scripts/lumos:22762`
問題與判準:PRIOR-ART 沒回答為什麼要另立一張指紋表，不用既有的安裝紀錄。
- `_vendor_toolchain` 結尾 `_vendored_manifest_write`（`scripts/lumos:22762`）已經把含三支 sidecar 的全部工具檔寫進 `.lumos/vendored.json`。
- spec 另立一份寫死在程式裡的指紋，這份跟 manifest 是兩處真相。
- 這個取捨可以有理由，例如 manifest 只在安裝時寫、事後被改過的 sidecar 會被當作原封不動。但 spec 沒寫，接手者無從判斷該不該合併。

節的覆蓋:
- git 掛鉤豁免清單：已讀，無 finding。
  - `scripts/hooks/pre-commit:258` 和 `scripts/hooks/post-commit:69` 都已含三支 sidecar，與 `_VENDORED_TOOLKIT`（`scripts/lumos:22331`）一致，而且有 `t_precommit_whitelist_drift_guard`。
  - 要同步的位置圖譜有寫，缺的只有 HND-2 說的第五處。
- 安裝與更新流程：已讀，無 finding。三支檔在 `_VENDORED_TOOLKIT`，`_vendored_pending` 和 `copy2` 會一併處理。更新到一半被中斷造成的混裝，正是本 spec 要擋的情境。全域 `lumos` 是 symlink，`resolve()` 後落到來源 repo，那裡有三支 sidecar。
- 回退：已讀，無 finding。
- 實務隱患四條已讀，無 finding，因為：
  - 金流：沒有金流。
  - 對外送出：不對外，只載入本機檔案。
  - 不可逆：只讀檔和 exec，不寫檔。
  - 守衛面：不碰 code-loop 和 CI。

總結最嚴重 severity: major；blocking 共 1 條
