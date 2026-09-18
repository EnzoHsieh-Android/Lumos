severity: major

## 三問逐答(對照起點)

**問①`_is_code_file` vs 新的 `_docs_only_file`**——兩份「讀首行判 #!」的邏輯幾乎一樣(都是:磁碟有就讀磁碟,沒有就 `git show base:path` 讀範圍起點,兩邊都讀不到就保守判定),而且已經共用 `_head_is_shebang`(`scripts/lumos:5620-5622` 的註解就寫「每支檔有家與 `_is_code_file` 共用這一支」)。差別在 `_is_code_file`(`scripts/lumos:5628`)會先過 `_NODEHOME_EXCLUDE_GLOBS`/`_nodehome_is_test`/`_cochange_excluded` 三層豁免才看副檔名,`_docs_only_file`(`scripts/lumos:22287`)完全不過這三層、直接看白名單命中後就看副檔名。這是因為兩者回答的問題不同(一個是「要不要有家」、一個是「算不算純文件」),所以判定方向不同是合理的,不算引入沒對齊的第二種做法——保留「讀首行」那段沒抽成共用函式是可以再抽,但沒對齊到會出錯的程度,列為觀察不升級。

**問②既有的 `_sc_changed_files`(-z + numstat)vs 新的兩處 `git diff --name-only -z`**——`_sc_changed_files`(`scripts/lumos:5660`)用 `--numstat -z` 且★不帶 `--no-renames`★,自己解析三/五欄格式把改名攤成(新路徑, 新增, 刪除, 二進位, 舊路徑)。新的 `_test_suite_for_range`(`scripts/lumos:22319`)與 `_affected_test_keys`(`scripts/lumos:22338`)改用 `--name-only -z --no-renames`,理由在註解裡講明:要讓「從 scripts/ 搬進 docs/」被拆成「刪程式檔+加文件」才會判 full,測試 ⑥ 也真的釘住這個行為。這是刻意的行為分歧、有理由、有測試,不是沒看到的落差。但這兩個新函式各自重跑一次一模一樣的 `git diff --name-only -z --no-renames`(範圍相同、過濾邏輯相同),對同一批檔案各自呼叫一次 `_docs_only_file`——沒理由不共用一次算好的檔案清單,列 F3(效能重複,非正確性)。

**問③`_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS` 的消費者現在變幾個**——原本 7 處(`scripts/lumos:5671`、`15368`、`15369`、`22251`、`22252`、`22264`、`27752`),這批加了 `_test_suite_for_range`(`scripts/lumos:22328`)與 `_affected_test_keys`(`scripts/lumos:22344`)兩處,共 9 處消費者,兩處新增都正確沿用既有常數而不是自開正則——這點是對齊的,不是問題。

## F1 test_lumos.py 手抄一份白名單,不是引用既有的單一源

severity: major
blocking: yes

`scripts/lumos:22284` 定義 `_DOCS_ONLY_PATHS`,`scripts/test_lumos.py:34` 又手打一份幾乎逐字一樣的 `_DOCS_SUITE_PATHS`,靠新加的 `t_docs_suite_whitelist_matches_lumos` 去比對兩邊相等來抓漂移。但這份 repo 對「測試檔要用 lumos 本體的常數」早有現成寫法:`_load_lumos_inproc()`(`scripts/test_lumos.py:181`)把 `scripts/lumos`當模組載入,測試檔到處直接讀 `m._VENDORED_TOOLKIT`(`scripts/test_lumos.py:3310`、`7905`、`8080`、`10262`、`33398`、`37753`)、`m._DELGUARD_EXCLUDE_DIRS`(`3319`)、`m._DELGUARD_EXCLUDE_LOCKFILES`(`3334`)這些常數,從沒有另抄一份再寫測試釘相等。這批引入的是第二種做法:先複製一份字面量常數,再靠一支新測試防止它漂掉——結構上仍然可能漂(下一個 session 改了 `scripts/lumos` 那份白名單、卻沒想到或忘了跑那支釘測試,漂移窗口就存在),而既有寫法(`_DOCS_SUITE_PATHS = _load_lumos_inproc()._DOCS_ONLY_PATHS`,或在 `_docs_suite_select` 內部延遲讀 `_load_lumos_inproc()._DOCS_ONLY_PATHS`)讓漂移在結構上就不可能發生,不必靠人記得跑哪支測試。這正是「自己再刻一份已有的工具函式、繞過既有寫入口」的形狀。

引句:「跟 scripts/lumos 的 `_DOCS_ONLY_PATHS` 同一份名單(有測試釘兩邊相等)。」
引句:「不靠人手維護清單,新寫的測試只要提到 README/docs/… 就自動進子集。」

file: `scripts/lumos:22284`
file: `scripts/test_lumos.py:34`
file: `scripts/test_lumos.py:181`
file: `scripts/test_lumos.py:3310`

