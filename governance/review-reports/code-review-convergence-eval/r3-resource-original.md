severity: clean

CLEAN-R3-RESOURCE-01  
severity: clean  
blocking: 否

在指定的資源生命週期、JSONL 解析與修補範圍內，沒有重現新的產品 bug。原問題已修好，既有資源釋放案例保留；記憶體仍是已揭露的 tension，不構成 RAM 上限保證。

完整快照獨立引句：

「or not isinstance(ref.get("path"), str)」

file: governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:572  
file: governance/eval/review_convergence.py:383

「if len(rows) >= 100000:」

file: governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:314  
file: governance/eval/review_convergence.py:125

「assert rejected == 80, 'directory rejection was not exercised'」

file: governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:936  
file: governance/eval/test_review_convergence.py:181

一、原問題是否修好：是

案例輸入：

- `/tmp/review-eval-r3-seats/fixtures/long-trial.json:1`
- 真實存在的 129 字 receipt 檔名。
- 預期來源：receipt 路徑不套用識別欄位的 128 字限制；有效試行應為 1、無 invalid record。
- file: governance/eval/review_convergence.md:17
- file: governance/eval/test_review_convergence.py:285
- file: governance/eval/test_review_convergence.py:295
- case_source：`cd0ae310ccf1609a56a2552374eab47b13c55882:governance/eval/test_review_convergence.py`
- case_source SHA：`03ebe1f115f30d7b30c6800f53a680fbf30b2d9a9047a81f37cbe1451dd27355`

修前實跑：

