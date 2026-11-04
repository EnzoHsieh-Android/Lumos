severity: major

資源席第 3 輪結論:有 1 條 major 的資源問題(帳進版控的部分複製沒有防護,是原有漏查),另有 1 條 minor。上輪修補本身(帳被忽略時跳過分岔點、`_git_partial_clone`、10 秒預算、200 個上限)我實測都成立,沒有新增回歸。

1. 帳進版控(或判不了有沒有被忽略)的部分複製,規格閘讀分岔點那一版的帳時仍會觸發自動連遠端,而且不受 10 秒預算管。
引句:「    _d, added, bad = _gov_rows_delta(rr, fork or _EMPTY_TREE_SHA, None, b'"spec-gate-', _redbase_branch_keep)」
severity: major
blocking: 是
歸因:有證據的原有漏查。修前 6e10ae5b 與修後 fe970227 對這個輸入結果相同。修補只在 `ignored == "ignored"` 時跳過分岔點(`if head and ignored != "ignored":`),`"not"` 與 `"unknown"` 兩種狀態沒有套用部分複製判斷。
- 輸入:部分複製(`extensions.partialClone` 與 `remote.origin.promisor` 都有設,promisor pack 裡缺分岔點那版 `docs/.governance-log.jsonl` 的 blob),帳進版控,`ignored="not"`。這個狀態可能出現在別人 push 的分支被拉下來接手時。
- 走到的行:`scripts/lumos:14417` → `_gov_rows_delta` → `_gov_rows_at` → `_residual_blob_at`(`scripts/lumos:61030`)。它跑 `git show <分岔點>:docs/.governance-log.jsonl`,`timeout=60` 且沒有傳 deadline,git 自動去連承諾遠端。
- 量到的數字:我把 `_residual_blob_at` 的逾時改成 3 秒,把遠端 uploadpack 換成留記號並 `sleep 600` 的腳本。
  - 修後:`elapsed 3.2`、`fetched marker True`、回 `rows 0`,並印「讀不出起點那一版的治理帳」,去重與判綠觀測整個失效。
  - 逾時之後 `sh up.sh` 與 `sleep 600` 兩個孤兒子程序還活著(pid 8222、8261,收尾時我手動 kill 掉)。
  - 修前版本:同樣 `elapsed 3.2`、`marker True`、孤兒同在。
  - 對照:同一個 clone 改 `ignored="ignored"` 後 `elapsed 0.1`、`marker False`,修補在被忽略時確實有效。
- 正式碼的逾時是 60 秒,失敗後還有 20 秒的 `ls-tree`,所以規格閘最壞被擋約 80 秒。這是我從原始碼推的,沒有實跑 60 秒。
- 殺不到抓取的子程序,正是計劃天花板三自己承認的機制(「逾時殺不到抓取的子程序」)。
- 重現指令(兩版查證):
  1. 在 `/tmp` 下建一個來源 repo:`main` 兩個提交各有不同帳 blob,另開 `mate` 分支。
  2. `git clone --no-local -b mate` 後用 `git pack-objects` 重打包成排除分岔點帳 blob 的 promisor pack。
  3. 設 `extensions.partialClone` 與 `remote.origin.promisor`,把 `remote.origin.uploadpack` 指向 `touch 記號; sleep 600` 的腳本。
  4. 用 `python3.14 -I` 載入 `scripts/lumos` 與 `git show 6e10ae5b:scripts/lumos` 各一次,呼叫 `_redbase_branch_rows`。
  - 蘋果 git 2.39 的 `clone --filter` 在本機傳輸下被伺服端忽略(印 `filtering not recognized by server`),所以我用重打包代替。

