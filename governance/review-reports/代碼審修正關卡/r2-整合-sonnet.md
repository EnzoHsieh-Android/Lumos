severity: major

# r2 整合與接手(整合-sonnet)

查證範圍:`cmd_guard_kill`、`_kill_run`、`_kill_cap`、`_bound_tests_check`/`_run_bound_tests`/`_bound_tests_for_diff`/`_bound_tests_filter_probe`、`_lint_link_deps`、`cmd_gov` 與 `_GOV_FIELD_TYPES`、`_gate_event_build`、`_nodehome_is_test`、`cmd_impact_diff`,另掃三本帳的欄位型別、對 SKILL.md 與路線圖的引用。未讀第 1 輪報告。

## F1 先紅那棵樹的演算法會把「不在測試資料夾的輔助檔」換回 base,跟 S4 與計劃自己的說法互相打架
severity: major
blocking: 是
引句:「測試檔、輔助檔、測試資料都留修正後的版本」
file: `scripts/lumos:24776`(`_nodehome_is_test`)
file: `scripts/lumos:24725`(`_nodehome_layout`)
1. 計劃的演算法是:`base..修正後` 改到的檔,用 `_nodehome_is_test` 判,「判不是測試檔的都算非測試檔」,一律換回 `base`(`base` 沒有就刪)。條款 S4 卻要求「紅樹裡非測試的輔助檔(例:不在測試資料夾的共用夾具)應是修正後的版本」。依定義,不在測試資料夾的共用夾具會被 `_nodehome_is_test` 判成非測試檔,所以會被換回 `base`,跟 S4 矛盾。兩者不可能同時成立。
2. 實測(在 `git clone --shared` 的副本上載入 `scripts/lumos`,逐路徑呼叫 `_nodehome_is_test(p, ({}, {}))`):
   - `conftest.py` → False
   - `testutil.py` → False
   - `common/fixtures.py` → False
   - `helpers/shared_fixture.py` → False
   - `scripts/fixtures/sample.json` → False
   - `Sources/Mocks/FakeClock.swift` → False
   - `tests/data/a.json` → True
   - `tests/helpers.py` → True
3. 失敗場景:修補在根目錄 `conftest.py` 新增一個 fixture,新測試用它。紅樹把 `conftest.py` 換回 `base`,測試因為「找不到 fixture」而紅,不是因為修補前的程式有 bug。這一項判「紅,過」,是放水。這正是計劃〈跟提案不同〉自稱已解決的洞(輔助檔漏掉),只是方向從「漏掉」變成「被還原」。
4. 照字面實作,S4 的夾具(共用夾具不在測試資料夾)必然測出紅變綠以外的結果。實作者要不就改演算法,要不就改 S4。演算法需改成「只還原 `base..修正後` 有改、而且被某條 fixed 路徑 `at` 指到的檔」或「還原清單用白名單」。這由編排者裁,這裡只指出矛盾。

