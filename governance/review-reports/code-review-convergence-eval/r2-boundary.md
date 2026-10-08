severity: major

seat: code-review-convergence-eval/r2/邊界-gpt-5.6-sol

實讀範圍:
- `CLAUDE.md:1-101`
- `r2-graph-lens.txt:1-69`
- `r2-repair-binding.json:1-143`
- `r2-dispositions.json:1-55`
- 固定 module `1-557`
- 固定 tests `1-430`
- binding 指定 repair_source_files 的固定兩端 `-U0` 完整修補，384 行
- `r2-paired-cases.json:1-56`
- 未讀 r1 報告、intake、歷史卷證正文
- Windows 原生驗證依指示排除

實驗限制:
指定 `/tmp/review-eval-r2-seats/boundary-tmp` 無法建立，系統回覆 `Operation not permitted`；heredoc 也因無法建立暫存檔而失敗。後續案例全為純記憶體、零寫入探針；receipt 的邏輯 root 仍傳入指定路徑，固定兩端產品碼由 `git show` 載入。實際 cwd 為 `/private/tmp/lumos-future-repair-regression-research`，repo 未被修改。

BND-R2-01：128 字識別欄位限制被誤套到 receipt 路徑，破壞既有合法輸入

severity: major

blocking: 是

引句:「+    if not isinstance(value, str) or not value.strip() or len(value) > 128:」

file: `governance/eval/review_convergence.py:249`
file: `governance/eval/review_convergence.py:372`
file: `governance/eval/review_convergence.md:15`

`text_field()` 的 128 字限制原本用來約束識別欄位，修補卻讓 `load_receipt()` 也用它驗證相對檔案路徑。129 字、無 `..`、非絕對路徑、單一檔名仍低於常見檔案系統的 255-byte component 上限，before 能正常載入，after 在讀檔前直接回 `receipt-reference`。`compare()` 會因此把有效試行列進 `invalid_records`，污染品質與成本摘要。

case_source: `inline no-write boundary probe`
case_source_sha256: `12b1c44879bd658ffe0fde23fca10ca7ccf38f330b9ce14a3f2f34cc529f507d`

input:
- 相對路徑為 124 個 `r` 加 `.json`，共 129 字
- receipt、manifest、arm pins、SHA 與 outcome 皆有效
- `read_bytes` 僅替換成回傳同一份已雜湊 raw bytes；路徑驗證與 `check_trial` 均執行固定端原碼

expected_source:
- before 接受任意字串路徑，再以 anchor、`..`、symlink 與 receipt SHA 控制安全邊界
- 修後文件只宣告「字串識別欄位最多128字元」，未宣告 receipt 路徑上限

before:
- command: `ENDPOINT=8950308b71969f95119c7b2780f7a9ef93f669ac /opt/homebrew/bin/python3.14 -c '<inline no-write boundary probe>'`
- cwd: `/private/tmp/lumos-future-repair-regression-research`
- loaded commit: `8950308b71969f95119c7b2780f7a9ef93f669ac`
- loaded module SHA256: `6e7b04fcc03c0c9712de38d7e4f47e4cce04429f52390905c9da58c9380e2dc4`
- executed: 是
- rc: 0
- raw_output: `{"actual":{"error":null,"quality_pass":true},"case_source_sha256":"12b1c44879bd658ffe0fde23fca10ca7ccf38f330b9ce14a3f2f34cc529f507d","expected":"accepted valid relative receipt path","receipt_relative_path_chars":129}`

