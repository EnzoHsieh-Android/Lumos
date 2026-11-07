severity: major

**第三輪邊界席 F1 核對:已修好。** 我拿 `null`、`[1]`、`{"a":`、30 萬個 `[`、6000 位整數,以及非 UTF-8 的 `\xff\xfe{`,餵給 `check-graph-sync.py`、`impact-hook.py`、`stop-lint-hook.py` 三支鉤子。三支全部 rc0,沒有崩潰。

F1 新發現:`_wt_changed_nofilter` 在被檢查目錄是 repo 子目錄時,路徑基準不一致,會對乾淨的工作樹回報大量假改動。
- 輸入:repo 根目錄下有 `sub/`、`other/`、`root.py`,全部已提交、工作樹乾淨。把 `CLAUDE_PROJECT_DIR`(也就是 `project_root`)設成 `repo/sub`,呼叫 `_git_status_entries(Path(".../repo/sub"))`。
- 實際:回 `[('R ', 'a.py'), ('R ', 'c.py'), ('D ', 'other/b.py'), ('D ', 'root.py')]`。
- 預期:空清單。`git status --porcelain` 在 repo 根和在 `sub` 底下都是空的。
- 原因:`ls-tree -r -z --full-tree HEAD` 給的是 repo 根為基準的完整路徑。`ls-files -s`、`ls-files -o`、`rev-parse --git-path` 加上 `lstat` 都是以 `-C project_root` 的 cwd 為基準。HEAD 和索引兩邊的路徑對不上,`sub/` 外的所有檔被當成「HEAD 有、索引沒有」,算成刪除;`sub/` 內的檔被當成「HEAD 沒有、索引有」,配成改名。
- 後果:呼叫端在 `check-graph-sync.py` 的 `code_entries` 過濾後,`other/b.py`、`root.py` 這種被「刪除」的程式碼檔不會被濾掉。每次收工都會誤擋,點名一批根本沒改的檔,而且動了筆記也不會停。
- 與舊版比較:舊版 `git status --porcelain` 在子目錄下是乾淨的,所以這是這輪修補新引入的退步。
- 修法方向:`ls-tree` 去掉 `--full-tree`,讓它跟其他指令同樣以 cwd 為基準。或者所有指令都改以 `rev-parse --show-toplevel` 為基準。
- 這支函式在主程式 `scripts/lumos` 有逐字複本,同樣的路徑基準問題應該一起存在。我沒有在 `scripts/lumos` 裡實跑確認。

引句:「raw = ok("ls-tree", "-r", "-z", "--full-tree", "HEAD", *lit) if h.returncode == 0 else b""」
severity: major
blocking: 是

總結:最嚴重是 major(`_wt_changed_nofilter` 在子目錄專案下對乾淨工作樹回報假的刪除與改名,會誤擋收工),會擋 1 條。

相關檔案:`/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/check-graph-sync.py`(`_wt_changed_nofilter`、`_git_status_entries`)。
