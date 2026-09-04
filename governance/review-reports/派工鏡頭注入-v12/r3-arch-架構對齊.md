# r3 架構對齊審查——派工鏡頭注入 v1.2(固定席 0 篇備援段,第 3 版/上限輪)

審查範圍:凍結審材 `派工鏡頭注入-v12-r3.md` 的「## v1.2」節(第 184-203 行)。只判這節設計跟本 repo 既有做法一不一樣,不找 bug、不評風格。

## r2 驗收(三條,查證後皆已改)

r2 架構對齊席(`r2-arch-架構對齊.md`)判出的 f4/f5/f6 在這版逐一核對:

1. **f4(設定讀 base 無機制)→ 已加「從 git ref 讀 JSON」helper**:r2 判「`.lumos/cochange.json` 讀 base 版」沒有既有函式可循,`_cochange_load_config`(scripts/lumos:13371)與 `load_test_profile`(scripts/lumos:2622)全部寫死讀工作樹路徑。r3 第 189 行改成「新增一個小 helper『從 git ref 讀 JSON』(`git show <base>:<path>` 解 JSON,沒有→回預設)……測試 profile 與 cochange 設定都用它讀 base 版」——方向對齊(見〈檢查 1〉細節),f4 消解為「機制已定,落地細節仍有一處待確認」,折入下方 f7。
2. **f5(測試格自造 stem 判定)→ 已沿 `_testmap_stem`/`_testmap_strip`**:r2 判「找內容提到該檔 stem」是另立一套邏輯,沒碰 `cmd_testmap_build` 既有的 naming/content 雙訊號。r3 第 191 行改成「★沿 `cmd_testmap_build` 既有的檔↔測試比對邏輯(`_testmap_stem`/`_testmap_strip`+內容正規式)★」,查證 `_testmap_stem`(scripts/lumos:14365)、`_testmap_strip`(scripts/lumos:14405)確實是原本判定 stem 的函式,而且新加的「無副檔名檔(如 `scripts/lumos`)用完整路徑比對,不用 stem」是有理由的例外——`_testmap_stem("scripts/lumos")` 因為找不到 `.`(`i = name.rfind(".")` 回 -1,不滿足 `i > 0`)會直接回傳整個檔名 `"lumos"` 當 stem,這正是通才席實測「stem `lumos` 命中 221/585 支」的成因,不是無的放矢的特判。f5 消解。
3. **f6(排序缺收尾鍵)→ 已補收尾鍵**:r2 判三格排序都只給單一分數鍵,沒有本 repo「主鍵+至少一個決定性收尾鍵」的多鍵慣例(scripts/lumos:16242 註解)。r3 三格分別改成「命中次數降冪+路徑」「confidence 降冪+路徑」「被引次數降冪+路徑」——每格都補上路徑當收尾鍵,滿足 f6 原話「主鍵+決定性收尾鍵」的門檻(f6 本身沒有要求正好三鍵,`cmd_cochange_rules` 的三鍵是它自己因為有三個判準欄位,不是通則)。f6 消解。

三條驗收通過,可以往下看新結構。

## 新結構逐項檢查(協審指定的五個點)

### 檢查 1:「從 git ref 讀 JSON」helper 放哪、命名跟既有 `_lens_git`/`_git_commit_exists` 一致嗎

底層機制對齊:helper 描述「`git show <base>:<path>` 解 JSON」,這正是 dispatch-lens 自己已經在用的呼叫——`_lens_git(root, "show", f"{base_sha}:{it['rel']}", quote=True)`(scripts/lumos:16702)讀 base 版節點全文,新 helper 只是同一招換一個路徑目標再包一層 `json.loads`,不是新機制。命名慣例上,整個 dispatch-lens 區塊(scripts/lumos:16487-16712)所有輔助函式一律 `_lens_` 前綴——`_lens_range_ok`(16499)、`_lens_git`(16511)、`_lens_full_sha`(16522)、`_lens_cache_path`(16540)、`_lens_cache_read`(16546)、`_lens_cache_write`(16560)、`_lens_contract_lines`(16574)、`_lens_contract_rows`(16592)——這條命名慣例很硬,但 v1.2 原文只寫「新增一個小 helper」,沒有給名字也沒有講放在哪個檔案哪個區塊。