after:
- command: `ENDPOINT=c909bf980125dc90f1696372205e322e2ac877c7 /opt/homebrew/bin/python3.14 -c '<inline no-write boundary probe>'`
- cwd: `/private/tmp/lumos-future-repair-regression-research`
- loaded commit: `c909bf980125dc90f1696372205e322e2ac877c7`
- loaded module SHA256: `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- executed: 是
- rc: 0
- raw_output: `{"actual":{"error":"receipt-reference","quality_pass":null},"case_source_sha256":"12b1c44879bd658ffe0fde23fca10ca7ccf38f330b9ce14a3f2f34cc529f507d","expected":"accepted valid relative receipt path","receipt_relative_path_chars":129}`

可比與歸因:
- 同一 case SHA、同一 Python 3.14、同一 receipt bytes；只更換固定產品端。
- before 通過、after 由新增的 `text_field(ref.get("path"))` 拒絕，可直接歸因本輪修補。
- 固定 tests `1-430` 只涵蓋 NUL、越界與 symlink 類案例，未觀察到大於 128 字的合法 receipt 路徑案例；不據此宣稱不存在其他測試。

BND-R2-02：JSON `true` 與數字 `1` 被當成相同記錄，衝突成本會依輸入順序改變

severity: major

blocking: 是

引句:「+            if token in seen_tokens and seen_tokens[token] != row:」

file: `governance/eval/review_convergence.py:130`
file: `governance/eval/review_convergence.py:145`
file: `governance/eval/review_convergence.py:167`

同一 token 的兩筆 JSON 記錄分別帶 `tokens: 1` 與 `tokens: true`。模組自己的 `number()` 明確拒絕布林，但 Python 的 dict equality 視 `True == 1`，使衝突掃描把兩筆當成相同重複資料。數字列在前時會發布 `total: 1`；布林列在前則發布 `total: null`。同一資料集合僅改順序便改變研究輸出。

case_source: `inline no-write bool-vs-int token probe`
case_source_sha256: `236b3ae40c3507ee66eb447b7e5e9887c0546b4e7f1c99e3383bd5896f07bb52`

input:
- forward: 相同 loop/round/token，依序為 `tokens: 1`、`tokens: true`
- reverse: 同兩筆反序
- expected: `conflicting_tokens=true`、成本總量未知，且不受順序影響

before:
- command: `ENDPOINT=8950308b71969f95119c7b2780f7a9ef93f669ac /opt/homebrew/bin/python3.14 -c '<inline no-write bool-vs-int token probe>'`
- cwd: `/private/tmp/lumos-future-repair-regression-research`
- loaded module SHA256: `6e7b04fcc03c0c9712de38d7e4f47e4cce04429f52390905c9da58c9380e2dc4`
- executed: 是
- rc: 0
- raw_output: `{"forward":{"conflicting_tokens":false,"duplicate_records":1,"tokens":{"known_records":1,"total":1}},"reverse":{"conflicting_tokens":false,"duplicate_records":1,"tokens":{"known_records":0,"total":null}}}`

after:
- command: `ENDPOINT=c909bf980125dc90f1696372205e322e2ac877c7 /opt/homebrew/bin/python3.14 -c '<inline no-write bool-vs-int token probe>'`
- cwd: `/private/tmp/lumos-future-repair-regression-research`
- loaded module SHA256: `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- executed: 是
- rc: 0
- raw_output: `{"forward":{"conflicting_tokens":false,"duplicate_records":1,"tokens":{"known_records":1,"total":1}},"reverse":{"conflicting_tokens":false,"duplicate_records":1,"tokens":{"known_records":0,"total":null}}}`

可比與歸因:
- 同一 case SHA、固定兩端、純記憶體執行。
- 兩端結果相同，因此這是修後仍存在的具體缺陷，不歸因為本輪新回歸。
- 本輪確實改寫全域 token 衝突偵測，但沒有處理 JSON 型別敏感相等；不能把「修後發現」寫成 fix-induced。

修補三問

1. 原問題有沒有修好？

三個直接對應新增邊界碼的案例已修好：
- NUL receipt：before 為未捕捉 `ValueError: open: embedded null character in path`；after 回 `(None, 'receipt-path')`。
- 孤立 surrogate：before 接受 `'\ud800'`；after 回 `DataError: input-json`。
- `tokens: true` outcome：before 接受；after 回 `DataError: cost-tokens`。

共同 case_source_sha256: `3c26fdf422b5ffbb529280f11fb054864110267775737856365f581c842c5ac7`

before:
- command: `ENDPOINT=8950308b71969f95119c7b2780f7a9ef93f669ac /opt/homebrew/bin/python3.14 -c '<inline repair-boundary probes>'`
- loaded module SHA256: `6e7b04fcc03c0c9712de38d7e4f47e4cce04429f52390905c9da58c9380e2dc4`
- rc: 0；executed: 是
- raw_output: `{"bool_cost":{"exception":null,"returned":"None"},"nul_receipt":{"exception":"ValueError:open: embedded null character in path","returned":null},"surrogate_json":{"exception":null,"returned":"'\\ud800'"}}`

