severity: major

1. code/standard 帶 `--round` 的迴圈,「席數不足」關卡被悄悄放寬(⚠ 我只讀程式碼推得,沒真跑這條路)
severity: major
blocking: 是
引句:「width = sum(1 for _s in _roster0["seats"] if _s.get("occupies_w") and _s.get("requirement") != "conditional") or width」
file: `scripts/lumos:15691`
- 這個 `width` 不只是印出來的數字,後面原封不動傳進 `cmd_loop_status(..., min_seats=width)` 當收斂閘的每輪最少人數,見 15691 行附近。`min_seats` 又被 `_panel_extra_checks` 和 legacy 的 min-seats 檢查拿去擋人數不足。
- 改前:code/standard、`panel_fmt`(帳帶 `--round`)時,`seq` 為 False,`width` 取 `_TIER_PARAMS` 的 3,閘要求每輪至少 3 個不同審查員。
- 改後:`_TIER_ROSTER[("code","standard")]` 只有「單reviewer」一席佔人數,`width` 變 1,閘只要求 1 人。同一個迴圈本來要 3 席才收斂,現在 1 席就過。
- 輸入例子:code-xxx 迴圈,第一筆記帳帶 `--tier standard --round r1`,三席各一筆,或只有一席。
- 作者想修的是「印出來的數字」,修法卻動到閘的判定,commit 與筆記沒有一處提到收斂閘被放寬。要嘛只改顯示用的變數,不動傳給閘的 `min_seats`;要嘛明講放寬並補測試。
- `cap` 仍用 3 輪,上限沒跟著動,兩個數字也不一致。
- 還有一個連帶影響:`plant-canary` 的 `canary_type` 在這條路從 3 個 slot 變成 1 個。

2. 新測試沒測到呼叫點,也沒測多候選與過濾條件,做錯時不會翻紅
severity: minor
blocking: 否
引句:「mb = m._codeloop_default_base(root)」
file: `scripts/test_lumos.py`(patch 內 `t_codeloop_default_base_prefers_newest_mainline`)
- 測試只直接呼叫新函式。真正的行為改動在 `_codeloop_guard_verdict`:`mb == head_sha` 早退的語意,以及找不到起點時走 fail-open。
- 把呼叫點改回舊的「本機 main 優先」迴圈,這條測試照綠。早退(HEAD 本身就是主線祖先)和「無 merge-base 則 fail-open」都沒有案例。
- 函式內的邏輯也沒被鎖住,下面這些做錯測試都不會紅:
  - `ref.count("/") == 3` 過濾:remote 名稱含斜線的 ref 被排除,`origin/HEAD` 與 `origin/feat/main` 的排除。
  - main 與 master 並存。
  - `merge-base --all` 回多個分岔點時取歷史最長。
  - 沒有共同祖先時回 None。
  - git 逾時時回 None。
- 測試的 `mb == new` 只在「遠端領先、本機落後」這一個形狀成立。
- 另一條 `t_loop_next_width_matches_roster`:`want` 就是從同一份名冊算出來的,和被測程式碼同一個算式,屬於重寫實作式的斷言,只有人讀輸出那條 `"這輪要 1 人審"` 是獨立的。它也沒有斷言閘的 `min_seats` 行為,所以抓不到第 1 條。

3. 候選納入所有 `refs/remotes/*/main|master`,早退範圍變廣(⚠ 語意改變,不確定是否算 bug)
severity: minor
blocking: 否
引句:「cands += [ref for ref in (rr.stdout.split() if rr is not None and rr.returncode == 0 else [])」
file: `scripts/lumos:50950`
- 改前:HEAD 只有是「本機 main(或沒有 main 時的 master)」的祖先,才會走 `merge-base == HEAD` 早退而放行。
- 改後:HEAD 只要是任何一個遠端追蹤的 main/master 的祖先就會放行。例如某個 fork remote 的過期 `fork/main` 剛好包含 HEAD,就整個 branch diff 被視為空,tier 回 `standard`,不擋。
- 反過來,候選全是 merge-base 輸入,不會比舊行為算出更舊的起點,所以不會多算。風險只在「少擋」。
- 另外有一處小差異:舊碼用 `subprocess.run` 沒設逾時,新碼經 `_lens_git` 預設 20 秒逾時。逾時時兩邊都落到 fail-open,行為一致。

沒找到問題的形狀:
- 沒有遠端:只剩本機 main/master,等同舊行為。
- 無任何候選:回 None,走 fail-open。
- 沒有 `main@{upstream}`:`rev-parse -q` 失敗被跳過,不會丟例外。
- 淺複製或沒有共同祖先:`merge-base --all` 回非 0,得到 None,與舊行為一致。
- detached HEAD:`HEAD` 照常解析。
- 候選共用同一個 sha:有去重。

我沒有在 repo 裡建任何暫存或做 git 寫入,沒有東西需要清理。

總結:最高等級 major,blocking 共 1 條