## F2 先決條件「已受版控的改動」在共用工作目錄的日常狀態下會卡死,而且驗證本身並不需要它
severity: major
blocking: 是
引句:「未追蹤的檔不看(同一個 repo 常有別的會談留下的未追蹤檔;所有測試都在隔離工作樹跑」
file: `scripts/lumos:11898`(`_repo_root_from_env`)
file: `scripts/lumos:38385`(`_bound_tests_for_diff` 內呼叫 `_platform_test_index(repo_root)`,吃的是傳進去那個路徑)
1. 計劃只豁免「未追蹤檔」,但別的並行會談留下的是「已受版控的改動」。本次對話開頭的 git status 就有 ` M .claude/output-styles/colleague-plain.md`(`.claude/` 不在 `docs/`、`governance/` 底下)。照字面實作,這種狀態下 `fix-check` 回 2 並印「先提交修正」。使用者全域規則要求不碰別人的未提交改動,編排者無法「先提交」,等於逼到 `LUMOS_SKIP_FIX_CHECK=1`。
2. 該跳過會記 `skipped-env`,直接灌高 RETIRE-IF 的「跳過比例超過三成」,而那是機制本身造成的,不是人偷懶。
3. 這個前提其實不是驗證所需:先紅後綠、合約測試都在固定 40 碼的隔離樹跑。計劃唯一還讀工作目錄的是第 3 項「測試存在」的 `_platform_test_index`(讀工作目錄)。把第 3 項的索引改成對綠樹建,這個前提就可以拿掉或縮成只看 `base..修正後` 動到的檔。
4. 訊息「先提交修正」對「不是你造成的改動」是誤導。至少要區分「你的改動」和「不相干的改動」。
5. 副問題:`git status --porcelain -z` 的改名項有兩個路徑欄位(新、舊),計劃沒講怎麼切,只比對第一欄會漏判。

## F3 共用工作樹函式的參數表不夠,「行為不變」缺實際守衛
severity: minor
blocking: 否
引句:「參數是在哪個 repo 建、檢出哪個提交、資料夾前綴、要不要保留」
file: `scripts/lumos:14193`(`cmd_guard_kill` 內建工作樹與 finally 段)
1. `cmd_guard_kill` 實際有這些計劃沒提的細節:
   - `worktree add` 失敗時不是丟例外,而是對該平台每條配方記 `verdict: error`、`detail: worktree add 失敗: <stderr 前 120 字>`,再 `continue` 下一個平台(`tmp_parent` 照樣收)。以 `with` 實作的函式若丟例外,這段要重寫。
   - finally 的 `wt_ok` 分流:add 失敗只刪資料夾、不跑 `worktree remove`。
   - `--keep-worktree` 的訊息輸出口隨 `as_json` 在 stdout/stderr 之間切換。
   - `ghead` 可能是空字串(`rev-parse` 失敗),這時 `worktree add --detach wt` 不帶提交(落在 proot 的 HEAD)。
   - 多平台時 `git -C proot worktree add` 建的是整個 repo 的樹,而 `_kill_run(cmd, wt, …)` 的工作目錄是樹頂,不是平台根。這與計劃要求的「工作樹 + 平台根相對 repo 頂的路徑」不同,所以共用函式必須只回樹頂,平台子路徑由呼叫端算,不能偷偷改 guard kill 的行為。
2. 回歸網是 `-k kill` 子集(37 支)。我查 `scripts/test_lumos.py`:`worktree add 失敗` 這句沒有任何測試釘它,多平台 guard kill 也沒有名稱帶 multi/plat 的測試。只有 `--keep-worktree` 與 dirty 警告有測試。所以「`-k kill` 全綠」證不了 add 失敗與多平台路徑沒變。
3. 實作者要先在計劃補:函式如何回報 add 失敗(回 None 或帶 stderr)、輸出口由誰印、樹頂與平台子路徑的分工,並替 add 失敗路徑補一支先紅的測試。

## F4 殘骸掃描的路徑比對在 macOS 會對不上,標記檔與 TMPDIR 資料夾的歸屬沒講
severity: minor
blocking: 否
引句:「路徑帶修正關卡前綴、標記檔的行程已經不在的」
file: `scripts/lumos:14176`(guard kill 用 `tempfile.mkdtemp(prefix="lumos-kill-")`)
1. 實測(clone 副本):`T=$(mktemp -d)` 得到 `/var/folders/.../T/tmp.XXXX`,`git worktree add --detach $T/wt HEAD` 後,`git worktree list --porcelain` 印的是 `/private/var/folders/.../T/tmp.XXXX/wt`。`mkdtemp` 回 `/var/...`,git 記 `/private/var/...`。若掃描用整條路徑的前綴去比對 `tempfile.gettempdir()` 加前綴,macOS(本機就是 Darwin)永遠比不到,殘骸永遠不清。必須用資料夾名(basename 的父層)比前綴,或兩邊都 `realpath`。
2. 標記檔放「暫存資料夾」(`wt` 的上一層),porcelain 列出的卻是 `wt` 本身,掃描要先取 parent 才找得到標記。計劃沒寫。
3. 標記檔未寫成前被 SIGKILL(mkdtemp 與標記檔之間、或 `worktree add` 失敗前)會留下「沒標記」的資料夾。計劃的規則是「標記檔的行程已經不在」,沒標記是清還是不清沒定義:清可能砍到並行中的另一次 fix-check,不清就永遠漏。`worktree add` 前就死的情形不會出現在 `git worktree list`,更是掃不到。
4. 計劃說 `TMPDIR` 指到「修正關卡自己的暫存資料夾,跟工作樹一起刪」。兩棵樹各自 mkdtemp,那這個 TMPDIR 資料夾是第三個、獨立的,沒說前綴、標記檔、SIGKILL 後誰清。S10 的測試夾具要指定:殘骸的 TMPDIR 資料夾也要清。

## F5 第 5 項呼叫 `_bound_tests_check` 的幾條旁路:TMPDIR、過濾探針快取、總時間
severity: minor
blocking: 否
引句:「它寫的治理帳事件落在綠樹裡、跟著刪掉,不進主 repo 的帳」
file: `scripts/lumos:38641`(`_run_bound_tests` 呼叫 `_kill_run`,不帶環境)
file: `scripts/lumos:38565`(`_bound_tests_filter_probe` 快取鍵含 `realpath(root)|run_cmd`)
file: `scripts/lumos:38384`(`_bound_tests_log` 經 `_vault_in(repo_root)` 寫 `docs/.governance-log.jsonl`)
1. 治理帳寫在綠樹那一半屬實:`_bound_tests_log` 用 `_vault_in(repo_root)` 再 `_append_governance_log(vault, …)`,而 `docs/.governance-log.jsonl` 是受版控檔,樹裡有一份,會一起被刪。這點計劃對。
2. 但 `_kill_run` 的 `env` 參數只有計劃第 4 項自己跑測試時帶 TMPDIR;第 5 項走 `_bound_tests_check → _run_bound_tests → _kill_run`,中間沒有任何環境變數入口。實測 `scripts/test_lumos.py` 紅時會留「這一輪的暫存現場留著沒刪」在 TMPDIR(`/var/folders/.../gctl-run-xxxx`),所以合約測試有紅時會在系統 TMPDIR 留垃圾。要嘛 `_bound_tests_check` 開環境入口,要嘛 fix-check 在這段包 `os.environ["TMPDIR"]`,計劃沒選。
3. 過濾探針快取鍵含綠樹的 `realpath`,每次 `mkdtemp` 路徑都不同,快取永遠 miss,每次多跑一次假名探針、並在 `~/.cache/lumos/bound-filter/` 留一個 14 天才過期的檔。python 棧有 `_RAN_EVIDENCE` 不走探針,所以本 repo 不受影響,但沒有實測樣式的棧(計劃〈實務隱患〉自己承認)每次都付代價並且寫進 `$HOME`。這與〈已排除:對外送出〉的口吻(只在本機跑)不衝突,但「只讀寫工作樹」的暗示不成立。
4. 第 6 項「總時間」對第 5 項無效:`_bound_tests_check` 沒有截止時間參數,一旦開跑就跑到底(最壞每支 180 秒,整套跑的 600 秒)。計劃寫「還沒跑的測試與項目不跑」,只對先紅後綠那段做得到。實作者要在計劃補:第 5 項啟動前先判剩餘預算,並承認一旦啟動就不可中斷。
5. `_kill_run` 加 env 參數:`subprocess.Popen(env=…)` 傳入的是整個取代,不是合併。計劃寫「選填參數帶環境變數」,實作者若直接傳 `{"TMPDIR": …}` 會丟掉 `PATH`,測試跑不起來。要寫明「與 `os.environ` 合併」。
6. 對其他呼叫者的影響:`_kill_run` 的呼叫者共四處(guard kill 兩處、過濾探針、`_run_bound_tests`),加「被中斷時砍群組再丟」與選填 env 都不改回傳形狀。外層唯一值得注意的是過濾探針那層是 `try … except Exception`,`KeyboardInterrupt` 不是 `Exception`,會照常穿出去,沒有被吞的風險。已讀,這一條行為不衝突。

## F6 `kind` 用 `blocked` 與「兩步都只提醒不擋」不符,會被 gov 統計算成「硬擋」
severity: minor
blocking: 否
引句:「kind `passed` / `blocked`(照鄰居的用字)」
file: `scripts/lumos:7470`(`cmd_gov --stats`:`hard = [r for r in ded if r.get("kind") == "blocked"]`,印「硬擋 N 次」)
file: `scripts/lumos:25830`(鄰居 `nodehome-check` 的用字:非擋模式用 `warned`,只有真的擋才用 `blocked`,且 `hard=(kind == "blocked")`)
1. 鄰居的用字其實是「擋才 blocked,只提醒就 warned」。計劃第 1、2 步都不擋,卻把驗不過記成 `blocked`。`lumos gov --stats` 的「閘的動作」段會印「硬擋 N 次:fix-check N」,對一道不擋的關卡是錯的。〈上線〉之後「轉成擋」那個小改動也會讓 `blocked` 的語意在同一道閘中途翻轉,舊事件分不出擋與沒擋。
2. 計劃另一處「擋下過幾次真問題」(REVISIT)要靠這個 kind 數。建議事件帶 `hard` 欄與 kind 分開表達(不擋時記 `warned`、轉擋後才記 `blocked`),或在計劃明寫統計為何接受這個算法。

## F7 治理帳讀端:`token` 本來就在去重鍵裡,要補的是「讓 mapper 吐 token」;欄位型別我掃過,沒有衝突
severity: minor
blocking: 否
引句:「`token` 放進去重鍵,不然同一個提交上連跑兩次同結果會被折成一筆、統計少算」
file: `scripts/lumos:7649`(治理帳 mapper 的 `token` 只在 canary+blocked 與 code-loop 的 dispositions/recall-miss 才有值)
file: `scripts/lumos:7727`(去重鍵 `(commit, nodes, gate, kind, token, check)` 已含 `token`)
1. 去重鍵已經含 `token`。真正要改的是 `.governance-log.jsonl` 那支 mapper:`fix-check` 事件要吐 `d.get("token")`,否則所有 `fix-check` 事件的 `token` 都是空字串,同一提交同一 kind 連跑兩次仍被折成一筆。寫「放進去重鍵」會讓接手者去改去重鍵(本來就有)而漏掉 mapper。
2. 去重鍵的 `commit` 是 `head_sha[:7]`(`_gate_event_build`),不是 40 碼,所以「同一提交」是 7 碼比較,可接受,但 S7 夾具要用 `LUMOS_` 之類手段造同一提交連跑兩次。
3. 我實際掃了三本帳(`docs/.governance-log.jsonl` 101724 筆、`docs/.canary-log.jsonl` 2612 筆、`docs/.signoff-log.jsonl` 8 筆)與其他三本,結果:
   - `secs`:只在治理帳出現,254 筆全是 `float`。fix-check 要寫 `secs` 就必須是 `float`,或把表寫成 `(int, float)`,不要 `round(x)` 出整數。
   - `head_sha`:治理帳 1779 筆全是 `str`(其餘帳沒有)。
   - `loop`:審查帳 2611 筆全是 `str`;`round`:審查帳 2438 筆全是 `str`(沒有 `int`)。表上現有的 `(str, None)`、`(str, int, None)` 都容得下。
   - `record_sha256`、`failed_items`:三本帳都不存在。`token`:審查帳 2612 筆全是 `str`,表上現有 `(str,)` 容得下。
   所以「加表前先掃」這個方法在本 repo 現狀下沒有衝突。唯一的風險是 `secs` 的型別必須能收 float。
4. 補一條:`_gate_event_build` 把 `extra` 以 `ev.update(extra)` 合併,可以覆蓋 `ts`、`kind` 等核心欄位。計劃放的 `loop`、`round` 不撞,但實作者別把 `kind` 之類放進 `extra`。

## F8 S12 的後半句不是這支測試能斷言的
severity: minor
blocking: 否
引句:「guard kill 改用共用的隔離工作樹函式之後,`-k kill` 子集全綠 [test:t_fix_check_template]」
file: `scripts/test_lumos.py:31423`(`TEST_TIMEOUT_SEC` 預設 180 秒,合約測試閘用同一個上限)
1. 這句是「改完重構後另一組測試全綠」的過程條件,不是一支測試能斷言的行為;它被綁在 `t_fix_check_template` 上,該測試也跑不出 `-k kill` 子集(約 5 分鐘,超過每支 180 秒上限,而且 `-k kill` 子字串還會選中 S10 的 `t_fix_check_cleans_up_after_kill`,測試內再跑子集會遞迴)。
2. 實作者只會寫出前半句的測試,這半句沒有任何機械守衛,規格閘(綁定、跑紅綠)會看到條款沒被測試約束。建議把它搬到〈實務隱患〉當一次性的人工回歸步驟,條款只留 `--template` 行為。

## F9 `base` 沒有保存的家,接手與中斷復原時找不回來
severity: minor
blocking: 否
引句:「(手冊第 1 步凍結材料時順手記 `git rev-parse HEAD`)」
1. 手冊第 1 步只說「順手記」,沒指定記在哪。第 1 步到 fix-check 之間隔著派席、收貨、判讀、修與釘(第 2 到第 5 步),可能跨會談與上下文壓縮。`lumos handoff` 與 `loop next` 都不讀它。三個月後接手的人只看得到 `rN-snapshot.patch`(那是 diff,不含提交編號)。
2. `--template` 印 `base` 留空,沒有任何來源可以預填。建議把這個值落在每輪都會寫的檔裡(例如 `rN-dispatch.json` 或快照旁邊一個 `rN-snapshot.base`),並讓 `--template` 優先讀它。計劃現在的寫法把一個脆弱的步驟放在人的記憶裡,而 `base` 填錯是「失敗方向是擋」(〈實務隱患〉),等於每次記錯都要花一次迴圈。

## F10 改名偵測與測試地圖兩個小洞
severity: minor
blocking: 否
引句:「`base..修正後` 有程式檔被改名時這項也判不過」
file: `scripts/lumos:36475`(`cmd_impact_diff` 用 `git diff --name-only <範圍>`,預設偵測改名,只列新路徑)
file: `.gitignore`(`.lumos/testmap.json` 不進版控)
1. `impact --diff` 的改名漏洞對任何檔案都成立,不只「程式檔」:筆記正文裡用反引號寫的路徑可以是設定檔、資料檔、腳本。計劃只對「程式檔」改名判不過,改名的設定檔或資料檔照樣漏掉舊路徑牽連的合約,卻會判「綠」。偵測要用同一個範圍再跑一次帶改名偵測的 `git diff --name-status -M`,有任何 `R` 就判不過,不論副檔名。
2. 第 5 項最後一句:「照檔案對應(測試地圖建過才有)推出來的測試檔只印成…」。`.lumos/testmap.json` 被 `.gitignore` 排除,綠樹裡沒有這份檔。若這段「參考」是在綠樹裡呼叫,永遠印不出來。要明寫從主工作目錄讀。

## 沒問題的節(已讀,無 finding)
- 〈共用的隔離工作樹〉依賴 `_lint_link_deps(real_dir, snap_dir)` 的簽章核對正確(`_LINT_DEP_DIRS = ("node_modules", ".venv", "venv")`,`link.exists()` 才建),已讀,無 finding。
- 先紅後綠的「紅」判讀(非 0、支數恰好 1):實測本 repo 的執行器對 `-k t_gov_stats_gate_drift` 在把 `_KNOWN_GATES` 弄壞後 rc=1,輸出第一行是 `lumos 測試(1 案例)`、結尾是 `4 passed, 1 failed`,所以 `_ran_count` 的 `count_re` 讀得到支數;支數行在輸出開頭,不會被 `_kill_cap` 的頭尾截斷砍掉(超過 256KB 時頭尾各留一半)。`-k` 選中 0 支時輸出「選中 0 個測試…視為失敗」,與計劃「支數 0 → 不過」一致。已讀,無 finding。
- `_kill_run` 加中斷處理:呼叫者共四處(guard kill 兩處、過濾探針、`_run_bound_tests`),新增行為只影響被中斷時;SIGTERM 轉成例外只在 fix-check 內生效。詳見 F5 第 6 點。
- 手冊步驟編號(第 1、5、6、7 步)與計劃的引用逐步對上;路線圖 1a-3 那列存在可補句;`lands_in` 的三篇系統筆記裡 `Systems/代碼審修正關卡` 尚未建立是計劃明講的新開,不算壞引用。
- 條款夾具:S1–S3、S5、S6、S9、S11、S13–S16 都能用既有的暫存 repo 夾具(有 vault、單平台 `run_cmd`)寫出來;S4 要一支「支援 `-k` 子字串並印 `Ran N tests`」的迷你執行器(unittest 即可,`count_re` 已涵蓋);S10 要把 fix-check 開成子行程後送 SIGTERM、SIGKILL 並驗標記檔與 `git worktree list`;S11 的 `fix_check.max_minutes` 要能填小數或測試要注入時鐘(計劃沒寫是否整數)。

最高等級:major,blocking 共 2 條
