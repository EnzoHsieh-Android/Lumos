---
type: project
status: doing
created: 2026-11-21
updated: 2026-11-21
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/規格閘
  - Systems/pitfalls-code-loop
related:
  - "[[Projects/改動選擇點都要有需求守住_計劃]]"
  - "[[Projects/Android寫法寫完當下自動檢查_計劃]]"
---
# 代碼審通過前自動跑選擇點_計劃

## 白話

改動選擇點(Kotlin 改動行上挑壞寫法、跑計劃條款綁的測試,壞法活下來就要處置)現在只在推送前那一道機械判定;`lumos choice-kill` 要編排者自己記得在代碼審記通過之前跑。忘了跑,推送時才被擋——這時才補放行檔或改計劃,已經記好的代碼審留痕會失效,整個要重跑。這份計劃讓 `lumos code-loop pass`(代碼審最後一關)在記通過之前,用推送前那一圈的同一支判定快速看一次(不跑測試):有行缺紀錄、存活沒處置,就不記通過,當場印出要跑的 `choice-kill` 與處置指令。

WHY:`code-loop pass` 記通過之前,在新增告警與表態兩道之後多一道「選擇點預判」:不跑測試,只用推送前那一圈判一次,有擋下原因就不記通過並指路 [出處:2026-11-21 使用者要 choice-kill 在代碼審最後一關自動觸發;設計審 r1 指出既有方針「會跑測試的閘掛在擋的路徑、不掛記錄的路徑」與 pass 內跑 choice-kill 最壞 20 分鐘以上後,使用者裁「pass 只預判不跑測試」] [因:選擇點的處置(放行檔、situation-rule 改計劃、補測試)都會改非簿記檔,必須在記通過之前做;只靠推送前那道擋,發現時已經太晚;預判只要幾秒,不違反「跑測試不掛 pass」] [不選:pass 內自動跑 choice-kill(違反既有方針、最壞 20 分鐘以上、對話裡會被逾時砍、使用者 2026-11-21 裁不走);推送前自動跑(存活處置時已記過通過,陷阱只解一半);pass 時另寫一套判定(第二種做法);在 pass 自動處置存活(處置是人裁)]
PRIOR-ART: Google〈Practical Mutation Testing at Scale〉把變異結果放在 code review 當下呈現,讓審查者在合併前處理,而不是事後(https://arxiv.org/pdf/2102.11378 2.3、5);本 repo `code-loop pass` 已經在記通過前自動跑新增告警與表態兩道([[Projects/Android寫法寫完當下自動檢查_計劃]] 範圍 2,`_codeloop_pass_mech`;那兩道不跑測試,跑測試的受波及合約測試閘照方針掛在 check),新的一道照同形狀接在後面;判定直接重用推送前那一圈 `_choice_push_round`,多一個「場合」參數(推送或 pass),跟 `_codeloop_guard_verdict` 的 `mech_only` 同一種「同一支判定、模式參數分流」寫法。
RETIRE-IF: 上線兩個月後,pass 這一道擋下的紀錄裡,過半在同一個 HEAD 推送前也會被擋(代表 pass 這道沒有提早抓到東西),或使用者回報 pass 擋得多、改走 `skip`——就把這一道拿掉,回到只靠推送前那道。

## 舊否決比對

- [[Projects/留痕驗過審查_計劃]] 否決過「pass 內重跑處置閘」(要自帶 spec 路徑、多一條判定入口)。這次不重跑處置閘;跑的是選擇點判定,而且直接呼叫推送前那一圈 `_choice_push_round`,不新增判定入口。
- [[Systems/pitfalls-code-loop]] 記新增告警與表態兩道進 pass 時,否決過「另寫一支共用判定(兩套判法會漂開)」——這次照那次的做法,重用推送前同一支。
- 受波及合約測試閘([[Systems/bound-tests-gate]])定下「會跑測試的閘掛在擋的路徑(check)、不掛記錄的路徑(pass)」,理由是測試結果隨提交變。設計審 r1 撞到這條,使用者 2026-11-21 裁照方針走:pass 這道只預判、不跑測試。

## 範圍

- 做:①`code-loop pass` 在新增告警與表態兩道之後、留痕驗證之前多一道「選擇點預判」(`_codeloop_pass_gate` 裡,跟那兩道一樣不被「沒有審查帳」「light」提早返回跳過);②判法重用 `_choice_push_round`,多一個場合參數 `site`(預設 `push`,行為不變;pass 傳 `pass`),它決定四件事:帳從哪讀、訊息前綴、「缺紀錄」那條的處置說明、擋下事件記在哪個場合;③有擋下原因 → 不記通過,印同一段原因與處置指示,治理帳記一筆 `code-loop-pass` 擋下(`blocks` 帶 `choice`);④`gov --stats` 的選擇點段把「被擋筆數」分出 pass 與推送;⑤手冊與筆記同步。
- 不做:pass 不跑 `choice-kill`、不跑任何測試;不改判定規則本身(原因、回報上限、生效日、乾節點、只看 Kotlin);推送前那一道行為不變(`site` 預設值);不自動處置存活;不自動提交帳;不改 standard、light 分級要不要跑 `pass`(它們不一定走到這一關,推送前那道照舊兜底);不新增略過旗標。

## 做法

- **接點**:`_codeloop_pass_gate` 裡,`_codeloop_pass_mech` 回 True 之後、`_codeloop_pass_verify` 之前,呼叫新的 `_codeloop_pass_choice(repo_root, head_sha, branch)`;回 False 時 gate 回「不放行」。預判只讀帳與掃語法樹,不跑測試,所以排在留痕驗證之前不會讓人白等。
- **範圍**:`_choice_range(rr, None, None)`,也就是 `lumos choice-kill` 不帶 `--diff` 時的同一套(頂端=目前分支,起點=推送前那道的 `_push_range_start`,遠端舊值或分岔點)。pass 擋下時印的 `lumos choice-kill` 指令不帶 `--diff`,跑的就是同一段。`_choice_range` 回原因(目前在主線上、頂端已在主線、算不出起點)→ 這一道印一行原因、放行(同推送前那道「範圍算不出來就放行」)。
- **不用圖譜物件**:`_choice_push_round` 一族只用 repo 根(`env` 參數沒有被讀),pass 傳 `None`;所以沒有圖譜資料夾的專案這一道也照常判。
- **場合參數 `site`**:從 `_choice_push_round` 穿到 `_choice_push_scan`、`_choice_push_unverified`、`_choice_push_part_unverified`、`_choice_push_read`、`_choice_push_ledger`、`_choice_push_verdict`、`_choice_push_event`。`site="pass"` 時:
  - 帳:`_choice_push_ledger` 讀工作目錄那一份(`_gov_rows_at` 的 rev=None 模式),因為編排者剛跑的 `choice-kill` 紀錄是簿記檔、pass 時還沒提交;檔不在 = 帳不在。放行檔、守的測試、計劃照舊從頂端提交讀。
  - 前綴:`[spec-gate 推送前]` 換成 `[code-loop pass 選擇點]`;「被推版本」「修好再推」這類字樣換成「這一版」「處置後再 pass」。
  - 「缺紀錄」的處置說明換成:跑 `lumos choice-kill`(可放背景,可能要幾分鐘)後再 pass;通過後治理帳跟代碼審帳本一起提交。另加一句:放行檔與計劃的改動要先提交才算(預判從頂端提交讀它們)。
  - 事件:擋下與算不出來照舊記 gate `choice-kill` 的 blocked/unverified(同一個頂端、同一組原因照舊只記一次),多一個欄位 `site: "pass"`;推送那邊不帶這欄。
- **擋下**:`_choice_push_round` 回的清單不空 → 印出來,再印一句「處置後提交,再重跑 code-loop pass」,記 `code-loop-pass` 擋下(`blocks` 帶 `choice`,跟那兩道同形狀)。其餘提早返回全照那一圈:生效日(當天就要判)、要不要求、型錄缺檔只提醒、型錄表壞擋、ast-grep 不在或算不出來只提醒、無規格擋、只能人驗只提醒。
- **統計**:`gov --stats` 選擇點段的「被擋 N 筆」後面加「其中 pass 擋下 M 筆」(數 `site == "pass"` 的 blocked);舊帳沒有這欄的都算推送。

## 驗收條款

- [S1] 當生效日已過、範圍內有 Kotlin 改動行有選擇點且碰到進行中計劃、帳上沒有紀錄時,`code-loop pass` 應 以 rc 2 不記通過,印出那一行、`lumos choice-kill` 指令與「放行檔與計劃要先提交」那句,治理帳多一筆 `code-loop-pass` 擋下(`blocks` 含 `choice`)與一筆 gate `choice-kill` blocked(`site` 是 pass),而且不跑任何測試 [test:t_codeloop_pass_choice]
- [S2] 當編排者照指示跑完 `choice-kill`、壞法都被殺掉、紀錄還沒提交時,`code-loop pass` 應 讀工作目錄的帳判過、照常記通過;對同一頂端跑推送前那一道(紀錄沒提交) 應 照舊擋缺紀錄 [test:t_codeloop_pass_choice]
- [S3] 當帳上有存活的壞法、沒有處置時,`code-loop pass` 應 以 rc 2 不記通過,印三種處置指令 [test:t_codeloop_pass_choice]
- [S4] 當生效日還沒到、或範圍內沒有 Kotlin 改動時,`code-loop pass` 應 照常記通過,治理帳不多 gate `choice-kill` 的事件 [test:t_codeloop_pass_choice]
- [S5] 當 ast-grep 不在 PATH 時,`code-loop pass` 應 只提醒、照常記通過 [test:t_codeloop_pass_choice]
- [S6] 當專案沒有圖譜資料夾、其他條件同 S1 時,`code-loop pass` 應 照 S1 擋下,不噴例外 [test:t_codeloop_pass_choice]
- [S7] 當放行檔有那一行的放行但還沒提交時,`code-loop pass` 應 照舊擋存活,訊息含「放行檔與計劃的改動要先提交才算」 [test:t_codeloop_pass_choice]
- [S8] 當新增告警那一道已經擋下時,`code-loop pass` 應 不跑選擇點預判(治理帳沒有新的 gate `choice-kill` 事件) [test:t_codeloop_pass_choice]
- [S9] 當同一頂端 pass 擋下一次、推送前又擋下一次、原因相同時,治理帳 應 只有一筆 gate `choice-kill` blocked;`gov --stats` 應 印「其中 pass 擋下」的筆數 [test:t_codeloop_pass_choice]
- [S10] 當目前分支就是主線(範圍算不出來)時,`code-loop pass` 應 印一行原因、照常記通過 [test:t_codeloop_pass_choice]
- [S11] 當讀手冊時,lumos-code-loop 手冊與命令速查 應 寫到 pass 會先預判選擇點、缺紀錄時先跑 choice-kill、存活要在 pass 之前處置並提交 [manual:讀 SKILL.md 第 8 步、06 命令速查的 pass 那一列]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 生效日 2000-01-01、Vm.kt 改一行有選擇點、計劃綁了測試、帳上沒紀錄 | rc 2、印 `lumos choice-kill`、`code-loop-pass` blocked 帶 choice、choice-kill blocked 帶 site pass、假 runner 的執行紀錄是空的 | 本計劃〈範圍〉③;使用者 2026-11-21 裁「pass 只預判不跑測試」 |
| S2 | S1 之後跑 `choice-kill` 判 killed、不提交,再 pass | rc 0 記通過;同一頂端跑推送前那道 → 擋缺紀錄 | 本計劃〈做法〉場合參數:帳讀工作目錄 |
| S3 | 帳上那一行 survived(已提交) | rc 2、印 `situation-rule --point`、`lint-waive choice:`、補測試三條 | 本計劃〈範圍〉③ |
| S4 | 生效日 9999-12-31 | rc 0、沒有新的 choice-kill 事件 | 本計劃〈範圍〉不改生效日規則 |
| S5 | PATH 裡沒有 ast-grep | 只提醒、rc 0 | 選擇點計劃〈用詞〉ast-grep 不在 PATH:工具壞不能擋所有人 |
| S6 | 刪掉圖譜資料夾,其他同 S1 | rc 2、沒有 Traceback | 本計劃〈做法〉不用圖譜物件 |
| S7 | survived 那一行寫了放行但沒提交 | rc 2、訊息含「要先提交才算」 | 本計劃〈做法〉場合參數:放行檔從頂端提交讀 |
| S8 | 分支帶進一條新增告警 | rc 2、擋下原因只有新增告警、沒有新的 choice-kill 事件 | 本計劃〈範圍〉①排在那兩道之後 |
| S9 | 同一頂端先 pass 擋缺紀錄、再跑推送前那道 | choice-kill blocked 只有一筆;`gov --stats` 有「其中 pass 擋下 1 筆」 | 本計劃〈做法〉事件與統計 |
| S10 | 在 main 上跑 pass | 印一行原因、rc 0 | 本計劃〈做法〉範圍:算不出來就放行 |
| S11 | 讀 SKILL.md 第 8 步 | 寫到預判、先跑 choice-kill、存活先處置並提交 | 本計劃〈範圍〉⑤ |

## 回退

- 把 `_codeloop_pass_gate` 呼叫 `_codeloop_pass_choice` 那一行拿掉,`site` 參數留著(預設值等於推送前的行為),統計那一句照留(沒有 pass 的事件就印 0);手冊還原。推送前那一道的行為沒變,回退不影響任何凍結判定。

## 實務隱患

已排除:金流:只改代碼審記通過前的檢查,不碰付款
已排除:對外送出:不連網、不寄送;pass 這道不跑測試
已排除:不可逆:擋下時不寫留痕、不改程式;只寫治理帳(簿記檔)
- 守衛面:`code-loop pass` 是代碼審留痕的寫入口,多一道會擋的檢查。擋錯的代價是 pass 記不進去、要處置或跑 choice-kill;防線:判定跟推送前那道同一支函式、同一套範圍(推送前同一頂端本來就會擋同一批),工具沒裝或算不出來只提醒,生效日前不判。
- 耗時:預判只掃語法樹與讀帳,不跑測試;掃描沿用推送前那道的時限(`_CHOICE_PICK_BUDGET` 等),這次沒另外量 pass 時的耗時。真正耗時的 choice-kill 由編排者照指示另跑,可放背景。
- 讀工作目錄的帳:pass 時工作目錄的治理帳可能有別的未提交簿記事件,判定只取 gate `choice-kill` 的列(`_gov_rows_at` 的篩選),其他不看;讀不出來的壞行由 `_gov_rows_at` 先丟掉,型別不對的列再由 `_gov_event_types_ok` 略過。
- 審過之後的修補:存活的處置(補測試、改計劃)發生在代碼審之後、pass 之前,這段改動沒有被審查席看過;這跟現在推送前被擋再處置一樣,pass 只是把時間點提前,沒有新增沒審過的路徑。
- 測試環境沒裝(Gradle、JDK):choice-kill 會判「跑不出結果」,pass 預判照擋;出路照推送前那道:修環境重跑,或 `lint-waive choice:… 不適用`。
- 併發與交易:單人依序操作,不考慮兩個程序同時寫帳。

REVISIT:2027-01-21 數上線兩個月 site 為 pass 的 choice-kill blocked 有幾筆、其中幾筆同一頂端推送前也擋了,照 RETIRE-IF 判

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 變異結果在 code review 當下呈現、合併前處理 | Practical Mutation Testing at Scale 2.3、5 | https://arxiv.org/pdf/2102.11378 |
| pass 記通過前自動跑機械檢查、擋下記 code-loop-pass blocked | 本 repo 既有做法 | [[Projects/Android寫法寫完當下自動檢查_計劃]] |
| 選擇點判定與處置規則 | 本 repo 既有做法 | [[Projects/改動選擇點都要有需求守住_計劃]] |

## 審計修正紀錄

- r1(2026-11-21,4 席:通才、正確性、邊界、架構對齊,全 sonnet):23 條/blocking 5/架構對齊席指出 pass 內跑 choice-kill 違反既有方針「跑測試的閘不掛 pass」,邊界與通才席指出最壞 20 分鐘以上、沒有圖譜資料夾會當掉、範圍跟推送前不同。使用者裁「pass 只預判不跑測試」,整份改寫:不跑 choice-kill、不建圖譜物件、範圍改用 `_choice_range`、三個參數併成一個 `site`、事件不另開抑制開關。卷證 `governance/review-reports/代碼審通過前自動跑選擇點/`
- r1 例:帳上沒紀錄 → pass rc 2、印 `lumos choice-kill`、不跑測試;跑完 killed 不提交 → pass 讀工作目錄帳判過。
