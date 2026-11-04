---
type: project
status: todo
created: 2026-10-31
updated: 2026-10-31
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
lands_in:
  - Systems/android-e2e-acceptance
  - Systems/lumos-cli-write
related:
  - "[[Projects/Android端到端驗收_計劃]]"
  - "[[Projects/Android側UI測試綁圖譜工作流_計劃]]"
  - "[[Projects/E2E紅燈現場與不穩帳_計劃]]"
  - "[[Projects/截圖基準驗收流程_計劃]]"
pending_questions:
  - id: Q1
    text: "情境還沒寫驗收句(沒有 accept)時怎麼判?(建議:專案在 e2e 段設 accept_required: true 才擋;沒設時每次推送列出哪些情境還沒有驗收句。KDS 接上這版後就打開)"
    class: 過渡
    stage: 架構
    status: 已決
    blocking: true
    decision: "#d1"
  - id: Q2
    text: 哪些功能的驗收句要人點頭、不能只由代理審?(建議:情境標 risk 為金流、對外送出或不可逆時,accept_review.by 必須是 human:)
    class: 審查
    stage: 驗證
    status: 已決
    decision: "#d2"
  - id: Q3
    text: 判定讀 Maestro 執行紀錄還是靜態解析 flow 的 YAML?
    class: 判定
    stage: 實作
    status: 自答
    source: "2026-10-31 SM-X710 實測:commands.json 帶 label 與 COMPLETED/WARNED/SKIPPED,分得出 optional 失敗與條件沒跑;靜態解析看不出,且 lumos 零依賴沒有 YAML 解析器"
  - id: Q4
    text: 驗收句放在哪裡?
    class: 格式
    stage: 架構
    status: 自答
    source: 放 e2e.features 的情境底下:e2e 段已算進指紋(改句子舊紀錄自動失效),按功能挑選也已經用這張表(Projects/Android端到端驗收_計劃)
  - id: Q5
    text: 檢查數變少要擋還是提醒?
    class: 判定
    stage: 驗證
    status: 自答
    source: "2026-10-31 對話:AI 提「檢查數比上一版少要點名、先只提醒」,Enzo 對整理後的五步流程回「可以」"
decisions:
  - content: 不溯及既往:逐句對照與「零檢查判沒過」只套在新開發的情境與流程——主線(與主線的分岔點)上 e2e.features 沒有的情境、e2e.flows 沒有的流程檔;既有的情境與流程照舊判,只在推送時列出還沒有驗收句或零檢查的舊項目,不擋;舊情境自己補了 accept 就照新規則判
    id: d1
    context: Q1:還沒寫驗收句的舊情境怎麼判。考慮過:專案開關打開才擋、零檢查一律擋(AI 建議);升版後全部立刻擋
    why_chosen: Enzo 2026-10-31 原話:「不錯及既往,應該以新開發的功能為主」(不溯及既往)。新功能從第一天就照依據寫,舊流程不因升版突然變紅;代價:舊情境裡的零檢查流程仍會放行,要靠推送時的清單提醒逐步補
    decided: 2026-10-31
    valid: true
  - content: 單向門類型的情境(金流、對外送出、不可逆資料三類,定義同規格閘的計劃風險表)驗收句要人點頭:accept_review.by 必須是 human:;其他情境由另派的代理審即可。判定方式:情境名、驗收句命中規格閘同一張關鍵字表即視為單向門(硬訊號,不可申辯),作者可加 one_way 往嚴標、不能往鬆標
    id: d2
    context: Q2:哪些功能的驗收句要人點頭。考慮過:AI 建議金流、對外送出、不可逆三類;另一路是全部由代理審
    why_chosen: Enzo 2026-10-31 原話:「單向門類型要人點頭」。沿用規格閘既有的單向門/雙向門判準(還原之後外面要不要人收拾),不另立一套;用驗收句文字比對而不掃程式碼,因為程式裡 send、notify 這類字太常見會滿屏誤判。代價:驗收句寫得避開關鍵字就躲得掉,靠審驗收句的代理抓
    decided: 2026-10-31
    valid: true
---
# UI流程驗收句與檢查對照

