severity: blocker

Finding 1 — 副本保留 `.git/worktrees` 的外指路徑，可改壞真實 linked worktree

severity: blocker
blocking: 是
引句:「副本不接受另一套Git資料或指到副本外的工作樹連結。」
file: `scripts/scenario_probe.py:525`
file: `scripts/scenario_probe.py:553`
最小重現：建立一般 repo `src`，再用 `git worktree add ../linked` 建外部 linked worktree；`make_sandbox(src)` 會接受。副本的 `git worktree list` 仍列出真實 `linked` 路徑；執行 `git -C <副本> worktree repair <真實linked>` 回傳 0，並把真實 `linked/.git` 從指向 `src/.git/worktrees/linked` 改成指向臨時副本。副本清除後，真實 linked worktree 即指向不存在路徑。
證據：`make_sandbox=accepted`、`copy_lists_real_worktree=True`、`repair_rc=0`、`outside_gitfile_changed=True`。根因是 `_check_git_metadata_links` 只拒絕符號連結，而 `_check_worktree_entries` 又把主 `.git` 整棵排除，不檢查 `.git/worktrees/*/gitdir` 這種文字外指路徑。

Finding 2 — 新增的假身分設定仍會被父環境覆蓋，測試只驗設定值而假綠

severity: major
blocking: 是
引句:「"[user]\n\tname = probe\n\temail = probe@local\n")」
file: `scripts/scenario_probe.py:577`
file: `scripts/scenario_probe.py:394`
最小重現：父程序設定 `GIT_AUTHOR_NAME/EMAIL` 與 `GIT_COMMITTER_NAME/EMAIL` 為真實身分，再執行 `make_sandbox`；`_git_env()` 只移除 `GIT_CONFIG*`、`GIT_TRACE*` 與定位變數，因此上述環境值仍傳給儀器及模型的 Git。即使 `git config user.name/email` 顯示 `probe/probe@local`，實際快照提交及後續模型提交作者仍是真實身分。
證據：`config_identity=('probe','probe@local')`，但 `snapshot_effective_identity='REAL PERSON <real@example.test>'`，後續模型提交亦相同。新增測試只執行 `git config --get`，沒有真正提交並核對作者，故 37 項邊界測試全綠仍漏掉此缺陷。

清理 fail-closed：已讀，無 finding。
`--keep` 普通題／讀碼題混合順序：已讀，無 finding。
限額重試逐場時間與有效分母：已讀，無 finding。
表態記錄 `py-eventloop na`：已讀，無 finding。同步命令列批次仍無事件迴圈。
`Systems/codex-harness`：上述兩條 finding。
`Systems/測試假綠形態`：Finding 2 的測試只驗設定、未驗有效提交身分。
其餘固定席節點：已讀，無 finding。

驗證：凍結 patch SHA256 與派工值一致；`probe_boundary_` 37 passed、`probe_source_probe_main` 9 passed、清理失敗子集 3 passed。所有重現只使用臨時 repo；未修改 workspace 或 Git 狀態。

總結：最嚴重 severity: blocker；blocking: 2 條。
