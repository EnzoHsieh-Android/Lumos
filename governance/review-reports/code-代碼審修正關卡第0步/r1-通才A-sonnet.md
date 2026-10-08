severity: minor

## F1 修正紀錄的 base 或 at 含 NUL 字元時,fix-check 直接丟 traceback、回 1(應回 2)
severity: minor
blocking: 否
引句:「r = subprocess.run(["git", "-C", str(repo_root), "rev-parse", "--verify", "--quiet", "--end-of-options", rev.strip() + "^{commit}"],」
佐證行:file: `scripts/lumos:11693`(`_fix_rev`,patch 第 383-391 行);同類呼叫 `_fix_ls_tree`(patch 第 402-413 行,引句:「r = subprocess.run(["git", "-C", str(repo_root), "ls-tree", "-z", "--full-tree", rev, "--", path], capture_output=True)」)

1. 輸入:修正紀錄 JSON 的 `"base"` 填 `"<40碼>\u0000x"`,或某條路徑 `"at"` 填 `"pro\u0000d.py:clamp"`(JSON 合法,`_fix_load_record` 只驗形狀不驗字元)。
2. 路徑:前者在 `cmd_loop_fix_check` 的 `base = _fix_rev(rr, rec.get("base", ""))`、後者在 `_fix_item_record` 的 `kind = _fix_ls_tree(tree, head, fpath)`;subprocess 收到含 NUL 的參數,Python 丟 `ValueError: embedded null byte`,沒有任何 try 接。
3. 重現(在我的 clone,用 `_fc_env/_fc_ledger/_fc_record/_fc_check` 夾具):
   - `_fc_record(r, b+"\u0000x", [_fc_group()])` → `_fc_check` 結果 `rc=1`,stderr 末行 `ValueError: embedded null byte`
   - `_fc_record(r, b, [_fc_group(at="pro\u0000d.py:clamp")])` → 同樣 `rc=1` + traceback
4. 後果:docstring 與計劃寫「rc 1=驗了沒過;2=輸入錯(不寫治理帳事件)」,實際 rc 是 1 且沒記事件、沒有人話訊息(隔離樹與暫存資料夾有確實收掉:跑完 `lumos-fixcheck-*` 為 0、`git worktree list` 只剩主樹)。只有手寫/AI 寫出 `\u0000` 才會觸發,影響小,故 minor。修法一句:`_fix_load_record` 對 base 與所有 at/tests 字串拒絕 `\x00`,或 `_FIX_ID_BAD_RE` 同一條規則套到這些欄位。

## 已核對、未發現問題的部分(附說明)
引句:「class _IsolatedWorktree:」
- `_IsolatedWorktree`:`__enter__` 的 mkdtemp 之後 `subprocess.run` 丟例外會 rmtree 再 raise;`ok=False` 時 `__exit__` 仍刪暫存資料夾、不呼叫 worktree remove/prune;keep=True 兩層都留。我實測 fix-check 在「樹裡設定檔壞」(rc2)與 NUL 例外兩條提早離開路徑後,暫存資料夾與 worktree 登記都無殘留。
- guard kill 改用它:`for plat` 迴圈裡 `with` 區塊內的 `continue`(建樹失敗)會走 `__exit__`,行為同原 `finally`;`--keep-worktree` 在建樹失敗時原本就會印路徑,新版 `on_keep` 也印,一致;原本的 `import shutil/tempfile` 已無其他使用處(`cmd_guard_kill` 內 grep 無殘留引用)。`t_isolated_worktree_shared` 9 項全綠。
- `_isolated_worktree_sweep`:只清同前綴且 mtime 超過 `_LINT_NEW_STALE_SEC`(86400)的資料夾;別的前綴與不到一天的不動(測試 ⑧⑨ 覆蓋)。
引句:「def _spec_gate_judge_items(rr, items, per_prof, loose_for):」
- `_spec_gate_judge_items` 三處呼叫端(`_spec_gate_run_clauses`、`_spec_gate_regress`、`_spec_gate_push_one`)逐行對照:tails 鍵 `(node_id, plat, method)`、`_ran_count`/`_spec_gate_declared`/`_spec_gate_verdict` 參數、跑不起來時的印字與 fails 字面、相依回歸紅字面用的第 6 欄 detail,都與抽出前一致;push_one 傳的 per_prof lambda 與原內聯式相同。
引句:「def _classify_test_refs(text, node, split, default, methods_for, hay_for):」
- `_classify_test_refs` 與 `_bound_tests_for_diff` 原內聯段:ValueError→一筆 bad-name、方法名白名單、Class.Method 與 fake 判斷、例外時 real/fake=False,逐項相同。
引句:「if regression_set is not None:」
- `cmd_canary --regression-set`:區塊在 `if f_set is not None` 內、`F` 已定義;none 大小寫不拘、空字串/只有逗號/不在 findings-set/第一輪非 none/缺 --loop 皆 rc2;存 sorted+去重。`t_canary_regression_set` 10 項全綠。
引句:「else str(d.get("token") or "") if d.get("gate") == "fix-check" else ""),」
- 治理帳讀端:巢狀三元運算式優先序正確;`_GOV_FIELD_TYPES` 新增的 `secs`、`head_sha`、`record_sha256`、`failed_items` 我對 `docs/` 下全部帳檔掃過型別:`head_sha` 1800 筆全 str、`secs` 255 筆全 float,現有行不會被新型別表跳過。`_KNOWN_GATES` 補 fix-check 無漏。
引句:「with _IsolatedWorktree(rr, head, _FIX_CHECK_PREFIX, sweep_repo=rr) as iw:」
- `cmd_loop_fix_check` 其餘分支:`tests`/`findings`/`category` 型別錯(字串、list)、at 以 `/` 結尾的目錄、pathspec 魔法字串(`:(glob)*.py:clamp`)都被擋成 record 項失敗或 rc2,不當掉;`fix_check` 的 status 判法(最後一筆同輪事件、record_sha256、head_sha 40 碼、`_codeloop_record_valid_ex`)與 S8 條款一致;`_disposal_tpl` 與原 `disposal_cmd` 在 plant-canary 的字串一致(`rmode`/`_qid` 等價),gate-pending 只在 code- 第 2 輪起附範本。循序(無 --round)的 code 標準分級迴圈沒有 `--regression-set` 佔位,但那種迴圈本來就沒有 round、fix-check 也跑不了,屬設計範圍不報。
- 我跑過的測試子集:`-k fix_check` 82、`isolated_worktree` 9、`canary_regression` 10、`loop_next_fix` 13、`gov_stats` 59、`guard_kill` 257、`spec_gate` 101、`bound_tests` 95 項全綠。未做逐條「拿掉實作會不會紅」的變異驗證。

固定席筆記:派工詞末端沒有附上 hook 的固定席筆記,故無逐節點判定可寫。

最高等級:minor,blocking 共 0 條