白話:Android 端到端驗收判「UI 流程通過」只看 Maestro 有沒有跑完,不看流程裡寫了什麼檢查。流程是代理自己寫的,只寫「點這裡、點那裡」不寫「應該看到什麼」,App 壞了照樣綠。這份計劃讓檢查有依據:每個使用情境先寫「驗收句」(這種情況下使用者應該看到什麼),流程裡每個檢查用 Maestro 的 `label` 標它對應哪一句,驗收判定讀 Maestro 的執行紀錄,確認每一句都有一個真的跑過、真的通過的檢查;一個檢查都沒有的流程直接判沒過。

緣起:2026-10-31 Enzo 問全自動開發 Android 缺什麼,調研排出五塊缺口,這是第四塊的前半(後半「新畫面自動升成代碼審」Enzo 否決:改個按鈕或字眼就要整輪審查,過頭)。Enzo 問「檢查是以什麼依據立下」,同意「代理寫驗收句、另派代理審」,並補一條:寫驗收句之前要先看那個流程的畫面程式。

PRIOR-ART: 需求追溯矩陣(每條需求對到至少一個測試,軟體工程的老做法);BDD 的驗收條件(Given/When/Then,Cucumber 一類);各家「測試沒有斷言」的檢查(SonarQube 規則 S2699 Tests should include assertions、eslint-plugin-jest 的 expect-expect);Lumos 自己的規格條款「[S1] 當…應… [test:]」與規格閘([[Systems/bound-tests-gate]]);Maestro 每個指令都收的 `label` 與 `optional` 兩個共同參數、`--debug-output` 留下的 `commands.json`(逐條指令的執行狀態)。借用:追溯的概念、「沒有斷言就紅」的規則、Maestro 的 label 與執行紀錄、既有的端到端驗收判定與指紋([[Systems/android-e2e-acceptance]])。自建:驗收句的設定格式、讀執行紀錄的對照判定。不選:Gherkin/Cucumber(要多一套執行器與依賴,Maestro 已經是執行器;零依賴家規);靜態解析 flow 的 YAML 數檢查(lumos 零依賴、沒有 YAML 解析器,而且看不出條件分支有沒有跑到、`optional` 有沒有失敗,執行紀錄看得到);只做「至少一個檢查」(擋得住零檢查、擋不住無關痛癢的檢查,Enzo 問依據時否決)。

RETIRE-IF: 連續兩個月,推送檢查因「驗收句沒有檢查對到」擋下的次數裡,過半在下一個提交只改了 label 那幾行就放行、檢查內容沒變(人工抽查治理帳的擋下紀錄與對應提交;等於只在填表);或 Maestro 原生提供需求追溯與覆蓋報告,就改讀它、拿掉自建的對照。

## 實測(2026-10-31,SM-X710、Maestro 2.10.0)

- **洞存在**:在 macrobench-lab 把清單頁改壞(每一列文字變空白),原本的流程(有「第 1 列」檢查)回 1;拿掉檢查的同名流程回 0。照正式流程 `--case list.scroll --no-perf` 跑驗收,判定印「✓ UI 流程 .maestro/list.yaml」。那次整體判沒過,是截圖那支流程開頭自己的「第 1 列」檢查先紅,不是截圖比對抓到;沒開截圖的專案(KDS)連這道都沒有。證據見 [[Verification/2026-10-31_無檢查流程實機放行]]。
- **執行紀錄看得到 label 與結果**:系統設定 App 上一支探針流程(`name: label_probe`),照範本腳本同一組旗標(`--test-output-dir <ev> --debug-output <ev>/debug --flatten-debug-output`)跑,執行紀錄落在 `<ev>/debug/label_probe/commands.json`(依 flow 的 `name:` 分子目錄;`<ev>` 底下沒有另一份)。裡面有 label 的 `assertVisible` 記成 `assertConditionCommand`、label 原樣在、狀態 `COMPLETED`;加了 `optional: true` 而失敗的記成 `WARNED`;條件不成立的 `runFlow` 記成 `SKIPPED`、裡面的檢查不出現。所以「真的跑過、真的通過」讀執行紀錄就分得出來。中文 `name:` 的子目錄怎麼命名沒測(S12 實測)。

## 做法

