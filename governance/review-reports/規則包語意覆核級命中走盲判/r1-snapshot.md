---
type: project
status: todo
created: 2026-11-05
updated: 2026-11-05
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
related:
  - "[[Projects/Android寫法語意情境表態與盲判_計劃]]"
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Systems/kotlin規則包]]"
  - "[[Systems/pitfalls-code-loop]]"
lands_in:
  - Systems/pitfalls-code-loop
  - Systems/kotlin規則包
  - Systems/linter精選目錄
pending_questions:
  - id: Q1
    text: 盲判判成真問題的覆核命中要不要擋推送?建議:要擋,跟新增告警同一句擋下與同一個放行出口;出處不全的 7 條例外,只提醒
    class: 擋停策略
    stage: 架構
    status: 已決
    blocking: true
    decision: "#d1"
  - id: Q2
    text: 有覆核命中卻還沒盲判時要不要擋推送?建議:要擋並印跑盲判的指令,跟情境題缺盲判同一條規則;代價是每次有命中都要派一個代理
    class: 擋停策略
    stage: 架構
    status: 已決
    blocking: true
    decision: "#d2"
  - id: Q3
    text: 盲判判成誤報的命中自動記一筆 AI 放行、進既有的人工複查清單(doctor 會數還沒人看過的),可以嗎?建議:可以,照 Semgrep 判誤報不直接消失的做法,沿用既有清單不另起一套
    class: 範圍
    stage: 架構
    status: 已決
    blocking: true
    decision: "#d3"
decisions:
  - content: Q1:盲判判成真問題的覆核命中擋推送,擋下訊息與放行出口跟新增告警相同;出處不全的 7 條判成真只提醒
    id: d1
    context: 覆核命中原本不擋也沒人看
    why_chosen: 使用者 2026-11-07 原話「照建議」;依據不足的規則不准擋人,跟型錄自檢出處不全只准提示級同一條線
    decided: 2026-11-07
    valid: true
  - content: Q2:有覆核命中卻還沒盲判時擋推送,印跑盲判的指令
    id: d2
    context: 盲判要派代理,有成本
    why_chosen: 使用者 2026-11-07 原話「照建議」;跟情境題缺盲判同一條規則,不擋等於沒判
    decided: 2026-11-07
    valid: true
  - content: Q3:判成誤報的覆核命中自動記一筆 origin ai 的放行,進既有 AI 放行複查清單,直到人 ack
    id: d3
    context: 判成誤報的不能直接消失
    why_chosen: 使用者 2026-11-07 原話「照建議」;照 Semgrep 判誤報藏起來集中給人複查的做法,沿用既有清單不另起一套
    decided: 2026-11-07
    valid: true
---

# 規則包語意覆核級命中走盲判_計劃

> 白話:Kotlin 規則包有一類規則,形狀抓得到可疑寫法、卻分不出它是不是真的錯(要知道型別或語意,例:`.setValue` 是 LiveData 還是 Firebase、`.value.add` 是狀態容器還是 Map.Entry)。這類規則放在第三級「語意覆核級」(`rules-review/`,ast-grep 的 info 等級),不擋、也不降成容易被忽略的提示級;這份計劃讓它們的每個新增命中由沒看過作者說法的代理逐筆判「真問題 / 誤報」,判定留痕、可複查、統計準確率。2026-11-07 使用者裁定範圍擴大到提示級(`rules-hints/`)50 條一起處理:兩級共 62 條,現在既不擋、也不量、也沒人看。使用者原話(2026-11-07):「62 條一起處理，先建語意覆核接盲判的計劃」。使用者原話(2026-11-05):「如果形狀都改不好,是不是可以參語意判斷?會不會比 hint 靠譜一點,因為 hint 感覺是會被忽略的東西,或你上網查看看大家是怎麼做的」。從 [[Projects/Android寫法語意情境表態與盲判_計劃]] 範圍 8 拆出(那份設計審 r2 對範圍 8 報 blocker,累計折入已過熔斷門檻)。

