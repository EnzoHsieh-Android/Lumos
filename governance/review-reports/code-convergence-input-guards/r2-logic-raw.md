severity: major

## state-F1：staged 路由證據可能來自已不再變更的測試

severity: major  
blocking: 是

引句:「if key in changed_paths:」

觀察：staged 路徑先保存 `changed_paths`，之後才分別以 live index 的 `ls-files` 與 `git show :path` 分類候選。`from_git=True` 只排除工作樹，沒有把索引固定成同一版本。  
file: `scripts/lumos:27368`  
file: `scripts/lumos:27413`

判準：寫回路由只能採信「同一份 staged 狀態中，已宣告且實際改動」的合法測試；候選身分與內容分類不可來自不同時點的索引。

具體輸入 → 錯結果：

1. staged 同時包含 src/a.py、TestHome 正文與其宣告的 tests/check.py。
2. `changed_paths` 算完後，另一程序把 tests/check.py 的 index entry 恢復成 HEAD；最終 staged diff 已不含該測試。
3. 候選集合仍保留 tests/check.py；後續 live index 分類又看到一支合法測試，因此 TestHome 被視為有同提交路由證據。
4. 現行結果可為 rc0；正確結果應為 rc1，指出 TestHome 不是任何一支實際改動檔的家。

可執行證據：在 synthetic repo 包裝 `_nodehome_route_tests`，首次呼叫前以 `git update-index --cacheinfo` 把 tests/check.py 換回 HEAD blob；前置斷言確認 cached diff 已不含該測試，再要求 `home check --staged` 拒收。現有 snapshot-race 測試只換工作樹，殺不到 index 於候選擷取後改變的情況。

本席未實跑此重現：唯讀權限沒有可寫 temporary fixture；以上為程式路徑推論。

### 資料狀態五問

- 新舊互讀：range 路徑按提交及所有父版分類，刪除、改名與中間版本都有覆蓋；未見跨提交主動合成。staged 路徑則受 state-F1 影響。
- 寫一半：H 首次讀取、UTF-8 解碼及第二次 raw hash 讀取失敗都在成功帳追加前返回；未知 read／quote-parser Runtime 仍逸出。
- 衍生資料：H 的引句結果與首讀 bytes 綁定，第二次 raw hash 不同即拒收；N 的判定層只消費 `staged_route_tests`／`route_tests`，正式 `g_code`、`wb_files` 與啟動條件未擴大。
- 時間：commit SHA 路徑不可變且安全；可變 index 沒有固定版本，是本席唯一 blocking 問題。
- 不可逆：目標錯誤不會追加成功 canary；既有 Governance blocked 紀錄語意未被擴大。N 僅作守衛判定，沒有新增不可逆寫入。

### 固定圖譜鏡頭

- `Systems/design-loop.md`：不影響；未改處置閘的計劃格式或條款綁定判定。
- `Systems/lumos-cli-read.md`：不影響；未改 search 的 superseded/stale 濾網。
- `Systems/pitfalls-code-loop.md`：不影響；未改風險分級與 pitfalls 路徑。
- `Systems/bound-tests-gate.md`：不影響；未改合約測試執行或 blocked 判定。
- `Systems/guard-kill.md`：不影響；未改 rc 優先序或 JSON stdout 合約。
- `Systems/授權與歸屬.md`：不影響；未改 vendored 清單、deinit 或授權檔頭。
- `Systems/測試假綠形態.md`：既有新增測試具備工作樹競態、分組故障等現場前置斷言，未直接破壞合約；但缺少 index 時序反控制，形成 state-F1。
- `Systems/lumos-cli-lifecycle.md`：不影響；未改 reinject 或 sentinel 外內容。

### 已讀材料

- `governance/review-reports/code-convergence-input-guards/r2-source.patch`
- `governance/review-reports/code-convergence-input-guards/r2-graph.patch`
- `governance/review-reports/code-convergence-input-guards/r2-file-index.txt`
- `governance/review-reports/code-convergence-input-guards/r2-graph-lens.txt`
- `governance/review-reports/code-convergence-input-guards/r2-pitfalls.json`
- `governance/review-reports/code-convergence-input-guards/r2-dispositions.json`
- `governance/review-reports/code-convergence-input-guards/r2-test-layers.txt`

### 額外定點 context

- `scripts/lumos:9598-9663`
- `scripts/lumos:27368-27447`

最高級：major；blocking：1。