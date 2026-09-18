severity: clean

## 三問逐問答

### 問①:`_vault_slug_of` 跟既有 `_vault_in`/`find_vault`/`_nodehome_key` 是不是又一份圖譜路徑工具?

不是又一份,是把原本三處各寫一次的邏輯收成一支,而且跟既有的「不讀磁碟」慣例對齊。

- `_vault_slug_of` 吃的是 git 路徑「字串」(某個提交/樹裡的相對路徑),不碰檔案系統;`_vault_in`/`find_vault`(`file: \`scripts/lumos:16560\``、`file: \`scripts/lumos:16576\``)吃的是 `Path`,靠 `.is_dir()`/`.iterdir()` 真的去掃磁碟。兩者服務的問題不同:後者答「這台機器上 vault 在哪」,前者答「這個(可能不是目前 checkout 的)提交裡,這支檔算不算落在某個 vault 底下」——docstring 自己講了原因:
  引句:「三個讀者共用(推送前家的檢查、刪除守衛、推送測試範圍);2026-09-18 代碼審 code-文件子集收緊 r2 架構席:原本兩處各寫一次、第三處又換正則。"""」
- 這個「字串比對、不讀磁碟」的設計早有先例:`_nodehome_key`(`file: \`scripts/lumos:20867\``)docstring 寫著「★不讀磁碟★——比對的是被檢查那個版本裡的樣子,推送一個不是目前 checkout 的分支時,磁碟上的拼法跟那個提交對不上」,理由跟 `_vault_slug_of` 一模一樣。`_vault_slug_of` 是延續這個既有慣例,不是另立一套。
- 收斂確實落地,三個呼叫點在 HEAD(c244d592)都改用它,沒有漏收:
  引句:「vaults = sorted({_vault_slug_of(p) for p in lst[1]} - {None})」(cmd_home_check,`file: \`scripts/lumos:21478\``)
  引句:「graph = any(_vault_slug_of(f) for f in files)」(_test_suite_for_range,`file: \`scripts/lumos:22351\``——這處在 r2 仍是 `re.match(r"docs/[^/]+-knowledge/", f)`,r3-delta 才真的併過去,docstring 講的「第三處又換正則」就是指這裡)
  引句:「slugs = sorted({_vault_slug_of(p) for p in base_tree} - {None})」(cmd_dispatch_lens,`file: \`scripts/lumos:26519\``)
- 順帶查了一個形狀類似但沒被收進去的地方:`_dispositions_check_issue`(`file: \`scripts/lumos:27855-27856\``)也在從 `git ls-tree` 結果篩 `-knowledge` slug,但它吃的是 `git ls-tree --name-only <sha> docs/` 回來的「docs/ 底下第一層的裸目錄名」(不帶 `docs/` 前綴),跟 `_vault_slug_of` 吃「完整相對路徑字串」的輸入形狀不同,套不進去;這支不在這次 diff 改動範圍內,不算本輪的不對齊。

### 問②:`_docs_suite_select` 用 `_load_lumos_inproc().find_vault(...)` 取真圖譜路徑,跟本檔其他地方取法一不一樣?

寫法不一樣,但方向是對的,不算不對齊。

- 新增這行:
  引句:「_vault = _load_lumos_inproc().find_vault(Path(GRAPHCTL).resolve().parent.parent)」(`file: \`scripts/test_lumos.py:104\``)
- 本檔其他地方取「真圖譜路徑」壓倒性地是把字面字串 `"docs/lumos-toolchain-knowledge"` 直接寫死接在 `Path(GRAPHCTL).resolve().parent.parent` 後面,例如 `file: \`scripts/test_lumos.py:3387\``(`node = (Path(GRAPHCTL).resolve().parent.parent / "docs" / "lumos-toolchain-knowledge" ...`)、`file: \`scripts/test_lumos.py:17522\``(`actual_vault = Path(GRAPHCTL).resolve().parent.parent / "docs" / "lumos-toolchain-knowledge"`)、`file: \`scripts/test_lumos.py:13678\``、`file: \`scripts/test_lumos.py:15199\`` 等,全檔字面出現 `lumos-toolchain-knowledge` 141 處。`_docs_suite_select` 這行是全檔唯一一處呼叫 `find_vault()` 動態算 vault 名字,形式上確實是第二種取法。
- 但這不算「引入第二種做法」該罰的那種:其餘 141 處是在測「這個 repo 自己的圖譜長什麼樣」(lumos-toolchain 自己 dogfood 自己的圖譜),寫死名字沒問題;`_docs_suite_select` 是子集選測邏輯,而 `scripts/test_lumos.py` 是會被 vendor 進消費專案的檔(CLAUDE.md「每支檔有家」一節與 `_vendor_toolchain` 的白名單機制),消費專案的圖譜資料夾不會叫 `lumos-toolchain-knowledge`——寫死字面字串在這一處反而是真正的 bug(換了專案就永遠比不到),用 `find_vault()` 動態抓「這個 repo 真正的 vault 叫什麼」才是唯一能跨專案成立的寫法。
- 失敗路徑也接得住:`try/except Exception: pass` 後 `_vault` 為 `None` 時退到 `r"(?!x)x"`(恆不匹配的規則),不會誤判——沒有 fail-open 成「什麼都算圖譜測試」的風險。

### 問③:hook 探 `"--graph"` 的寫法(位置、退回方式)跟探 `"--suite"`/`"--shard"` 一不一致?

探測機制(讀檔找旗標字樣、不執行)三者完全同款,退回範圍不同是因為三者在決策鏈裡的層級本來就不同,不是新引入一套機制。

- 三個探測用的是同一個 `grep -q -- '"--旗標"' "$REPO_ROOT/scripts/test_lumos.py"` 句式:
  引句:「if [[ "$_SUITE_SEEN" -eq 1 && "$_SUITE_FULL" -eq 0 ]] && grep -q -- '"--suite"' "$REPO_ROOT/scripts/test_lumos.py" 2>/dev/null; then」(`file: \`scripts/hooks/pre-push:401\``)
  引句:「if grep -q -- '"--graph"' "$REPO_ROOT/scripts/test_lumos.py" 2>/dev/null; then」(`file: \`scripts/hooks/pre-push:411\``)
  `--shard` 探測用同一句式但不在這次 diff 範圍內(`file: \`scripts/hooks/pre-push:395\``:`if ! grep -q -- '"--shard"' "$REPO_ROOT/scripts/test_lumos.py" 2>/dev/null; then`),三者文字結構一致,沒有走位置不同的探法(不是先跑再看輸出那種——這正是同一段註解點名要避開的舊坑)。
- 位置差異:`--shard` 探測獨立、無條件跑;`--suite` 探測是進入 docs/light 模式的閘門條件(擋在最外層 `&&` 裡);`--graph` 探測巢狀在「已經決定要跑 docs/light」之後,因為 `_SUITE_GRAPH` 這個訊號本來就依附在「這次推送有 docs 判定」之上(`_test_suite_for_range` 只在 `suite=="docs"` 分支才會給 `graph` 真值,`file: \`scripts/lumos:22349-22351\``)。位置差是決策依賴關係造成的必然結構,不是另一套探法。
- 退回範圍差異:`--suite` 探不到 → 一開始就不進 docs 模式(維持預設 `full`);`--graph` 探不到 → 把已經設好的 `_suite_mode`/`_suite_args`/`_suite_word` 全部倒回 full。這是因為 `--graph` 判定發生在 `--suite` 判定之後,要撤回就得撤回到同一個「全部測試」的預設值,退回目標(`full`)其實跟 `--suite` 探不到時的退回目標一致,只是觸發點在鏈路下游、需要顯式重置已賦值的變數而已。這個方向本身也跟同檔另一處講的 fail-safe 原則一致(算不出範圍就多跑不少跑,`file: \`scripts/lumos:22337\`` 附近);r3-delta 也补上了先前(r2)漏掉的探測(對照:「同一個理由:硬塞不認得的旗標,執行器會整個報錯,被判成「測試有紅」(r2 通才席實測重現)」,`file: \`governance/review-reports/code-文件子集收緊/r3-delta.patch:19\``——這行本身不在 r3-snapshot 的固定引句範圍內,只作對照,不算引句)。
- CI 端(`.github/workflows/ci.yml`)兩者都不探測、直接照 `suite`/`graph` 兩個輸出值拼旗標,這跟既有 `--suite docs` 在 CI 端本來就不探測的寫法(CI 用的執行器永遠跟同一個 commit 的 `scripts/test_lumos.py` 一起 checkout,天生不會有 hook 那種「舊版執行器」問題)一致,`--graph` 沒有另開一套。

## 不對齊共 0 條,其中 major 0 條

## 驗過的路徑
- 讀完 `governance/review-reports/code-文件子集收緊/r3-snapshot.patch`(612 行)全文與 `r3-delta.patch`(271 行)全文,sha256 對過凍結 patch。
- 在 `git worktree add --detach /tmp/seat-架構對齊-r3-sonnet HEAD`(唯讀,已 remove)裡實跑 `python3 scripts/test_lumos.py -k runner_suite_flags`、`-k prepush_and_ci_wired_for_docs_suite`、`-k prepush_docs_and_light_run_subset`、`-k test_suite_docs_only_judgement`,共 60 案例全綠,確認 `--graph` 探測、退全套、`_vault_slug_of` 三處收斂的行為跟程式碼描述一致。
- 查過 `scripts/lumos` 裡 `_vault_in`/`find_vault`(16560-16585)、`_nodehome_key`(20867-20870)、`_vault_slug_of`(22275-22283)三支的職責邊界,以及全檔 `-knowledge` 相關的其餘寫法(2344、14884、15502、15791、16475-16566、21538、27856-27867),確認沒有第四處該收沒收進 `_vault_slug_of` 而被漏掉的同構重複(`_dispositions_check_issue` 那處輸入形狀不同,見問①)。
- 查過 `scripts/test_lumos.py` 裡取真 vault 路徑的其餘寫法(grep `lumos-toolchain-knowledge` 141 處),抽查 3387、13678、15199、17522 幾處,確認 `_docs_suite_select` 改走 `find_vault()` 是因為本檔會被 vendor 到消費專案、不能寫死本專案的 vault 名字。
- 查過 `scripts/hooks/pre-push` 裡 `--shard`(387-397)、`--suite`(400-403)、`--graph`(404-417)三段探測與退回邏輯的完整脈絡,以及 `.github/workflows/ci.yml` 對應段落,確認退回範圍差異是決策依賴順序造成、不是引入新探法。
