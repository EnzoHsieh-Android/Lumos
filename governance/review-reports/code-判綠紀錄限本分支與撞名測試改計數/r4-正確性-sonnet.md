severity: major

第 4 輪驗收,正確性席(sonnet)。修後版 ae9c4d82 的程式行為我找不到會做錯的輸入,但有一條驗收條款(S10)綁的測試抓不住改壞,依判準算 major;另有兩條 minor。

我在自己的 detached 工作樹(`/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/正確性-sonnet/wt`)和複本上做實驗,沒有動 `/Users/enzo/harness/lumos-green-scope` 的任何檔。實驗完已用 `git worktree remove` 撤掉工作樹。

1. S10 條款括號裡的「判不了是不是部分複製」那一支,綁定測試完全沒走到,改壞測試照綠
引句:「elif _git_partial_clone(rr) is not False:」
severity: major
blocking: 是
歸因:有證據的修復回歸(S10 條款與這個分支都是修補新增的,修前 fe970227 不存在;程式行為修後是對的,缺口在測試)。
- 條款出處:`[S10] 當部分複製(或判不了是不是)而治理帳不是被忽略時,規格閘應不讀分岔點那一版的治理帳…`,綁 `t_redbase_branch_rows_fallback_keeps`。
- 測試只走了「`_git_partial_clone` 回 True」(S10 那條 `m._redbase_branch_rows(pc, "甲", "not")`),沒有任何案例讓它回 None(git config 逾時或回傳碼非 0/1)。
- 最小重現(在我的複本改):把 `is not False` 改成 `is True`,在 `wt` 跑 `python3.14 scripts/test_lumos.py -k redbase`(197 passed, 0 failed)、`-k partial_clone`(21 passed)、`-k born_unknown`(10 passed),全綠。
- 改壞後的實際行為:用 `_git_partial_clone` 回 None 的 stub 呼叫 `_redbase_branch_rows(g2, "L", ignored="not")`,原版回 `[]` 並印說明,改壞版讀了分岔點那一版、回 10 筆。這正是 S10 要擋的「部分複製讀舊版本自動連遠端」。
- 兩版對照(修前 fe970227 在同一個 stub 輸入下):回 10 筆(沒有這道檢查);修後 ae9c4d82:回 `[]` 且印「部分複製(或判不了是不是)不讀分岔點那一版的治理帳」;改壞版:回 10 筆。
- 還原翻紅釘缺「判不了」這一支的前置斷言,也不合測試假綠形態 ★INVARIANT★ 的要求。
- 補法:在 `t_redbase_branch_rows_fallback_keeps` 加一案,把 `m._git_partial_clone` 換成回 None 的函式,斷言 `got == []`、有印說明、`_lens_fork_point` 沒被呼叫。

2. SHA-256 的 repo,治理帳不是被忽略時仍用 SHA-1 空樹,r3 只修了被忽略那條路
引句:「_d, added, bad = _gov_rows_delta(rr, fork or _EMPTY_TREE_SHA, None, b'"spec-gate-', _redbase_branch_keep)」
severity: minor
blocking: 否
歸因:有證據的原有漏查(7d029f46、fe970227、ae9c4d82 三版同結果)。
- 輸入:`git init --object-format=sha256 -b featA`,有一個提交,`docs/.governance-log.jsonl` 沒被忽略,裡面有一筆同 loop 的判綠;沒有 main/master,或直接在 main 上工作(此時 `fork` 為 None)。
- 走到的那行:`fork or _EMPTY_TREE_SHA` 傳進 `_gov_rows_delta`,SHA-256 的 repo 讀不到 SHA-1 的空樹,印「讀不出起點那一版的治理帳」並回 `[]`。
- 三版實測都回 0 筆;同一情境換成 sha1 回 1 筆(提交後回 2 筆),所以原因是物件格式。
- 後果:判綠觀測與去重沒有作用,「判綠過不存紅燈版」的保護失效,但有印訊息,不是靜默。
- 這是 r3 邊界席已指出那一類問題的同族另一處。`_drift_empty_tree(root)` 已提供依 repo 算空樹的辦法。
- 已有 `Issues/SHA-256的repo其他閘仍用SHA-1空樹`(REVISIT 2026-12-29),但它沒列這一處,建議補一行。