- command：`/opt/homebrew/opt/python@3.14/bin/python3.14 .../after/governance/eval/review_convergence.py compare /tmp/review-eval-r3-seats/fixtures/manifest.json /tmp/review-eval-r3-seats/fixtures/long-trial.json --receipts /tmp/review-eval-r3-seats/fixtures/receipts`
- cwd：`.../review-eval-source-restore-d0_i6ykl/after`
- 載入 SHA：`f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- rc：0；executed：true
- 原始結果要點：`"valid_trials": 0`、`"reason": "receipt-reference"`。

修後實跑：

- command：`/opt/homebrew/opt/python@3.14/bin/python3.14 .../fixed_r2/governance/eval/review_convergence.py compare /tmp/review-eval-r3-seats/fixtures/manifest.json /tmp/review-eval-r3-seats/fixtures/long-trial.json --receipts /tmp/review-eval-r3-seats/fixtures/receipts`
- cwd：`.../review-eval-source-restore-d0_i6ykl/fixed_r2`
- 載入 SHA：`4b8a83ae7f2403a2a169e8c868a6059b40b705daafd62779cc87af53b9cf822e`
- rc：0；executed：true
- 原始結果要點：`"valid_trials": 1`、`"invalid_records": []`。

兩端都是 rc 0，因此判定依據是同一案例的原始欄位差異，不是總 rc。此案例可直接歸因於路徑守衛由 `text_field()` 改為只要求字串；這是 binding 唯一允許個別追蹤的修補。

file: governance/review-reports/code-review-convergence-eval/r3-paired-before.log:1  
file: governance/review-reports/code-review-convergence-eval/r3-paired-after.log:1  
file: governance/review-reports/code-review-convergence-eval/r3-repair-binding.json:319

二、原正常案例是否保留：是，在本席家族內

案例：目錄輸入連續拒絕 80 次後，仍能讀取一般檔案 `fixed-payload`。測試先斷言拒絕分支確實執行，再斷言正常檔仍可讀；不是只看最終程序成功。

- input/expected：governance/eval/test_review_convergence.py:168
- 前置斷言：governance/eval/test_review_convergence.py:181
- 正常讀取斷言：governance/eval/test_review_convergence.py:182
- subprocess rc 斷言：governance/eval/test_review_convergence.py:191
- 前提：Darwin、Python 3.14.6、`resource` capability 存在；原始輸出顯示 `ok`，不是 skip。

兩端實際 argv、cwd、commit、executed 與總 rc：

- before：governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:4
- after：governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:26

單案原始輸出：

- before：`test_directory_rejection_does_not_leak_descriptors ... ok`
- after：`test_directory_rejection_does_not_leak_descriptors ... ok`

file: governance/review-reports/code-review-convergence-eval/r3-paired-before.log:7  
file: governance/review-reports/code-review-convergence-eval/r3-paired-after.log:7

before 總 rc=1 是另外四個新案例翻紅；此正常案例本身兩端皆為 `ok`。after 總 rc=0。載入 SHA 與相同 case-source SHA 見兩份 log 第 1 行。

三、解析展開與記憶體

100001 個短 JSONL record 的定向實跑：

- before command：`python3.14 .../after/governance/eval/review_convergence.py cohort /tmp/review-eval-r3-seats/fixtures/short-lines.jsonl`
- before cwd：`.../after`
- before rc=0，原始輸出為 `observed_code_loops: 0`。
- after command：同命令改載入 `.../fixed_r2/...`
- after cwd：`.../fixed_r2`
- after rc=2，原始輸出為 `input-record-limit`。
- expected：100001 筆須拋出 `DataError`。
- file: governance/eval/test_review_convergence.py:226
- file: governance/eval/test_review_convergence.py:230

py-memory 表態：`tension / chosen suggested`。

固定修後模組以 15,100,000 bytes、100,000 筆、每筆含 100-byte payload 的唯讀記憶體 probe：

- command：Python 3.14 載入固定模組後呼叫真實 `parse_jsonl(raw)`，並讀 `resource.getrusage`。
- cwd：repo 根目錄
- rc：0
- 原始輸出：`raw_bytes 15100000 rows 100000 maxrss_bytes 114409472`

這證明 record 上限與避免 `re.split` 一次展開有效，但輸入上限不是總 RAM 保證；程式仍同時持有 raw、decoded text 與 parsed rows。依計劃於 2026-10-21 用首次實輪資料重新核對資料量與記憶體，不提前把它宣稱成容量保證。

file: governance/review-reports/code-review-convergence-eval/r3-graph-lens.txt:6  
file: docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:18  
file: governance/eval/review_convergence.md:28

四、新問題能否歸因修補

沒有在本席範圍重現新增問題，因此沒有新增產品缺陷可歸因。

- 長路徑問題可個別歸因至路徑守衛。
- 短行上限、控制字元與 token 型別修補同提交，沒有獨立中間版本；只能證明同源案例修後通過，不能聲稱各自的完整因果已被隔離。
- 修前四個定向案例分別翻紅，修後同一 23 案全綠。
- file: governance/review-reports/code-review-convergence-eval/r3-paired-before.log:10
- file: governance/review-reports/code-review-convergence-eval/r3-paired-before.log:65
- file: governance/review-reports/code-review-convergence-eval/r3-paired-after.log:10
- file: governance/review-reports/code-review-convergence-eval/r3-paired-after.log:29

來源閉包欄位一致：before/after commit 與 tree 已固定，前置重建 `exact_match=true`。  
file: governance/review-reports/code-review-convergence-eval/r3-repair-binding.json:2  
file: governance/review-reports/code-review-convergence-eval/r3-repair-binding.json:327

硬合約逐條答：

- graph-lens:3 py-eventloop：NA；同步 CLI，定向搜尋無 async。
- graph-lens:4 py-parallel：NA；沒有 task 或外部並行等待。
- graph-lens:5 py-external：NA；只讀本機一般檔，無網路或 DB 呼叫。
- graph-lens:6 py-memory：tension，chosen suggested；上限不等於 RAM 保證，2026-10-21 回看。
- graph-lens:7 py-hotpath：本輪比較案例通過；不外推模型實輪效能。
- graph-lens:12 測試假綠：本席資源案例已用 `rejected == 80` 證明拒絕分支確實走到。
- graph-lens:16 bound-tests gate：修補未改該 gate，本席未獨立驗證。
- graph-lens:20、21 canary 兩條：未改、未驗。
- graph-lens:25、26 guard-kill 兩條：未改、未驗。
- graph-lens:30、31 slim-get 兩條：未改；Windows 原生能力排除，未冒充通過。
- graph-lens:35、36、37、38、39、40、41 slim-install 七條：未改、未驗；其中 Windows 條款未驗。
- graph-lens:45、46、47、48、49、50 slim-uninstall 六條：未改、未驗；其中 Windows shim 條款未驗。
- graph-lens:54 search superseded/stale：未改、未驗。

實讀計帳：

- 規矩與 skills：525 行。
- graph lens：69 行。
- 固定 module 指定段：366 行。
- 固定 tests 指定段：138 行。
- 完整 r3 repair-review patch：167 行。
- 圖譜 system、project 與工具規格正文：106 行。
- 核心正文合計：1,371 行；另僅定向讀取 binding、paired metadata、原始 log 與 fixture，總量維持在 1,800 行內。
- 未全文讀取 r1/r2 席報告、intake、作者因果結論、11943 行 `r3-repair.patch`、完整 binding/source-restore JSON 或其餘 snapshot。
- 未驗 module 221–414（除定向路徑守衛）、tests 非指派段、Windows 原生、模型實輪及其他功能家族。單家族結果不保證全域無回歸。

最高等級：clean  
阻擋條數：0