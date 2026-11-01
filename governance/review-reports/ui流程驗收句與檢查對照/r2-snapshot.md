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
  - Systems/規格閘
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
   - `accept`:清單,寫了就至少一項;每項 `{"id": "A1", "text": "<這種情況下使用者應該看到什麼>", "state": "<畫面狀態,選填,例:空清單、網路錯誤、正常>"}`。`id` 在同一情境內唯一、只收英數字;`text` 非空;`state` 只給審驗收句的代理對照「每種狀態都有一句」,判定不讀它。條數與字數上限沿用 e2e 段既有清單的上限(`E2E_PATH_LIST_MAX` 那一級)。
   - `accept_review`:`{"by": "agent:<模型>" 或 "human:<名字>", "at": "YYYY-MM-DD"}`。跟放行紀錄的 `by` 只記 human/ai 不同:這裡要記「誰」,單向門要能看出是哪個人點的頭。
   - `one_way`:這個情境碰哪幾類單向門,值是 `payment`、`external-send`、`prod-irreversible` 的清單,一類都不碰寫 `[]`;**新情境必填**(見第 6 條)。
   - 格式檢查放在 e2e 段共用的設定檢查(`--check-config` 與推送檢查都走同一支),不只放在 `--check-config` 的路徑:推送檢查讀到提交樹裡格式壞的設定要擋,不能在判定內部出例外。現在的情境檢查不擋未知鍵,所以要新增;舊版 lumos 讀到新鍵會靜默忽略。e2e 段整段算進指紋,三個鍵改了,舊的通過紀錄自然失效、要重跑。
2. **寫驗收句的程序**(寫進 lumos-android-evidence 的端到端驗收一節與 lumos-project-notes 的〈產 maestro UI flow 的派工要求〉,是程序不是機械擋):
   1. 先讀需求,再讀這個情境畫面的程式(Compose 或 Activity/Fragment、對應的 ViewModel)。
   2. 從程式列出畫面所有狀態與分支(正常、空、載入中、錯誤、輸入不合法、權限被拒…),每一種寫一句驗收句。
   3. **預期結果照需求寫,不照程式抄**;程式跟需求對不上的地方標出來問人,不寫成驗收句(否則把錯的行為鎖成對的)。程式只拿來找分支、拿確切文字與元件識別名。
   4. 照需求判這個情境碰哪幾類單向門,寫進 `one_way`。
   5. 另派一個代理,只給需求、驗收句與 `one_way`、**不給程式**,審有沒有漏狀態、有沒有偏向程式、`one_way` 有沒有少標;審過把 `accept_review` 寫成 `agent:<模型>`。單向門情境要人點頭,`accept_review.by` 必須是 `human:<名字>`(決策 d2)。**人點頭要在跑整套驗收之前做**:簽名會改 e2e 段、讓先跑的紀錄失效。
   6. 新畫面一律開新情境,不塞進既有情境(既有情境不溯及既往、不做逐句對照,塞進去等於躲開檢查)。
   7. e2e.flows 列的是驗收流程,一定要有檢查;只做前置(登入、清資料)的步驟寫成子流程用 runFlow 引進來,不列進 e2e.flows。
