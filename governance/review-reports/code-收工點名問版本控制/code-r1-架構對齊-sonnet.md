severity: minor

## 材料完整性警訊(⚠ 交編排者判斷,不計入下方「不對齊」總數)

severity: minor
blocking: 否

被審的 `r1-code.patch` 除了 `scripts/hooks/claude/check-graph-sync.py`、`scripts/test_lumos.py`(新增測試那段)之外,還含 `scripts/hooks/pre-push` 與 `scripts/lumos` 兩支檔、以及 `scripts/test_lumos.py` 裡整段刪除「純文件推送只跑文件子集」(`_DOCS_ONLY_PATHS` / `_test_suite_for_range` / `_affected_test_keys` / `--suite docs|keys` 等)的 hunk。我用 `git -C <本 worktree> diff 79a7072c..d557630d --stat` 核對,**這兩支檔在 LUMOS-IMPACT 指定的範圍裡完全沒有被改動**;`git show d557630d --name-only` 也不含它們。往回追,「純文件推送只跑文件子集」是 `9b180e4d`(分支 `main`)才加進去的功能,而本次審查所在的 `79a7072c`(分支 `fix/stop-hook-shell-coverage`)這條系譜從頭到尾都不含這個功能——所以 patch 裡「移除它」的那幾個 hunk 是拿另一條分支(`main`,含 `9b180e4d`)當 diff 底,不是拿 `79a7072c`。

引句:「原本閘門 2 與閘門 3 都靠列舉工具名算清單(三個編輯工具 + rm/mv/cp 那幾個命令)」
file: `scripts/hooks/claude/check-graph-sync.py:19`(這句在真實 diff 內,屬於本案範圍,無問題;上面警訊指的是 pre-push/scripts/lumos 那兩支檔的 hunk)

**建議**:請編排者確認 `r1-code.patch` 是否用錯 base 重新生成;下面三問只針對確定屬於本次變更範圍的 `scripts/hooks/claude/check-graph-sync.py`(與其對應的 `scripts/test_lumos.py` 新測試)作答,pre-push / scripts/lumos 兩支檔的內容不計入判準。

---

## 問一:分層與依賴方向

severity: clean

這支 hook 本來就並存三種對外呼叫:①純自算(解析逐字稿/字串,如 `is_code_file`、`touched_graph_via_cli`)、②直接呼叫系統工具、不經信任檢查(`find_notes_mentioning` 呼叫 `obsidian` CLI)、③經信任路徑檢查再呼叫本專案主程式(`_trusted_lumos()` 之後呼叫 `lumos impact --diff`)。

file: `scripts/hooks/claude/check-graph-sync.py:502-531`(`find_notes_mentioning` 直接 `subprocess.run(["obsidian", ...])`,無信任檢查)
file: `scripts/hooks/claude/check-graph-sync.py:605-741`(`_trusted_lumos()` 一路驗 symlink/uid/可寫性,才把路徑交給呼叫端執行 `lumos`)

新增的 `_git_status_entries` / `_head_shebang` 走的是②(直接呼叫系統工具 `git`,不經信任檢查):
file: `scripts/hooks/claude/check-graph-sync.py:304-321`
file: `scripts/hooks/claude/check-graph-sync.py:346-357`

計劃節點裡有明白表態選這條路、且理由跟既有 `obsidian` 呼叫、以及 `pre-commit`/`pre-push` 兩道閘一致(它們也是直接呼叫 `git`,不查信任):
引句:「本案選直接呼叫版本控制工具,不經信任檢查」
file: `docs/lumos-toolchain-knowledge/Projects/收工點名問版本控制_計劃.md`(〈這個查詢要怎麼呼叫〉節)

所以**這次新增走的是這支檔既有三種裡的第②種,跟同檔既有同類呼叫(`obsidian`)一致,不是新開一條路**。`main()` 裡的呼叫順序也沒有變:閘門 2/3 仍在 `main()` 內部依序判,新函式只是換了資料來源,沒有把查詢邏輯挪到別層或反向呼叫。

有一點值得記錄但不構成不一致:舊的閘門 3 判準函式 `touched_graph_via_cli`(解析逐字稿裡的 `obsidian` mutate 呼叫)在這次改動後已經沒有任何呼叫點(`main()` 不再用它,測試也沒有引用它),變成孤兒函式。
file: `scripts/hooks/claude/check-graph-sync.py:425`(定義處,repo 內搜尋不到其他呼叫點)
這屬於清理遺漏而非分層不一致,不列入嚴重度判定(bug/清理類,不是本次審查範圍)。

