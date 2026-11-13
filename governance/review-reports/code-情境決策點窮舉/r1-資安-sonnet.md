severity: clean

我讀了 r1-snapshot.patch 的程式與測試部分(`check.py`、`scripts/lumos`、`test_lumos.py`、樣本、README、`jvm-only.txt`)。`.api` 兩支是掃過,governance 卷證和 sweep 副本則只看了開頭、並對全 patch 做關鍵字掃描(密鑰、信箱、`subprocess`/`eval`/`exec`/`curl`/網址),沒有逐行細讀。我沒有實際執行任何東西。

**① 提示注入:已看,無。**
- 新增的程式沒有把筆記、檔名、分支名或席報告送進派工詞或 hook 附加段。
- 型錄表格內容只拿去做比對:用 `re.compile(lumos._kt_trigger_re(...))` 組正規式,`_kt_trigger_re` 內有 `re.escape`,所以表格文字不能注入正規式語法。
- 把型錄片段包成假檔走切段,只是 `_kt_sit_text_segments` 的字串輸入,沒有執行、沒有寫檔。
- 席報告(`r*-*-sonnet.md`)和 `sweep/*.py.txt` 是 patch 內的純文字檔。新增程式沒有任何一處讀它們,也沒有餵進派工詞。
- `.py.txt` 副檔名不會被當 Python 執行。

**② 讀寫與執行越界:已看,無。**
- `load_lumos` 用 `SourceFileLoader` 執行整份 `scripts/lumos`,但路徑是 `HERE.parents[2] / "scripts" / "lumos"`,由 `check.py` 自己的位置算出,不吃環境變數或參數。
- `load_lumos` 本身是既有函式,這次只多了幾個呼叫端(`api_decision_problems`、`bad_snippet_reach_problems` 等)。信任邊界不變:要先手動跑那份 `check.py`,而且不在任何 hook 或 CI 的自動路徑上。我用 grep 查過,`scripts/lumos` 只在註解和 docstring 裡提到 `check.py`。
- 讀檔範圍:
  - `coroutines-api/` 的兩個檔名由型錄版本號組成。版本號被 `_API_HEAD_RE` 的 `(\S+)` 接住,理論上可含 `../`,但型錄是 repo 內受審的檔,攻擊者要先改型錄,不構成新權限。
  - `samples/bad/<rule_id>` 的 rule_id 來自 `rules/` 內的規則檔,同樣是 repo 內檔。`rglob` 在 3.14 預設不跟目錄捷徑。
- 寫檔只有測試的 `tempfile.mkdtemp(prefix="gctl-apidp-")` 和 `"gctl-reach-"`。兩處都有 `try/finally` 加 `rmtree(tmp, ignore_errors=True)`,路徑是自己建的,沒有跟外來路徑。
- 新增的 `subprocess.run([sg, "scan", ...])` 是既有的 `scan` 抽出 `scan_ranges`。`sg` 來自 `--sg` 參數,陣列式呼叫,沒有 shell 插值。
- 網址只出現在 README 和型錄第一行當出處字串,沒有任何下載程式碼。
- 密鑰與信箱:對新增行 grep 密鑰樣式與信箱,只中兩類假陽性。一類是 `.api` 檔簽名裡的 `@`,另一類是 governance 帳本行裡的 `token=`/branch 字樣(我只看了 grep 命中的行頭,沒展開確認內容)。
- 第三方 `.api` 檔是資料檔,只被 `read_text` 與 `sha256` 讀,不會被執行。README 有寫授權(Apache-2.0)來源。

**③ 非刻意一步繞過守衛:已看,無。**
- `_kt_sit_path_ok` 把「不是測試檔且過 `_stack_changed_ok`」抽成共用函式,推送端兩處改為呼叫它。新舊條件邏輯等價(`not TEST_PAT.search(x) and _stack_changed_ok(x, skip)`),守衛沒有放寬,`skip` 參數照舊傳入。
- 新自檢沒有讀 `LUMOS_SKIP_*` 之類的環境變數。
- `--sg` 掃描逾時或失敗時,新增的 `SCAN_FAILED` 一律判問題,不會默默放行。
- 母體 `.api` 有 sha256 核對(`_api_mother_problems`),被改或檔不在都會報。
- 這份卷證與 sweep 副本的內容,在 `catalog_problems` 與推送閘裡不會被當成正式碼處理。

全份最嚴重:clean;blocking 條數:0。
