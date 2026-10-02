severity: major

# r3 整合與接手席(整合-sonnet)報告

立場:三個月後照這一版實作、照手冊操作的接手者。實測在 `git clone --shared` 出來的副本裡用 `git worktree add --detach` 建一棵樹,直接呼叫 `_run_bound_tests` 與 `_bound_tests_check`:

- `_run_bound_tests(樹, [(節點, "python", "t_guard_kill_rc_precedence", "real")], tails={})` 回 green、`tails` 讀得到「lumos 測試(1 案例)」,工作樹路徑下跑得起來(單支約 19.6 秒,不是計劃寫的 2.7 秒;只是量級差,不算 finding)。
- `_bound_tests_check(樹, "a5877e38~1..a5877e38")` 回 `green`、59 支、跑 245.8 秒、算 40.8 秒,整次 258.8 秒,跟計劃〈實務隱患〉「59 支 258 秒」對得上。跑完 `git -C 樹 status` 只有 `docs/.governance-log.jsonl` 被改(`_bound_tests_log` 寫進樹裡的治理帳,會跟著樹刪掉),主 repo 副本乾淨。傳進去的 `repo_root` 必須是 `Path`(多平台分支用 `repo_root / root_str`,傳字串會炸),計劃沒寫,但實作時一跑就知道,不另立 finding。
- 沒有 `{method}` 之外的先決條件缺失:`.lumos/config.json` 在本 repo 是進版控的,工作樹裡讀得到;`load_platforms(樹)` 的平台根會解到樹裡(單平台 legacy 分支回傳的 `root` 就是傳進去的 `repo_root`)。

## F1 「簿記檔」判準在程式裡沒有一支現成函式長這樣,計劃把它掛在留痕消費者名下是錯的
severity: major
blocking: 是
引句:「或事件之後又改了簿記檔以外的檔(含 `governance/` 底下的程式)時也印」
file: `scripts/lumos:39233`
file: `scripts/lumos:39269`
file: `scripts/lumos:6896`
file: `scripts/lumos:22660`