3. 計劃的〈回退〉沒涵蓋 r3/r4 新增的行為改動,且與同節「跟現在一樣」自相矛盾
引句:「三項加寫回筆記,各自獨立:第 1 項拿掉 `_redbase_branch_rows` 的過濾與兩處多傳的 ref」
severity: minor
blocking: 否
歸因:有證據的修復回歸(修補新增了 S10 的提前返回、`_drift_born_env_err` 改用共用判斷,回退節沒跟上)。
- 照字面回退只拿掉「過濾」與兩處 ref,會留下:非被忽略路徑遇部分複製(或判不了)就 `return []` 的提前返回;`_drift_born_env_err` 把 None 判成「git 跑不起來」。
- 做法 1 同一條 bullet 又寫「不是『被忽略』(進版控或判不了)就到此為止,跟現在一樣」,但 S10 已讓部分複製在這條路上有不同行為。
- 這只影響回退時的完整性,不影響現行行為。

兩個鏡頭問題與三問

- 回頭條件那支(`_drift_born_env_err`)在 git 偶發失敗時沒有變嚴到誤擋。
  - 我把 `config` 呼叫換成回 None:修前 fe970227 回 None(繼續往下標,有誤標成「寫下時就成立」的風險),修後回「git 跑不起來」,整批標 unknown。
  - `born` 欄位在 `scripts/lumos` 只被 `_drift_born_print`、`_drift_born_summary` 用(印一行彙總),不進退出碼或擋推。所以只是更保守的標籤,不是更容易擋人。
- `_redbase_branch_rows` 三條路(被忽略、部分複製、一般)回傳形狀一致,都是 `list[dict]`。
  - 被忽略路徑我餵了 13 筆敵意列:ref 為數字或 list、head_sha 為 None、整數、大寫、帶換行、loop 為 list、壞 JSON、非物件。不崩,型別不對的 ref 照留,只有 loop 不符與分支名不同的被丟。
  - 帳不可讀時回 `[]` 並印訊息,與另兩條路一致。
- 三問
  - ① 修復效果:實跑 `_git_partial_clone`,fe970227 對「裸鍵 promisor、promisor = 2、遠端名含空白且 false」得 False、False、True(都錯),ae9c4d82 全對。對 `git config --type=bool` 做對照只有 `0k` 不同,`_git_bool` 回 True,屬保守方向。SHA-256 且帳被忽略的路徑也確認直接讀工作目錄。
  - ② 相鄰路徑:新舊 repo 都沒壞,見上面兩個鏡頭。`-k spec_gate` 406 passed、`-k t_tq_guard_string_comma_args` 通過。
  - ③ 新發現的修前修後:發現 1 修前 10 筆、修後 `[]`、改壞版 10 筆且測試照綠;發現 2 三版皆 0 筆;發現 3 為文件。

repair 與 preserve 選例我另外獨立改壞驗證:
- 拿掉三引號那一段後,`t_tq_guard_string_comma_args` 紅,可抓到。
- 把 `_TitleIndex._join` 改成不快取,`t_name_collision_scales` 的②紅(id 集合 513),可抓到。
- 拿掉寫入端兩處 `ref=`,`-k redbase` 分別紅 2 條、3 條,可抓到。
- 唯一倖存的是發現 1 那個改壞。

圖譜固定席節點(lumos-cli-read、pitfalls-code-loop、guard-kill、design-loop、lifecycle、loop-convergence、reversibility 等)都判不影響:diff 只動規格閘紅燈版的讀取過濾、比對工具的常值樣式與部分複製判定,沒碰它們宣稱的搜尋排除、guard kill rc、sentinel、帳本可逆性。唯一牽連是「測試假綠形態」★INVARIANT★(還原翻紅釘要配前置斷言),發現 1 就是這條的缺口。

未驗範圍:
- 真實 blobless 遠端複製(只用設定與留記號的腳本代替);
- Windows、git 2.39 以外的版本;
- 時鐘倒退、無 commit-graph 的大 repo;
- 全套測試(只跑了上述子集)。

我跑測試留下的暫存,已用字面絕對路徑刪了 `gctl-run-0rbed3ib`、`gctl-run-znpp2nts`、`gctl-run-yb380dzf`、`gctl-run-1d5e5y8k`。同目錄另有 `gctl-run-6knnru_d` 可能也是我的 `t_tq_guard` 改壞實驗留下的,無法確認歸屬所以沒刪。我的暫存目錄 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/正確性-sonnet/`(含 `t1`~`t7.py` 與 `old/` 內的舊版複本)留給編排者收貨後刪。

最嚴重等級是 major,blocking 共 1 條。
