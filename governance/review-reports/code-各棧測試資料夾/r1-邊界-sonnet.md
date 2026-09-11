severity: minor

### F1 模組層級快取 `_NODEHOME_STACK_TEST_DIRS` 沒鎖——查證為誤報
severity: minor
blocking: 否 — repo 內完全沒有 threading/multiprocessing(全域搜尋 `threading|ThreadPoolExecutor|multiprocessing|asyncio` 只命中 pitfalls 掃描器自己的規則字串),lumos 是單行程 CLI,同一顆 `TEST_PROFILES` 在執行期不會被改寫(`load_test_profile` 只 `dict()` 淺拷貝出區域變數,不動全域表),所以沒有競態可言。
- 這個 lazy cache 的寫法跟既有 `_TESTMAP_DIR_RE`(`scripts/lumos:19848`,同款 `global` + `is None` 判斷、也沒鎖)是同一套既有慣例,不是這次新引進的風險形態。
- 會被抓出來純粹是因為 `scripts/lumos:16792` 那條 pitfalls 併發規則機械比對 `global\s+\w+`,逢 global 必問「有沒有鎖」,不分真假共享。
引句:「_NODEHOME_STACK_TEST_DIRS = None   # lazy:(頂層資料夾結尾樣式, src/ 底下的測試資料夾名)」
file: `scripts/lumos:16792` pitfalls 併發規則(`global\s+\w+`)是機械字串比對,不分辨是否真有多執行緒共享
file: `scripts/lumos:19848` 既有 `_TESTMAP_DIR_RE = None  # lazy` 同款無鎖寫法,是這次新快取沿用的先例

### F2 圖譜鏡頭——8 個帶內容的固定席 INVARIANT 節點逐一核對,皆不受影響
severity: minor
blocking: 否 — 這次 diff 只新增 `_nodehome_stack_test_dirs`/`_nodehome_in_stack_test_dir` 兩支私有函式、在 `_nodehome_is_test` 裡多插一個判斷分支,以及一支新測試,沒有碰到下列任何節點管的程式路徑。
- bound-tests-gate/canary-audit/guard-kill 管的是「綁定測試逐支真跑擋 rc」「canary 落盤可讀回」「guard kill rc 優先序與 JSON 純度」,這次改動沒有動任何 `cmd_*` 入口的 rc 邏輯、canary 記錄或 guard kill 流程——只是多一支被綁定的測試,不影響 bound-tests-gate 的機制本身。
- slim-get-一行安裝/slim-install-安裝器/slim-uninstall-一行卸載 管的是 `.ps1`/CLAUDE.md 注入/manifest/vendored 白名單的安裝解除安裝流程,跟 `_nodehome_*` 系列函式完全是不同程式碼區塊,没有呼叫關係。
- 授權與歸屬管的 `_VENDORED_TOOLKIT`/`_VENDORED_TREE_FILES` 是寫死的路徑白名單(`scripts/lumos:13515`),不呼叫 `_nodehome_is_test`/`TEST_PROFILES`;測試假綠形態管的是另外兩支既有測試(manifest 清理、deinit unlink 失敗)的「還原翻紅釘」手法,這次沒有動到那兩支測試。
引句:「改在每支檔有家自己那層另認各棧的測試資料夾(從測試棧對照表推),不動測試地圖的判定規格(那份是設計審定過、有導入專案實測的)」
file: `scripts/lumos:13515` `_VENDORED_TOOLKIT` 是固定 5 檔的靜態白名單,跟本次改動的判定函式無交集

### F3 其餘 16 個「超出上限只列名」節點——名稱與子系統範圍判斷,未逐條驗內容
severity: minor
blocking: 否 — 這 16 篇(lumos-cli-lifecycle、lumos-cli-read、design-loop、pitfalls-code-loop、lumos-deinit、loop-convergence-recording、節點範圍與索引守衛、lumos-refcheck、cochange-guard、check-r-guard、doctor-irreversible-hint、reversibility-governance-ledger、check-t-sentinel、core-invariant-baseline、judge-severity-gate)在派工附檔裡只列名、沒有 KEY/INVARIANT 內容可核對,是「超出上限」被截斷的參考清單。
- 光看名稱都是 scripts/lumos 裡其他子系統(生命週期、CLI 讀取、design-loop、pitfalls-code-loop、deinit、canary 收斂記錄、節點範圍守衛、refcheck、共改守衛、可逆性相關閘)——跟這次改動的 `_nodehome_stack_test_dirs`/`_nodehome_in_stack_test_dir`/`_nodehome_is_test`(scripts/lumos:17780-17833)沒有函式呼叫或資料交集,判斷不受影響,但沒有內容可逐條核對,附此聲明供編排者知悉材料侷限。
引句:「測試檔另認各棧的測試資料夾——從測試棧對照表推(Gradle src/ 底下的 androidTest、Xcode 與 .NET 頂層名稱以 Tests 結尾的資料夾)」

### F4 漂移守衛的結構性天花板:新 dir_mode 若不落在 suffix/rglob_under=="src",不會被守衛覆蓋到(失效方向安全)
severity: minor
blocking: 否 — 實測構造一個新 profile(dir_mode 非 suffix、rglob_under 非 src)驗證:production 端 `_nodehome_stack_test_dirs()` 與測試裡的漂移守衛用同一組 `if/elif` 條件,兩邊永遠同步,不會出現「production 認了、守衛沒測到」的假綠;但若新棧要用全新概念的 dir_mode(例如非 suffix 也非限定 src 的遞迴模式),兩邊都不會生成任何探測路徑——這不是假綠,而是守衛壓根不會被觸發,production 端維持「不認、要家」的安全預設(過嚴而非漏檢)。
- 額外構造「空字串資料夾名」的退化情境實測驗證:production 用 `if d` 過濾掉空字串不納入 `sufs`/`under_src`(避免 `"".endswith` 誤判每支檔),而測試裡的漂移守衛沒有同款 `if d` 過濾,兩邊出現落差時守衛會正確判紅(`Demo/x.fk` 探測失敗、check ⑤ 出 miss),不是假綠。
- 這條是既有設計已經自陳的取捨(Issue 筆記「沒涵蓋」段與函式註解都寫了「其餘遞迴模式的棧不推」),不是這次 diff 藏起來的新缺口。
引句:「Python 那份把 scripts 當測試資料夾、Playwright 的 tests/e2e 不限位置,錨定太鬆會把真程式檔放掉。」
file: `scripts/lumos:17793` `_nodehome_stack_test_dirs()` 的 `if prof.get("dir_mode") == "suffix": ... elif prof.get("rglob_under") == "src":` 與測試裡漂移守衛(`scripts/test_lumos.py:36742-36751`)用完全相同的兩條件分支,兩邊天然同步

總結:最高 severity minor,blocking 共 0 條
