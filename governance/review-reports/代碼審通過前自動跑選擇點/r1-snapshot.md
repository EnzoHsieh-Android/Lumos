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
related:
  - "[[Projects/改動選擇點都要有需求守住_計劃]]"
  - "[[Projects/Android寫法寫完當下自動檢查_計劃]]"
---
# 代碼審通過前自動跑選擇點_計劃

## 白話

改動選擇點(Kotlin 改動行上挑壞寫法、跑計劃條款綁的測試,壞法活下來就要處置)現在只在推送前那一道機械判定;`lumos choice-kill` 要編排者自己記得在代碼審記通過之前跑。忘了跑,推送時才被擋——這時才補放行檔或改計劃,已經記好的代碼審留痕會失效,整個要重跑。這份計劃讓 `lumos code-loop pass`(代碼審最後一關)在記通過之前自動跑 `choice-kill`,判定沿用推送前那一圈,有存活又沒處置就不記通過,當場指路處置。

WHY:`code-loop pass` 記通過之前,在新增告警與表態兩道之後多一道「選擇點」:先用推送前那一圈判,有可重跑的原因就自動跑 `choice-kill`,再判一次,仍有擋下原因就不記通過 [出處:2026-11-21 使用者「確認這個 choice-kill 能不能加在代碼審最後一關 自動觸發」、回「動手」] [因:選擇點的處置(放行檔、situation-rule 改計劃、補測試)都會改非簿記檔,必須在記通過之前做(計劃 [[Projects/改動選擇點都要有需求守住_計劃]]〈實務隱患〉「跟代碼審的先後」);只靠推送前那道擋,發現時已經太晚] [不選:只在 pass 跑 choice-kill 印結果不擋(存活照樣要到推送才擋,陷阱還在);pass 時另寫一套判定(第二種做法);在 pass 自動處置存活(處置是人裁:補測試、改規格或放行要人決定)]
PRIOR-ART: Google〈Practical Mutation Testing at Scale〉把變異結果放在 code review 當下呈現,讓審查者在合併前處理,而不是事後(https://arxiv.org/pdf/2102.11378 2.3、5);本 repo `code-loop pass` 已經在記通過前自動跑新增告警與表態兩道([[Projects/Android寫法寫完當下自動檢查_計劃]] 範圍 2,`_codeloop_pass_mech`),新的一道照同形狀接在後面;判定直接重用推送前那一圈 `_choice_push_round`,只多三個帶預設值的參數(帳從哪讀、訊息前綴與範圍說明、要不要記 choice-kill 的擋下事件),預設值等於推送前的行為。
RETIRE-IF: 上線兩個月後,`code-loop pass` 因選擇點擋下的紀錄裡,過半是「沒跑完」(事件的 `choice_reasons` 裡自動跑之後仍有「缺紀錄」),或使用者回報 pass 等太久而改走 `skip`——就把這一道改成只跑不擋、時限縮短,回到推送前那道擋。

## 舊否決比對

- [[Projects/留痕驗過審查_計劃]] 否決過「pass 內重跑處置閘」(要自帶 spec 路徑、多一條判定入口)。這次不重跑處置閘;跑的是選擇點判定,而且直接呼叫推送前那一圈 `_choice_push_round`,不新增判定入口。
- [[Systems/pitfalls-code-loop]] 記新增告警與表態兩道進 pass 時,否決過「另寫一支共用判定(兩套判法會漂開)」——這次照那次的做法,重用推送前同一支。

## 範圍

- 做:①`code-loop pass` 在新增告警與表態兩道之後、留痕驗證之前多一道選擇點(`_codeloop_pass_gate` 裡,跟那兩道一樣不被「沒有審查帳」「light」提早返回跳過);②判法重用 `_choice_push_round`,只穿三個帶預設值的參數:`ledger`(預設讀被推版本已提交的帳;pass 傳 worktree,讀工作目錄那一份,因為 pass 時剛跑的 `choice-kill` 紀錄是簿記檔、還沒提交)、`label`(訊息前綴與範圍說明,預設 `[spec-gate 推送前]`/「推送範圍」)、`record`(要不要記 gate `choice-kill` 的 blocked/unverified 事件,預設記);③第一次判下來有任何擋下原因 → 自動跑 `choice-kill`(同一範圍),哪些行要跑由它自己挑,跑完再判一次;④第二次仍有擋下原因 → 不記通過,印同一段處置指示,治理帳記一筆 `code-loop-pass` 擋下;⑤手冊與筆記同步。
- 不做:不改判定規則本身(原因、回報上限、生效日、乾節點、只看 Kotlin);推送前那一道的行為不變(三個新參數用預設值);不自動處置存活;不自動提交帳;不改 standard、light 分級要不要跑 `pass`(它們不一定走到這一關,推送前那道照舊兜底);不新增略過旗標。

## 做法

- **接點**:`_codeloop_pass_gate` 裡,`_codeloop_pass_mech` 回 True 之後、`_codeloop_pass_verify` 之前,呼叫新的 `_codeloop_pass_choice(repo_root, head_sha, branch)`;回 False 時 gate 回「不放行」。
- **範圍**:`_codeloop_default_range(repo_root, head_sha, "HEAD")`(新增告警那道用的同一支)。分岔點就是 HEAD → 這一道靜默放行;算不出分岔點 → 照 `_gate_failopen` 記一筆放行帳、放行(同那道的規則)。
- **圖譜物件**:pass 原本沒有;生效日(`_choice_since()`)已過、而且範圍內有 `.kt` 改動時才建 `Env(_vault_in(repo_root))`(建一次約 4.7 秒),否則這一道直接放行。
- **判一次**:`_choice_push_round(env, rr, 範圍, push=None, ledger="worktree", label=("[code-loop pass 選擇點]", "分岔點..HEAD"), record=False)`。`ledger="worktree"` 時讀帳改用 `_gov_rows_at` 的工作目錄模式(rev=None),檔不在 = 帳不在;放行檔、守的測試、計劃照舊從 HEAD 讀。前綴與範圍說明要穿過 `_choice_push_round`、`_choice_push_scan`、`_choice_push_unverified`、`_choice_push_part_unverified`、`_choice_push_read`、`_choice_push_verdict` 這幾支。`record=False`:pass 這兩次判定都不記 gate `choice-kill` 的擋下或 unverified 事件(那是推送被擋的統計;pass 自己記 `code-loop-pass` 那筆),免得每次 pass 都在推送統計多一筆。其餘提早返回全照那一圈:生效日、要不要求、型錄缺檔只提醒、型錄表壞擋、ast-grep 不在或算不出來只提醒、無規格擋、只能人驗只提醒。
- **自動跑**:第一次判下來是空的 → 不跑,放行。有任何擋下原因 → 行程內呼叫 `cmd_choice_kill(env, diff=範圍, max_seconds=_CHOICE_PASS_SECONDS)`,`_CHOICE_PASS_SECONDS` = 600 秒。哪些行要跑由它的 `_choice_kill_pick` 決定:沒紀錄、過期、跑不出結果的一律跑;存活的只有守的測試雜湊變了才重跑(所以補強測試、提交後再 pass 會重跑);已有有效處置的跳過。它自己的前置檢查(工作目錄除簿記檔外乾淨、範圍右端是 HEAD、有計劃與可守的測試)不過就印原因回 2;它的 rc 不用,改看第二次判定。時限的語意照 choice-kill:在配方之間檢查,單支測試的基準最長另算,所以實際可能超過 600 秒。
- **判第二次**:參數同第一次。空的 → 放行,往下走留痕驗證;有 → 印擋下原因與處置指示,另加一句「處置後提交,再重跑 code-loop pass;沒跑完的行重跑 pass 會接著跑」,記 `code-loop-pass` 擋下:`blocks` 帶 `choice`,另加 `choice_reasons`(每種原因的行數)。
- **通過後**:pass 既有的「簿記檔還沒提交」提醒會列出治理帳;choice-kill 新記的紀錄要跟代碼審通過的帳本一起提交,推送前那道才讀得到。
- **中斷**:choice-kill 跑配方期間按 Ctrl-C,照它既有的規矩讓正在跑的配方跑完、記 interrupted 的 run 後正常返回,pass 接著做第二次判定(全部壞法都已判完時可能照樣放行);掃描或挑行階段按 Ctrl-C 則整個 pass 中止,不記通過。

## 驗收條款

- [S1] 當生效日已過、範圍內有 Kotlin 改動行有選擇點且碰到進行中計劃、帳上沒有紀錄時,`code-loop pass` 應 自動跑 `choice-kill`,壞法都被殺掉 → 照常記通過 [test:t_codeloop_pass_choice]
- [S2] 當自動跑之後仍有存活的壞法、沒有處置時,`code-loop pass` 應 以 rc 2 不記通過,印出那一行與三種處置指令,治理帳多一筆 `code-loop-pass` 擋下且 `blocks` 含 `choice`、`choice_reasons` 帶存活的行數 [test:t_codeloop_pass_choice]
- [S3] 當帳上那一行已有有效處置(killed 且殺它的測試仍被條款綁著、或放行檔有那一行)時,`code-loop pass` 應 不跑 `choice-kill`、照常記通過 [test:t_codeloop_pass_choice]
- [S4] 當生效日還沒到、或範圍內沒有 Kotlin 改動時,`code-loop pass` 應 不跑 `choice-kill`、照常記通過 [test:t_codeloop_pass_choice]
- [S5] 當 ast-grep 不在 PATH 時,`code-loop pass` 應 只提醒、照常記通過 [test:t_codeloop_pass_choice]
- [S6] 當帳上那一行是存活、守的測試沒變時,`code-loop pass` 應 不重跑那個壞法(治理帳沒有那一行新的判定),rc 2 並印處置指令;守的測試改過並提交後再 pass,應 重跑那一行 [test:t_codeloop_pass_choice]
- [S7] 當 `choice-kill` 在 pass 剛跑完、紀錄還沒提交時,第二次判定 應 讀得到那幾筆(讀工作目錄的帳);對同一 HEAD 跑推送前那一道 應 照舊只讀已提交的帳 [test:t_codeloop_pass_choice]
- [S8] 當新增告警那一道已經擋下時,`code-loop pass` 應 不跑選擇點那一道 [test:t_codeloop_pass_choice]
- [S9] 當 pass 判定與自動跑的過程中,治理帳 應 不多 gate `choice-kill` 的 blocked 或 unverified 事件(只多 choice-kill 自己記的判定與 run,以及擋下時那筆 `code-loop-pass`) [test:t_codeloop_pass_choice]
- [S10] 當讀手冊時,lumos-code-loop 手冊與命令速查 應 寫到 pass 會自動跑 choice-kill、存活要在 pass 之前處置、通過後帳要一起提交 [manual:讀 SKILL.md 第 8 步、06 命令速查的 pass 那一列]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 生效日 2000-01-01、Vm.kt 改一行有選擇點、計劃綁的測試會殺掉那個壞法、帳上沒紀錄 | `pass` 跑 `choice-kill`、治理帳多一筆 killed、rc 0 記通過 | 本計劃〈範圍〉③;使用者 2026-11-21「動手」 |
| S2 | 同 S1 但測試殺不掉那個壞法 | rc 2、印 `situation-rule --point`、`lint-waive choice:`、補測試三條;`code-loop-pass` blocked 帶 choice、`choice_reasons` 有存活 1 行 | 本計劃〈範圍〉④ |
| S3 | 帳上那一行已 killed(已提交) | 治理帳沒有新的 choice-kill run、rc 0 | 本計劃〈做法〉自動跑:第一次判空的不跑 |
| S4 | 生效日 9999-12-31 | 不跑、rc 0 | 本計劃〈範圍〉不改生效日規則 |
| S5 | PATH 裡沒有 ast-grep | 只提醒、rc 0 | 選擇點計劃〈用詞〉ast-grep 不在 PATH:工具壞不能擋所有人 |
| S6 | 帳上那一行 survived(已提交)、守的測試沒變;再把測試補強提交 | 第一次 rc 2、沒有那一行新的判定;補強後 rc 0、那一行多一筆 killed | 本計劃〈做法〉自動跑:存活只在測試雜湊變了才重跑 |
| S7 | pass 自動跑完 killed、沒提交,直接再判 | 判過;對同一 HEAD 跑推送前那一道 → 擋缺紀錄 | 本計劃〈做法〉判一次:帳讀工作目錄 |
| S8 | 分支帶進一條新增告警 | rc 2、擋下原因只有新增告警、治理帳沒有新的 choice-kill run | 本計劃〈範圍〉①排在那兩道之後 |
| S9 | S1 與 S2 兩種情況 | 治理帳不多 gate choice-kill 的 blocked/unverified 事件 | 本計劃〈做法〉判一次:record=False |
| S10 | 讀 SKILL.md 第 8 步 | 寫到 pass 自動跑 choice-kill、存活要先處置、帳一起提交 | 本計劃〈範圍〉⑤ |

## 回退

- 把 `_codeloop_pass_gate` 呼叫 `_codeloop_pass_choice` 那一行拿掉,`_choice_push_round` 一族的三個新參數留著(預設值等於推送前的行為);手冊還原。推送前那一道的行為沒變,回退不影響任何凍結判定。

## 實務隱患

已排除:金流:只改代碼審記通過前的檢查,不碰付款
已排除:對外送出:lumos 本身不連網、不寄送;choice-kill 跑的 Gradle 冷編譯可能下載相依套件,是既有行為,這次不新增
已排除:不可逆:擋下時不寫留痕、不改程式;choice-kill 只寫治理帳(簿記檔),在隔離工作樹套壞法
- 守衛面:`code-loop pass` 是代碼審留痕的寫入口,多一道會擋的檢查。擋錯的代價是 pass 記不進去、要處置或重跑;防線:判定跟推送前那道同一支函式(推送前本來就會擋同一批),工具沒裝或算不出來只提醒,生效日前不跑。
- 耗時:`choice-kill` 實測 Gradle 熱時 1 個壞法約 17.5 秒([[Verification/2026-11-15_改動選擇點真實Android端到端驗收]]);一次最多 30 個壞法。pass 時限 600 秒(配方之間檢查,單支測試基準另算),沒跑完的行照「缺紀錄」擋,重跑 pass 會接著跑(未判完的壞法不記帳,下次照沒紀錄挑)。冷編譯耗時還沒量。
- 中斷:見〈做法〉中斷;choice-kill 自己的中斷規矩見選擇點計劃 S12。
- 讀工作目錄的帳:pass 時工作目錄的治理帳可能有別的未提交簿記事件,判定只取 gate `choice-kill` 的列(`_gov_rows_at` 的篩選),其他不看;讀不出來的壞行由 `_gov_rows_at` 先丟掉,型別不對的列再由 `_gov_event_types_ok` 略過。
- 併發與交易:單人依序操作,不考慮兩個程序同時寫帳。

REVISIT:2027-01-21 數上線兩個月 `code-loop-pass` 帶 choice 的擋下有幾筆、其中幾筆是沒跑完,照 RETIRE-IF 判

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 變異結果在 code review 當下呈現、合併前處理 | Practical Mutation Testing at Scale 2.3、5 | https://arxiv.org/pdf/2102.11378 |
| pass 記通過前自動跑機械檢查、擋下記 code-loop-pass blocked | 本 repo 既有做法 | [[Projects/Android寫法寫完當下自動檢查_計劃]] |
| 選擇點判定與處置規則 | 本 repo 既有做法 | [[Projects/改動選擇點都要有需求守住_計劃]] |

## 審計修正紀錄