3. **流程裡標對應**:每個檢查加 `label: "驗收:<功能>.<情境>#<id>"`;一個檢查只對一句。
4. **judge 記事實**(只在整套跑寫紀錄時做:新情境、新流程一定改到 e2e 段,推送檢查一定要整套紀錄,按功能跑的紀錄用不到):
   - **怎麼找執行紀錄**:範本腳本每次嘗試已經有獨立的 debug 目錄(`<run>/ui/<名>.try<N>/debug`),改成把這個路徑寫進 steps.json 那次嘗試的 `evidence.debug`;judge 只讀這個路徑底下**唯一的那個子目錄**裡的 commands.json。子目錄零個或超過一個、檔不在、讀不懂,都記 `checks: null` 加原因。judge 不讀 flow 的 YAML、不猜 `name:`。
   - **怎麼數**:遞迴走完 commands.json 的每一層(runFlow 引進來的子流程、repeat、retry 裡的指令照算),指令是 `assertConditionCommand`(assertVisible、assertNotVisible、extendedWaitUntil 都落在這)、`assertScreenshotCommand`,以及 assertTrue 對應的指令,而且狀態是 `COMPLETED`;`WARNED`、`SKIPPED`、AI 類檢查(預設 optional、結果不穩定)不算。`count` 是算數的執行次數(repeat 會讓它變大,只用來判「是不是 0」與提醒),`labels` 是去重後的清單、上限沿用同一級。巢狀層數與檔案大小給專用上限(實作第 0 步量過實際形狀再定,不沿用 `_e2e_load_json` 的 20 層),超過記 `checks: null`。巢狀形狀、assertTrue 與 assertNotVisible 的實際指令名在第 0 步實測後寫進這節(S14)。
   - **寫在哪**:查證紀錄 `runs.blocks.ui` 那支 flow 的新欄位 `checks: {"count": <整數>, "labels": [<字串>…]}`,或 `checks: null` 與 `checks_reason`;`_e2e_record_err` 同步驗這兩欄的型別(判定會讀的欄位在那裡驗,跟既有慣例一致)。
   - judge 的過與不過照原本規則,不因檢查數改判;只在終端多印一段預覽(零檢查的流程、有 `accept` 的情境沒對到的句子),註明「哪些會擋由推送檢查依主線判」。預覽與推送檢查用**同一支**逐句對照函式,不寫兩份。
5. **推送檢查判,只對新開發的情境與流程**(決策 d1):
   - **位置**:接在讀進紀錄之後、放行判斷與「整套通過就放行」之前;CI 裡不判、`LUMOS_SKIP_ANDROID_E2E=1` 整道略過,都跟現行同一條路。放行只有人放的(`by` 是 human)蓋得過這幾條;AI 放行蓋不過——這幾條的成因是設定與流程內容,不是裝置狀態造成的誤擋,AI 自己補檢查、補驗收句就解得開,而單向門要人點頭(d2)本來就不能由 AI 代簽。
   - **新舊怎麼認**:流程路徑先照既有的正規化(`_e2e_norm`)再比。「新流程」= 主線與分岔點的 `e2e.flows` 都沒有這支檔。「新情境」= 主線與分岔點的 `e2e.features` 都沒有這個 `<功能>.<情境>`;**但主線與分岔點都還沒有 features 表時**(專案第一次導入功能對照表),情境底下的 flow 全是舊流程的,算舊情境。用推送檢查既有的挑主線結果;主線判不出來照那道判定原本的規則(判不清就擋);主線根本沒有 e2e 段時那道判定本來就不跑(不需要驗收),新規則也不跑,這是第一次導入 E2E 的分支,沒有主線可比。
   - **逐句對照只對有 flows 的新情境**:只列截圖、效能或記憶體、沒有 flows 的新情境,沒有可以帶 label 的地方,不要求 `accept`(那幾塊各有自己的判準);`one_way` 照樣必填、單向門照樣要人點頭。
   - 對新的項目,下面任一成立就擋:
     - 新流程在紀錄裡 `checks.count` 是 0 →「這支流程沒有任何檢查」。
     - 新流程 `checks` 是 null,或紀錄裡根本沒有 `checks` 欄(舊版 lumos 寫的)→「讀不到執行紀錄:<原因>」;沒有欄位的原因寫「紀錄是舊版 lumos 寫的,更新 lumos 後重跑」。
     - 有 flows 的新情境沒有 `accept` →「新情境要先寫驗收句」。
     - 新情境的某一句,在這個情境所有 flow 的 `checks.labels` 聯集裡找不到 `驗收:<功能>.<情境>#<id>` →「A<n> 沒有檢查對到」。
     - label 的前綴指到一個新情境、但那個情境沒有這個 id,或指到根本不存在的情境 →列出那個 label(打錯字會讓句子看似有人管)。前綴指到舊情境的 label 不管(共用流程裡別的情境的 label 不算多餘)。
     - 新情境沒寫 `one_way` →「新情境要宣告碰哪幾類單向門(一類都不碰寫 [])」。
     - 新情境是單向門(第 6 條)而 `accept_review.by` 不是 `human:` 開頭 →印命中的類別與字。
   - **擋下訊息與下一步**:這幾條各自一個擋下代碼,寫進治理帳的 `gate_code`(撤除條件要數);下一步印「改設定或流程再跑整套」,不印整套重跑就好的那一行,也不附 AI 放行的指令。訊息裡的 label 與驗收句文字走既有的外來文字出口(`_out_clean`),條數超過上限只印前幾條加總數。
