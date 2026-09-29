severity: major

鏡頭:整合與知識同步(guard settle / drift ack / drift scan / lumos set / doctor 的接縫、要同步的文件與指令表、lands_in 落點)。對照 repo 為 clone-ns,以下 file: 路徑都是該 repo 內相對路徑。

## F1 治理事件閘名 drift-fix 不在已知閘名單上,照字面實作會警告並且不落帳
severity: major
blocking: 是 — 不改,每次 drift fix 成功都會在 stderr 喊一句寫不進去、治理帳沒有修復事件,實作者還會以為有記
引句:「成功後記一筆治理事件(閘名 `drift-fix`,同 `drift ack` 記事件的方式)」
file: `scripts/lumos:1154`
file: `scripts/lumos:6904`
file: `scripts/lumos:27142`
1. `_gate_event`(被 `_gate_event_or_warn` 呼叫)在寫帳前檢查 `gate not in _KNOWN_GATES`,不在名單就印「⚠ 想記一筆 gate=…沒有寫」並回 False,不寫任何一行。
2. `_KNOWN_GATES`(scripts/lumos:6904 起的 tuple)目前沒有 `drift-fix`;`drift ack` 自己用的閘名其實是 `drift-check`(27142),不是新名字。spec 一面說新閘名 `drift-fix`、一面說「同 drift ack 的方式」,兩句互相矛盾。
3. spec 的〈做法〉第 7 節同步清單與 [S9] 條款都沒提「要把 `drift-fix` 登進 `_KNOWN_GATES`」;另有漂移釘 `t_gov_stats_gate_drift` 掃「閘名字面值必須在名單內」。照字面實作:要嘛帳靜默漏掉(只多一行警告),要嘛沿用 `drift-check` 但 spec 沒這樣寫。
4. RETIRE-IF 與 REVISIT 量的是修復帳本身,不受影響;但〈實務隱患〉「併發」與 S9 宣稱的「成功後記治理事件」會是假的。

## F2 guard settle 補改 pass 節點的 git 查詢會落進寫入鎖裡,跟第 1 節「git 放鎖外」的理由自相矛盾
severity: major
blocking: 是 — 不改,settle 路徑上 c1 日期的 git 查詢在大 repo 超過 30 秒時,鎖被當成死鎖接手,兩個寫入者同時改同一篇
引句:「放在鎖外,因為寫入鎖 30 秒沒放就被當成死鎖接手(`_VAULT_LOCK_STALE_SEC`),git 在大 repo 可能超過」
引句:「還有預告句就走第 2 節同一支(日期規則、前提檢查、不疊、修復帳 `via: guard settle`)」
file: `scripts/lumos:12195`
file: `scripts/lumos:12208`
file: `scripts/lumos:14714`
1. 現況 `cmd_guard_settle` 一進來就 `with _vault_write_lock(...)`,狀態(pass 或 pending)是進鎖之後才在 `_guard_settle_locked` 讀的。spec 第 3 節說 pass 且還有預告句時「走第 2 節同一支」,第 2 節第 2 點的 `git log --reverse -G "^status: pass"` 就會在這把鎖裡跑。
2. 第 1 節第 1 步明講 git 一定要在鎖外,理由是鎖 30 秒沒放會被 `_excl_lock_try` 原子接手。這個理由對 settle 路徑同樣成立,但第 3 節沒有給「先不拿鎖偷看 status、決定要補改後在鎖外推日期、再進鎖重讀重判」的結構,也沒說 settle 的補改路徑要不要有自己的鎖外準備步驟。
3. 接手的人照字面把第 2 節那支函式接到 `_guard_settle_locked` 裡,就會做出鎖內跑 git 的版本;[S3] 條款與測試名 t_guard_settle_pass_completes_prose 只綁行為,不會抓到。
4. ⚠ 需要 settle 也拆成「鎖外準備、鎖內重讀重判」兩段;spec 沒寫,實作者得自己發明。

