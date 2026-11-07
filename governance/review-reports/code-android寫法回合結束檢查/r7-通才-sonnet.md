severity: minor

我先核對第六輪通才席的兩條,再找新問題。這輪沒找到會做出錯行為的缺陷。

- **r6 F1 已修好。** 子目錄專案裡,同 repo 兄弟目錄被刪的程式碼檔不再被點名。我拿 `_rel_in_project` 實跑:`scriptsX/a`、`scripts/../docs/a`、空字串、絕對路徑都回 False;`scripts`、`scripts/`、`./scripts/a` 回 True。作者新增的 `t_r6del_*` 兩支測試和 `t_r6sh_*` 幾支測試我只讀了,沒跑。
- **r6 F2 是作者選擇不改。** `_repo_top` 的說明講了理由(`_wt_changed_nofilter` 是逐字複本,不動它),我當作已回應。這輪 `main()` 把 `top` 傳進 `_git_status_entries`,沒有再多一次 rev-parse。
- **新增的洗 PATH 段:** `_lumos_r="${PATH:-}:"` 那段,我讀過的邊界(空 PATH、全是相對項、尾端冒號)都能正確退回 `/usr/bin:/bin`,沒有找到錯處。
- **`graph_touched` 不受影響。** 圖譜目錄來自 `find_graph_root(project_root)`,一定在專案底下,所以整批濾掉專案外的條目不會讓它少判。

F1
severity: minor
blocking: 否
標題:找 python 的啟動器取到相對路徑就整個放棄,不會繼續找後面的候選;相對的 PATH 項會把本來找得到的 python 擋掉。
引句:「*) _LUMOS_NO_PY_MSG="找到的 python 是相對路徑 $_LUMOS_ANY_EXE(PATH 有空項或相對項,會解到目前目錄的檔),不用。」
失敗情境:
- `command -v` 只回 PATH 上第一個命中。`_lumos_any_python_find` 在第一個命中就 `return 0`,新增的檢查在它外面,拒掉之後不回頭找下一個候選。
- 輸入:四支安裝腳本不洗 PATH。PATH 含相對項(例如 `.venv/bin`,或結尾有 `:`)且目前目錄有可執行的 `python3.14`;同時 `LUMOS_PYTHON_SEARCH_DIRS` 或 `/opt/homebrew/bin` 有真的 `python3.14`。
- 實際(實跑):`PATH=":/usr/bin:/bin"`、cwd 有 `python3.14`、`LUMOS_PYTHON_SEARCH_DIRS` 指向真的 python 所在目錄,結果印 `NO`,訊息是「找到的 python 是相對路徑 ./python3.14 … 不用」加「找不到任何 python」。
- 預期:跳過相對路徑那個,繼續試固定位置和後面的候選,找到真的 python 後成功。
- 代價:合法的環境(venv 用相對 PATH)裝不起來。訊息有講原因,所以只是被擋、不會誤執行。
- 修法:把「是不是絕對路徑」判斷放進 `_lumos_any_python_find` 每個 `command -v` 之後,不合格就 continue。
- 現有的 `t_r6sh_launcher_relative` 把 `LUMOS_PYTHON_SEARCH_DIRS` 設成空字串,測不到這條。
- 範圍:七份啟動器逐字複本要同步改,三支掛鉤那三份已被 path-clean 先洗掉,實際只影響四支安裝腳本。
佐證 file: `scripts/hooks/pre-push:236`

F2
severity: minor
blocking: 否
標題:`_git_status_entries` 的過濾對每個條目都重算一次兩個 `resolve()`,專案前綴其實只要算一次。
引句:「            if p and (_rel_in_project(p, project_root, top) or (o and _rel_in_project(o, project_root, top)))]」
失敗情境:
- `_rel_in_project` 每次呼叫都 `project_root.resolve()` 和 `top.resolve()`,結果對整批條目都一樣。
- 實測(本機 `scripts/` 當專案根):5 萬個條目約 1.66 秒,每條約 33 微秒。
- 輸入:專案裡有大量沒被 `.gitignore` 擋掉的未追蹤檔,例如沒忽略的建置輸出。
- 影響:這是收工鉤子,有 `--budget` 時間預算,時間會花在可以事先算好的東西上。
- 修法:把前綴算一次(例如拆成 `_project_prefix(project_root, top)` 加一個純字串的比對),迴圈裡只比前綴。
佐證 file: `scripts/hooks/claude/check-graph-sync.py:548`

F3
severity: minor
blocking: 否
標題:新增的測試只有一個空行就接下一個 `def`,還有一處三個空行,排版不一致。
引句:「+def t_r5imp_fifo_guard():」
失敗情境:
- 這個 hunk 新增的 `t_r6sh_launcher_relative` 結尾和 ` def t_r5imp_fifo_guard():` 之間只隔一個空行(PEP 8 E302 要兩個),`t_r6del_status_entries_scope` 和 `_R6SH_HOOKS` 之間則是三個空行(E303)。
- 如果專案的 ruff 規則啟用 E30x,推送前閘會紅。我在 repo 根沒找到 `ruff.toml` 或 `pyproject.toml`,看不出專案有沒有啟用這組規則。全域規則要求推送前跑程式規則檢查,所以列出來讓作者確認一次。

總結:最嚴重是 minor(啟動器遇相對路徑就整個放棄、不再試後面的候選),不會擋任何一條,會擋 0 條。
