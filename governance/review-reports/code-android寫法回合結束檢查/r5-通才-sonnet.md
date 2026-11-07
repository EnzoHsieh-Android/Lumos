severity: major

第四輪通才席 F1、F2、F3 的核對結果:
- F2(difflib 平方時間)已修好。`_impact_line_delta` 改用 Counter 相減,是線性時間,讀取總量另有 8MB 上限。
- F3(刪除檔模式)已修好。已刪除的檔改取 HEAD 的模式,需要看首行的改讀 HEAD 那一版。
- F1(子目錄點名靜默失效)只修了一半。`_wt_changed_nofilter` 在子目錄不再回 None,但沒有端到端修好。下面兩條是我實測出來的。

F1
severity: major
blocking: 是
標題:專案根是 repo 子目錄時,`_wt_changed_nofilter` 現在回的是 repo 根相對路徑,但收工鉤子下游都拿 `project_root / 路徑` 去接,多接了一層子目錄,走錯路徑。
引句:「    paths 是相對 repo_root 的,前面補 --show-prefix。回傳的路徑從 repo 根算起(同 git status --porcelain)。」
失敗情境:
- 輸入:repo 裡有 `sub/tool`(無副檔名、首行 `#!/bin/sh`)和 `sub/docs/x-knowledge/Systems/n.md`,兩支都改過,`CLAUDE_PROJECT_DIR=<repo>/sub`。
- 實際(實跑 `_git_status_entries`、`_entry_is_code`、`is_graph_file`):
  - 回 `[(' M','sub/docs/x-knowledge/Systems/n.md'), (' M','sub/tool')]`。
  - `_entry_is_code` 對 `sub/tool` 回 False,因為它去查 `<repo>/sub/sub/tool`。
  - `graph_touched` 回 False,因為它查 `<repo>/sub/sub/docs/...`。
- 預期:`sub/tool` 判成程式碼,筆記有動時 `graph_touched` 為 True。
- 後果:
  - 無副檔名的腳本改了不會被點名,這跟第四輪要修的靜默失效是同一類,只是換了位置。
  - 筆記明明動過,卻被當成沒動,還可能出誤報。
- 呼叫端:`check-graph-sync.py` 的 `_entry_is_code`、`src_files = [str(project_root / r) ...]`、`is_graph_file(str(project_root / r), ...)`。
- 修法:`_git_status_entries` 回傳前把路徑換成相對 `project_root` 的(去掉 `--show-prefix`),或呼叫端改用 repo 根當基準。
- 補一個「子目錄專案根 + 無副檔名腳本 + 筆記在子目錄」的端到端測試。
佐證 file: `scripts/hooks/claude/check-graph-sync.py:1001`

F2
severity: major
blocking: 是
標題:`lumos impact --worktree-nofilter --repo <子目錄>` 在 `cmd_impact_diff` 開頭就被拒絕,`_impact_wt_nofilter` 裡新加的子目錄處理永遠走不到,收工點名在子目錄專案仍然靜默失效。
引句:「    候選走 _wt_changed_nofilter(同 git diff --name-only --no-renames HEAD:不含未追蹤、改名兩端都列;路徑從 repo 根算起,--repo 可以是子目錄)。」
失敗情境:
- 輸入:`python3.14 scripts/lumos impact --diff HEAD --sync-check --worktree-nofilter --json --repo <repo>/sub`。
- 實際:印「擋下:找不到 git 專案,用 --repo 指定」,rc=2。
- 原因:`cmd_impact_diff` 先檢查 `(repo_root / ".git").exists()`,子目錄沒有 `.git`。
- 預期:照 patch 的說法,`--repo` 可以是子目錄,應該算出波及。
- 後果:`_impact_missing` 收到 rc≠0 就 fail-open 回 `[]`,第四輪 F1 提到的「主程式 `--repo` 傳子目錄」沒有真的修好。
- 修法:`cmd_impact_diff` 在 `wt_nofilter` 時像 `_lint_wt_toplevel` 一樣先用 `rev-parse --show-toplevel` 取根,或把「找 `.git`」換成 git 問出來的根。
佐證 file: `scripts/lumos:67470`

F3
severity: minor
blocking: 否
標題:`_impact_line_delta` 先列所有 `-` 行、再列所有 `+` 行,`_impact_hunk_query` 又只留前 4000 字,刪除量大的檔會把新增的內容全部擠掉。
引句:「    return ["-" + ln for ln in (a - b).elements()] + ["+" + ln for ln in (b - a).elements()]」
失敗情境:
- 一支檔刪掉 5000 字以上、同時加進事故正規式要比對的新寫法。
- 查詢文字只剩被刪的舊行,新增行被截掉,影響排名的準度。
- 舊的 difflib 和 `git diff` 那條路是交錯排列,不會有這個問題。
- 修法:`+` 行排在前面,或兩邊各配一半字數。
- 順帶:`_impact_hunk_query` 是先 join 全部再切 4000 字,可以用 `itertools.islice` 或邊累積邊停。
佐證 file: `scripts/lumos:67328`

總結:最嚴重是子目錄專案根在鉤子下游走錯路徑、以及 impact 對子目錄 `--repo` 直接拒絕,第四輪 F1 沒有端到端修好,會擋 2 條。

我建的實驗目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/通才-sonnet/` 已用字面絕對路徑刪除。
