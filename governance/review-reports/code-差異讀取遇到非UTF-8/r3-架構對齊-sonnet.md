severity: clean

### 鏡頭二問

**問1(守衛的命令來源判別法,跟既有 ast 守衛/scripts/lumos 自身的解析一不一樣)**
- 專案裡「module-level `_`前綴 helper 供 t_ 測試用、內部跑 `ast.parse` 靜態分析、自帶 bad/good 反面自我驗證」是既有大量慣例(test_lumos.py 有 100+ 個此類 helper),且明文立過「唯一真值來源、不准又一種」的判準。
  佐證:`scripts/test_lumos.py:6171` `_lumos_parser_tree` docstring「★為什麼是「唯一」而不是「又一種」★(2026-09-07 代碼審 r1 架構席判 blocking)」——這是專案對「同一件事出現第二套判別邏輯」的既有裁定先例。
- 新守衛 `_text_git_calls_missing_errors`(`scripts/test_lumos.py:9886`)結構完全對齊此慣例:module-level helper + `ast.parse`(對照 `t_no_zero_assertion_return_paths` `scripts/test_lumos.py:31537` 同樣 `import ast as _ast; ast.parse(src)`)+ 自我驗證 sample_bad/sample_good/反面(對照 `t_no_zero_assertion_return_paths` 尾段「反面:掃描器本身要抓得到」`scripts/test_lumos.py:31576`)。
- 「解析命令從哪來」(沿 `ast.Assign`/`for` 迴圈追變數來源)在 `scripts/lumos` 自己找不到對照:`_lens_py_defs`(`scripts/lumos:20791`)只做 `tree.body` 頂層 def/class 掃描,不追變數賦值。但這不是「同一問題的第二種解法」——工具鏈裡本來就沒有第一種「判斷某個 subprocess 呼叫的命令來源是不是 git」的解法,`grep -n "ast\.Assign" scripts/lumos` 命中 0 筆,所以不構成「又一種做法」,是這題目前唯一的一種。
- 判定:結構對齊既有 ast 守衛家族,不是第二套判別邏輯,不列為不對齊。

**問2(`_sp_run_text` 補 errors= 跟其他 58 處是否一致)**
引句:「return _sp.run(cmd, capture_output=True, text=True, errors="replace").stdout.strip()」(`scripts/lumos:145`)
- 逐行機械核對整份 diff(排除文件行、docstring、`check()`、測試自身的字串 `.replace()`)後,production code 裡新增 `errors="replace"` 的呼叫恰好 **59 處**,寫法一律是緊接在 `text=True`(或 `text=True` 前有 `capture_output=True`)之後插入 `errors="replace"`、其後才接 `cwd=`/`timeout=` 等既有關鍵字——跟 `_sp_run_text` 這行的插入位置完全同款,無例外。
- 引句對照(其一):「capture_output=True, text=True, errors="replace", cwd=str(vault)).stdout.strip()」(`scripts/lumos:159`,`_append_governance_log`)——與 `_sp_run_text` 同一插入慣例。
- 診斷筆記自稱「守衛管到的共 62 處:原本就有 3 處帶著,這次補了 59 處」與機械複核數字相符(引句:「這次補了 59 處」,`docs/lumos-toolchain-knowledge/Issues/風險掃描遇到非UTF-8內容整支中斷.md` diff 第 51 行),內部數字無矛盾。

不對齊共 0 條,其中 major 0 條

F3:修到 — `_sp_run_text` 本體已直接補上 `errors="replace"`(`scripts/lumos:145`),守衛的 `program()` 判別法也把「命令從參數傳進來、看不出跑什麼」一律當可能是 git,雙保險都補到,且在當前 `scripts/lumos` 上實跑守衛邏輯得 `bad == []`(已用 ast 抽取函式體驗證,非臆測)。

總結:最高 severity clean,blocking 共 0 條
