---
type: project
status: todo
created: 2026-11-05
updated: 2026-11-07
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
  - Systems/lint-declaration-health
  - Systems/棧別提問表態閘
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
    decision: "#d4"
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
    valid: false
    superseded_by: "#d4"
    ended: 2026-11-07
  - content: Q3 改裁:盲判判成誤報的覆核命中不寫放行,只記在治理帳;推送時那筆不擋,另列「AI 判誤報待人看」清單;人推翻(單筆或整批)就恢復成要擋
    id: d4
    context: 設計審 r1 六席中五席獨立點出原做法(判誤報自動寫成 AI 放行)撤不回、推翻無效、兩處寫一半、會被偽造身分利用
    why_chosen: 使用者 2026-11-07 原話「照建議」;照 Semgrep AI 判誤報不自動關、藏起來集中給人複查、人不同意就重新打開的做法;真相只留治理帳一處
    decided: 2026-11-07
    valid: true
---

# 規則包語意覆核級命中走盲判_計劃

> 白話:Kotlin 規則包有一類規則,形狀抓得到可疑寫法、卻分不出它是不是真的錯(要知道型別或語意,例:`.setValue` 是 LiveData 還是 Firebase、`.value.add` 是狀態容器還是 Map.Entry)。這類規則放在第三級「語意覆核級」(`rules-review/`,ast-grep 的 info 等級),不擋、也不降成容易被忽略的提示級;這份計劃讓它們的每個新增命中由沒看過作者說法的代理逐筆判「真問題 / 誤報」,判定留痕、可複查、統計準確率。2026-11-07 使用者裁定範圍擴大到提示級(`rules-hints/`)50 條一起處理:兩級共 62 條,現在既不擋、也不量、也沒人看。使用者原話(2026-11-07):「62 條一起處理，先建語意覆核接盲判的計劃」。使用者原話(2026-11-05):「如果形狀都改不好,是不是可以參語意判斷?會不會比 hint 靠譜一點,因為 hint 感覺是會被忽略的東西,或你上網查看看大家是怎麼做的」。從 [[Projects/Android寫法語意情境表態與盲判_計劃]] 範圍 8 拆出(那份設計審 r2 對範圍 8 報 blocker,累計折入已過熔斷門檻)。