after:
- command: `ENDPOINT=c909bf980125dc90f1696372205e322e2ac877c7 /opt/homebrew/bin/python3.14 -c '<inline repair-boundary probes>'`
- loaded module SHA256: `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- rc: 0；executed: 是
- raw_output: `{"bool_cost":{"exception":"DataError:cost-tokens","returned":null},"nul_receipt":{"exception":null,"returned":"(None, 'receipt-path')"},"surrogate_json":{"exception":"DataError:input-json","returned":null}}`

2. 之前正常路徑是否仍成立？

否。BND-R2-01 證明原先可讀取的 129 字合法相對 receipt 路徑在 after 被拒。

3. 新增問題是否能歸因修補？

- BND-R2-01：可以，固定 before 通過、after 在新增驗證分支失敗。
- BND-R2-02：不可以；兩端均重現，保留為既存但未修的 current bug。

圖譜硬合約逐條答

- H01 測試假綠形態：NUL、surrogate、布林成本三案有同案例 before/after 翻紅綠與現場輸入；BND-R2-01、02 未獲同等測試保護，故不宣告整體合約通過。
- H02 bound-tests 真跑與 rc：repair_source_files 未改 gate 實作；分工未讀完整 `scripts/test_lumos.py`，未判定。
- H03 canary record 成功必落盤：不在修補產品範圍，未判定。
- H04 canary second 純 telemetry：不在修補產品範圍，未判定。
- H05 guard-kill rc 優先序：不在修補產品範圍，未判定。
- H06 guard-kill JSON 純度：不在修補產品範圍，未判定。
- H07 三支 PowerShell ASCII-only：Windows 原生依指示排除，未判定。
- H08 PowerShell 不用保留名 `$Args`：Windows 原生依指示排除，未判定。
- H09 CLAUDE 注入保留 sentinel 外 bytes：不在修補產品範圍，未判定。
- H10 CLAUDE 注入冪等：不在修補產品範圍，未判定。
- H11 完整版區塊 byte-level 備份：不在修補產品範圍，未判定。
- H12 安裝時寫 manifest 身分證：不在修補產品範圍，未判定。
- H13 CLAUDE 注入前目標守衛：不在修補產品範圍，未判定。
- H14 `.cmd` 直譯器不得硬編碼：Windows 原生依指示排除，未判定。
- H15 Windows `lumos`/`lumos.cmd` 雙碰撞偵測：Windows 原生依指示排除，未判定。
- H16 卸載 bin 前依 manifest 內容比對：不在修補產品範圍，未判定。
- H17 四個卸載步驟互不阻擋：不在修補產品範圍，未判定。
- H18 skill 目錄移除前備份：不在修補產品範圍，未判定。
- H19 CLAUDE sentinel byte-level 還原：不在修補產品範圍，未判定。
- H20 `.cmd` 與 script 各自獨立移除：Windows 原生依指示排除，未判定。
- H21 卸載須清理 manifest：不在修補產品範圍，未判定。
- H22 search 排除 superseded、不排 stale：不在修補產品範圍，未判定。

表態核對:
- `py-memory` 的 `tension/chosen=suggested` 確實落成有限讀取與 receipt 欄位投影；BND-R2-01 顯示共用 validator 的套用邊界錯誤，不能據表態宣告 satisfied。
- `py-hotpath`、`py-eventloop`、`py-parallel`、`py-external`、`py-extcode` 未發現與本席兩項 finding 相反的證據，但本席不替其他鏡頭作正向認證。

未驗範圍:
- Windows 原生路徑與 PowerShell。
- `scripts/test_lumos.py` 完整產品樹及圖譜超出上限節點。
- r1 席報告、intake、歷史測試 log 與 archive-only 檔。
- 指定暫存目錄因 sandbox 拒絕，未做真實 129 字檔名落盤；BND-R2-01 僅隔離驗證讀檔前的路徑拒絕分支。
- 單家族邊界視角不保證無其他回歸。

最高等級: major

阻擋條數: 2