分兩段:**判定(judge)只記事實**——每支流程跑過哪些算數的檢查、各帶什麼 label;**推送檢查才判擋不擋**——它本來就讀得到主線與分岔點的設定([[Systems/android-e2e-acceptance]] 的推送判定),所以「哪些情境是新的」在這裡算。judge 拿不到主線(它的輸入只有 run 目錄與專案根),硬在 judge 裡判新舊要另寫一套挑主線的邏輯、本機與推送時還可能算出不同結果。

1. **設定格式**:`.lumos/macrobench.json` 的 `e2e.features.<功能>.cases.<情境>` 多三個選填鍵:
   - `accept`:清單,每項 `{"id": "A1", "text": "<這種情況下使用者應該看到什麼>", "state": "<畫面狀態,選填,例:空清單、網路錯誤、正常>"}`。`id` 在同一情境內唯一、只收英數字;`text` 非空;`state` 只給審驗收句的代理對照「每種狀態都有一句」,判定不讀它。
   - `accept_review`:`{"by": "agent:<模型>" 或 "human:<名字>", "at": "YYYY-MM-DD"}`。
   - `one_way`:作者主動標單向門,值是 `payment`、`external-send`、`prod-irreversible` 三者之一或其清單(同 [[Systems/規格閘]] 計劃風險表的前三類)。
   - `lumos macrobench --check-config` 驗這三個鍵的格式(現在的情境檢查不擋未知鍵,所以要新增檢查;舊版 lumos 讀到新鍵會靜默忽略)。e2e 段整段算進指紋,三個鍵改了,舊的通過紀錄自然失效、要重跑。
2. **寫驗收句的程序**(寫進 lumos-android-evidence 與產 flow 的派工要求,是程序不是機械擋):
   1. 先讀需求,再讀這個情境畫面的程式(Compose 或 Activity/Fragment、對應的 ViewModel)。
   2. 從程式列出畫面所有狀態與分支(正常、空、載入中、錯誤、輸入不合法、權限被拒…),每一種寫一句驗收句。
   3. **預期結果照需求寫,不照程式抄**;程式跟需求對不上的地方標出來問人,不寫成驗收句(否則把錯的行為鎖成對的)。程式只拿來找分支、拿確切文字與元件識別名。
   4. 另派一個代理,只給需求與驗收句、**不給程式**,審有沒有漏狀態、有沒有偏向程式;審過把 `accept_review` 寫成 `agent:<模型>`。單向門情境(見第 6 條)要人點頭,`accept_review.by` 必須是 `human:<名字>`(決策 d2)。
   5. 新畫面一律開新情境,不塞進既有情境(既有情境不溯及既往、不做逐句對照,塞進去等於躲開檢查)。
3. **流程裡標對應**:每個檢查加 `label: "驗收:<功能>.<情境>#<id>"`;一個檢查只對一句。
4. **judge 記事實**(整套跑與按功能跑都做):每支 flow 通過的那次嘗試,從 steps.json 那次的 `evidence.dir` 讀 `<dir>/debug/<flow 的 name:>/commands.json`,把算數的檢查記進查證紀錄 `runs.blocks.ui` 那支 flow 的新欄位 `checks: {"count": <數>, "labels": [<label>…]}`(按功能跑的 `feature_runs` 同樣帶);讀不到(`evidence.dir` 是空、檔不在、格式看不懂)記 `checks: null` 加 `checks_reason`。
   - 算數的檢查:指令是 `assertConditionCommand`(assertVisible、assertNotVisible、extendedWaitUntil 都落在這)、`assertScreenshotCommand`,以及 assertTrue 對應的指令,而且狀態是 `COMPLETED`;`WARNED`、`SKIPPED`、AI 類檢查(預設 optional、結果不穩定)不算。assertTrue 與 assertNotVisible 的實際指令名在實作第 0 步實測後寫進這節(S12)。
   - judge 的過與不過照原本規則,不因檢查數改判;只在終端多印一段預覽:零檢查的流程、有 `accept` 的情境裡沒對到的句子,並註明「哪些會擋由推送檢查依主線判」。