6. **單向門怎麼認**:新情境的 `one_way` 宣告是主要來源,審驗收句的代理看著需求核它;另有一層機械地板——功能名、情境名、任一驗收句的 `text`,用規格閘的同一支掃描(`_door_keyword_hits`,含它的全形與零寬字元正規化)比對,只留 payment、external-send、prod-irreversible 三類的命中(不取第四類 self-governance:那是工具鏈自己的守衛面,跟 App 功能無關)。命中的類別一律併進宣告(作者只能往嚴標),合起來不是空的就是單向門。這張表是為計劃散文寫的,認不得「付款、結帳、刪除、發送」這類 UI 用詞(2026-10-31 實跑全部零命中),所以靠宣告加代理審補;**不為了這裡擴表**:擴表會同時改變規格閘與 pitfalls 對每份計劃的判法,要另案問 Enzo。
7. **檢查數變少只提醒**:推送時,對這次紀錄裡有 `checks` 的 flow,用分岔點那棵樹的 e2e 段算指紋,在被推送提交的樹裡找 `.lumos/e2e-records/<指紋>.json`;找得到、同一支 flow 也有 `checks`、而且數量比這次多,就列出「<flow> 檢查從 5 個變 2 個」,不擋(刪檢查有時是合理的;repeat 次數改了也會讓數字變)。找不到紀錄或舊紀錄沒有 `checks` 欄,印一行「分岔點沒有可比的紀錄,這次不比」——分岔點那一版的紀錄常常沒進這棵樹,這行會常出現,只是提醒。
8. **舊項目只列出**:推送時列出主線上已經有、但沒有 `accept` 的有 flows 舊情境,以及紀錄裡 `checks.count` 是 0 的舊流程(各列名字,超過上限只列前幾個加總數),不擋;舊情境自己補了 `accept`,就照第 5 條判。這幾行與第 7 條的行在放行時也要印:以「提醒」開頭,接進推送檢查放行路徑既有的提醒出口。

## 待決問題

題目、建議答案與自答出處在開頭欄位 `pending_questions`(`lumos show` 看得到);Q1、Q2 的題目文字是當時的建議(裡面的 accept_required、risk 都沒採用),以裁定後的決策 d1(不溯及既往)、d2(單向門要人點頭)為準。

## 驗收條款

