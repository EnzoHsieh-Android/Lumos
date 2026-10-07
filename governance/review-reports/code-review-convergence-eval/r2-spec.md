severity: major

ID: SPEC-R2-F1  
severity: major  
blocking: 是  
引句:「無完整成本資料不灌零；重複token相同原件只計一次，有衝突則保留問題與未知。」

同一 token 的 `tokens: 0` 與 `tokens: false` 被誤判成相同原件。Python 中 `0 == False`，因此 file: `governance/eval/review_convergence.py:145` 的字典比較沒有標記衝突，第二筆進入 file: `governance/eval/review_convergence.py:168` 的重複分支，最後在 file: `governance/eval/review_convergence.py:200` 回報已知成本 `0`。

這違反 file: `docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:26` 的衝突保留未知要求，也使 S1 的資料完整性不成立。

案例證據：

- case_source：`reviewer:inline/type-strict-token-conflict-v1`
- input：同一 `code-x/r1/token=T` 兩筆資料，`tokens` 分別為 JSON number `0` 與 JSON boolean `false`
- expected 來源：file: `docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:26`
- expected：`conflicting_tokens=true`、`tokens.total=null`
- 前提：Python 3.14；固定 git 物件存在；無網路；來源由 stdin 載入
- command：`git -C /private/tmp/lumos-future-repair-regression-research show <sha>:governance/eval/review_convergence.py | /opt/homebrew/opt/python@3.14/bin/python3.14 -c <type-strict-token-conflict probe>`
- cwd：`/tmp/review-eval-r2-seats`
- before：commit `8950308b71969f95119c7b2780f7a9ef93f669ac`；loaded SHA `6e7b04fcc03c0c9712de38d7e4f47e4cce04429f52390905c9da58c9380e2dc4`；executed=true；rc=1
- before 原始輸出：`actual={"conflicting_tokens":false,"duplicate_records":1,"tokens_total":0}`
- after：commit `c909bf980125dc90f1696372205e322e2ac877c7`；loaded SHA `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`；executed=true；rc=1
- after 原始輸出：`actual={"conflicting_tokens":false,"duplicate_records":1,"tokens_total":0}`
- 可比界線：兩端使用相同 Python、輸入與 assertion，只替換固定來源物件。
- 歸因：兩端皆翻紅，因此不是此次 repair 引入；它是修補前已有、修補後仍存的漏網缺陷。
- 建議修法：token 原件比較須保留 JSON 型別，例如遞迴做 type-strict equality；至少補 `0/false` 與 `1/true` 回歸案例。

修補三問：

1. 原問題有沒有修好？

提供的固定案例中，已列出的修補點確實由紅轉綠，但 F1 表明 S1 尚未完整修好：

- S1 round re-entry/token conflict：file: `governance/eval/test_review_convergence.py:156`，before `AssertionError: 2 is not None`，after `ok`
- S2 surrogate/max manifest：file: `governance/eval/test_review_convergence.py:242`，before `UnicodeEncodeError`，after `ok`
- S3 NUL receipt path：file: `governance/eval/test_review_convergence.py:313`，before `ValueError: embedded null character`，after `ok`
- S4 missing/duplicate cost：file: `governance/eval/test_review_convergence.py:394`，before `10.0 is not None`，after `ok`
- repair/preserve/new-defect 分列：file: `governance/eval/test_review_convergence.py:410`，before `KeyError: repair_passes`，after `ok`

共同證據：相同 test source SHA `6af875…029b`；before/after 實際載入 module SHA 分別為 `6e7b04…2dc4`、`f1e5df…933c`；executed=true；rc 分別為 1、0。完整 argv、cwd、環境與輸出位置見 file: `governance/review-reports/code-review-convergence-eval/r2-paired-cases.json:4`；原始逐案例輸出見 file: `governance/review-reports/code-review-convergence-eval/r2-paired-before.log:1` 與 file: `governance/review-reports/code-review-convergence-eval/r2-paired-after.log:1`。本席另核對四份檔案 SHA 與索引完全一致；這只證資料一致性，不證作者當時真的執行。

2. 之前正常路徑是否仍成立？

在提供的 20 案例範圍內，以下 12 個 before 已綠案例均為 `ok → ok`：file: `governance/eval/test_review_convergence.py:89`、file: `governance/eval/test_review_convergence.py:111`、file: `governance/eval/test_review_convergence.py:135`、file: `governance/eval/test_review_convergence.py:209`、file: `governance/eval/test_review_convergence.py:217`、file: `governance/eval/test_review_convergence.py:232`、file: `governance/eval/test_review_convergence.py:259`、file: `governance/eval/test_review_convergence.py:278`、file: `governance/eval/test_review_convergence.py:301`、file: `governance/eval/test_review_convergence.py:340`、file: `governance/eval/test_review_convergence.py:356`、file: `governance/eval/test_review_convergence.py:375`。未外推到未列案例或 Windows 原生行為。

3. 新增問題是否能歸因修補？

不能。F1 在 before 與 after 都以同一實際輸出翻紅，故標為「保留缺陷」，不是 fix-induced。

硬合約逐條：

- 測試假綠形態：列出的修補案例有固定來源 SHA、before 紅、after 綠及實際載入路徑證據；僅對這些案例成立。
- bound-tests gate：未修改 gate 判定；本席未重驗既有合約測試。
- canary 落盤/readback、second 純 telemetry：未修改相關產品碼；不作正常性外推。
- guard-kill rc 優先序、JSON 純度：未修改。
- slim-get 的 ASCII/BOM、`$Args`：未修改；Windows 原生驗證依指示排除。
- slim-install 七條合約：sentinel 位置、冪等、完整備份、manifest、目標守衛、直譯器選擇、雙 shim 碰撞皆未修改。
- slim-uninstall 六條合約：內容比對、四步獨立、skill 備份、CLAUDE 精確還原、cmd 獨立移除、manifest 清理皆未修改。
- lumos-cli-read 的 stale/superseded 搜尋：未修改。
- lens 僅列名而未附正文的 lifecycle、design-loop、deinit、check-r-guard、cochange-guard 等節點：未驗，不創造合約。
- py-memory：接受 disposition 的 `tension/chosen=suggested`，程式有 16MiB／1MiB／256KiB 上限，但仍整批解析；未改判為 satisfied。
- py-eventloop、py-parallel、py-external：新入口為同步本機檔案處理，未見相應機制。
- py-hotpath：只核對字典索引實作及提供案例，不外推大規模效能。

實讀範圍：

- `AGENTS.md` 指示、`CLAUDE.md`
- `lumos-project-notes` skill
- 完整 `r2-snapshot.patch` 1,235 行
- 完整 `r2-graph-lens.txt` 69 行
- 完整 `docs-repair.txt`
- `r2-paired-cases.json` 及兩端原始 paired logs
- `r2-dispositions.json` 的 Python disposition 欄位
- 固定 module/tests 的 SHA與必要案例位置
- 未讀任何 r1 席報告或 intake，未讀其他席輸出
- 未驗：Windows 原生 anchor、真實模型 baseline/candidate、歷史執行真實性
- sandbox 拒絕建立指定 `spec-tmp`；補充 probe 為無落盤管線，實際 cwd 是其父目錄，沒有修改 repo 或外呼

最高等級: major  
阻擋條數: 1