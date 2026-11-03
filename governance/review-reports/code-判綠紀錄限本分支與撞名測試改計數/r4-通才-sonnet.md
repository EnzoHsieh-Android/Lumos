severity: major

我沒有改動 `/Users/enzo/harness/lumos-green-scope` 底下任何檔案。實驗都在我自己的 detached worktree `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/通才-sonnet/wt`(停在 ae9c4d82)與同目錄的 probe 腳本、小 repo 上做;改壞實驗做完已還原。

1. 撞名效能測試的檢查②抓不到「串接不快取」,而它的 docstring 說抓得到。
severity: major
blocking: 是
引句:「joined.setdefault((kind, fold), set()).add(id(got))   # 同一種串接每次拿回同一份;重算一次就多一個物件」
- 位置:`scripts/test_lumos.py` 的 `t_name_collision_scales`。計劃 `[S3]` 要求「每種串接只算一次」,綁的就是這支測試。
- 根因:不快取時,每次回傳的 3 元組用完即釋放,下一個同大小元組會佔用同一位址,`id()` 於是相同,集合大小永遠是 1。
- 最小重現:在 wt 的 `scripts/lumos` 把 `_TitleIndex._join` 開頭加一行 `self._joined.pop(key, None)`(等於完全不快取),再跑 `python3.14 scripts/test_lumos.py -k name_collision_scales`。四條檢查全綠,共 4 passed、耗時 9.2s。
- 結果:`_join` 若被改成每次重算,這支測試照綠。
- 歸因:有證據的原有漏查。這支測試與 `_join` 在 fe97 和 ae9c 的文字相同,`Counting` 不在 r4 修補差異裡。
- 兩版命令:`git -C /Users/enzo/harness/lumos-green-scope show <提交>:scripts/test_lumos.py | grep -n 'id(got)'`,fe97 與 ae9c 各印出一行。
- 同族案例:`測試假綠形態` ★INVARIANT★ 要求還原翻紅釘配證明現場成立的前置斷言。本案前置只證明路徑被走到,沒證明檢查②能翻紅。

2. 部分複製「判不了」這個方向沒有真實路徑的測試。
severity: major
blocking: 是
引句:「elif _git_partial_clone(rr) is not False:」
- 位置:`_redbase_branch_rows` 的這一行,以及 `_git_partial_clone` 的 `if r is None or r.returncode not in (0, 1): return None`。
- 受影響條款:計劃 `[S10]`「部分複製(或判不了是不是)」綁的是 `t_redbase_branch_rows_fallback_keeps`。
- 重現一:把 `_git_partial_clone` 該處的 `return None` 改成 `return False`。`-k git_partial_clone` 21 passed、`-k drift_born_unknown` 10 passed、`-k redbase_branch` 22 passed、`-k partial` 47 passed、`-k born` 43 passed。
- 重現二:把 `is not False` 改成 `is True`。`-k redbase_branch` 22 passed。
- 為何抓不到:`t_git_partial_clone_keys` 只用 monkeypatch 把整支函式換成回 None,檢查回頭條件那支的 None 處理。真的 git 失敗時函式是否回 None、規格閘那側是否把 None 當部分複製,都沒有測試。
- 實際代價:git 叫不起來時,規格閘會被當成完整 repo 去讀分岔點那一版,在部分複製裡會連遠端。而這正是 r3 要修的情境。
- 歸因:未判定。None 方向是修補 c8ce2022 新增的。修前 `_drift_born_env_err` 直接 `if _git_partial_clone(root):`,把 None 當「不是」,沒有對應守衛可退化,所以不是行為回歸。