- [S1] 當一支 flow 通過、那次嘗試的 debug 目錄底下唯一的子目錄裡,commands.json 有兩個 COMPLETED 的 assertConditionCommand(一個帶 label、一個不帶,其中一個在 runFlow 子流程裡)時,judge 寫的查證紀錄裡那支 flow 應有 `checks.count` 為 2、`checks.labels` 只含那一個 label [test:t_android_e2e_checks_recorded]
- [S2] 當檢查加了 `optional: true` 而失敗(WARNED)、在條件不成立的 runFlow 裡沒跑到(不出現),或是 AI 類檢查時,judge 不應把它算進 `checks.count` [test:t_android_e2e_checks_warned_skipped_ai_not_counted]
- [S3] 當通過的那次嘗試 steps.json 沒有 `evidence.debug`、debug 目錄底下沒有或有兩個以上子目錄、commands.json 不在、讀不懂或超過巢狀與大小上限時,judge 應記 `checks: null` 與原因,UI 那塊的過與不過照原本規則 [test:t_android_e2e_checks_unreadable_null]
- [S4] 當查證紀錄的 `checks` 不是物件也不是 null、`count` 不是整數或 `labels` 不是字串清單時,`_e2e_record_err` 應判紀錄讀不懂,推送檢查走既有「修好或刪掉紀錄」那條路,不在判定內部出例外 [test:t_android_e2e_record_checks_type]
- [S5] 當新流程的 `checks.count` 是 0,或 `checks` 是 null,或紀錄裡沒有 `checks` 欄時,推送檢查應擋下並分別印「這支流程沒有任何檢查」、讀不到的原因、「紀錄是舊版 lumos 寫的,更新 lumos 後重跑」 [test:t_android_e2e_gate_new_flow_checks]
- [S6] 當有 flows 的新情境沒有 `accept`,或任何新情境沒寫 `one_way` 時,推送檢查應擋下並印對應原因;只列截圖、效能或記憶體的新情境沒有 `accept` 不應因此擋 [test:t_android_e2e_gate_new_case_requires_accept]
- [S7] 當新情境的某一句在它所有 flow 的 label 聯集裡找不到,或有 label 前綴指到新情境卻沒有那個 id、或指到不存在的情境時,推送檢查應擋下並分別列出;前綴指到舊情境的 label 不應因此擋;每一句都對到時不因此擋 [test:t_android_e2e_gate_accept_coverage]
- [S8] 當新情境的 `one_way` 非空,或功能名、情境名、驗收句經規格閘同一支掃描命中 payment、external-send 或 prod-irreversible,而 `accept_review.by` 不是 `human:` 開頭時,推送檢查應擋下並印命中的類別與字;只命中 self-governance 的字不算單向門;全形或夾零寬字元的關鍵字照樣命中 [test:t_android_e2e_gate_one_way_needs_human]
- [S9] 當新規則擋下、而這一版有 AI 放行(by 是 ai)時,推送檢查仍應擋;有人放行(by 是 human)時應放行;整套通過的紀錄不應讓新規則被跳過 [test:t_android_e2e_gate_new_rules_order_and_waiver]
- [S10] 當情境或流程在主線與分岔點已經存在(流程路徑正規化後比),或主線與分岔點都沒有 features 表而情境底下全是舊流程時,推送檢查都不應因此擋,而應在放行時也印出沒有 `accept` 的舊情境與零檢查的舊流程 [test:t_android_e2e_gate_legacy_listed_not_blocked]
- [S11] 當分岔點的紀錄裡同一支 flow 的 `checks.count` 比這次多時,推送檢查應印出前後數量但不擋;找不到紀錄或舊紀錄沒有 `checks` 欄時,印「分岔點沒有可比的紀錄,這次不比」 [test:t_android_e2e_gate_check_count_drop_notice]
- [S12] 當新規則擋下時,擋下訊息的下一步不應印整套重跑那一行或 AI 放行指令,治理帳應記對應的 `gate_code` [test:t_android_e2e_gate_new_rules_next_step]
- [S13] 當 `accept`、`accept_review` 或 `one_way` 格式不對(accept 是空清單、缺 id、id 重複或含英數字以外的字、text 空、by 不是 agent: 或 human: 開頭、at 不是 YYYY-MM-DD、one_way 有三個值以外的字或不是清單)時,`lumos macrobench --check-config` 應回 2 並印出哪一項壞,推送檢查讀到同樣的設定也應擋而不是出例外;三個鍵都不寫的舊設定照舊回 0 [test:t_android_e2e_accept_config_strict]
- [S14] 當實作開始時,應先在實機上實測 assertNotVisible、extendedWaitUntil、assertTrue、assertScreenshot 在 commands.json 裡的指令名與狀態、runFlow 子流程與 repeat 的巢狀形狀與層數,寫進〈做法〉第 4 條並據此定巢狀與大小上限 [manual:SM-X710 上跑一支探針流程,結果寫進本計劃]
- [S15] 當在 macrobench-lab 開一個新情境、照實測那組重跑(清單頁改壞、流程拿掉檢查)時,推送檢查應擋下;補回帶 label 的檢查、App 改回正常、重跑驗收後應放行 [manual:SM-X710 上跑兩次並各推一次到本機假遠端,結果寫進驗證紀錄]

## 實務隱患