## F3 spec 引用的 `_CMD_HELP` 不存在,實際是 HELP_WHEN,而且要補的不只 drift 一條
severity: minor
blocking: 否 — 實作者搜一下就找得到,只是指令說明會漏補 drift fix 與 settle 兩個鍵
引句:「`_CMD_HELP` 的 drift 說明與 argparse 的 help 一起補」
file: `scripts/lumos:35573`
file: `scripts/lumos:35687`
file: `scripts/lumos:35609`
1. repo 內沒有 `_CMD_HELP`;單一來源是 `HELP_WHEN`(35573),`_fill_help_when` 用「父 子」鍵灌進子指令的 description。
2. 現有鍵是 `"drift"`、`"drift check"`、`"drift scan"`、`"drift ack"`(35687–35690):要補的是新鍵 `"drift fix"`,並改 `"drift"` 那句(現在寫「check…scan…ack…exam」)。`guard settle` 的說明在鍵 `"settle"`(35609,寫「預告的那條做完了…綁上測試」),spec 說 settle 語意變了(pass 補改句、`--test` 選填),卻沒列這個鍵要改。

## F4 「合併時聯集」的緩解指到一支做別的事的函式,「以最新一筆為準」又假設檔內順序等於時間順序
severity: minor
blocking: 否 — 錯的是風險說明與緩解的出處,行為方向(多列不漏列)不變,實作者不會做出壞系統,但會以為有一層防護
引句:「照既有的 JSONL 聯集合併做法處理(`_pull_source_or_abort` 對簿記 JSONL 取聯集)」
引句:「★以最新一筆為準★(表態檔只追加不改,後寫的蓋前寫的)」
file: `scripts/lumos:17600`
file: `scripts/lumos:17632`
1. `_pull_source_or_abort` 處理的是「工具鏈來源 clone 在 update/bootstrap 前,工作目錄只髒了簿記帳」,拿本機未提交的行補回 pull 之後的檔案。它不管專案分支之間 `git merge`/`rebase` 兩邊都在檔尾加行的衝突;repo 的 `.gitattributes` 也沒有對 jsonl 設 `merge=union`。所以兩個工作樹各自追加修復帳/表態檔再合併,結果是 git 文字衝突,不是「聯集」。
2. 修復帳一行含改前整篇原文(常是數 KB 到數十 KB),衝突時人手處理一整段很長的行。
3. S8「以最新一筆為準」用檔內出現順序當時間順序;合併衝突人手解完之後順序不保證按日期。方向上是多列或照舊放行的差別,沒有 `date` 欄兜底;⚠ 影響有限(表態記的是當時清單,較舊的較小清單排後面只會多列),但 spec 不該把它說成「同一種風險與解法」。

## F5 提示要改的地點清單三處講法不一致,漏了計劃收尾與 check 只列出那條路
severity: minor
blocking: 否 — 不改,不同入口對同一件事的指路不一致,實作者要自己猜要改哪幾處
引句:「⑨提示文字改成指到新指令(drift check 擋下時、drift scan 每種發現的建議、drift ack 的提示)」
引句:「`drift check` 擋下時「預告句那幾筆」那段(現在教人手改,改寫)」
file: `scripts/lumos:27234`
file: `scripts/lumos:2273`
file: `scripts/lumos:26193`
1. 範圍 ⑨ 寫「drift ack 的提示」,〈做法〉第 7 節卻列「doctor Z 段的建議」,沒有 drift ack;⑨ 沒有 doctor Z。[S10] 只列 drift check 與 drift scan。三處兩兩對不上,doctor Z 的 advice(scripts/lumos:2273 寫死「lumos drift ack …」)到底改不改沒有明確條款。
2. drift check 的 c3、c4 只走「只列出」那條(`_drift_print_findings(listed…)`,27220),不經過 `_drift_report_must` 的「預告句那幾筆」文字;[S10] 說「drift check 擋下或 drift scan 列出 c1/c3/c4」,但擋下(must)只會有 c1,c3、c4 的指路擺哪沒定義。
3. `lumos set <計劃> status done` 的連帶待辦(`_drift_print_followups`,26193)會列出「驗證紀錄 pending,plan_refs 指的計劃都已收尾」= c3,是最自然的指到 `drift fix --kind c3` 的地方,spec 沒列;`drift ack` 新增的「這一行現在不是 c2/c3,不用表態」訊息也沒指到新指令。

