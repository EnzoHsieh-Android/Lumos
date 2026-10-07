severity: minor

F1
severity: minor
blocking: 否
引句:「resource.setrlimit(resource.RLIMIT_NOFILE,(min(64,soft),hard))」

修補新增的檔案描述符回歸測試直接匯入 Unix-only 的 `resource` 模組，沒有平台判斷或 skip。Windows Python 執行正式測試時，子程序會在測試產品碼前因 `ModuleNotFoundError: resource` 失敗，使跨平台測試假紅。

外部查證file: `governance/eval/test_review_convergence.py:171`

歸因：由 `r2-repair-review.patch` 新增，屬修補引入的測試問題；不代表描述符產品修復失效。

案例：

- input：Windows Python 3.14 執行 `CohortTests.test_directory_rejection_does_not_leak_descriptors`
- expected：測試應可執行，或在沒有 `resource` 時明確 skip
- case_source：`/tmp/review-eval-r2-seats/tests.txt`
- case_source SHA：`6af875e4b41aa01e368e35aa0b1f09104db31cdaf1655b7b10f90609a13a029b`
- before command：固定 paired loader＋before module＋上述 tests
- after command：固定 paired loader＋after module＋上述 tests
- cwd：Windows 原生環境；本席未執行
- before/after 實際載入 SHA：未載入；目標分別為 `6e7b04fc…`、`f1e5df1e…`
- rc／是否執行／原始輸出：兩端皆 `rc=N/A`、`executed=false`、無原始輸出；依指示排除 Windows 原生驗證
- 可比界線：此結論來自標準庫可用性與無條件 import；未冒充 Windows 真機結果

修補三問

1. 原問題有沒有修好？

在提供的固定 20 案例範圍內有修好。相同測試來源下，before 為 5 failures＋3 errors、after 為 20/20 通過。

2. 之前正常路徑是否仍成立？

提供的 12 個 before 已通過案例，在 after 仍通過；包含既有 cohort 篩選、錯誤輸入、成對品質與缺成本處理。這只證明列出的案例，不保證單家族視角沒有其他回歸。

3. 新增問題能否歸因修補？

F1 可直接歸因於修補新增的測試。下述記憶體問題在 before/after 都存在，不列為修補引入。

固定案例證據包：

- input/expected：`/tmp/review-eval-r2-seats/tests.txt` 的固定 20 案例
- case_source SHA：`6af875e4b41aa01e368e35aa0b1f09104db31cdaf1655b7b10f90609a13a029b`
- command：`/opt/homebrew/opt/python@3.14/bin/python3.14 -c <r2-paired-cases.json 固定 importlib loader> <endpoint module> /tmp/review-eval-r2-seats/tests.txt`
- before cwd：`…/review-eval-source-restore-d0_i6ykl/before`
- before loaded SHA：`6e7b04fcc03c0c9712de38d7e4f47e4cce04429f52390905c9da58c9380e2dc4`
- before：`rc=1`、`executed=true`；原始輸出 `r2-paired-before.log:1-129`
- after cwd：`…/review-eval-source-restore-d0_i6ykl/after`
- after loaded SHA：`f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- after：`rc=0`、`executed=true`；原始輸出 `r2-paired-after.log:1-26`
- 前提：Python 3.14.6、Darwin、無網路、同一測試來源
- 可比／歸因界線：case 字典重構和修復未隔離；只能確認固定案例由紅轉綠及既有案例保持綠，不能單獨估計各重構的效果
- 獨立核對：本席以 `shasum -a 256` 核對兩端模組及測試來源，均吻合卷證；沙盒拒絕建立指定 `general-tmp`，未重新執行測試

未判定 U1：解析後記憶體放大

引句:「raw = read_bytes(args.ledger)」

`cohort` 雖把原始輸入限制為 16 MiB，仍同時保留 raw bytes、解碼字串、`re.split` 片段與全部解析後 dict。大量短記錄可在合法位元組上限內放大成數百 MiB；這也表示 `py-memory` 的 `tension / chosen suggested` 尚未完整消除。

外部查證file: `governance/eval/review_convergence.py:521`、`governance/eval/review_convergence.py:524`、`governance/review-reports/code-review-convergence-eval/r2-dispositions.json:26`

此路徑在 before 已存在，不算 fix-induced。原擬在指定 temp 目錄跑兩端受限記憶體案例，但 `mkdir` 實得 `Operation not permitted`；因此不升格為 major finding。

圖譜硬合約逐條答覆

下列合約在 lens 均標示有綁定測試；384 行修補沒有修改其實作或綁定測試。本席未執行這些超出固定 20 案例的測試，因此逐條均為「未觸及、未重新驗證」：

- H01 修 bug 翻紅釘須有現場前置斷言：未觸及、未重新驗證
- H02 bound-tests 固定席測試須真跑：未觸及、未重新驗證
- H03 canary record 成功必須可讀回：未觸及、未重新驗證
- H04 canary second 不影響 gate：未觸及、未重新驗證
- H05 guard-kill rc 優先序：未觸及、未重新驗證
- H06 guard-kill JSON 純度：未觸及、未重新驗證
- H07 `.ps1` ASCII-only、無 BOM：未觸及、未重新驗證
- H08 `.ps1` 不使用 `$Args`：未觸及、未重新驗證
- H09 CLAUDE sentinel 外內容 byte-equal：未觸及、未重新驗證
- H10 安裝器冪等：未觸及、未重新驗證
- H11 完整版區塊精確備份：未觸及、未重新驗證
- H12 安裝時寫 bin 身分 manifest：未觸及、未重新驗證
- H13 CLAUDE 注入前三層目標守衛：未觸及、未重新驗證
- H14 `.cmd` 直譯器不得寫死：未觸及、未重新驗證
- H15 Windows 碰撞同時檢查 `lumos`／`lumos.cmd`：未觸及、未重新驗證
- H16 卸載前比對 bin 身分：未觸及、未重新驗證
- H17 四個清理步驟互不阻擋：未觸及、未重新驗證
- H18 skill 目錄刪除前備份：未觸及、未重新驗證
- H19 CLAUDE sentinel 精確還原：未觸及、未重新驗證
- H20 `.cmd` 與主程式各自獨立移除：未觸及、未重新驗證
- H21 卸載清除 manifest：未觸及、未重新驗證
- H22 search 排除 superseded、不排 stale：未觸及、未重新驗證

實讀範圍

- 使用者提供的 AGENTS、席 prompt；`CLAUDE.md:1-101`
- `r2-graph-lens.txt:1-69`
- 固定 after module：`module.txt:1-557`
- 固定 tests：`tests.txt:1-155,340-430`
- 完整修補：`r2-repair-review.patch:1-384`
- binding/dispositions/source-restore/paired-cases 的指定欄位
- paired logs 僅測試狀態、載入 SHA 與總結行
- snapshot 僅核對引句位置
- 未讀任何 r1 席報告或 intake；未讀純歷史席報告正文

最高等級：minor
阻擋條數：0