2. 預算與上限幾乎重疊,在慢機器上過濾會被預算截斷。
引句:「_REDBASE_ANC_BUDGET_SEC = 10   # 判綠紀錄是不是這條分支的:整批 git 詢問共用的截止時間」
severity: minor
blocking: 否
歸因:有證據的修復新增(新程式碼);只在超過 200 個不同 head_sha 的規模才會碰到。
- 輸入:`ignored="ignored"`、同分支名同計劃有 20000 筆各自不同的 head_sha(對本機不存在的提交),其中 200 個進入詢問。
- 量到的數字:`_redbase_branch_rows` 整體 `elapsed 8.14s`,輸出「19800 筆判不了」。每個不存在的 sha 要 2 次 git(`merge-base` 加 `cat-file -e`),本機 git 約 20ms 一次,200 個約 8 秒,已吃掉 10 秒預算的八成。更慢的機器上 200 個上限不會先到,預算先把後面的紀錄放行。
- 這是計劃天花板三已記的取捨,而且 200 個以上的紀錄在真實使用下不常見,所以只列 minor。每次規格閘都會重問全部 stale sha,沒有快取。

三問回答:

1. 子程序在逾時、Ctrl-C、例外時有沒有被收掉。
   - 修補範圍內(`_redbase_on_branch`、`_git_partial_clone`、`_drift_born_env_err`):都經 `_lens_git` 或 `subprocess.run`,逾時與例外時直接子程序會被殺。
   - 殺不到的只有 git 自己叫起的抓取孫程序。帳被忽略或有 `_git_partial_clone` 把關的路徑我實測沒有抓取(`marker False`)。沒有把關的路徑就是 finding 1。
2. 時間預算在大輸入或慢機器上有沒有擋下正常操作,或讓過濾被跳過。
   - 讀帳與算分岔點不吃那 10 秒。
   - 過了截止時間或超過 200 個的紀錄照留並印一句,方向是安全的(finding 2)。
   - 讀帳那一段(`_residual_blob_at` 60 秒)沒有預算,見 finding 1。
3. 有沒有把大帳整本讀進記憶體或做二次方工作。
   - 本 repo 真實帳 21MB、124201 列(其中含 `spec-gate-` 的 233 列)。我造的帳 13MB(2 萬列)最大常駐約 129MB;133MB(20 萬列)約 877MB、耗時 12 秒。
   - `_redbase_on_branch` 的過濾與去重都是線性。
   - 帳被忽略時只讀工作目錄一份(原本兩版),修補讓記憶體減半,不是回歸。

已驗過的主張:
- `t_name_collision_scales` 0.4 秒。
- `t_spec_gate_redbase_green_other_branch` 15.4 秒(11 項全綠)。
- `t_spec_gate_redbase_green_tracked_unfiltered` 3.3 秒。
- `t_redbase_branch_rows_fallback_keeps` 4.6 秒(19 項全綠)。
- `t_drift_born_unknown` 16.3 秒(9 項全綠)。
- 新測試的子程序腳本都立刻 `exit 1`,不留孤兒;我用的 `TMPDIR` 跑完是空的。
- `_TG_CONST_PAT` 新加的三引號分支用 `fullmatch` 加佔有式量詞,2MB 的未收尾輸入約 0.01 秒,沒有二次方問題。

配對案例(repair 與 preserve 分開報):
- G1 repair:只寫 promisor 的部分複製照認,我的重打包 clone 上 `_git_partial_clone` 回 True,`marker False`。
- G1 preserve:舊式 `extensions.partialClone` 照認,同一個 clone 兩個設定都開時成立。
- G2 repair:帳被忽略不算分岔點,`ignored="ignored"` 的對照量到 `elapsed 0.1`、不連遠端。
- G2 preserve:判不了或帳進版控時仍算分岔點,這正是 finding 1 的走法,行為與修前一致,所以洞也一樣。

未驗範圍:
- 真實網路上的 blobless/treeless 遠端複製與 60 秒的實際阻擋時間。
- Windows。
- 沒有 commit-graph 的大 repo 單次判祖先耗時。
- 兩個程序同時寫(題目已排除)。

圖譜鏡頭:固定席節點(`lumos-cli-read`、`測試假綠形態`、`pitfalls-code-loop`、`design-loop`、`guard-kill`、`lifecycle` 等)的 INVARIANT 都沒有被這份 diff 碰到。唯一相關的是「測試假綠形態」要求還原翻紅釘配前置斷言,新測試的 ★前置★ 已齊。計劃文件的天花板三對部分複製的描述與 finding 1 一致,但它只講被忽略的路徑,版控路徑沒有被寫進天花板。

最嚴重等級是 major,blocking 共 1 條。