## 問二:命名與錯誤處理

severity: minor

**這支 hook 既有的「算不出來怎麼辦」慣例是:回傳一個特殊值(`None` 或空容器),呼叫端靜默放行/跳過**,不印堆疊、不擋:
引句:「回 None 時呼叫端要靜默跳過那段功能」
file: `scripts/hooks/claude/check-graph-sync.py:590-592`(`_trusted_lumos()` 註解區)
`find_notes_mentioning` 查不到 `obsidian` 就回 `{}`(file: `scripts/hooks/claude/check-graph-sync.py:520-521`)。

新增的 `_git_status_entries` 完全照這個慣例:任何例外或非零 retcode 一律回 `None`,呼叫端 `if entries is None: return 0`:
file: `scripts/hooks/claude/check-graph-sync.py:304-321`(定義)
file: `scripts/hooks/claude/check-graph-sync.py:952-953`(呼叫端)
`_load_printed` 讀不到也回 `None`、當「沒印過」處理,同一慣例:
file: `scripts/hooks/claude/check-graph-sync.py:391-400`

**命名風格**(`_動詞/名詞_名詞` 的小寫底線)也跟鄰居一致,例如既有 `_stop_mark_path` / `_stop_dir_ok` 對應新增的 `_printed_mark_path` / `_entry_is_code`,新舊都是「先講對象、再講判斷」的次序,沒有另立一套命名法。

**唯一的 minor 落差**:`_git_status_entries` 與 `_head_shebang` 各自重複寫了一遍 `subprocess.run(["git", "-C", str(project_root), ...], capture_output=True, ..., timeout=_inner_budget(default=20))`,而同一批鄰居檔裡 `scripts/hooks/claude/memory-sweep.py` 對「多次呼叫 git」已經抽出共用的 `_git(*args, cwd=None)` 小函式(三個呼叫點共用一份逾時/例外處理)。
引句:「全部用參數陣列呼叫外部程式,沒有 shell,所以記憶檔裡的字串不可能被當成指令執行」
file: `scripts/hooks/claude/memory-sweep.py:183-187`(`_git()` 定義)
file: `scripts/hooks/claude/memory-sweep.py:197`、`218`、`222`(三個呼叫點共用)

本檔兩個新呼叫點沒有比照抽出等價的 `_git()` helper,而是各自內嵌一次 `subprocess.run` + `_inner_budget(default=20)`。兩處寫法本身一致(同一套逾時/例外處理),不算「第二種做法」,只是沒有把重複的兩行收斂成鄰居檔已示範過的共用小函式——命名/錯誤處理的「風格」層面跟鄰居有落差,結構(直接呼叫、fail-open)沒有問題。

引句:「timeout=_inner_budget(default=20))」
file: `scripts/hooks/claude/check-graph-sync.py:317`
引句:「timeout=_inner_budget(default=20))」
file: `scripts/hooks/claude/check-graph-sync.py:343`

blocking: 否

## 問三:第二種做法

### 3a. 版本控制清單的第四種查詢——計劃裡的理由查證

severity: minor
blocking: 否

計劃節點主張「本 repo 既有三處算『哪些檔改了』,分別是提交前那道閘(`git diff --cached --name-only`)、推送前那道閘(`git diff --name-only <範圍>`)、以及**這支 hook 的閘門 3 那條分支**(`git diff --name-only HEAD`)」,並以「第三種看不到未追蹤新檔」為由,論證需要引入第四種查詢(`git status --porcelain -uall`)。

file: `docs/lumos-toolchain-knowledge/Projects/收工點名問版本控制_計劃.md`(〈為什麼非得用 git status --porcelain -uall〉節表格,第三列寫「閘門 3 那條分支 | `git diff --name-only HEAD`(工作樹對上次提交) | 看不到」)——此表非被審 diff 本身,是本案唯一單源計劃節點的一部分,列為查證對象而非引句

**我自己核對了改動前(base `79a7072c`)的原始碼,這個表格對「閘門 3 那條分支」的描述不成立**:改動前的閘門 3 判準函式 `touched_graph_via_cli` 根本沒有呼叫 `git`,它是純字串解析——逐字稿裡的 bash 指令若含 `obsidian <mutate 子命令>` 才算「動過圖譜」,跟 `git diff --name-only HEAD` 無關:

file: `scripts/hooks/claude/check-graph-sync.py:427`(函式 `touched_graph_via_cli` 的文件字串「只有 obsidian CLI 用了 mutate 子命令(create/append/property:set 等)才算」;此函式未被本次 diff 觸碰,改動前後原始碼相同,只是改動後不再被 `main()` 呼叫,見 `scripts/hooks/claude/check-graph-sync.py:425` 起無任何呼叫點)

同樣,改動前的閘門 2(`src_files = [f for f in file_paths if is_code_file(f, project_root)]`)靠的是 `collect_turn_actions()` 解析逐字稿裡的編輯工具呼叫,加上 `extract_bash_file_paths()` 正則比對 `rm/mv/cp/git mv/git rm` 這幾個指令字面——同樣不是呼叫 `git diff`。也就是說,**這支 hook 改動前對「哪些檔改了」從未真正問過版本控制**,repo 裡會呼叫 `git` 問改動範圍的只有 pre-commit 與 pre-push 兩道閘,不是三處。

這不代表最終選擇(改用 `git status --porcelain -uall`)是錯的——**結論本身依然成立且合理**:pre-commit 用的 `--cached` 只看已暫存、pre-push 用的提交範圍比較只看已提交,兩者確實都看不到「從未被加入版本控制的新檔」,所以「需要一種能看到未追蹤檔的查詢」這個需求是真的。但**論證引用的參照點(閘門 3 現行怎麼查)是編造/誤記的**——它把「這支 hook 過去完全不查版本控制」錯寫成「查了,但查的方式看不到新檔」,弱化了這次改動的實際幅度:這不是「既有四種查詢挑第四種」,而是「這支 hook 第一次把資料來源從逐字稿解析換成版本控制查詢」。呼叫方式本身(問二已確認)跟鄰居一致,不算跨層或第二做法,但計劃裡用來自我對齊既有做法的那張表格站不住,請編排者知悉、必要時要求作者更正計劃節點,而不是照單全收「這是既有慣例的自然延伸」這個說法。

### 3b. `_stop_block_dir` 參數化為 `_cache_dir_under_home` 加兩個薄包裝

severity: clean

file: `scripts/hooks/claude/check-graph-sync.py:741-780`(`_cache_dir_under_home(name, label)` 定義)
file: `scripts/hooks/claude/check-graph-sync.py:777-780`(`_stop_block_dir()` 薄包裝)
file: `scripts/hooks/claude/check-graph-sync.py:782-786`(`_printed_dir()` 薄包裝)

引句:「★參數化而不是抄第二份★(2026-09-18 收工點名改問版本控制那一批):收工點名的去重紀錄需要自己的目錄」

這支檔裡確實有反例——**但反例的性質是「跨檔複製」,不是「同檔內共用」**:`_mkdir_under_home` 的文件字串明講它是把主程式(`scripts/lumos`)的 `_mkdir_trusted_under_home` 邏輯**手抄一份**,理由是這支 hook 是獨立部署檔、不能 `import` 主程式:

file: `scripts/hooks/claude/check-graph-sync.py:791-793`(既有文件字串:跟主程式 `_mkdir_trusted_under_home` 同一套判準,因這支 hook 是獨立檔不能 `import` 主程式,所以邏輯抄一份;判準有一邊改了、另一邊要跟著改——此文字非本次 diff 新增,是既有反例的出處)

同一份文件字串也解釋了 `_stop_dir_ok` 裡「路徑比對不寫死名字」的改法,理由同樣是要跟主程式判準對齊、卻仍然保留「抄一份」的事實,而不是改成呼叫主程式。

**這兩個反例(跨檔抄一份)剛好反過來支持本次改動(同檔內參數化共用)是一致的**:`is_code_file`、`is_graph_file`、`EXCLUDE_PATH_CONTAINS`/`EXCLUDE_FILENAMES` 等現有共用邏輯,在同一支檔內本來就是「定義一次、多處呼叫」,不會為每個呼叫點各抄一份。`_stop_block_dir`/`_printed_dir` 兩者都在同一支檔、同一個行程裡,沒有「不能 import」的限制,參數化收斂成同一套判準(symlink/uid/可寫性檢查)反而是延續同檔內既有的共用慣例。**本檔的實際規律是「同檔內共用、跨檔複製」,不是「各寫各的、不共用」**;本次參數化沒有引入新的做法,也沒有違反那條反例揭示的規則。

不對齊共 3 條,其中 major 0 條(材料完整性警訊 1 條 + 命名/錯誤處理 minor 1 條 + 第四種查詢理由查證 minor 1 條;分層與依賴方向、共用函式參數化兩題判 clean)。
