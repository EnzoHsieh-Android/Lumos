severity: major

我只讀了 diff 並實跑極端輸入,臨時目錄已刪。`include_test_paths` 的各種壞輸入、`_RULEPACK_SAMPLE_RE`、`check.py` 在系統 python3.9 上的相容性都沒問題。有一條 major(`check.py` 的 `scan()` 失敗被當成零命中)和三條 minor。

## Findings

severity: major
blocking: 是
位置:`configs/ast-grep/kotlin-android/check.py` 的 `check()`,diff 第 315 行附近。
引句:「for (i, f) in scan(sg, cfg, TEST_ONLY_ANCESTOR) or []:」
失敗場景:`scan()` 在 ast-grep 非 0/1 結束時回 `None`。`or []` 把這個失敗當成「零命中」,所以「只掃測試碼的規則不准命中祖先目錄叫 test 的正式碼」這道守衛在工具壞掉時安靜通過。同一支檔對 `samples/bad` 和 `samples/good` 的 `None` 都會報「跑不起來」,只有這一處吞掉。
重現:用一個遇到 `ancestor-named-test` 路徑就 `exit 2` 的 ast-grep 包裝腳本,其餘參數轉給真的 ast-grep。
```
python3.14 -I configs/ast-grep/kotlin-android/check.py --sg <包裝腳本>
→ 規則 208 條,問題 0 個
```
預期要報「掃 samples/ancestor-named-test 跑不起來」,實際零問題、退出碼 0。

severity: minor
blocking: 否
位置:`check.py` 的 `check()`,規則目錄全空時。
引句:「規則 {len(rules)} 條,問題 {len(problems)} 個」
失敗場景:`rules/` 與 `rules-hints/` 的 `*.yml` 全刪掉(或目錄改名),`load_rules()` 回空清單。`loaded_count` 也是 0,於是什麼都沒檢查就通過。
重現:在副本刪光兩個目錄的 yml,輸出「規則 0 條,問題 0 個」,退出碼 0。
建議:規則數為 0 直接當問題。

severity: minor
blocking: 否
位置:`check.py` 的 `load_rules()`,YAML 用正規式解析。
引句:「msg = re.search(r"^message:\s*(.+)$", doc, re.M)」
失敗場景:以下合法 YAML 都會被誤判,方向是報錯(不是漏報):
- 行尾有註解:`message: '[API-1] x; 改用 y'  # note`,引號剝不掉,報「message 要以 [型錄編號] 開頭」。
- 摺疊或多行 `message: >`,取到 `>`。
- 雙引號內的 `\"` 不還原,長度算多。
- id 或 severity 加引號,如 `id: 'kt-g'`,報「id 要用 kt- 前綴」。
- 檔首有 BOM,該規則整條被跳過,只靠 `loaded_count` 的數量差才抓得到。

目前 208 條規則都是單行單引號,沒有實害。以後有人寫別的 YAML 形式,會被逼著改寫成這支解析器剛好吃得下的樣子。

severity: minor
blocking: 否
位置:`scripts/lumos` 的 `_lint_new_config`,diff 第 390 行。
引句:「cfg["include_test_paths"] = frozenset(x.strip().lstrip(".").lower() for x in v if x.strip().lstrip("."))」
失敗場景:不合法的值會警告,但這幾種被靜默吞掉,一樣是「設了卻沒效」:
- `[""]` 和 `[" . "]` 變成空集合,沒有警告。
- `["tar.gz"]` 留著多段副檔名,而 `Path.suffix` 只會給 `gz`,永遠對不上。
- `["kt "]`、`["..kt"]`、`["KT"]` 會被正規化成 `kt`,這是正向的。

實跑 `_lint_new_config(..., from_snapshot=True)`:`[None]`、`{}`、`"kt"`、`[1]` 都有警告並照沒設處理。10 萬個元素的清單不會出問題。

## 試過、沒問題
- `_RULEPACK_SAMPLE_RE` 用 `.match`,只擋 repo 根的 `configs/ast-grep/<x>/samples/`。消費專案若剛好有同名路徑的真程式碼,會被靜默排除出風險掃描。巢狀路徑如 `sub/configs/ast-grep/x/samples/` 不排除。目前不影響本 repo,只算隱性取捨。
- 路徑含空白、中文、`..` 的 `src/test/…A.kt`,在 `keep_test_ext={"kt"}` 下行為一致:大小寫不分(`A.KT` 也過),`.kts` 不過。git 不會產生反斜線路徑,所以 Windows 路徑情境不成立。
- 新的 frozenset 沒被任何地方存成 JSON。
- `check.py` 用 `/usr/bin/python3`(3.9.6)和 `-I` 跑,完整 208 條與 `--catalog-only` 都過;語法也通過 `feature_version=(3,8)`。
- 把整份包複製到路徑含 `good/` 的目錄下跑,結果相同,`parts.index` 沒有被騙(ast-grep 輸出的是相對路徑)。
- 型錄缺〈待查證〉節時會報錯,不會崩;表格的跳脫直線和反引號內直線的處理正常。
- 測試專用規則的偵測正規式(`^files:.*src/test…`,DOTALL)在現有 17 條上與逐行判讀一致,只有 `kt-setmain-in-androidtest`(區塊式清單)不同,是設計用意。
- 順帶:`--sg` 後面沒給值會直接 IndexError(minor,未獨立列點)。

總結:唯一要擋的是 `scan(...) or []` 讓守衛在 ast-grep 失敗時假通過;其餘三條是邊緣輸入的 minor。
