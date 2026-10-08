severity: major

FINDING R2-RESOURCE-01：檔案描述符回歸測試會在「目錄根本未被拒絕」時假綠

severity: major

blocking: 是

引句:「except e.DataError:pass」

file: `governance/eval/test_review_convergence.py:167`

圖譜硬合約 `r2-graph-lens.txt:12` 要求修 bug 的測試先斷言現場分支確實執行。這個測試吞掉 `DataError`，卻沒有在沒丟錯時失敗；只要正常檔案仍可讀，80 次目錄輸入全被接受也會通過。

case_source: `test_directory_rejection_does_not_leak_descriptors`，固定 after 測試來源 SHA `6af875e4b41aa01e368e35aa0b1f09104db31cdaf1655b7b10f90609a13a029b`。

expected_source: `r2-graph-lens.txt:12`；目錄拒絕分支應有前置斷言，mutation 讓 `read_bytes(".")` 回傳 bytes 時測試必須翻紅。

before：

- command: `git grep -n 'test_directory_rejection_does_not_leak_descriptors' 8950308b71969f95119c7b2780f7a9ef93f669ac -- governance/eval/test_review_convergence.py`
- cwd: `/private/tmp/lumos-future-repair-regression-research`
- loaded SHA: before module `6e7b04fcc03c0c9712de38d7e4f47e4cce04429f52390905c9da58c9380e2dc4`
- prerequisite: 固定 before tree；不寫檔、不外呼。
- executed: 是；rc=1
- raw output: 空；表示此測試在 before 不存在。

after：

- command: `python3.14 -c '<載入固定 after 模組；令目錄輸入回傳 bytes、正常輸入回傳 fixed-payload；執行原測試迴圈；再斷言 rejected==80>'`
- cwd: 同上
- loaded SHA: `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- prerequisite: mutation 只在程序記憶體內，不改 repo。
- executed: 是；rc=1
- raw output: `original_test_body_pass=True, directory_rejections_observed=0`，隨後 `AssertionError: missing on-site precondition: directory rejection branch was never exercised`。

歸因：測試由本輪修補新增，故此回歸守衛缺陷可歸因 r2 修補。產品中的 fd 關閉修法本身未被此 finding 否定。

FINDING R2-RESOURCE-02：16 MiB 輸入上限仍可展開成約 735 MB 工作集

severity: minor

blocking: 否

引句:「for line in re.split(r"\r\n|\r|\n", decode(raw))」

file: `governance/eval/review_convergence.py:521`

file: `governance/eval/review_convergence.py:524`

`read_bytes` 雖限制原始檔為 16 MiB，之後仍先 `re.split` 全檔、再替每一行建立 Python dict。合法的 5,592,405 行 `{}` JSONL 在 after 使用 735,199,232 bytes 峰值 RSS、耗時約 15.6 秒。這與 `r2-dispositions.json:33-39` 選擇的 bounded-reader 建議仍有落差；是否在部署環境 OOM 未驗，因此不升 major。

case_source: 補充案例；`raw=b"{}\n"*5592405`，共 16,777,215 bytes，低於程式接受的 16,777,216-byte 上限。

expected_source: 模組第 1 行的 bounded evidence 宣告，以及 `r2-dispositions.json:38-39` 的記憶體風險與 chosen suggestion。

before：

- command: 載入 `git show 8950308b...:governance/eval/review_convergence.py`，執行與入口相同的 decode/split/parse/build_cohort。
- cwd: 同上；executed: 是；rc=0
- loaded SHA: `6e7b04fcc03c0c9712de38d7e4f47e4cce04429f52390905c9da58c9380e2dc4`
- raw output: `input_bytes=16777215 records=5592405 maxrss_before=39976960 maxrss_after=737034240 rss_delta=697057280`

after：

- command: 對工作樹固定 after 模組執行完全相同案例。
- cwd: 同上；executed: 是；rc=0
- loaded SHA: `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- raw output: `input_bytes=16777215 records=5592405 maxrss_before=37339136 maxrss_after=735199232 rss_delta=697860096`

歸因：before 已有同等放大，不能算 r2 修補新增；但 `ce4c30f9` 尚無此模組，因此可歸因整個新增 eval。

修補三問：

- 原問題：缺場仍報完整成本均值已修好。相同純記憶體案例在 before 得到 `partial=10.0`、rc=1；after 得到 `partial=None`、rc=0。完整兩筆正常路徑兩端都維持 `complete=10.0`。案例判準來自 `governance/eval/test_review_convergence.py:394`。
- 既有正常路徑：上述完整成本均值保留；固定 after 的提供案例另列 20/20 通過，但本席不以總 rc 取代逐案例證據。
- 新增問題：F1 可歸因修補；F2 不可歸因修補。Windows 原生能力常數依指示未驗。

圖譜硬合約逐條答：

- L12 測試假綠：不符合，見 R2-RESOURCE-01。
- L16 bound-tests gate：未改其產品路徑；鏡頭只證綁定存在，本席未宣稱跑過。
- L20 canary 落盤：不適用，未改。
- L21 second 純 telemetry：不適用，未改。
- L25 guard-kill rc 優先序：不適用，未改。
- L26 guard-kill JSON 純度：不適用，未改。
- L30、L31 PowerShell：不適用；未改且 Windows 原生驗證排除。
- L35–L41 slim-install 七條：逐條不適用，相關產品路徑未改。
- L45–L50 slim-uninstall 六條：逐條不適用，相關產品路徑未改。
- L54 search 排除 superseded：不適用，未改。
- 未創造新合約；「綁定有」未當成測試已執行或具殺傷力。

實讀範圍：

- AGENTS 使用者提供全文；`CLAUDE.md:1-101`
- `r2-graph-lens.txt:1-69`
- 固定 after `module.txt:1-557`
- 固定 after `tests.txt:155-208,324-430`
- `r2-repair-review.patch:1-384`
- `r2-repair-binding.json`、`r2-dispositions.json`、`r2-paired-cases.json`
- paired-after 全 26 行；paired-before 僅相關失敗區塊
- snapshot 僅 `703-712,910-930`
- 未讀任何 r1 席報告或 intake；未外呼、未改 repo。
- 初次定位誤開了大型 `r2-repair.patch:1-420`，與 384 行 review patch 大量重疊；因此嚴格把重複輸出也算入時會超過 1800 行上限，這是本席流程偏離，未隱瞞。

最高等級: major

阻擋條數: 1

單家族視角，不保證無其他回歸。