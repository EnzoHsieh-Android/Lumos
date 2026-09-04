### f1

引句:「三格各上限 8、★全部只用 base 樹★」

file: `scripts/lumos:2622`

severity: blocker

blocking: 是

既有 profile loader 只會從工作樹 `.lumos/config.json` 讀 `test_profile`、副檔名及可自訂的 `method_regex`，規格卻沒有要求從 base blob 載入測試 profile。照「依既有 profile」實作會讓分支控制測試格的搜尋與輸出，違反全部只用 base 樹，也重新形成自由文字抽取管道。

### f2

引句:「★沿 v1.0 快取★(鍵含 base sha),同輪只有第一席付」

file: `scripts/lumos:16540`

severity: major

blocking: 是

現有快取鍵只有 repo、base SHA、head SHA，沒有格式或功能版本；部署 v1.2 後，相同範圍可在 TTL 內直接命中 v1.1 的零篇空輸出，完全不執行備援。沿用快取前須換 namespace、加入 schema/version，或拒讀缺少 `fallback_status` 的舊資料。

### f3

引句:「本格若超時整段備援跳過、印固定字串「既有相依:略(超時)」」

file: `scripts/lumos:16511`

severity: blocker

blocking: 是

`cmd_dispatch_lens` 現況沒有共享的 45 秒 deadline，只有每次 Git 子行程各自最多 20 秒；逐一 `git show` 上千個 base blob 時，可反覆付出 20 秒而不會進入指定的超時狀態。照現有結構追加三格，無法保證整段在內層預算內降級。

### f4

引句:「三格皆空(且無新增檔)→印「三格皆空(已查:受影響測試 0、共改 0、呼叫者 0)」」

file: `governance/review-reports/派工鏡頭注入-v12/r2-snapshot.md:194`

severity: major

blocking: 是

此規則禁止有新增檔時印「三格皆空」，但驗收又要求只新增檔時同時印該行並回 `attached-empty`（同檔第 200 行）。照字面實作必然無法通過驗收 ②，需統一條件與狀態定義。

最高 severity: blocker；共 4 條 finding，blocking 4 條。
