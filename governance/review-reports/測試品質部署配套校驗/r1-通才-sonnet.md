severity: major

我只在 /tmp/lumos-seat-work/測試品質部署配套校驗/通才-sonnet/ 的複本上實驗，/tmp/lumos-readme-oct-audit 沒動。該 repo 的 `git status` 顯示有未提交改動，不是我造成的。派工時沒有附合約或事故節點，所以那一項略過。

ID: GEN-1
severity: major
blocking: 是
引句:「每支先讀最多 10 MiB 的 bytes，全部對上才從同一批 bytes 載入。」
file: `scripts/test_quality_semgrep.py:10`、`scripts/lumos:49454`

「全部從同一批已驗 bytes 載入」不成立。`test_quality_semgrep.py` 頂層有 `from test_quality import CaptureInterrupted, CaptureTimeout, run_capture_command`。`_TEST_QUALITY_BUNDLE_DIGESTS` 的順序是 semgrep、scan、test_quality，`_test_quality_load_bundle` 照這個順序 exec。exec semgrep 時 `sys.modules['test_quality']` 還沒登記，所以走一般 import，從磁碟載入未驗的 test_quality。這個磁碟版會吃 `__pycache__`，也就是 spec 開頭要防的同時間戳、同大小舊 bytecode。之後驗過的 test_quality 雖然覆蓋 `sys.modules`，semgrep 手上的 `run_capture_command` 與 `Capture*` 仍是磁碟版。

我做了兩個實驗，都用 repo 現有的 digest 表，來源逐位元組與原檔相同：

- **模組層**：植入同時間戳、同大小的舊 pyc 後，`sys.modules['test_quality_semgrep'].CaptureTimeout().args` 回 `('timeout; STALE detected',)`，驗過的 test_quality 回 `never detected`。`run_capture_command.__globals__ is tq.__dict__` 為 False。
- **端到端**：舊 pyc 把 `if remaining <= 0:` 換成 `>= 0:`，來源還原到與原檔 `cmp` 相同。接著跑 `lumos test-quality scan --json --semgrep <fake> T.kt`，健康時是 `status: unavailable`，舊 pyc 下變成 `status: timeout, reason: backend timed out`。

所以 `scan --semgrep` 這條路徑上，執行外部 backend 的共用 runner 仍可被舊 bytecode 回到舊判讀，S2 沒有覆蓋到。現有 `test_source_bytes_not_stale_bytecode_authorize_capture`（`scripts/test_test_quality_cli.py:760`）只對 test_quality.py 植舊 cache，只跑 capture，所以抓不到。

spec 的做法一節沒有寫模組間 import 依賴與載入順序，也沒有一條 `scan --semgrep` 搭配 stale 的反例。判準：任何一支 sidecar 的頂層 import 另一支時，必須先註冊被依賴者，或改成延遲 import。

ID: GEN-2
severity: minor
blocking: 否
引句:「CLI 應在執行收證命令前回退出2及 complete:false、not_assessed 的 JSON，提供更新指引。」
file: `scripts/lumos:49700`

配套不完整時，佔位入口的 `test-quality` 只宣告了 `REMAINDER` 位置參數與 `--help`。第一個 token 是選項時，argparse 在佔位入口之前就報錯。實測 `test-quality -h`、`--json scan`、`--out x capture` 都回 rc2，輸出是「擋下:不認得這幾個參數:-h」加「看用法: lumos --help」，不是結構化 JSON，也沒有 `lumos update` 指引。配套完整時 `test-quality -h` 會印正常說明。

S1 只驗了 `test-quality scan` 和 `--` 開頭的形式，沒驗這種排列。調用方若依賴 JSON 判讀部署錯誤，這些排列會拿到純文字。判準：佔位入口須接住 `-h` 與任意前導選項，或明寫它們不在保證範圍內。

ID: GEN-3
severity: minor
blocking: 否
引句:「這只證版本配套一致，業務 oracle 與報告真實性仍由呼叫者負責。」
file: `scripts/test_quality_scan.py:290`、`scripts/test_quality_scan.py:295`

⚠ 報告裡的 `tool.source_sha256` 與 `adapter_source_sha256` 是執行期用 `Path(__file__).read_bytes()` 重讀磁碟再算的，不是已驗的那批 bytes。它也是原始位元組的 sha256，不是 `_vendored_digest` 的 LF 正規化值。

- **檢查時間與使用時間不同**：載入後到產報告之間，磁碟若被 `lumos update` 換掉，報告簽的是新檔，執行的是舊 bytes。
- **CRLF 檢出**：CRLF 檢出的配套能過 digest，報告 sha 卻是另一個值。

spec 沒有說明報告裡的來源指紋與配套指紋的關係。實測只看到這兩處沒有任何比對消費者，所以目前只是來源對不上的風險。判準：把來源指紋改為取自已驗 bytes，或在 spec 註明這兩個欄位不等於配套校驗結果。

**實務隱患逐類**

- **併發**：`lumos update` 若在 3 支 sidecar 之間被換檔，同時啟動的 lumos 會看到「配套版本不一致」。這是 fail-closed，暫時性，無實害。檢查與使用的時間差見 GEN-1 與 GEN-3。
- **效能**：每次 `main()` 都讀三檔、算 sha256、compile、exec。我量 `lumos --version`，約 0.6 秒，有無載入差距在雜訊內，無隱患。
- **資源**：每檔上限 10 MiB，三檔最多約 30 MiB，無隱患。
- **回退**：回退只動入口校驗，不影響歷史卷證，無隱患。
- **S3**：`--vault X test-quality scan` 在配套不完整時回結構化 JSON，rc2。`--version`、`--help` 在配套不完整時仍正常，S3 成立。`test-quality --vault X scan`（`--vault` 放在子命令後）在健康與不完整時都被拒，不是「合法頂層 --vault」，屬一致行為。

S1 的「缺檔／混裝回 JSON rc2」已實測成立。「已讀，無 finding」的段落：問題與最小解（PRIOR-ART、RETIRE-IF 引用的 `_vendored_digest` 存在）、回退、實務隱患。

總結最嚴重 severity: major；blocking 共 1 條