1. 〈名詞〉說簿記檔是「代碼審留痕認定」的那一組:`_BOOKKEEPING_FILES`、`_BOOKKEEPING_DIRS` 加圖譜筆記資料夾,而且「不另訂」。實際讀碼:留痕那個消費者是 `_codeloop_record_valid_ex`(39233 行起),它的豁免只看那兩個常數,**不含圖譜筆記資料夾**;另外它對「簿記資料夾底下的程式檔」有特例(`_codeloop_bookkeeping_code`,39303 行),註解明寫「簿記資料夾底下的程式檔不算簿記(只改這一個消費者;小改動閘、風險掃描、推送前測試範圍、來源髒檔合併照舊只看前綴)」。
2. 唯一把圖譜筆記資料夾算進去的是小改動閘的 `_sc_changed_files` 裡的區域函式 `_bk`(6896 行,是閉包,外面叫不到),它又沒有「資料夾底下的程式檔不算簿記」的特例。
3. 計劃要的是三者的混合:S8 要「事件之後只改了圖譜筆記或帳本時不印」(要有筆記資料夾)、同時「含 `governance/` 底下的程式」也印(要有特例)。照字面「用 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS` 前綴 + 筆記資料夾」實作,`governance/review-reports/`、`governance/replay/`、`governance/code-loop/`、`governance/note-verdicts/`、`governance/reread-verdicts/` 這五個前綴底下的程式檔會被當簿記,修正之後有人把程式放在那裡改,`loop next` 的提醒會被靜音;反過來直接呼叫 `_codeloop_record_valid_ex` 又會把筆記改動判成「動了代碼」,S8 的「只改圖譜筆記不印」會紅。第 5 項的「簿記檔以外的檔被改名」同一個判準,同樣兩頭落空。
4. 結論:實作者要新寫第三支「檔 + 資料夾 + 筆記 + 資料夾內程式特例」的判斷,而計劃寫著「不另訂」,而且〈做法〉沒有說這支要放哪、誰來維護(新增第六個消費者時漂移)。計劃要明寫:新抽一支共用函式、由它組合 `_codeloop_bookkeeping_code` 與筆記前綴,並說明為什麼這次跟留痕那邊多了筆記豁免。
5. 未用指令重現(讀碼即可驗證);要重現可 `grep -n "_BOOKKEEPING_DIRS" scripts/lumos` 看六個消費者各自怎麼用。

## F2 S13 對 guard kill「現在的行為」的描述跟程式不符,「先補測試、先綠、抽完照綠」做不到
severity: major
blocking: 是
引句:「多平台時 guard kill 應在平台所在的 repo 建樹、測試在平台根跑,跟抽函式之前一樣」
file: `scripts/lumos:14179`
file: `scripts/lumos:14203`
file: `scripts/lumos:14233`

1. 現在的 guard kill:`proot = Path(pentry["root"])`(平台根),`git -C proot worktree add --detach wt ghead`,之後測試是 `_kill_run(cmd, wt, …)`——工作目錄是 `wt` 本身。
2. 平台根若是 repo 的子資料夾(〈名詞〉自己舉例 `ios/`),`git -C ios worktree add` 建出來的是整個 repo 的樹(實測:`git init` 一個含 `ios/a.txt`、`top.txt` 的 repo,`git -C ios worktree add --detach ../wt HEAD` 後 `ls wt` 是 `ios top.txt`),測試跑在 `wt` 頂層,**不是** `wt/ios`。所以「測試在平台根跑,跟抽函式之前一樣」只在平台根剛好就是 repo 頂層(或平台根自己是一個獨立 repo)時成立。
3. 〈共用的隔離工作樹〉又寫「guard kill 傳平台所在 repo 的頂層,照它現在的 `-C`」(現在的 `-C` 是平台根,不是頂層)與「平台根的子路徑由呼叫端自己接」。照這句實作,guard kill 在子資料夾平台會把測試改到 `wt/<子路徑>` 跑——行為變了;不接就跟 S13 那句「測試在平台根跑」對不上。
4. 接手者撞牆的步驟:〈共用的隔離工作樹〉要求「抽函式前先補這兩條測試,再抽(先綠、抽完照綠)」。多平台那條測試若用子資料夾平台根當夾具,對抽函式之前的程式寫「測試在平台根跑」會是紅的(實際在 wt 頂層),「先綠」做不到;若用獨立 repo 當平台根才綠,但那就不是〈名詞〉說的 `ios/` 情境。
5. 計劃要先裁定:子資料夾平台根是保留現況(測試在 wt 頂層)還是順便修成在子路徑跑,並把 S13 與〈共用的隔離工作樹〉寫成同一個說法。修正關卡自己的紅綠樹不受影響(它們走 `_run_bound_tests(樹, …)`,`load_platforms(樹)` 會把平台根解到 `樹/ios`)。

## F3 總時間預算要「每支測試的逾時取較小」,但 `_run_bound_tests` 沒有任何逾時參數
severity: minor
blocking: 否
引句:「`fix_check.budget_sec` 用完時,`fix-check` 應停止還沒跑的測試、回 1」
file: `scripts/lumos:38606`
file: `scripts/lumos:38620`

1. `_run_bound_tests(repo_root, items, tails=None)` 的簽章沒有逾時;每支的逾時是函式裡讀 `os.environ["LUMOS_TEST_TIMEOUT"]`(預設 180)決定的,整批 items 一次跑完中間沒有回呼點。
2. 要做到〈做法〉第 6 項「每支測試的逾時取自己的逾時與剩下的時間較小的」與 S11「停止還沒跑的測試」,實作者只有兩條路:(a)每支測試各呼叫一次 `_run_bound_tests` 並在呼叫前暫時改行程環境的 `LUMOS_TEST_TIMEOUT`(又是一個改全域環境的點,跟 `TMPDIR` 同類,計劃沒寫);(b)替 `_run_bound_tests` 加參數(它有合約測試閘、規格閘兩個既有呼叫者,〈範圍〉與〈要同步的文件〉都沒列這個改動)。兩條都要人拍板,計劃兩邊都沒寫。
3. 另外,逾時判紅的辨認(「逾時算紅」)只能靠 `results` 裡 detail 以「超時(」開頭這個字面,而不是結構化欄位;計劃沒點名。
4. 這只是要做決定、不是做出錯行為,所以 minor。

## F4 `TMPDIR` 只對子行程生效,行程內的 `tempfile` 不跟著走,「共用工作樹函式建在哪」計劃沒定
severity: minor
blocking: 否
引句:「整次執行期間把行程環境的 `TMPDIR` 指到修正關卡自己的暫存資料夾(子行程繼承;結束時刪掉、還原環境)」
file: `scripts/lumos:14202`
file: `scripts/lumos:13987`
file: `scripts/test_lumos.py:31705`

實測(`/opt/homebrew/bin/python3`):
```
tempfile.gettempdir()           # 已被呼叫過、快取了
os.environ["TMPDIR"] = d
tempfile.mkdtemp().startswith(d)   # -> False
```
1. Python 的 `tempfile` 第一次用到就把 `tempfile.tempdir` 快取住,之後改 `os.environ["TMPDIR"]` 對行程內的 `mkdtemp`/`TemporaryFile` 無效;只有子行程(測試工具)看得到新 `TMPDIR`。`cmd_guard_kill` 現在用 `tempfile.mkdtemp(prefix="lumos-kill-")`、`_kill_run` 用 `tempfile.TemporaryFile`,都是行程內呼叫。
2. 所以共用工作樹函式的暫存資料夾會落在哪,取決於改環境變數之前有沒有人呼叫過 `tempfile`:有(例如殘骸掃描用了 `tempfile.gettempdir()`)就落在原系統暫存資料夾、無視新 `TMPDIR`;沒有就第一次呼叫時把 `tempfile.tempdir` 釘死成修正關卡的資料夾,而結束時資料夾被刪、環境還原了,`tempfile.tempdir` 還指著已刪的路徑(同一行程之後再呼叫 `tempfile` 會 `FileNotFoundError`;測試總檔在行程內直接呼叫 `cmd_fix_check` 時,runner 自己在 31705 行把 `tempfile.tempdir` 釘死了,所以測試看不到這個差異,但真 CLI 單次執行會因寫法而異)。
3. 連動到〈中斷與殘骸〉:殘骸掃描只認「位在系統暫存資料夾底下、資料夾名以修正關卡前綴開頭」,「系統暫存資料夾」是取 `tempfile.gettempdir()`、環境變數還是 `/tmp`,計劃沒寫;S10 的測試跟真 CLI 可能走不同路徑。
4. 另外 SIGKILL 時被刪不掉的是 `TMPDIR` 那個資料夾本身(裡面有測試工具紅時留的現場),掃描是靠 `git worktree list` 驅動的,只清得到登記過的工作樹;在 `mkdtemp` 之後、`git worktree add` 之前被砍的資料夾(計劃自己提到的「標記檔寫之前那一瞬間」)沒登記,永遠掃不到。
5. 計劃要補一句:行程內的暫存資料夾位置一律明寫 `dir=`(或明確 `tempfile.tempdir = …` 並在 finally 還原),殘骸掃描的「系統暫存資料夾」用哪個值要固定。

## F5 過濾探針的快取不在綠樹裡,計劃的說法有誤
severity: minor
blocking: 否
引句:「它寫的治理帳事件、測試快取都落在綠樹裡、跟著刪掉,不進主 repo」
file: `scripts/lumos:38564`
file: `scripts/lumos:38572`

1. `_bound_tests_filter_probe` 的結果快取在 `~/.cache/lumos/bound-filter/<sha256(realpath(root)|run_cmd|schema)>.json`(家目錄,不是樹),保鮮 14 天,沒有任何清理。治理帳事件確實落在樹裡(實測 `git -C 樹 status` 只有 `docs/.governance-log.jsonl`),測試工具自己的失敗快取 `.lumos/test-cache*.json` 也在樹裡(被 `.gitignore` 蓋住)。
2. 本 repo 是 python profile,有 `_RAN_EVIDENCE`,不走探針(實測跑完 `~/.cache/lumos/bound-filter` 沒有檔);非 python 棧每次 `fix-check` 因樹路徑不同(`mkdtemp` 隨機)多寫一個 ~100 位元組的檔進家目錄,不會被刪。
3. 影響小(堆積慢),但「落在綠樹裡、跟著刪掉」這句話是錯的,接手者驗收 S4「跑完沒有殘留」時會對錯地方找。

## F6 手冊第 5 步沒有叫人先提交修正,照手冊做第一次就會撞到「`fixed` 的檔沒改動」
severity: minor
blocking: 否
引句:「第 5 步(修與釘:修完寫修正紀錄,可用 `--record-template`;修正動到的檔都要列成 `fixed`)」
file: `skills/lumos-code-loop/SKILL.md:57`

1. `fix-check` 只認提交(HEAD 的 40 碼;主工作目錄沒提交的改動只印提醒),手冊第 5 步現況是「真問題修進真碼」,提交要到第 8 步才提(「程式、筆記、卷證、帳本放進同一個功能提交」)。照〈要同步的文件〉列的新第 5 步文字,沒有「先提交」。
2. 接手者照做:修完、寫紀錄、跑 `fix-check` → `fixed` 的檔在 `base..HEAD` 沒改動 → 回 1,「檔沒改過=紀錄寫錯」,方向是誤導的;〈做法〉只在「不是先決條件、只印提醒」那段講了「修正忘了提交時」,手冊卻沒帶到。
3. 手冊第 1 步下一輪凍結本來就用 `git diff <merge-base>..HEAD`(只含提交),所以下一輪之前本來就得提交,只是沒寫在第 5 步。要同步的文字加一句「修完先提本機提交(推之前壓成一個)再跑 `fix-check`」即可。

## F7 `base_commit` 寫進派工單:讀端不會出事,但實際派工單有三種形狀與「同輪多檔」,計劃只講了一種
severity: minor
blocking: 否
引句:「派工單多一個欄位 `base_commit`(派工當下 `git rev-parse HEAD` 的 40 碼;手冊第 2 步寫派工單時一起寫)」
file: `scripts/lumos:11144`
file: `scripts/lumos:21339`

1. 既有讀者不會因多一欄出事:`_roster_dispatch_entries` 只取 `auditor`/`seats`,多餘的鍵忽略;`cmd_seat_check` 用 `disp.get(...)`,同樣忽略。這部分已讀,無 finding。
2. 但實際卷證(本 repo `governance/review-reports/*/*-dispatch*.json`,實數):428 個「頂層 dict 帶 `seats`」、105 個「單席 dict(頂層 `auditor`)」、1 個「頂層 list」;25 個輪次同輪有多個 `rN-dispatch-*.json`(每席一檔)。計劃寫的是單一 `rN-dispatch.json`:`--record-template` 要從哪個檔讀 `base_commit`、list 形狀的檔沒有地方放欄位、同輪多檔時各檔的 `base_commit` 不一致怎麼辦,都沒寫。
3. 結果:這類迴圈 `--record-template` 的 `base` 留空,`fix-check` 因「`base` 轉不成存在的提交」回 2,接手者得手填;計劃只寫「沒有就留空」,沒告訴人這時要自己填。補一句「只認 `rN-dispatch.json` 這個檔名、頂層 dict」即可。

## F8 「沒有 `docs/`」時 `_gate_event_or_warn` 是靜默的,計劃說它會印警告
severity: minor
blocking: 否
引句:「寫不進治理帳(沒有 `docs/`)時照 `_gate_event_or_warn` 印警告,輸出多一句」
file: `scripts/lumos:1204`
file: `scripts/lumos:1234`

1. `_gate_event` 對「沒有 `docs/`」回 `None`(註解:「這個 repo 根本沒有這本帳」不是「寫不進去」),`_gate_event_or_warn` 對 `None` 直接 `return None`、不印任何東西;只有 `OSError` 才回 `False` 並印 `telemetry-write-failed`。
2. 且沒有 `docs/` 就沒有審查帳,`fix-check` 在先決條件「審查帳找得到這一輪的載體席」就回 2 了,走不到記帳。所以這句話描述的情境走不到、描述的行為也不是函式的行為。「這次通過沒記到帳」那一句要靠呼叫端自己判 `False`,不是 `None`。

## F9 `fix_check.link_dirs` 的「寫法照 `_lint_link_deps`」不能照用
severity: minor
blocking: 否
引句:「才在兩棵樹的同一位置用連結指回主工作目錄(寫法照新增告警閘的 `_lint_link_deps`)」
file: `scripts/lumos:23630`

1. `_lint_link_deps(real_dir, snap_dir)` 走的是寫死的 `_LINT_DEP_DIRS` 常數,不接受外部清單,也沒有「相對 repo 頂的路徑清單(例如 `ios/Pods`)」那種多層路徑的處理(它只在 `real_dir/dep` 單層連)。要做 `link_dirs` 得新寫一支;「照」只能當形狀參考。
2. 另外沒有寫 `link_dirs` 項目的驗證(絕對路徑、`..`、指到工作樹外),連結端會建在樹的外面。這個設定檔是專案自己放的,風險低,留給邊界席。

## 沒問題的節
- 〈修正紀錄〉的樣板指令、`--record-template` 印到標準輸出/標準錯誤:已讀,無 finding(命名沿用 `--dispositions-template`)。
- 條款 S1–S12 的夾具需求,實作者可直接推出(不需另問人):S1/S2/S3/S6/S7/S9/S12 只要一個含 `docs/<名>-knowledge/` 與 `docs/.canary-log.jsonl`(載體席帶 `round`、`findings_set`、`folded_set`、`finding_kinds`)的暫存 git repo + 一份 `rN-fix.json`;S4/S5/S10/S11 還要 `.lumos/config.json`(`run_cmd` 帶 `{method}` 與 `{python}`)、一支會印「Ran N tests」或「lumos 測試(N 案例)」的假測試工具(python profile 認這兩種)、至少兩個提交(base 與修正後);S5 要一篇有 `★INVARIANT★` 與 `[test:]`、且用反引號寫了被改檔路徑的筆記;S10 要能被 SIGTERM 的卡住測試與寫好標記檔的殘骸資料夾。唯一例外是 F2(S13 的多平台夾具選哪種平台根,計劃兩處講法不同)。
- 簿記檔清單新增消費者要不要改清單本身:不用改常數,但見 F1(要新抽共用判斷)。

最高等級:major,blocking 共 2 條