真正沒答的是更底層的問題:`_cochange_load_config`(scripts/lumos:13371-13399)不是純粹的「讀檔」函式,它把「讀檔」跟「型別守衛」「`min_support` 硬底線 2」這些驗證邏輯焊在一起(這條底線本身是 code-loop r1 修過的真事故,不是隨手寫的);`load_test_profile`(scripts/lumos:2622)同構。v1.2 說「測試 profile 與 cochange 設定都用它讀 base 版」,但沒說清楚驗證邏輯怎麼辦——如果新 helper 只回傳解析後的裸 dict、兩個呼叫端各自繞過 `_cochange_load_config`/`load_test_profile` 直接用,min_support 底線這類既有保護就會在 base 版讀取路徑上消失;如果 helper 只回傳原始文字、仍舊餵給 `_cochange_load_config`/`load_test_profile`(只是它們的讀檔那一步換成從 base 讀),驗證邏輯就保住了。兩種做法結構上差很多,spec 沒表態。判不準,列 f7。

### 檢查 2:共用 deadline 用單調時鐘——repo 有沒有「總預算 deadline」先例

有,而且沿得很準。`cmd_delguard_check`(scripts/lumos:13773)整段就是同一個模式:`t0 = time.monotonic()`(13780)、`deadline = float(os.environ.get("LUMOS_DELGUARD_DEADLINE", "15.0"))`(13782)、`_over()` 閉包比較經過時間(13785),之後每個耗時步驟(git diff、confidence 計算、vault scan 迴圈)前都呼叫 `_over()` 決定要不要提早降級放行、印固定訊息、記治理帳。v1.2「備援段開始時取單調時鐘 30 秒 deadline,每次 `git show` 前檢查剩餘,超過→整段備援跳過、印固定字串」是同一套技術(monotonic 起點+迴圈前檢查+固定降級訊息),不是另立一套。

唯一的差異是 `_delguard` 的 deadline 可用環境變數覆寫、v1.2 的 30 秒是寫死的常數——但這不算偏離,因為 dispatch-lens 自己在 v1.0 就已經是這個風格:`scripts/hooks/claude/dispatch-lens-hook.py:20` 的 `INNER_TIMEOUT = 45` 同樣是模組層寫死常數、無環境變數覆寫(註解「外層 HOOK_ENTRIES 宣告 60;內層必須明顯小於外層」)。v1.2 沿用的是 dispatch-lens 自己已經定的規矩,不是 `_delguard` 的規矩,兩者剛好一致,不列不對齊。

severity: clean

### 檢查 3:快取鍵加 schema 版本——`_lens_cache_path` 現在怎麼組鍵,加版本要不要換目錄

`_lens_cache_path(repo_root, base_sha, head_sha)`(scripts/lumos:16540-16543)現在的做法是把三個欄位字串接起來(`f"{repo_root}|{base_sha}|{head_sha}"`)餵 `hashlib.sha256`,檔名=雜湊值,目錄固定 `~/.cache/lumos/dispatch-lens/`——版本區隔本來就是靠雜湊輸入決定,不是靠目錄分層。v1.2「快取鍵=(repo, base sha, head sha, schema 版本 2)」只是把同一個雜湊輸入從三元組擴成四元組,目錄照舊,是這個函式現有機制的直接延伸,不需要也沒有理由換目錄。

severity: clean

### 檢查 4:「函式本體範圍」需要解析 def 邊界——repo 有沒有既有的 python def 範圍工具

有,而且是同一個 repo 裡已經在用的成熟做法,但 v1.2 沒有沿用。「精簡版」產生器 `scripts/slim-gen.py` 整支就是靠 `ast.parse`+`ast.walk`+`ast.FunctionDef` 做 python 程式碼的可達性分析與刪除範圍計算,其中恰好就是算「一個函式的本體行範圍」:`start = min([n.lineno] + [d.lineno for d in n.decorator_list])` 接 `dels.append((start, n.end_lineno))`(scripts/slim-gen.py:202-203)——用 AST 節點的 `lineno`/`end_lineno`(含裝飾器)取得函式從定義到結尾的精確行區間。同一招在 `scripts/slim-scan.py:131-138`(`ast.parse`+`node.lineno`)、`scripts/test_lumos.py:18295-18298`(`ast.walk` 找 `FunctionDef`/呼叫關係)都在用。`ast` 是標準庫,不算違反零依賴家規,而且「呼叫者」這格本來就已經限定只處理 python(v1.2 原文「非 python 印『非 python 檔,呼叫者格跳過』」),沒有 `discover_test_methods`/`build_code_haystack` 那種要跨語言 profile 通吃的理由要迴避 `ast`。

