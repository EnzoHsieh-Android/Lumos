severity: major

第三輪通才席 F1 到 F3 的核對結果:
- F1 已修好。`_unchecked_kind` 先判 `isinstance(k, str)`,非字串回 `"error"`,不再丟 TypeError。
- F2 已修好。判定層不再補預設,`_lint_new_classify` 的 `report_only` 與 `sep_emptied` 兩處各自明寫 `deliberate`,JSON 層沒寫明的落 `failed`。
- F3 已修好。計劃範圍 2 第 5 條已補上 `unchecked_kind` 的記法。

下面是這輪新找到的問題,共 3 條。

F1
severity: major
blocking: 是
標題:收工點名鉤子在專案根是 repo 子目錄時,`_wt_changed_nofilter` 永遠回 None,整道點名靜默失效。
引句:「    raw = ok("ls-tree", "-r", "-z", "--full-tree", "HEAD", *lit) if h.returncode == 0 else b""」
失敗情境:
- `ls-tree --full-tree` 給的是 repo 根相對路徑,`ls-files -s`、`ls-files -o` 和 `hash-object --stdin-paths` 給的是 cwd 相對路徑或以 repo 根為基準,兩邊的鍵對不上。
- 輸入→實際→預期:我建了 repo,裡面有 `sub/a.py`,把它改掉,`_git_status_entries` 在 `CLAUDE_PROJECT_DIR=<repo>/sub` 時回 None。同一個改動在 repo 根回 `[(' M','sub/a.py')]`。
- 直接原因:`hash-object` 報 `fatal: could not open 'a.py'`(它從 repo 根開檔),函式的 `got is None` 分支回 None。呼叫端 `_git_status_entries` 把 None 當「算不出來」,fail-open 放行,不報錯。
- 就算 `hash-object` 沒失敗,`other/b.py` 這類 HEAD 有、子目錄索引列不到的檔也會被判成刪除。
- 舊的 `git status --porcelain` 在子目錄跑不會整次失敗。
- 修法:各個 git 呼叫統一加 `--full-name` 並用 repo 根當基準。或先用 `rev-parse --show-toplevel` 取根,把 `-C` 和 `repo_root` 都換成根。
- 主程式 `_impact_wt_nofilter` 的 `--repo` 如果傳子目錄,也有同樣問題。
佐證 file: `scripts/hooks/claude/check-graph-sync.py:345`

F2
severity: major
blocking: 是
標題:`_impact_wt_nofilter` 用 `difflib.unified_diff` 算改動行,重複行多的檔是平方時間,會吃光鉤子預算。
引句:「        lines = [ln for ln in difflib.unified_diff(a, b, lineterm="", n=0) if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]」
失敗情境:
- 檔案上限是 `_CODELOOP_BOOKKEEPING_HEAD_CAP` = 1MB,這個上限只管讀檔,管不到 difflib 的成本。
- 實測 `a=["l%d"%(i%150) for i in range(n)]` 對上 `b=["l%d"%((i*7)%150) for i in range(n)]`,耗時如下。這種形狀是重複行很多、不同行很少,例如生成碼或資料表。

| 行數 n | 耗時 |
|---|---|
| 5000 | 1.0 秒 |
| 10000 | 7.4 秒 |
| 20000 | 57 秒 |

- 20000 行遠小於 1MB,卻已經 57 秒。
- 收工鉤子的 impact 子程序只有約 `_inner_budget(default=30)` 的預算,逾時就被殺,`_impact_missing` 回 `[]`,整次點名沒了。
- 舊做法是每檔一支 `git diff`,不會有這種成本。
- 另一個問題:同一函式把所有候選檔的 HEAD 版本一次讀進記憶體。`_nodehome_cat_blobs_capped` 沒給 `max_total_bytes`,每支至多 1MB,合計沒有上限。
- 修法:
  - 行數或位元組超過一個小上限(例如 2000 行)就退回只用路徑(列進 `fallback`),不跑 difflib。
  - 或改用有線性上限的比對。
  - 逐檔讀取、逐檔釋放,或傳入 `max_total_bytes`。
佐證 file: `scripts/lumos:67321`

F3
severity: minor
blocking: 否
標題:已刪除檔在 `_impact_wt_nofilter` 裡拿不到模式,沒副檔名的刪除檔分類失準。
引句:「            modes[p] = ("100755" if st.st_mode & 0o111 else "100644", _head_is_shebang(new, lenient=True) if ok else None)」
失敗情境:
- 這行只在 `st is not None` 時執行,工作樹上已刪的候選沒有 `modes[p]`。
- 呼叫端 `modes.get(f, (None, None))` 把 mode 和 shebang 都當未知。
- 舊路徑 `_impact_diff_modes` 對刪檔取舊物件的模式。
- 影響:刪掉主程式這類沒副檔名、靠首行 `#!` 認出的檔,在 `_IMPACT_RECORD_DIRS` 下被 `unknown_is_code` 當成程式收進來,不過這邊是多查不是漏查。
- 修法:`st is None` 時,用上面已經讀到的 HEAD blob(`old`)補 `_head_is_shebang(old, lenient=True)`,模式取自 `ls-tree` 的結果。
佐證 file: `scripts/lumos:67315`

總結:最嚴重是子目錄專案根讓收工點名靜默失效(F1),以及 `difflib` 平方成本會吃光預算(F2),會擋 2 條。

我建的實驗目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/通才-sonnet/` 已刪除。