## F6 scan 每筆 c1 各印一條 fix 指令,同一篇會印 4 條、照貼後 3 條回 2
severity: minor
blocking: 否 — 不改,不傷資料,但 rtb 20 筆 c1 會印 20 行,大半照貼就報「這一行現在不是 c1」
引句:「`drift scan` 的輸出(現在沒有下一步建議,新增:c1/c3/c4 每筆印 `lumos drift fix <節點> <行號> --kind <種類>`)」
file: `scripts/lumos:27313`
file: `scripts/lumos:12086`
1. c1 是一句一筆(`_drift_guard_findings`),一篇守衛紀錄最多 4 筆;第 2 節又說 fix 一次改整篇、改完該篇 c1 全消失。
2. 照 spec 字面「每筆印」,同一篇會印 4 條幾乎一樣的指令,只有第一條會成功,其餘照第 1 節第 3 步回 2、訊息叫人重跑 scan。這正是使用者要靠指令提示走完修復清單的入口,體驗會像壞掉。
3. 沒有說 c1 要按篇去重(每篇印一條),[S10] 只斷言「指到 lumos drift fix」。

## F7 修復帳承諾「退得回去」,但沒有還原指令、崩潰窗口與讀回失敗的殘列都沒接住
severity: minor
blocking: 否 — 已知錯誤路徑有處理;缺的是還原入口與 kill 中斷,實作者不會做出壞系統,但交接的人拿不到「退回去」的手段
引句:「修復帳每一筆都有改前整篇原文,c1、c3、c4 都能逐筆寫回」
引句:「★帳寫不進去就把筆記還原成改前原文、回 2★」
file: `scripts/lumos:8511`
1. spec 全篇沒有任何指令(`drift fix --undo`、`--restore` 之類)把帳上的 `before` 寫回;〈回退〉只說「能逐筆寫回」。接手的人得手寫腳本讀 JSONL、比 `after_sha256`。c4 沒帶參數時根本不寫,「c1、c3、c4 都能」也不精確。
2. 第 1 節第 5、6 步之間(筆記已落盤、帳還沒追加)行程被 kill 或斷電,筆記改了、帳沒有——正是理由句「筆記改了、帳上沒有,事後就找不回來」描述的狀況,而「還原」只涵蓋函式還活著的錯誤路徑。
3. `_jsonl_append_verified` 在「寫成功但讀回自驗失敗」時回 2,那一行可能已經在檔裡;spec 這時把筆記還原成改前,帳上卻留一筆看起來成功的紀錄(`after_sha256` 對不上現在的檔)。⚠ 那一行後續怎麼處理沒寫。

## F8 c3 合法狀態把 abandoned 也收進來,而且指到的常數名與實際不符、另有一份重複的字串表
severity: minor
blocking: 否 — c3 排除守衛紀錄,abandoned 在這裡沒有語意;不擋不會做出壞資料,但繞過了 guard abandon 要簽核那條
引句:「合法值是驗證紀錄的合法狀態扣掉 pending——把 `cmd_lint` 裡的類型狀態表抽成模組層常數(`_TYPE_STATUSES`),lint 與 fix 共用,不另寫一份」
file: `scripts/lumos:5245`
file: `scripts/lumos:5493`
file: `scripts/lumos:12330`
1. cmd_lint 裡現有的是區域變數 `_STATUS_ENUM`(5246),驗證紀錄是 {pass, stale, superseded, pending, abandoned};扣掉 pending 還剩 abandoned。程式註解說 abandoned 是守衛紀錄的墓碑,棄置要走 `guard abandon` 並有簽核帳(12330 起)。c3 的判定明確排除守衛紀錄(`GUARD_MARK_FIELD`),所以 `--status abandoned` 對 c3 沒意義,卻等於開了一條不用簽核的路。
2. 5493 另有一份手寫的訊息字串 "pass/stale/superseded/pending/abandoned",抽常數時若不一起改就是同一張表兩份;spec 說「不另寫一份」但沒點名這處。