3. 修補沒掃完同族路徑:SHA-256 的 repo、帳進版控、找不到分岔點時,仍走只對 SHA-1 有效的空樹常數。
severity: minor
blocking: 否
引句:「_d, added, bad = _gov_rows_delta(rr, fork or _EMPTY_TREE_SHA, None」
- r3 只在「帳被忽略」那條路改成直接讀工作目錄,非忽略路徑沒動。
- 實測:SHA-256 repo、帳已提交、在 main 上,`_redbase_branch_rows(root, "甲", "not")` 印出「讀不出起點那一版的治理帳:這次的判綠觀測與去重沒有作用」,回 0 筆。同一個 repo 用 `"ignored"` 則回 1 筆。
- 兩版對照:fe97 的 `not` 與 `ignored` 都是 0;7d02 呼叫 `_redbase_branch_rows(root)` 也是 0 並印同一句。
- 歸因:有證據的原有漏查。
- 全域 CLAUDE.md「修審查發現」要求每組替所有相似路徑各寫測試;這條只有「帳被忽略」那條路有測。

4. 「帳被忽略時分岔點那一版根本沒有帳」這個前提不成立。
severity: minor
blocking: 否
引句:「"ignored" 時分岔點那一版根本沒有帳、相減等於整本帳」
- 重現:main 的歷史已提交過帳,內含一筆 loop 甲的 spec-gate-green(無 ref)。在分支上 `git rm --cached` 帳並加進 `.gitignore`,此時 `check-ignore` 回 ignored,origin/main 仍是舊版。
- 結果:`_redbase_branch_rows(root, "甲", "ignored")`,ae9c 與 fe97 都回 1 筆,7d02 呼叫 `_redbase_branch_rows(root)` 回 0 筆。
- 後果:主線歷史上的判綠(head_sha 是祖先、沒記 ref)被當成本分支的。該測試之後判紅會被標「曾判綠」而不存紅燈版,與 `t_spec_gate_redbase_skips_after_green` S6「主線上早就有的判綠不算」矛盾。
- 範圍:只發生在帳「提交過→改成忽略」的過渡期,窄。
- 歸因:有證據的原有漏查。fe97 就已如此,是行為相對 7d02 的改變,不是 r4 修補造成。

5. `_git_bool` 重做 git 的布林解析,且文件宣稱「照 git 自己的規則」與實際有出入。
severity: minor
blocking: 否
引句:「return int(v, 0) != 0」
- 重用:專案內沒有既有 git 布林解析可借,但 `t_git_partial_clone_keys` 自己用 `git config --type=bool --get-regexp` 當對照組。正式碼可以直接問 git 取得 true/false,少掉這個函式。
- 實測分歧:`promisor = 0k`,git 判 false、`_git_partial_clone` 回 True。`0_0` 在 git 是 fatal,這裡回 False(Python 數字允許底線)。
- 現況:前者偏保守,後者 git 本身就會死,都構不成實害,只是維護與文件準確度。
- 歸因:修補自己引入(r3 的 `_git_bool`)。

圖譜鏡頭(固定席節點):
- `測試假綠形態` ★INVARIANT★ 與本案相關,對應第 1 條:前置斷言有,但沒證明檢查能翻紅。
- `pitfalls-code-loop` ★RISK★ 是審查鏡頭範圍,與本案無衝突。
- `lumos-cli-read`、`design-loop`、`guard-kill`、`lifecycle` 的合約行與本案無關。
- 計劃、`Systems/規格閘`、`存量漂移守衛`、`回頭條件寫下時就成立` 的新增敘述,與程式行為相符,例如 `_drift_born_env_err` 判不了回「git 跑不起來」。唯一不符是第 4 條的「那一版根本沒有帳」前提。

三問:
1. 原問題的修復效果:
   - 三個設定的判定:`_git_partial_clone` 在 fe97 與 ae9c 的實測是裸鍵 promisor False→True、promisor=2 False→True、遠端名含空白且 promisor=false True→False,其餘兩案不變。
   - SHA-256 且帳被忽略:`_redbase_branch_rows(..., "ignored")` 從 0 筆變 1 筆。
   - 真實 `clone --filter=blob:none`:`_git_partial_clone` 回 True,`_drift_born_env_err` 回「partial clone…」。
   - 測試:`-k redbase_branch` 22 passed、`git_partial_clone` 21 passed、`drift_born` 27 passed。
2. 修補處的正常、錯誤與相鄰呼叫路徑:
   - 正常路徑成立。
   - 錯誤路徑中,「判不了」方向沒有真實測試(第 2 條)。
   - 相鄰路徑中,SHA-256 且帳進版控沒修(第 3 條),帳曾提交過再忽略的情境會漏(第 4 條)。
   - 呼叫端 `_drift_born_annotate` 只把 err 當 `unknown` 標註,沒被弄壞。
   - 兩個寫入端的 `ref` 沒有其他讀者誤用。
3. 新發現的同一案例修前與修後:
   - 第 1 條:fe97 與 ae9c 的測試與 `_join` 相同,結果都是改壞仍綠。
   - 第 3 條:fe97 與 ae9c 的 `not` 都是 0 筆。
   - 第 4 條:fe97 與 ae9c 都是 1 筆,7d02 是 0 筆。

未驗範圍:真實 git 逾時或 128 的故障注入、Windows、git 2.39 以外的版本、大 repo 的效能與記憶體、doctor 與推送閘對新增 `ref` 欄位的全部讀者(只 grep 到無衝突)。

最嚴重等級是 major,blocking 共 2 條。
