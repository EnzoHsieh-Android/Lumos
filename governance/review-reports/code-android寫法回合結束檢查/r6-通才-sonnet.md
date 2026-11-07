severity: major

第五輪通才席 F1、F2、F3 的核對:三條都修好了,另外找到一條新的 major 和一條 minor。

- F1(子目錄專案路徑接錯)已修好。鉤子新增的 `_repo_top` 讓 `_entry_is_code`、`src_files`、`graph_touched` 都改接在 repo 根上。我用 `sub/` 當專案根實跑 `_git_status_entries` 加 `_entry_is_code`,`sub/a.py` 判成程式碼。
- F2(`impact --worktree-nofilter --repo 子目錄` 被拒)已修好。`cmd_impact_diff` 在 `wt_nofilter` 時改用 `_git_toplevel` 判 git 專案。其他呼叫端仍要求 `.git`,行為沒變。
- F3(新增行被截掉)已修好。`+` 行排在前面,`_impact_hunk_query` 改成邊累積邊停,輸出和先接再切等價。
- 另外查了 skip-worktree(`S`)、assume-unchanged(小寫)和暫存過再標 skip-worktree 三種情況。`_wt_changed_nofilter` 的輸出都跟 `git status --porcelain` 一致。
- `_clean_path_env` 在八支鉤子的 `__main__` 第一句、主程式 `main()` 第一句都有呼叫。`_py_floor_gate` 在 `main()` 之前跑,但它用 `_py_which` 只收絕對路徑,不受相對 PATH 項影響。

F1
severity: major
blocking: 是
標題:專案根是 repo 子目錄時,同 repo 其他子目錄「已刪除」的程式碼檔,會被當成本專案的程式碼檔,而且可能讓收工被擋停。
引句:「    code_entries = [(c, r) for c, r in entries if _entry_is_code(c, r, project_root, top)]」
失敗情境:
- 原因:`_wt_changed_nofilter` 回的是整個 repo 的改動,不限專案子目錄。`_entry_is_code` 對沒刪除的檔,最後由 `is_code_file` 用 `resolve().relative_to(project_root)` 擋掉專案外的檔。但已刪除的檔走的是另一條路,只看副檔名或 HEAD 首行是不是 `#!`,不判位置。
- 輸入:repo 有 `sub/a.py`(專案)和 `other/b.py`、`other/tool`(首行 `#!/bin/sh`),提交後刪掉 `other/` 下兩支,`sub/` 不動或只動 `sub/a.py`,專案根設為 `<repo>/sub`。
- 實際:實跑 `_git_status_entries` 加 `_entry_is_code` 得到 `[(' D','other/b.py',True), (' D','other/tool',True), (' M','sub/a.py',True)]`。`other/` 兩支已刪除的檔都判成程式碼。
- 預期:`other/` 在專案根 `sub/` 之外,應該是 False。
- 後果:只要別的子專案刪了碼檔,本專案的收工就會印「有程式碼檔還沒提交」,第一次 Stop 還會走 `stop_block_decision` 擋停一次,要求補筆記。
- 範圍:刪除檔繞過位置檢查,主線原本就有。r5 之前路徑接錯,這條幾乎不會被觸發,這輪修好接路徑之後才暴露。
- 修法:`_entry_is_code` 的刪除分支補一道位置判斷,例如 `(top / relpath).resolve().relative_to(project_root.resolve())` 失敗就回 False。刪除檔的路徑已經不存在,`resolve()` 不需要檔案存在。
- 補測試:子目錄專案根加同 repo 兄弟目錄刪除碼檔,應該不被點名。
佐證 file: `scripts/hooks/claude/check-graph-sync.py:1021`

F2
severity: minor
blocking: 否
標題:鉤子的 `_repo_top` 另外多跑一次 `git rev-parse --show-toplevel`,但 `_wt_changed_nofilter` 裡已經算過同一個值。
引句:「        r = _git(project_root, "rev-parse", "--show-toplevel")」
失敗情境:
- 每次收工點名,多一個 git 子程序,重複算了 repo 根。
- 因為 `_wt_changed_nofilter` 是不能改回傳形狀的逐字複本,作者選擇多算一次。這個取捨在筆記裡沒有寫進 `_repo_top` 的說明,是已知代價,不阻擋。
- 更簡單的做法:讓 `_git_status_entries` 回 `(entries, top)`,或把 `_repo_top` 的結果跟狀態表放在一起傳,只算一次。
佐證 file: `scripts/hooks/claude/check-graph-sync.py:528`

總結:最嚴重是子目錄專案根下,同 repo 其他子目錄已刪除的碼檔被當成本專案的程式碼檔並可能擋停,會擋 1 條。