`scripts/lumos` 本體確實整支零 `import ast`(已查全檔),用的是正規式/縮排式掃描(`build_code_haystack`、`discover_test_methods` 那套),但那是為了跨語言(C#/Kotlin/…)profile 可插拔;v1.2 這格已經自己把範圍縮小到純 python,卻選擇「定義行到下一個頂層定義前」這種文字/縮排式 heuristic 重新發明同一個問題(裝飾器算不算進函式起點?巢狀定義怎麼辦?字串常數裡出現 `def ` 開頭的文字會不會誤判邊界?),而不是複用同 repo 已經解掉這些邊界情況的 `ast.parse`。這是同一個問題的第二種做法。列 f8(major/blocking)。

### 檢查 5:「識別度門檻 20%」這種啟發式閾值有沒有既有慣例寫法

有慣例可循,且沒有證據顯示 v1.2 會偏離。本 repo 寫這類啟發式門檻的慣例是「模組層具名常數+行內註解交代來源」:`_EL_NEAR_THRESHOLD = 0.6`(scripts/lumos:5917,註解「B 的檔名 difflib 單判準……沿用(spec EL-16)」)、`_RANK_TYPE_MULT_MOC = 0.4`(scripts/lumos:1976,註解交代訓練來源)都是這個形狀,不是寫進 `.lumos/config.json` 讓使用者調——`.lumos/config.json`/`.lumos/cochange.json` 目前收的是「使用者可能想因專案而異的設定」(測試 profile、cochange 門檻),不是演算法內部的實驗性常數。v1.2「命中超過 base 測試方法總數 20%」沒寫常數名字或位置,但既然整個 `_lens_*` 區塊本來就是這種寫死常數的風格(`_LENS_SHA_RE`、`_LENS_HEADER`、`_LENS_KIND` 皆同款),這格留白比較像是留給實作時機的細節,不是跟既有做法對著幹的訊號。判不準但沒有具體衝突,不列不對齊。

severity: clean

## 不對齊清單

### f7

分層與資料源:「從 git ref 讀 JSON」helper 要不要保留 `_cochange_load_config`(scripts/lumos:13371)/`load_test_profile`(scripts/lumos:2622)既有的型別守衛與 `min_support` 硬底線(這條底線本身是 code-loop r1 修過的既有事故,scripts/lumos:13397-13399),spec 沒寫清楚——是這兩支函式改造成可插拔讀檔來源(驗證邏輯保留、對齊),還是新 helper 繞過它們直接把裸 JSON 交給呼叫端用(驗證邏輯在 base 版讀取路徑上消失、算第二種做法)。命名與放置位置(是否沿 `_lens_` 前綴、放進 dispatch-lens 區塊)spec 也沒講。

引句:「新增一個小 helper「從 git ref 讀 JSON」」

severity: ⚠

blocking: 否

### f8

第二種做法:「呼叫者」格用文字/縮排式「定義行到下一個頂層定義前」heuristic 自行判定函式本體行範圍,沒有沿用同 repo 已經在用、更正確的 `ast.parse`+`FunctionDef.lineno`/`end_lineno`(含裝飾器起點)做法——`scripts/slim-gen.py:202-203`、`scripts/slim-scan.py:131-138`、`scripts/test_lumos.py:18295-18298` 都是這個問題已有的解法。這格本來就已經限定只處理 python,沒有跨語言 profile 的理由迴避 `ast`,`ast` 也是標準庫、不違反零依賴家規。

引句:「函式本體範圍(定義行到下一個頂層定義前)」

severity: major

blocking: 是

## 小結

不對齊共 2 條,其中 major 1 條。
