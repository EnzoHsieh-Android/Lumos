severity: major

核對第五輪的兩條:

- **r5 F1(sparse-checkout 與 skip-worktree 誤報)已修好。** 我實跑 `_wt_changed_nofilter`:skip-worktree 的檔被改,回 `[]`,`git status --porcelain` 也是空;assume-unchanged 的檔也一致。`ls-files -s -v -z` 輸出是 `h 100644 oid 0\tpath`,`entries(idx, 4)` 解析無誤。
- **r5 F2(影響分析入口拒收子目錄)已修好。** 在 monorepo 對 `--repo <根>/app` 跑 `impact --diff HEAD --sync-check --worktree-nofilter --json`,不再印「找不到 git 專案」,往下走到找圖譜那步。我的測試 repo 沒有圖譜,所以影響分析的後半段(拿筆記比對)沒驗到。

## F1 專案根是 repo 子目錄時,專案外被刪的程式碼檔仍被當成「該寫筆記的程式碼」,可能擋停收工
- 輸入:monorepo `mono/`,專案根 `mono/app`。刪掉專案外的 `other/B.kt`,同時改 `app/A.kt`。
- 實際:`_git_status_entries` 回 `[(' M','app/A.kt'), (' D','other/B.kt')]`,`_entry_is_code(c, r, project_root, top)` 兩條都回 True。`other/B.kt` 進 `code_entries`,出現在提醒清單和擋停理由的完整清單裡。
- 預期:專案外的檔不算。沒被刪的檔會走 `is_code_file(str((top or project_root) / relpath), project_root)`,它先判「在不在 project_root 之下」,所以專案外的修改檔和新檔都被擋掉。
- 原因:被刪的檔在 `_entry_is_deleted` 那個分支提早 return,只看副檔名或 `_head_shebang`,沒有「在不在專案底下」那道。這輪在 `_repo_top` 的註解寫「圖譜位置與在不在專案底下照舊用 project_root 判」,但被刪檔的路徑沒套這句。
- 影響:子目錄專案的 session 只要改了專案內一支檔,別的子專案或別的會談在 repo 其他位置刪了程式碼,就會被點名,甚至觸發 `stop_block_decision` 的 `decision: block`。這輪修補讓子目錄專案真的能運作,於是這個不一致第一次碰得到。
- 修法:`_entry_is_deleted` 分支先用 `top / relpath` 判是否落在 `project_root` 底下,不在就回 False。
- 引句:「if Path(relpath).suffix.lower() in CODE_EXTS:」
- file: `scripts/hooks/claude/check-graph-sync.py:519`(`_entry_is_deleted` 後面那段刪除檔分支,在 `_entry_is_code` 內)
severity: major
blocking: 是

審的範圍裡沒發現其他問題:

- `_clean_path_env` 九份逐字相同。`scripts/hooks` 底下所有有 `__main__` 的鉤子都已呼叫,沒有漏的。
- `_git_toplevel` 在「已是根」和「問不出來」兩種情況,行為與舊的 `_lint_wt_toplevel` 一致。
- `_impact_hunk_query` 提早停的邏輯,輸出結果與原本先接再切相同。
- 這輪沒動到 `_lens_git`,鏡頭 4 沒有新問題。

總結:最嚴重是 F1(子目錄專案裡專案外被刪的程式碼檔會被點名甚至擋停收工),會擋 1 條。

我沒修改 repo。我的臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/正確性-sonnet/` 已刪;上一層目錄還有別的席位的資料,我沒動。