PRIOR-ART: Semgrep 在固定規則上疊模型判誤報:只在有把握時判;判成誤報的不自動關,而是藏起來集中給人批次複查;準確率底線九成(https://semgrep.dev/blog/2025/announcing-ai-noise-filtering-and-triage-memories )。學術上 ZeroFalse(https://arxiv.org/html/2510.02534v1 )、Wagner 等(https://arxiv.org/abs/2506.16899v1 )讓模型裁判靜態分析結果。採用「規則抓寬、模型逐筆判、判成誤報的進複查清單不直接消失」;不採「模型判完自動放行且沒人看」。r2 通才席指出原範圍 8 引用了這個做法卻讓誤報判定直接放行,跟引用的做法相反。
RETIRE-IF: 上線八週後:某條語意覆核級規則經人複查的判定準確率低於九成 → 那條規則的命中改回人判;整級八週內新增命中少於 5 筆 → 撤掉這一級,規則降提示級。

## 狀態

設計第二版(2026-11-07,折入設計審 r1 六席),還沒過第二輪。

## 用詞

- **覆核宣告**:`.lumos/lint-review.json`(本案新增的檔,格式跟 `.lumos/lint.json` 一樣是「副檔名 → 命令清單」),宣告覆核命令;本案範本宣告規則包的 `sgconfig-review.yml` 與 `sgconfig-hints.yml` 兩條。不放進 `.lumos/lint.json`:那個檔的每個頂層鍵都被當副檔名嚴格驗,依賴層(`.lumos/lint-deps.json`)與 lint-watch 已兩次為同一理由另開檔。
- **覆核命中**:覆核命令在這次改動新帶進來的命中。身分(`seg`)是新增告警閘的指紋:`_lint_new_key` 的(規則, 檔名, 命中行片段)取 sha256 前 16 碼。同檔同片段的多處共用一個身分;判定記下「判定當時這個身分在這支檔有幾處」,之後處數變多就要重判。
- **規則判定**:盲判代理對一筆覆核命中判的 `real`(真問題)、`false`(誤報)或 `unsure`(判不準),附一句理由(去空白後至少 10 字、有實字)。跟情境題的照做判定(`applies/followed`)是兩種東西,材料分份、帳欄分開。
- **對應型錄列**:規則訊息開頭方括號裡的型錄編號(例 `[STATE-16]`)指到的主型錄表那一列。一條規則只對一列(2026-11-07 用程式核對 62 條成立);一列可對多條規則(STATE-7 有 3 條)。
- **出處不全規則**:對應型錄列名稱標「出處不全」的規則(提示級 7 條、語意覆核級 0 條)。
- **待人看清單**:治理帳裡判成 `false`、還沒有人複查的覆核命中。
- **人複查**:人用 `lumos code-loop rule-review`(本案新增的子指令)對一筆(給指紋)或一整次記帳(給那次記帳的 token)表態 `agree`(同意)或 `overturn`(推翻),值的用詞照 `canary second` 既有的同意/推翻;寫一筆治理帳事件,不碰放行檔。

## 範圍

### 做

1. **覆核宣告另開檔**(解 r1 架構對齊 1、正確性 1、整合 F1、回滾 F4):`.lumos/lint-review.json`,讀法照 `_lint_deps_load` 那套(另一支讀檔函式、另一份驗證);驗證要求每條命令帶 `{LINT_FILES}` 或 `{LINT_FILES_CSV}`(沒有佔位符的覆核命令直接報錯,不降成只報不擋)。`.lumos/lint.json` 與它的驗證器、detekt 提醒、`--smoke` 都不動。`lint-check --smoke` 另加一段對覆核宣告冒煙。
2. **算覆核命中只有一支共用函式**(解 r1 資源 F1、整合 F6、架構對齊 3):新增 `_rule_review_hits(repo_root, diff_range, deadline)`,回(新增命中清單, 沒跑原因清單)。推送前檢查、`blind-judge --template`、`blind-judge <結果檔>` 記帳三處都呼叫它,範圍一律用 `_codeloop_disp_range`(表態與情境題盲判共用的那一支),三處算出同一組身分。內部照新增告警閘的做法抽兩份快照、跑命令、比對新增,覆核命令不套 `lint_new.include_test_paths` 的測試路徑過濾(規則包的覆核與提示規則自己用 `files:` 限定範圍;解 r1 正確性「測試目錄 8 條永遠不響」)。它不讀治理帳、不寫任何檔。
3. **擋停放在代碼審那一層**(解 r1 架構對齊 2、資源 F2、整合 F5):`_lint_new_verdict` 與 `_lint_new_classify` 完全不動。`_codeloop_lint_new_step` 在一般段之後另跑一段覆核:呼叫範圍 2 那支拿命中,讀治理帳的規則判定(分支、版本、合併提交那一側照表態那一道 `_disp_bj_source` 的讀法),逐筆判擋不擋。這一段自己接住例外(解 r1 資源 F3、正確性 2):出例外時只把覆核記成「算不出來」並寫一筆 fail-open 事件,一般段的判定照舊。新增告警閘的 `mode`(`warn` 降成提醒、`off` 整道不跑)與 `LUMOS_SKIP_LINT_NEW` 一體適用於覆核。一般段沒有要跑的命令(`no-files` 早退)時覆核照跑。`code-loop pass` 的記通過前機械檢查跟推送前同一支,覆核擋也會擋 pass。
4. **材料**(解 r1 資源 F7、邊界 5、整合 F6、正確性「template 介面」、架構對齊 4、5):
   - `lumos code-loop blind-judge --template --rule-hits`(本案新增旗標)印覆核命中那一份;不帶 `--rule-hits` 照舊只印情境段。兩種材料各自分份、各自 `--part` 編號(每份最多 30 筆),stdout 一次只有一份 JSON。
   - 每筆給:檔名、這支檔裡同一片段的**每一處**命中行前後各 8 行(多行命中以起點為準,檔頭檔尾不足 8 行就給到邊界為止)、規則訊息、對應型錄列的「壞寫法形狀、標準寫法、後果、情境怎麼認」四欄;不給任何作者說法。
   - 選哪些:模式沿用 `cl_bj_mode` 那組互斥選項,多一個 `--unsure`(只印第一判是 `unsure`、還沒仲裁的筆),跟 `--missing`、`--disagreements` 互斥;`--unsure` 的結果用 `--arbiter` 記,角色判斷照既有 `mode == "disagreements"` 那條改成「mode 是 disagreements 或 unsure」。
   - 讀型錄主表:沿用載入 check.py 的那一支(`_load_hook_file`,`required` 從 `("dt_table",)` 擴成 `("dt_table", "main_rows")`),不另開載入。型錄讀不到時:材料四欄寫「型錄讀不到」、出處不全一律當「不是出處不全」(會擋,寧多擋不漏)。規則訊息沒有型錄編號或編號對不到列時同樣處理。
   - 型錄自檢(`check.py` 的 `catalog_problems`)多驗一條:覆核與提示規則訊息開頭的型錄編號要在主表存在、而且主表那個編號只有一列(解 r1 架構對齊 5:「一條規則只對一列」原本只靠一次性核對)。
   - `blind-judge --rule-hits` 這條路不需要情境型錄與情境段算得出來(情境側的 `_KT_DT_ERR` 與段算不出來只擋情境那條路)。
5. **結果檔與記帳**(解 r1 正確性「seg 沒對照當次命中」、邊界 5、資源 F5、回滾 F3、整合 F2):
   - 結果檔頂層可以只有 `rule_hits: [{"seg", "verdict", "reason"}]`,也可以跟 `segments` 同檔;`_kt_bj_validate` 改成兩個鍵至少一個非空,`rule_hits` 的每個 `seg` 要在範圍 2 那支當下算出的新增命中裡,不在就整份拒收(擋偽造與抄錯)。
   - 治理帳:同一個 `code-loop` 閘、種類 `blind-judge`,新欄 `rule_hits: [{"seg", "rule", "file", "occurrences", "verdict", "reason"}]`(rule 是規則 id、occurrences 是判定當時同片段處數),另帶這次記帳的 `token`。只寫治理帳一處,不碰放行檔。`rule_hits` 登記進 `_GOV_FIELD_TYPES`、`_gov_row` 帶出;讀端逐筆驗形狀,不合的那筆略過並印一行,不丟例外。
   - 同一格只認第一筆(照既有);`overturn` 讓那一筆作廢後,同一格可以再判(見範圍 6)。
6. **判定怎麼用**(使用者裁定 d1、d2、d4):
   - `real`:擋,擋下訊息與放行出口跟新增告警相同(`lumos lint-waive <指紋>`);出處不全規則判 `real` 只提醒(d1)。
   - `false`:不擋,列進待人看清單(推送前小結印筆數、doctor 唸)(d4)。
   - `unsure`:等仲裁;還沒仲裁算「還沒判」;仲裁判 `real` 擋、`false` 照上一條、仍 `unsure` 只提醒並記帳。
   - 還沒判:擋,印跑盲判的指令(d2);出處不全規則的命中例外,還沒判也只提醒(解 r1 邊界 4:依據不足的規則不准擋人,判前判後都一樣)。
   - 判定之後同片段處數變多:那筆判定不再適用,算還沒判(解 r1 回滾 F5、資源 F6:新增的那一處沒被判過)。
   - 人複查:`lumos code-loop rule-review <指紋> agree|overturn --note "…"` 或 `--batch <token> overturn --note "…"`(整次記帳一起推翻,解 r1 回滾 F1:壞掉的盲判一次判錯一批時救得回來);只准單筆或單一 token,沒有 `--all`(解 r1 回滾 F6)。`overturn` 之後那幾筆的判定作廢、恢復成要擋,可以重派盲判(解 r1 回滾 F2、邊界 1)。
7. **沒跑要講出來、而且要留帳**(解 r1 資源 F4、整合 F7、邊界與正確性「沒跑原因」):範圍 2 那支回的沒跑原因分四種:工具不可用、時間預算用完、參數太長、例外;任一種都印一行「覆核沒跑:<原因>」並寫一筆 `code-loop` 閘 fail-open 事件(scope `rule-review`),跟新增告警閘自動放行同樣被 `gov --stats` 數。沒有 `.lumos/lint-review.json` 的專案不印這行;doctor 只在 `.lumos/lint.json` 宣告了規則包 `sgconfig.yml`、卻沒有覆核宣告時提醒一行。覆核命令吃一般段跑完剩下的時間預算。
8. **統計與升降建議**(解 r1 整合 F2、F4、邊界 minor、回滾 F7):`lumos gov --stats` 多一段「覆核規則」,全部從治理帳算(判定事件、人複查事件、放行事件):每條規則列判定幾筆、`real`/`false`/`unsure` 各幾筆、`false` 被人複查幾筆與其中 `overturn` 幾筆、`real` 判定後被放行幾筆(人放、AI 放分開數)。只出建議、不自動改:`real` 至少 20 筆、被放行(人加 AI)少於一成 → 建議移到 `rules/`;`false` 經人複查至少 20 筆、`agree` 至少九成、而且 `false` 佔該規則判定八成以上 → 建議刪掉或改形狀。一成取 Google 有效誤報的經驗數字,20 筆取情境題升擋同一個樣本下限,九成、八成是本案自訂,上線後照 REVISIT 回頭校準。
9. **範本與手冊**:[[Systems/linter精選目錄]] 的 Kotlin 規則包範本加 `.lumos/lint-review.json` 兩條命令,「提示級規則預設不接」那句改成「接在覆核宣告、命中交盲判」;同步改 `skills/lumos-code-loop/SKILL.md` 與 `skills/lumos-project-notes/commands/06-代碼審與推送.md` 的盲判段、`skills/kotlin-idioms/checks-catalog.md` 第 11 行「語意覆核級要等計劃接上」、`configs/ast-grep/kotlin-android/check.py` 開頭「接上前不擋」註解、`lint-waive` 與 `code-loop blind-judge` 的說明。

### 不做

- 不在收工鉤子(回合結束檢查)跑覆核命令:收工那一道要秒級、不派代理(覆核只在 `_codeloop_lint_new_step` 跑,工作樹模式碰不到;S9 釘住)。
- 不自動升降規則等級:只出建議,改等級要改規則檔、過代碼審。
- 不替出處不全的 7 條補出處:那是型錄逐列查證的工作(另一條線)。
- 不寫放行檔:判誤報只留治理帳(d4)。
- 不讓同一個代理同時判覆核命中與情境段:兩種材料分份印、各派一席。

## 實務隱患

- **盲判成本**:每次推送有覆核命中就要派代理,一份最多 30 筆。上線前用兩個真專案(實驗專案、nowinandroid)整份跑一次兩份覆核 sgconfig 量命中筆數(2026-11-05 的真專案實測只跑了會擋的 `sgconfig.yml`)。改檔名會讓整支檔的舊命中被當成新增、要重判;REVISIT 看實際筆數。
- **同家族偏誤**:盲判跟寫程式的是同一家模型;準確率只算人複查過的那部分。
- **待人看清單沒人看**:清單只靠 doctor 與推送前小結提醒;沒人複查就沒有準確率,RETIRE-IF 判不了。REVISIT 看有沒有人在複查。
- **AI 自己放行真問題**:判 `real` 被擋時,AI 跑 `lint-waive` 也能放行(記成 origin ai),跟新增告警閘現在一樣;統計把 AI 放行算進「被放行」,所以 AI 一直自放行的規則不會被建議升擋。
- **語境變了、命中行沒變**:身分只看命中那一行(SonarQube 也是用命中行內容雜湊當身分),行沒變、前後型別變了時沿用舊判定;寫進〈天花板〉。
- **治理帳長大**:每筆判定理由最長 2000 字,一份 30 筆約 60KB 進版控治理帳;REVISIT 一起看帳的大小。
- 已排除:金流:不碰付款
- 已排除:對外送出:只讀本機檔與跑本機 ast-grep,不連網
- 已排除:不可逆:新增一支宣告檔、一份材料、一個帳欄與一個子指令,退提交即回原狀;已寫進治理帳的判定與複查事件留著,舊版不讀 `rule_hits` 欄
- 守衛面:不排除——新增告警那一道多一條會擋的路徑(判 `real`、還沒判、人推翻),動的是守衛面;判風險高,走完整設計審

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| AI 判誤報不關、藏起來集中給人複查、人不同意就重新打開 | Semgrep Assistant 的雜訊過濾與 triage memories | https://ai.semgrep.dev/blog/2025/announcing-ai-noise-filtering-and-triage-memories |
| 同上(人同意就關、不同意就重新打開) | Semgrep Assistant 文件 | https://semgrep.dev/docs/semgrep-assistant/best-practices-for-memories |
| 命中身分用規則加命中行內容雜湊 | SonarQube 的問題比對:規則加命中行內容雜湊(去空白),誤報標記跟著身分走、人可以手動重新打開 | https://docs.sonarsource.com/sonarqube-server/latest/user-guide/issues/solution-overview/ |
| 模型判靜態分析命中的準確度量得到 | ZeroFalse 讓模型裁判靜態分析結果並量誤報過濾率 | https://arxiv.org/html/2510.02534v1 |
| 同上(第二個來源) | Wagner 等以模型過濾靜態分析告警 | https://arxiv.org/abs/2506.16899v1 |
| 誤報門檻一成、沒人採取行動的告警就是噪音 | Google 靜態分析經驗:有效誤報的定義與門檻 | https://cacm.acm.org/magazines/2018/4/226371-lessons-from-building-static-analysis-tools-at-google/pdf |
| 只看這次新帶進來的命中 | SonarQube Clean as You Code:品質閘只看新程式 | https://docs.sonarsource.com/sonarcloud/improving/clean-as-you-code |
| 覆核宣告另開檔 | 專案既有共識:非「副檔名→命令清單」的宣告不進 lint.json | `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` |
| 兩級 62 條一起處理 | 使用者裁定 | 使用者 2026-11-07:「62 條一起處理，先建語意覆核接盲判的計劃」 |
| 擋停三題照建議 | 使用者裁定 | 使用者 2026-11-07:「照建議」 |
| 判誤報改成只留治理帳 | 使用者裁定(設計審 r1 後改裁) | 使用者 2026-11-07:「照建議」 |
| 不降成提示級、要語意判斷 | 使用者提問 | 使用者 2026-11-05:「如果形狀都改不好,是不是可以參語意判斷?會不會比 hint 靠譜一點」 |
| 樣本下限 20 筆 | 情境題升擋門檻已在表態閘筆記立為回頭條件 | `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md` |

## 驗收條款

- [S1] 當專案有 `.lumos/lint-review.json` 時,覆核宣告的驗證 應 逐條照命令規則驗,沒有檔案佔位符的命令 應 報錯;`.lumos/lint.json` 的驗證 應 跟改動前一字不差 [test:t_rule_review_decl_file]
- [S2] 當覆核命令在這次改動有新增命中、而且還沒有規則判定時,`lumos code-loop check` 應 擋並印跑盲判的指令;規則是出處不全時 應 只提醒;同一條規則宣告在 `.lumos/lint.json` 時 應 照舊直接擋 [test:t_rule_review_missing_judgment_blocks]
- [S3] 當一筆覆核命中判 `real` 時,推送前檢查 應 擋,用 `lint-waive` 放行後 應 放行;規則是出處不全時 應 只提醒 [test:t_rule_review_real_blocks_waivable]
- [S4] 當一筆覆核命中判 `false` 時,推送前檢查 應 不擋並把它算進待人看清單;放行檔 應 不變;`rule-review <指紋> overturn` 之後 應 恢復成要擋;`--batch <token> overturn` 應 讓那次記帳的每一筆都恢復成要擋 [test:t_rule_review_false_queue_overturn]
- [S5] 當一筆覆核命中第一判是 `unsure` 時,推送前檢查 應 擋(算還沒判);`--template --rule-hits --unsure` 應 只印那幾筆;仲裁判 `false` 應 照 S4、仍 `unsure` 應 只提醒 [test:t_rule_review_unsure_arbiter]
- [S6] 當 `blind-judge --template --rule-hits` 印材料時,每筆 應 含檔名、同片段每一處的前後 8 行、規則訊息與對應型錄列四欄,應 不含任何表態內容;不帶 `--rule-hits` 時 應 跟改動前一樣只印情境段 [test:t_rule_review_template_material]
- [S7] 當覆核命令工具不可用、時間預算用完、參數太長或那一段出例外時,推送前 應 印「覆核沒跑」與原因、應 寫一筆 fail-open 事件、應 不擋;一般段的新增告警 應 照舊判 [test:t_rule_review_not_run_isolated]
- [S8] 當治理帳有規則判定、複查與放行事件時,`lumos gov --stats` 應 逐條規則列筆數與複查結果;符合門檻 應 印升級或刪除建議;不足 20 筆 應 不印建議 [test:t_rule_review_stats_suggestion]
- [S9] 當收工鉤子或 `lint-new --worktree` 跑工作樹模式時,覆核命令 應 不被執行 [test:t_rule_review_skipped_in_worktree]
- [S10] 當結果檔的 `rule_hits` 有一個 `seg` 不在當下算出的新增命中裡時,記帳 應 整份拒收、應 不寫治理帳 [test:t_rule_review_record_rejects_unknown_seg]
- [S11] 當一筆判定之後同片段在那支檔的處數變多時,推送前檢查 應 把它當還沒判、擋 [test:t_rule_review_more_occurrences_rejudge]
- [S12] 當合併提交推上主線、判定記在被合進來的分支時,推送前檢查 應 認那一側的判定 [test:t_rule_review_merge_side]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `.lumos/lint-review.json` = `{"kt": ["ast-grep scan --config …/sgconfig-review.yml {LINT_FILES} …"]}` | 驗過 | 範圍 1 |
| S1 | 覆核命令沒有 `{LINT_FILES}` | 報錯 | 範圍 1 |
| S1 | 專案有覆核宣告時跑 `.lumos/lint.json` 驗證 | 結果跟改動前一樣 | 範圍 1 |
| S2 | 覆核新增 1 筆、沒有判定、規則不是出處不全 | 擋,印 `blind-judge --template --rule-hits` 指令 | 範圍 6;d2 |
| S2 | 覆核新增 1 筆、沒有判定、規則是出處不全 | 只提醒 | 範圍 6;r1 邊界 4 |
| S2 | 同一條規則宣告在一般段、新增 1 筆 | 直接擋(不要盲判) | 範圍 1 |
| S3 | 判 real、規則不是出處不全 | 擋 | 範圍 6;d1 |
| S3 | 判 real 之後 `lint-waive` 那個指紋 | 放行 | 範圍 6 |
| S4 | 判 false | 不擋;待人看清單 +1;放行檔不變 | 範圍 6;d4 |
| S4 | 判 false 後 `rule-review <指紋> overturn` | 擋 | 範圍 6;Semgrep 人不同意就重新打開 |
| S4 | 一次記帳 3 筆 false,`--batch <token> overturn` | 3 筆都擋 | 範圍 6;r1 回滾 F1 |
| S5 | 第一判 unsure、還沒仲裁 | 擋 | 範圍 6 |
| S5 | 仲裁仍 unsure | 只提醒 | 範圍 6 |
| S6 | 同檔同片段兩處 | 材料兩處都有前後 8 行 | 範圍 4 |
| S6 | 命中在檔案第 3 行 | 前文給到第 1 行為止 | 範圍 4 |
| S7 | ast-grep 沒裝 | 印覆核沒跑:工具不可用;一筆 fail-open 事件;不擋 | 範圍 7 |
| S7 | 覆核那一段丟例外、一般段有 1 筆新增告警 | 覆核沒跑:例外;一般段照擋 | 範圍 3;r1 資源 F3 |
| S7 | `lint_new.gate` 是 warn、覆核判 real | 只提醒 | 範圍 3 |
| S8 | 某規則 real 20 筆、被放行 1 筆 | 建議移到 rules/ | 範圍 8 |
| S8 | 某規則 false 人複查 20 筆、agree 19 筆、false 佔 85% | 建議刪掉或改形狀 | 範圍 8 |
| S8 | 某規則判定 19 筆 | 不印建議 | 範圍 8 |
| S9 | 收工鉤子跑工作樹模式、有覆核宣告 | 覆核命令沒被執行 | 範圍 3;不做 1 |
| S10 | 結果檔 `rule_hits` 的 seg 是一般段某條告警的指紋 | 整份拒收、不寫帳 | 範圍 5 |
| S11 | 判 false 時同片段 1 處,之後變 2 處 | 擋(算還沒判) | 範圍 6 |
| S12 | 判定記在 feat 分支,feat 合進 main 推送 | 認 feat 的判定 | 範圍 3 |

## 回退

退回本計劃的提交:覆核宣告檔(`.lumos/lint-review.json`)沒人讀,消費專案留著也無害(`.lumos/lint.json` 的驗證沒動過,舊版不會因為它報錯);覆核不再跑、`--rule-hits` 與 `rule-review` 拿掉;治理帳已寫的 `rule_hits` 與複查事件留著,舊版不讀這些欄;放行檔沒被本案寫過,不用收拾。

## 天花板

1. 身分只看命中那一行:行沒變、前後語境變了時沿用舊判定(SonarQube 同樣做法);同片段處數變多才重判。
2. 放行一處等於放行同檔同片段的每一處(沿用新增告警閘的指紋語意)。
3. 盲判與作者同一家模型;準確率只有人複查過的那部分算數,沒人複查就沒有數字。
4. 覆核只在推送前與記通過前跑;收工時與寫的當下不跑;時間預算用完時這次不跑、留帳。
5. 出處不全的 7 條判前判後都不擋,要等型錄逐列查證補上出處。
6. 判 `real` 被擋時 AI 也能自己 `lint-waive` 放行,只留下 AI 放行待看紀錄。
7. 盲判材料帶程式碼,註解可以對代理下指示(跟情境題盲判同一個天花板,屬刻意偽造)。

REVISIT:2026-12-07 看規則判定上線一個月:總共幾筆覆核命中、盲判派了幾次、覆核沒跑幾次與原因、待人看清單有沒有人複查、治理帳長了多少;清單沒人看就改成判誤報也要人當下確認

## 審計修正紀錄

- 2026-11-07 改寫:母計劃設計審 r2 帶來的七個問題逐條解進〈範圍〉1–7;範圍擴大到提示級 50 條(使用者裁定)。
- 2026-11-07 舊否決比對(lumos rejections 512 行,按概念篩):「AI 放行一律擋」「AI 放行累積幾筆就擋」被否決過(Systems/test-guard、Projects/Android端到端驗收_計劃)——本案判誤報記成 AI 放行、只讓它事後可見不擋,跟那兩次裁定一致;「多數判作者沒照做就擋」被否決過(Systems/棧別提問表態閘)——規則命中沒有作者表態,不適用;「LLM 判可逆性」被否決過(Systems/doctor-irreversible-hint#d1,選字面掃描加軟提醒)——本案是模型判規則命中真假、不是判可逆性,而且情境題盲判已審過上線,概念相近處交設計審判。
- r1(2026-11-07,六席 sonnet:正確性、邊界、整合、資源、回滾、架構對齊):55 條/blocking 33/判誤報寫成放行撤不回、推翻無效、兩處寫一半(五席獨立)、身分不綁語境、宣告放進 lint.json 違反既有共識、擋停接線與例外隔離沒寫;照 Semgrep 與 SonarQube 換形狀(判誤報只留治理帳、人推翻就重新擋,使用者改裁 d4),全部折入,分組在 r1-intake.md。卷證:governance/review-reports/規則包語意覆核級命中走盲判/。