## F9 c4 換片段借用整欄重寫,區塊寫法會被攤平,跟「其他文字一字不動」衝突
severity: minor
blocking: 否 — 只發生在 valid_under 用多行區塊寫的筆記;⚠ 我沒有實測 as_list 對區塊的實際切法,判斷來自程式碼閱讀
引句:「寫入借既有的 `_set_conditions_locked` 的寫法(它已經處理單行、清單、空的、多行區塊四種寫法,並擋空值與換行)」
引句:「新值清單的項數與原本相同。」
file: `scripts/lumos:14863`
file: `scripts/lumos:13524`
1. `_set_conditions_locked` 是「整欄拿掉重寫」(單一值寫單行、多值寫一行一項清單),區塊寫法讀進來是一個含換行的字串;`_conds` 會把它拆成一行一項,`as_list` 卻只算一項。spec 第 4 節找 `--old` 的單位、「項數相同」的單位都沒說用哪一個。
2. 若用 `as_list`(整個區塊算一項),換完新值仍含換行,會被 `_conditions_rewrite` 的擋換行規則擋下,c4 對區塊寫法永遠回 2;若用 `_conds` 拆行,項數變多,違反「項數與原本相同」,而且區塊被攤成清單,不是 S5 說的「其他項目與文字一字不動」。

## F10 c1 前提說「不限測試名」,但共用的判定實際要求至少綁一支測試
severity: minor
blocking: 否 — 只影響少見的「正式行沒綁任何測試」的家節點,錯誤訊息會誤導
引句:「要真的有這條合約的正式行(`_guard_formal_line`,不限測試名)」
file: `scripts/lumos:12042`
1. `_guard_formal_line(..., method=None)` 只在正式行「有綁任一支測試」(`invariant_test_refs` 非空)時才回索引。家節點的正式行只帶 `[manual:…]` 或完全沒綁時回 None。
2. 這時 spec 的前提檢查會說「這條合約其實還沒轉正」,事實是已轉正、只是沒綁測試;訊息叫人「把 status 改回 pending 後走 guard settle」是錯的出路。與 c5 判定共用同一支所以行為一致,錯的是「不限測試名」這句與給人的說明。

## F11 「要跟著改的既有測試」兩條的說法與現有測試對不上
severity: minor
blocking: 否 — 那兩支測試照舊會綠,實作者照 spec 改反而多動測試
引句:「要跟著改的既有測試:`t_guard_settle_rewrites_planned_prose`」
file: `scripts/test_lumos.py:50740`
file: `scripts/test_lumos.py:50812`
1. `t_guard_settle_rewrites_planned_prose` 只有 pending 轉正、沒有手補「已轉正」段的情境,新行為不影響它已有的斷言;手補段刪行是新情境,要另寫,不是「改」這支。
2. `t_guard_settle_recovers_half_done` ③的節點是 settle 之後已改寫過預告句的 pass 紀錄,沒有預告句可補,新版仍走「已轉正,不用再做」回 0,斷言照舊成立;要改的是新增一支 pass 且留預告句的情境。
3. 真正要新增或改的是:HELP_WHEN 相關斷言、`guard settle` 不帶 `--test` 的 argparse 行為(現在 `required=True`,scripts/lumos:36073)。

## 已讀,無 finding
- 〈誠實界線〉:已讀,無 finding。
引句:「c4 的卷證目錄是用名字比對猜的,可能漏或多;所以只提議、不寫入。」
- 〈範圍〉〈同步清單〉逐項核對:commands/04 只有 drift-history 一列、INDEX.md 現在 4115 字元(上限 4500,補一行放得下)、06 的 guard settle 列與 reference.md 全覽「drift check·scan·ack·exam」都存在,且 2026-10-13 的 REVISIT 在存量漂移防線_計劃 247 行;`t_command_index_complete` 只查頂層與 loop/canary/guard 等八個父指令,drift 不在內,不會被強迫紅。
引句:「在 04 補 drift check/scan/ack/fix 各一列、INDEX 補一行、06 的 guard settle 那列拿掉」

最嚴重等級為第二高的一級,阻擋實作的共 2 條(F1、F2),全部共 11 條。