5. **推送檢查判,只對新開發的情境與流程**(決策 d1):「新情境」= 主線與分岔點的 `e2e.features` 都沒有這個 `<功能>.<情境>`;「新流程」= 兩邊的 `e2e.flows` 都沒有這支檔。用推送檢查既有的挑主線結果;主線判不出來時照那道判定原本的規則(判不清就擋)。對新的項目,下面任一成立就擋,擋下訊息列出項目與原因:
   - 新流程在紀錄裡 `checks.count` 是 0 →「這支流程沒有任何檢查」。
   - 新流程 `checks` 是 null →「讀不到執行紀錄:<原因>」(不放行;Maestro 太舊沒帶旗標、不是用範本腳本跑的、檔不在都走這條)。
   - 新情境沒有 `accept` →「新情境要先寫驗收句」。
   - 新情境的某一句,在這個情境所有 flow 的 `checks.labels` 聯集裡找不到 `驗收:<功能>.<情境>#<id>` →「A<n> 沒有檢查對到」。
   - 新情境的 flow 帶了 `驗收:<功能>.<情境>#<id>` 卻沒有這一句 →列出那個 label(打錯字會讓句子看似有人管)。
   - 新情境是單向門(第 6 條)而 `accept_review.by` 不是 `human:` 開頭 →印命中的類別與字。
6. **單向門怎麼認**:情境名或任一驗收句的 `text`,用規格閘的關鍵字表(`PITFALL_CLASSES`)只取 payment、external-send、prod-irreversible 三類比對,命中任一就是單向門(不取第四類 self-governance:那是工具鏈自己的守衛面,跟 App 功能無關);作者標了 `one_way` 也是。命中不可申辯,作者只能往嚴標。
7. **檢查數變少只提醒**:推送時,對每支這次紀錄裡有 `checks` 的 flow,用分岔點那棵樹的 e2e 段算指紋、找 `.lumos/e2e-records/<指紋>.json`;找得到、那份紀錄裡同一支 flow 也有 `checks`、而且數量比這次多,就列出「<flow> 檢查從 5 個變 2 個」,不擋(刪檢查有時是合理的)。找不到紀錄或舊紀錄沒有 `checks` 欄,印一行「分岔點沒有可比的紀錄,這次不比」。
8. **舊項目只列出**:推送時列出主線上已經有、但沒有 `accept` 的舊情境,以及紀錄裡 `checks.count` 是 0 的舊流程(各列名字),不擋;舊情境自己補了 `accept`,就照第 5 條判。

## 待決問題

題目、建議答案與自答出處在開頭欄位 `pending_questions`(`lumos show` 看得到);Q1、Q2 的題目文字是當時的建議,以裁定後的決策 d1(不溯及既往)、d2(單向門要人點頭)為準。

## 驗收條款