- 已排除:金流:只改驗收判定、推送檢查與設定格式,不碰任何付款或點數程式
- 已排除:對外送出:判定只讀本機的 Maestro 執行紀錄,不送資料到外部服務
- 已排除:不可逆:拿掉新規則的程式就回到現在的行為;查證紀錄只多 `checks` 一欄,舊紀錄沒有這欄只影響新流程(S5)
- 守衛面:命中。推送檢查決定擋不擋;寫錯會放行沒驗過的流程(S2、S3、S5、S9 守),或把好的、舊的流程誤擋(S6 後半、S7 後半、S10 守)。照走設計審。
- 單向門的機械地板認不得一般 UI 用詞(付款、結帳、刪除、發送),主要靠 `one_way` 宣告與審驗收句的代理;作者宣告 `[]` 又剛好避開表上的字,機械上擋不到——這是單人自用、不防刻意偽造的威脅模型下的天花板。反方向,「送出」「對外」這類字在點餐、廚房顯示這種 App 很常見,會讓很多情境要人點頭,這是 Enzo 裁的代價(寧可多問)。
- 不溯及既往的漏洞:把新畫面塞進既有情境、不開新情境,就能躲開逐句對照;機械上分不出「新畫面」,靠程序寫明「新畫面開新情境」與推送時的舊項目清單看得到。
- 本機驗收時與推送時看到的主線可能不同(中間合併過主線):以推送時為準,judge 的預覽只是預覽。
- Maestro 的執行紀錄格式不是公開合約,改版可能改指令名、欄位或目錄;讀不懂一律記 `checks: null`,新流程因此被擋(S5),不能當成零檢查或全通過。
- 資源:commands.json 可能很大或巢狀很深(repeat、子流程),讀檔有專用的大小與層數上限;labels 去重並設上限,紀錄不會被撐過既有的單檔上限。

## 回退

- 零檢查與讀不到執行紀錄兩條,不靠任何新鍵,對所有採用 E2E 的專案的新流程都生效;要撤只能還原工具鏈的程式。
- 專案層:情境拿掉三個新鍵,就不做逐句對照;但新情境的 `one_way` 必填,拿掉會被擋(要撤也只能還原工具鏈)。
- 工具鏈層:還原 judge 記 `checks` 的一段、範本腳本記 `evidence.debug` 的一行、推送檢查新增的那幾條與設定檢查;既有查證紀錄多出的 `checks` 欄被忽略即可。

## 落點

- [[Systems/android-e2e-acceptance]]:新判定、新設定鍵、紀錄的 `checks` 欄寫進這篇;要改的 lumos-android-evidence 技能檔,實作時加進這篇的 about_code(2026-10-31 查,它還不屬於任何 Systems 節點)。
- [[Systems/規格閘]]:補一行「Android 端到端驗收的單向門判定是這張關鍵字表的第三個消費者,改表會同時改變 Android 新情境要不要人點頭」。
- lumos-project-notes 的〈產 maestro UI flow 的派工要求〉:第 1 段(斷言)與第 4 段(完成判準)補驗收句與 label;第 5 段「斷言被刪掉不會有任何機械檢查翻紅」改寫成「新流程零檢查會被擋、新情境要逐句對到;舊流程照舊」。

## 審計修正紀錄

- r1(2026-10-31,4 席:正確性、邊界、整合、架構對齊,全 sonnet):41 條(major 15、minor 26,有大量重複)/blocking 15/結論:兩段分工站得住,但新判定的插入位置、執行紀錄怎麼找、紀錄型別驗證、單向門詞表漏報、新舊認定的邊界都沒定;依根因分九組全折,minor 部分附理由放行。席報告在 governance/review-reports/ui流程驗收句與檢查對照/。
- 新增機制前的「最小解為什麼不夠」:
  - `evidence.debug`(範本腳本多記一個路徑):不加的話 judge 要從 flow 的 YAML 猜 `name:`,lumos 沒有 YAML 解析器、`name:` 缺省時目錄名不明,四席都點到。
  - `one_way` 必填:不加的話單向門只靠詞表,詞表認不得付款、結帳、刪除、發送(實跑零命中);擴表會改變規格閘對所有計劃的判法,範圍更大。
  - 新規則專用的擋下代碼:不加的話擋下訊息會沿用「整套重跑」的處方(重跑解不開),撤除條件也數不到。