為什麼是 bug 而不是風格:review 這批自己在派工詞裡點名要查「同層對照檔的慣例相反」跟「自己再刻一份已有的工具函式」——`_load_lumos_inproc()` 讀常數正是同一支測試檔裡處理同一類問題(測試端要跟 lumos 本體常數同步)的既有慣例,這裡引入了平行的第二種做法(複製+釘測試)而不是沿用單一源,判準完全命中派工詞給的 major 條件。不是「兩種寫法都能接受的風格偏好」,是有現成單一源可以直接讀、卻選了會漂移的複製法。

## F2 CI 判斷 BEFORE 可不可用,跟同檔案既有寫法不一致

severity: minor
blocking: no

`.github/workflows/ci.yml` 裡早就有一段判斷 `github.event.before` 能不能拿來算 diff 範圍的邏輯(`code-loop gate`,約在檔案前段),用的是 `git cat-file -e "$BEFORE^{commit}"`——明確要求那個物件是 commit,不只是「存在」。這批新增的「這次推送要跑哪個測試範圍」那一步驟改成 `git cat-file -e "$BEFORE" 2>/dev/null`,少了 `^{commit}`,只確認物件存在、不確認型別。兩處在同一支檔案裡處理同一件事(webhook 給的 `before` sha 能不能信),寫法卻不同。實務上 GitHub webhook 的 `before` sha 幾乎必然是 commit,兩種寫法在正常情境下結果相同,尚未觀察到會產生不同行為的具體輸入,所以不升級成 major,但跟既有慣例不一致,值得統一。

引句:「[ "${{ github.event_name }}" = push ] && [ -n "$BEFORE" ] && [ "$BEFORE" != "0000000000000000000000000000000000000000" ]」
引句:「&& git cat-file -e "$BEFORE" 2>/dev/null; then」

file: `.github/workflows/ci.yml`(既有 code-loop 那步用 `git cat-file -e "$BEFORE^{commit}"`,行號在這批 diff 範圍之外、屬於 beb61e03 之前就有的內容)

## F3 `_test_suite_for_range` 與 `_affected_test_keys` 各自重算一次同一批檔案

severity: minor
blocking: no

兩支函式各自呼叫一次 `git diff --name-only -z --no-renames`(同一個 `diff_range`),各自再對每一支檔案呼叫一次 `_docs_only_file`(對沒副檔名又被刪的檔案,`_docs_only_file` 內部還可能多開一次 `git show` 子行程)。`_pitfall_diff_collect` 兩個 return 分支都是先呼叫 `_test_suite_for_range` 拿 `suite`,緊接著又呼叫 `_affected_test_keys` 重新掃一次同一批檔案。純粹重複運算,沒有共用「這個範圍改到哪些非文件檔」這個中繼結果,pre-push 熱路徑上每次 push 多付一次 git 子行程與可能的額外 `git show`。這是效能重複,不影響判斷結果的正確性,所以不升級成 major。

引句:「r = subprocess.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false", "diff", "--name-only", "-z",」

file: `scripts/lumos:22319`(`_test_suite_for_range`)
file: `scripts/lumos:22338`(`_affected_test_keys`)

## 驗過的路徑

- 實際跑了這批新增的五支測試(`t_test_suite_docs_only_judgement`、`t_docs_suite_whitelist_matches_lumos`、`t_runner_suite_flags`、`t_prepush_docs_and_light_run_subset`、`t_prepush_and_ci_wired_for_docs_suite`),全綠,行為跟宣稱相符。
- 讀過 `_is_code_file`/`_nodehome_code_kind`/`_NODEHOME_CODE_EXTS`/`_NODEHOME_EXCLUDE_GLOBS` 全文,核對 `_docs_only_file` 對「docs/ 底下的 .py」「無副檔名 #!」「被刪檔案回溯 base」三種情境的判定方向跟 `_is_code_file` 是否自洽(自洽,方向一致但套用範圍不同)。
- 讀過 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS` 全部消費者(9 處),核對新加的兩處沒有各寫一套排除邏輯。
- 讀過 `scripts/hooks/pre-push` 裡探測 `--shard`/`--suite` 旗標、暫存檔建立與清除、`_SUITE_SEEN/_SUITE_FULL/_SUITE_LIGHT` 在多 ref 迴圈裡聚合的順序,核對「任一 ref 是 full → 整體 full」「全部是 docs/light → 才走子集」的邏輯沒有反過來。
- 讀過 `.github/workflows/ci.yml` 既有的 `before..sha` 用法(code-loop 那步)跟這批新加的那步的差異。
- 沒有發現「該跑全套卻只跑了子集」的具體可重現輸入——`--no-renames` 刻意讓搬檔案進 docs/ 判成 full、被刪的 shebang 檔案回溯 base 判成 full、算不出範圍一律 full,fail-safe 方向都對。

## 總計

不對齊共 3 條,其中 major 1 條(F1)、minor 2 條(F2、F3)。