- [S1] 當一支 flow 通過、那次嘗試的 commands.json 有兩個 COMPLETED 的 assertConditionCommand(一個帶 label、一個不帶)時,judge 寫的查證紀錄裡那支 flow 應有 `checks.count` 為 2、`checks.labels` 只含那一個 label [test:t_android_e2e_checks_recorded]
- [S2] 當檢查加了 `optional: true` 而失敗(WARNED)、在條件不成立的 runFlow 裡沒跑到(不出現),或是 AI 類檢查時,judge 不應把它算進 `checks.count` [test:t_android_e2e_checks_warned_skipped_ai_not_counted]
- [S3] 當通過的那次嘗試 `evidence.dir` 是空、commands.json 不在或不是看得懂的格式時,judge 應記 `checks: null` 與原因,UI 那塊的過與不過照原本規則 [test:t_android_e2e_checks_unreadable_null]
- [S4] 當新流程的 `checks.count` 是 0 時,推送檢查應擋下並印「這支流程沒有任何檢查」 [test:t_android_e2e_gate_new_flow_zero_checks]
- [S5] 當新流程的 `checks` 是 null 時,推送檢查應擋下並印讀不到執行紀錄的原因 [test:t_android_e2e_gate_new_flow_checks_null]
- [S6] 當新情境沒有 `accept` 時,推送檢查應擋下並印「新情境要先寫驗收句」 [test:t_android_e2e_gate_new_case_requires_accept]
- [S7] 當新情境的某一句在它所有 flow 的 label 聯集裡找不到,或有 label 指到它沒有的句子時,推送檢查應擋下並分別列出缺的句子編號與那個 label;每一句都對到、沒有多餘 label 時不因此擋 [test:t_android_e2e_gate_accept_coverage]
- [S8] 當新情境的名稱或驗收句命中 payment、external-send 或 prod-irreversible 的關鍵字,或標了 `one_way`,而 `accept_review.by` 不是 `human:` 開頭時,推送檢查應擋下並印命中的類別與字;只命中 self-governance 的字不算單向門 [test:t_android_e2e_gate_one_way_needs_human]
- [S9] 當情境或流程在主線與分岔點已經存在時,不論有沒有 `accept`、`checks.count` 是不是 0,推送檢查都不應因此擋,而應列出沒有 `accept` 的舊情境與零檢查的舊流程 [test:t_android_e2e_gate_legacy_listed_not_blocked]
- [S10] 當分岔點的紀錄裡同一支 flow 的 `checks.count` 比這次多時,推送檢查應印出前後數量但不擋;分岔點沒有紀錄或舊紀錄沒有 `checks` 欄時,印「分岔點沒有可比的紀錄,這次不比」 [test:t_android_e2e_gate_check_count_drop_notice]
- [S11] 當 `accept`、`accept_review` 或 `one_way` 格式不對(缺 id、id 重複或含英數字以外的字、text 空、by 不是 agent: 或 human: 開頭、at 不是 YYYY-MM-DD、one_way 不在三個值裡)時,`lumos macrobench --check-config` 應回 2 並印出哪一項壞;三個鍵都不寫的舊設定照舊回 0 [test:t_android_e2e_accept_config_strict]
- [S12] 當實作開始時,應先在實機上實測 assertNotVisible、extendedWaitUntil、assertTrue、assertScreenshot 在 commands.json 裡的指令名與狀態,以及中文 `name:` 的子目錄命名,寫進〈做法〉第 4 條 [manual:SM-X710 上跑一支探針流程,結果寫進本計劃]
- [S13] 當在 macrobench-lab 開一個新情境、照實測那組重跑(清單頁改壞、流程拿掉檢查)時,推送檢查應擋下;補回帶 label 的檢查、App 改回正常、重跑驗收後應放行 [manual:SM-X710 上跑兩次並各推一次到本機假遠端,結果寫進驗證紀錄]

## 實務隱患

- 已排除:金流:只改驗收判定、推送檢查與設定格式,不碰任何付款或點數程式
- 已排除:對外送出:判定只讀本機的 Maestro 執行紀錄,不送資料到外部服務
- 已排除:不可逆:拿掉三個新鍵就回到現在的行為;查證紀錄只多 `checks` 一欄,舊紀錄沒有這欄照舊判
- 守衛面:命中。推送檢查決定擋不擋;寫錯會放行沒驗過的流程(S2、S3、S5 守),或把好的、舊的流程誤擋(S7 後半、S9 守)。照走設計審。
- 單向門關鍵字是子字串比對,「送出」「對外」這類字在點餐、廚房顯示這種 App 的驗收句裡很常見,會讓很多情境要人點頭;這是 Enzo 裁的代價(寧可多問)。
- 不溯及既往的漏洞:把新畫面塞進既有情境、不開新情境,就能躲開逐句對照;機械上分不出「新畫面」,靠產 flow 的派工要求寫明「新畫面開新情境」與推送時的舊項目清單看得到。
- 本機驗收時與推送時看到的主線可能不同(中間合併過主線):以推送時為準,judge 的預覽只是預覽。
- Maestro 的執行紀錄格式不是公開合約,改版可能改指令名、欄位或目錄;讀不懂一律記 `checks: null`,新流程因此被擋(S5),不能當成零檢查或全通過。

## 回退

- 專案層:情境拿掉三個新鍵就不做逐句對照與單向門判定;零檢查只對新流程擋。
- 工具鏈層:還原 judge 記 `checks` 的一段、推送檢查新增的那幾條與設定檢查;既有查證紀錄多出的 `checks` 欄被忽略即可。

## 不做

- 判斷檢查「有沒有驗到重點」(語意判斷,交給審驗收句的代理與代碼審)。
- 新畫面自動升成代碼審(Enzo 2026-10-31 否決)。
- 截圖比對的門檻與基準圖規則(另有 [[Projects/截圖基準驗收流程_計劃]])。