PRIOR-ART: Semgrep 在固定規則上疊模型判誤報:只在有把握時判;判成誤報的不自動關,而是藏起來集中給人批次複查;準確率底線九成(https://semgrep.dev/blog/2025/announcing-ai-noise-filtering-and-triage-memories )。學術上 ZeroFalse(https://arxiv.org/html/2510.02534v1 )、Wagner 等(https://arxiv.org/abs/2506.16899v1 )讓模型裁判靜態分析結果。採用「規則抓寬、模型逐筆判、判成誤報的進複查清單不直接消失」;不採「模型判完自動放行且沒人看」。r2 通才席指出原範圍 8 引用了這個做法卻讓誤報判定直接放行,跟引用的做法相反。
RETIRE-IF: 上線八週後:某條語意覆核級規則經人複查的判定準確率低於九成 → 那條規則的命中改回人判;整級八週內新增命中少於 5 筆 → 撤掉這一級,規則降提示級。

## 狀態

設計初稿(2026-11-07 改寫),還沒過規格閘。母計劃設計審 r2 帶過來的七個問題逐條解在〈範圍〉,對照表在〈審計修正紀錄〉。

## 用詞

- **覆核命令**:`.lumos/lint.json` 新的 `review` 段裡宣告的檢查命令(本案是規則包的 `sgconfig-review.yml` 與 `sgconfig-hints.yml` 兩條);它的新增命中不直接擋,交盲判。
- **覆核命中**:覆核命令在這次改動新帶進來的命中。身分(材料與紀錄裡的 `seg`)就是新增告警閘的放行指紋:`_lint_new_key` 的 (規則, 檔名, 命中行片段) 取 sha256 前 16 碼,跟 `lumos lint-waive` 認的鍵同一個字串。同檔同片段的多處共用同一個身分與同一個判定。
- **規則判定**:盲判代理對一筆覆核命中判的 `real`(真問題)、`false`(誤報)或 `unsure`(判不準),附一句理由(去空白後至少 10 字、有實字,跟 `lint-waive` 理由同一條門檻)。跟情境題的「照做判定」(`applies/followed`)是兩種東西,材料分份、紀錄分欄。
- **對應型錄列**:規則訊息開頭方括號裡的型錄編號(例 `[STATE-16]`)指到的主型錄表那一列;本案前提是一條規則只對一列(2026-11-07 用程式核對:62 條各唯一對到一列)。
- **出處不全規則**:對應型錄列的名稱標了「出處不全」的規則(提示級 7 條,語意覆核級 0 條)。
- **人複查**:人用 `lumos lint-waive --ack <鍵> --verdict agree|overturn`(本案新增的旗標;值的用詞照 `canary second` 既有的同意/推翻)確認一筆 AI 放行時,同時註記同不同意盲判;不帶 `--verdict` 的 ack 照舊只記看過、不進準確率。

## 範圍

### 做

1. **分流**(解問題 1):`.lumos/lint.json` 加選填的 `review` 段,值是「副檔名 → 命令清單」(`{"review": {"kt": ["…"]}}`);`_lintcheck_validate` 對 `review` 特判、逐條照既有命令規則驗。其他讀 lint.json 的地方(detekt 提醒、`--smoke`、Android CI 提醒)一律跳過 `review` 鍵,不把它當副檔名。不採「看命令裡 `--config` 指向哪個檔名」:那是字面判斷,改個檔名就分錯流。
2. **核對放在新增告警閘那一道**(解問題 2):分流點在 `_lint_new_tools` 組命令清單那一層——一般段照舊組 `cmd_targets`;`review` 段另組一份,在一般段跑完之後用剩下的時間預算跑,呼叫同一支 `_lint_new_run_cmds`,但結果放進另一份 `out`,再各自呼叫 `_lint_new_diff_claims` 算新增命中。覆核命中放在判定結果的 `review_new`,`_lint_new_classify` 的「有新增就擋」只看一般段。覆核命令沒跑到(預算用完、工具沒裝、逾時)記進 `review_undone`,只講出來、不擋(見範圍 6)。工作樹模式(`worktree=True`,收工鉤子與 `lint-new --worktree` 走的那條)明確不跑 `review` 段。不放在表態那一道:那一道在沒有適用題時提早返回。
3. **身分與放行用同一把鑰匙**(解問題 3):覆核命中的身分就是新增告警閘的放行指紋(見〈用詞〉),不另加序號;同檔同片段的多處共用一個判定,材料取檔內最後一處(複製貼上時新加的通常在後面),材料裡寫明「同片段另有 N 處」。放行沿用 `lumos lint-waive <指紋>`。
4. **判定材料與記帳**(解問題 5):
   - 材料:`lumos code-loop blind-judge --template` 多印一份 `rule_hits`(跟情境段分份印、各派一席,不同時給一個代理)。資料來源是 `--template` 當下用同一個改動範圍重跑覆核命令(呼叫範圍 2 那支,不從上一次 check 取),每筆給檔名、命中行前後各 8 行、規則訊息,以及對應型錄列的「壞寫法形狀、標準寫法、後果、情境怎麼認」四欄;不給任何作者說法。每份最多 30 筆,沿用 `--part`。
   - 讀型錄主表:lumos 照讀決策表的做法,用 importlib 借 `configs/ast-grep/kotlin-android/check.py` 的 `main_rows`(主表的唯一讀法),不自己再寫一套表格解析。
   - 結果檔:頂層多一個鍵 `rule_hits: [{"seg": <指紋>, "verdict": "real|false|unsure", "reason": "…"}]`,可以跟 `segments` 同檔或單獨一份;`_kt_bj_validate` 擴充認這個鍵,同一格已有判定不再收(沿用既有「同一格只認第一筆」)。
   - 治理帳:同一個 `code-loop` 閘、種類 `blind-judge`,判定放在新欄 `rule_hits`(不放進舊的 `blind_judge` 欄),舊版讀帳看不到這欄就略過整筆的這一部分,不會被誤讀成情境票。
5. **判定怎麼用**(解問題 4;使用者裁定 d1、d2、d3):
   - `real`:擋,跟新增告警同一句擋下與同一個放行出口;出處不全規則判 `real` 只提醒不擋(d1)。
   - `false`:不擋。記帳那一步(`lumos code-loop blind-judge <結果檔>`)替它寫一筆放行:origin 是 ai、理由是「盲判判誤報:<判定理由>」,進既有「AI 放行還沒人看過」的複查清單,直到人 ack(d3)。判定函式本身照舊不寫任何檔。
   - `unsure`:交第二個代理仲裁:`--template --unsure`(本案新增)只印第一判是 `unsure` 的那幾筆,結果用 `--arbiter` 記;仲裁判 `real` 擋、判 `false` 照上一條、仍 `unsure` 只提醒並記帳。
   - 還沒判:擋,印跑盲判的指令(d2)。
6. **沒宣告、環境不可用講出來**(解問題 6):沒有 `review` 段、覆核命令跑不出結果時,推送前印一行「覆核沒跑:<沒宣告|工具不可用|時間預算用完>」,跟「覆核過、沒有新增命中」分開;doctor 對宣告了 kt、卻沒有 `review` 段的專案提醒一行。
7. **統計與升降建議**(解問題 7):`lumos gov --stats` 多一段「覆核規則」,每條規則列:判定幾筆、`real`/`false`/`unsure` 各幾筆;`false` 判定被人複查幾筆、其中 `--verdict overturn` 幾筆;`real` 判定被人用 `lint-waive`(origin 是 human)放行幾筆。只出建議、不自動改:`real` 判定至少 20 筆、被人放行少於一成 → 建議移到 `rules/`(直接擋、不再要盲判);`false` 判定經人複查至少 20 筆、`--verdict agree` 至少九成、而且 `false` 佔該規則判定八成以上 → 建議刪掉或改形狀。這些門檻是本案自訂:一成取 Google 有效誤報的經驗數字,20 筆取情境題升擋同一個樣本下限;七成、八成是本案自己的數字,上線後照 REVISIT 回頭校準。
8. **範本**:[[Systems/linter精選目錄]] 的 Kotlin 規則包範本加 `review` 段兩條命令;那裡「提示級規則預設不接」那一句改成「接在 review 段、命中交盲判」。

### 不做

- 不在收工鉤子(回合結束檢查)跑覆核命令:收工那一道要秒級、不派代理(範圍 2 寫明、S9 釘住)。
- 不自動升降規則等級:只出建議,改等級要改規則檔、過代碼審。
- 不替出處不全的 7 條補出處:那是型錄逐列查證的工作(另一條線)。
- 不讓同一個代理同時判覆核命中與情境段:兩種材料分份印,各派一席。

## 實務隱患

- **盲判成本**:每次推送有覆核命中就要派代理。上線前用兩個真專案(實驗專案、nowinandroid)整份跑一次 `sgconfig-review.yml` 與 `sgconfig-hints.yml`,量命中筆數(2026-11-05 的真專案實測只跑了會擋的 `sgconfig.yml`,這兩份還沒量);命中多時材料分份(每份 30 筆)。
- **同家族偏誤**:盲判跟寫程式的是同一家模型;準確率只算人複查過的那部分(範圍 7),RETIRE-IF 照人複查的數字。
- **誤報清單沒人看**:本 repo 的 AI 放行清單 2026-11-07 有 62 筆沒人看過(`.lumos/lint-waivers.json` 數 origin 是 ai、沒 ack 的);多了覆核誤報會更長。REVISIT 看清單有沒有人消化。
- **AI 自己放行真問題**:判 `real` 被擋時,AI 跑 `lint-waive` 也能放行(沒有互動終端記成 origin ai),跟新增告警閘現在的語意一樣;它會進 AI 放行複查清單,統計把它算成「被放行」而不是「人放行」。
- **時間預算**:覆核命令吃一般段剩下的預算;一般段吃光時覆核記成「沒跑」不擋,所以專案很大時覆核可能常常沒跑。推送前那一行會講,doctor 不另唸。
- 已排除:金流:不碰付款
- 已排除:對外送出:只讀本機檔與跑本機 ast-grep,不連網
- 已排除:不可逆:新增一段設定、一份材料與一個帳欄,退提交即回原狀(已寫進治理帳與放行檔的紀錄留著,不影響其他判定)
- 守衛面:不排除——新增告警閘多一條會擋的路徑(判 `real` 與還沒判),動的是守衛面;判風險高,走完整設計審

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 規則抓寬、模型逐筆判、判成誤報的不直接消失 | Semgrep 在固定規則上疊模型判誤報,判成誤報的不自動關、藏起來集中給人複查 | https://semgrep.dev/blog/2025/announcing-ai-noise-filtering-and-triage-memories |
| 模型判靜態分析命中的準確度量得到 | ZeroFalse 讓模型裁判靜態分析結果並量誤報過濾率 | https://arxiv.org/html/2510.02534v1 |
| 同上(第二個來源) | Wagner 等以模型過濾靜態分析告警 | https://arxiv.org/abs/2506.16899v1 |
| 誤報門檻一成、沒人採取行動的告警就是噪音 | Google 靜態分析經驗:有效誤報的定義與門檻 | https://cacm.acm.org/magazines/2018/4/226371-lessons-from-building-static-analysis-tools-at-google/pdf |
| 只看這次新帶進來的命中 | SonarQube Clean as You Code:品質閘只看新程式 | https://docs.sonarsource.com/sonarcloud/improving/clean-as-you-code |
| 兩級 62 條一起處理 | 使用者裁定 | 使用者 2026-11-07:「62 條一起處理，先建語意覆核接盲判的計劃」 |
| 擋停與誤報去向三題照建議 | 使用者裁定 | 使用者 2026-11-07:「照建議」 |
| 不降成提示級、要語意判斷 | 使用者提問 | 使用者 2026-11-05:「如果形狀都改不好,是不是可以參語意判斷?會不會比 hint 靠譜一點」 |
| 樣本下限 20 筆 | 情境題升擋門檻已在表態閘筆記立為回頭條件 | `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md` |

## 驗收條款

- [S1] 當 `.lumos/lint.json` 有 `review` 段時,`_lintcheck_validate` 應 逐條照既有命令規則驗它,形狀不對 應 報錯;沒有 `review` 段 應 照舊通過;detekt 提醒與 `--smoke` 應 不把 `review` 當副檔名 [test:t_rule_review_lint_json_review_key]
- [S2] 當 `review` 段命令在這次改動有新增命中、而且還沒有規則判定時,`lumos code-loop check` 應 擋並印跑盲判的指令;同一筆命中在一般段時 應 照舊直接擋 [test:t_rule_review_missing_judgment_blocks]
- [S3] 當一筆覆核命中判 `real` 時,規則判定 應 擋,用 `lint-waive` 放行後 應 放行;規則是出處不全時 應 只提醒不擋 [test:t_rule_review_real_blocks_waivable]
- [S4] 當一筆覆核命中判 `false` 時,記帳 應 在 `lint-waivers.json` 多一筆 origin 是 ai、理由以「盲判判誤報:」開頭的放行,推送 應 不擋,doctor 應 把它算進還沒人看過的 AI 放行;判定函式 應 不寫放行檔 [test:t_rule_review_false_to_ack_queue]
- [S5] 當一筆覆核命中判 `unsure` 時,`--template --unsure` 應 只印那幾筆;仲裁判 `real` 應 擋、判 `false` 應 照 S4、仍 `unsure` 應 只提醒 [test:t_rule_review_unsure_arbiter]
- [S6] 當 `blind-judge --template` 印覆核命中材料時,每筆 應 含檔名、前後 8 行、規則訊息與對應型錄列的四欄,應 不含任何表態內容;同檔同片段兩處時 應 只印最後一處並寫明另有幾處 [test:t_rule_review_template_material]
- [S7] 當沒有 `review` 段、覆核命令跑不出結果、或時間預算用完時,推送前 應 印「覆核沒跑」與原因,應 不印「沒有新增命中」,應 不擋 [test:t_rule_review_not_run_distinct]
- [S8] 當治理帳有規則判定、放行檔有帶 `--verdict` 的人複查時,`lumos gov --stats` 應 逐條規則列筆數與複查結果;符合門檻 應 印升級或刪除建議;不足 20 筆 應 不印建議 [test:t_rule_review_stats_suggestion]
- [S9] 當收工鉤子或 `lint-new --worktree` 跑工作樹模式時,`review` 段命令 應 不被執行 [test:t_rule_review_skipped_in_worktree]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `{"kt": ["…"], "review": {"kt": ["ast-grep scan --config …/sgconfig-review.yml …"]}}` | 驗過 | 本計劃範圍 1 |
| S1 | `{"review": "ast-grep …"}`(不是物件) | 報錯 | 本計劃範圍 1 |
| S1 | 有 review 段時跑 lint-check --smoke | 不把 review 當副檔名、不報「沒有這種檔」 | 範圍 1 |
| S2 | review 命令新增 1 筆命中、沒有判定 | 擋,印 blind-judge --template 指令 | 範圍 5「還沒判」;d2 |
| S2 | 同一條規則宣告在一般段、新增 1 筆 | 直接擋(不要盲判) | 範圍 1 |
| S3 | 判 real、對應型錄列沒有出處不全 | 擋 | 範圍 5;d1 |
| S3 | 判 real、對應列標出處不全 | 只提醒 | 範圍 5;d1;型錄自檢出處不全只准提示級 |
| S3 | 判 real 之後 lint-waive 那個指紋 | 放行 | 範圍 3 |
| S4 | 判 false 並記帳 | 不擋;放行檔多一筆 origin ai、理由以「盲判判誤報:」開頭 | 範圍 5;d3;Semgrep 判誤報不直接消失 |
| S4 | 只跑 code-loop check(沒記帳) | 放行檔不變 | 範圍 5「判定函式不寫檔」 |
| S5 | 判 unsure、仲裁判 false | 照 S4 | 範圍 5 |
| S5 | 判 unsure、仲裁仍 unsure | 只提醒 | 範圍 5 |
| S6 | 同檔兩處相同片段 | 材料只有最後一處,寫「同片段另有 1 處」 | 範圍 3 |
| S7 | lint.json 沒有 review 段 | 印覆核沒跑:沒宣告;不擋 | 範圍 6 |
| S7 | ast-grep 沒裝 | 印覆核沒跑:工具不可用;不擋 | 範圍 6 |
| S7 | 一般段吃光時間預算 | 印覆核沒跑:時間預算用完;不擋 | 範圍 2、6 |
| S8 | 某規則 real 判定 20 筆、被人放行 1 筆 | 印建議移到 rules/ | 範圍 7 |
| S8 | 某規則 false 判定人複查 20 筆、agree 19 筆、false 佔 85% | 印建議刪掉或改形狀 | 範圍 7 |
| S8 | 某規則判定 19 筆 | 不印建議 | 範圍 7 |
| S9 | 收工鉤子跑工作樹模式、lint.json 有 review 段 | 覆核命令沒被執行 | 範圍 2;不做 1 |

## 回退

退回本計劃的提交時,驗證器要留著「認得 `review` 鍵、略過不跑」那一行(否則已照範本加了 `review` 段的消費專案,`lint-check` 會因為不認得的鍵報錯);其餘照退:覆核命令不再跑、`blind-judge --template` 的覆核命中份拿掉;治理帳已寫的 `rule_hits` 欄留著,舊版讀帳不讀這欄、不影響其他判定;放行檔裡 origin ai 的覆核誤報放行留著(它們本來就是合法放行)。

## 天花板

1. 放行一處等於放行同檔同片段的每一處(沿用新增告警閘的指紋語意);同片段多處共用一個判定。
2. 盲判與作者同一家模型;準確率只有人複查過的那部分算數,沒人複查就沒有數字。
3. 覆核只在推送前跑;收工時與寫的當下不跑;時間預算用完時這次不跑。
4. 出處不全的 7 條判成真也不擋,要等型錄逐列查證補上出處。
5. 判 `real` 被擋時 AI 也能自己 `lint-waive` 放行,只留下 AI 放行待看紀錄。

REVISIT:2026-12-07 看規則判定上線一個月:總共幾筆覆核命中、盲判花了多少、AI 放行清單有沒有人消化、有沒有人用 `--verdict` 複查;清單沒人看就改成判誤報也要人當下確認

## 審計修正紀錄

- 2026-11-07 改寫:母計劃設計審 r2 帶來的七個問題逐條解進〈範圍〉1–7;範圍擴大到提示級 50 條(使用者裁定)。
- 2026-11-07 舊否決比對(lumos rejections 512 行,按概念篩):「AI 放行一律擋」「AI 放行累積幾筆就擋」被否決過(Systems/test-guard、Projects/Android端到端驗收_計劃)——本案判誤報記成 AI 放行、只讓它事後可見不擋,跟那兩次裁定一致;「多數判作者沒照做就擋」被否決過(Systems/棧別提問表態閘)——規則命中沒有作者表態,不適用;「LLM 判可逆性」被否決過(Systems/doctor-irreversible-hint#d1,選字面掃描加軟提醒)——本案是模型判規則命中真假、不是判可逆性,而且情境題盲判已審過上線,概念相近處交設計審判。
