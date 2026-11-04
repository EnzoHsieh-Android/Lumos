---
type: project
status: done
created: 2026-10-31
updated: 2026-11-01
tags:
  - type/project
  - status/done
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
  - content: 新規則的擋下沿用端到端驗收現行的放行規則:人或 AI 都能放行,AI 放行照舊標成 AI 放的、在推送開場與體檢持續列出直到人確認;不另立「只有人放行蓋得過」的第二套放行語意
    id: d3
    context: 設計審 r2 架構對齊席指出 r1 折入的「只有人放行蓋得過新規則」是第二套放行語意;回滾席與通才席指出讀不到執行紀錄常是工具太舊造成、AI 補檢查解不開,只准人放行會讓無人看顧時卡死。考慮過:A 沿用現行;B 新規則只准人放行
    why_chosen: Enzo 2026-10-31 在 A、B 兩案中選「Ａ」。一套放行規則、跟 2026-10-25「AI 能放行,但要通知你」一致、無人看顧不卡死。代價:單向門情境也能先由 AI 放行,人點頭變成事後確認
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
- **執行紀錄看得到 label 與結果**:系統設定 App 上一支探針流程(`name: label_probe`),照範本腳本同一組旗標(`--test-output-dir <ev> --debug-output <ev>/debug --flatten-debug-output`)跑,執行紀錄落在 `<ev>/debug/label_probe/commands.json`(依 flow 的 `name:` 分子目錄;`<ev>` 底下沒有另一份)。裡面有 label 的 `assertVisible` 記成 `assertConditionCommand`、label 原樣在、狀態 `COMPLETED`;加了 `optional: true` 而失敗的記成 `WARNED`;條件不成立的 `runFlow` 記成 `SKIPPED`、裡面的檢查不出現。所以「真的跑過、真的通過」讀執行紀錄就分得出來。judge 不依賴 `name:`(見做法第 4 條,只讀唯一子目錄),所以中文 `name:` 的子目錄命名不用測。

## 做法

分兩段:**判定(judge)只記事實**——每支流程跑過哪些算數的檢查、各帶什麼 label;**推送檢查才判擋不擋**——它本來就讀得到主線與分岔點的設定([[Systems/android-e2e-acceptance]] 的推送判定),所以「哪些情境是新的」在這裡算。judge 拿不到主線(它的輸入只有 run 目錄與專案根),硬在 judge 裡判新舊要另寫一套挑主線的邏輯、本機與推送時還可能算出不同結果。

1. **設定格式**:`.lumos/macrobench.json` 的 `e2e.features.<功能>.cases.<情境>` 多三個選填鍵:
   - `accept`:清單,寫了就至少一項;每項 `{"id": "A1", "text": "<這種情況下使用者應該看到什麼>", "state": "<畫面狀態,選填,例:空清單、網路錯誤、正常>"}`。`id` 在同一情境內唯一、只收英數字;`text` 非空;`state` 只給審驗收句的代理對照「每種狀態都有一句」,判定不讀它、只驗是字串。條數與字數上限沿用 e2e 段既有清單的上限(`E2E_PATH_LIST_MAX` 那一級)。
   - `accept_review`:`{"by": "human" 或 "ai", "who": "<人名,或審查代理的模型名>"}`,`by` 的值跟放行紀錄同一套(human/ai);`who` 放行紀錄的 AI 放行固定寫 ai,這裡寫模型名,因為要看出是哪個代理審的(日期不另記,看 git 提交時間)。
   - `one_way`:這個情境碰哪幾類單向門,值是 `payment`、`external-send`、`prod-irreversible` 的清單,一類都不碰寫 `[]`;**新情境必填**(見第 6 條)。
   - 格式檢查放在 e2e 段共用的設定檢查(`--check-config` 與推送檢查都走同一支),推送檢查讀到提交樹裡格式壞的設定要擋,不能在判定內部出例外。現在的情境檢查不擋未知鍵,所以要新增;舊版 lumos 讀到新鍵會靜默忽略。e2e 段整段算進指紋,三個鍵改了,舊的通過紀錄自然失效、要重跑。
2. **寫驗收句的程序**(寫進 lumos-android-evidence 的端到端驗收一節與 lumos-project-notes 的〈產 maestro UI flow 的派工要求〉,是程序;其中「新情境要有審查紀錄」有機械地板,見第 5 條):
   1. 先讀需求,再讀這個情境畫面的程式(Compose 或 Activity/Fragment、對應的 ViewModel)。
   2. 從程式列出畫面所有狀態與分支(正常、空、載入中、錯誤、輸入不合法、權限被拒…),每一種寫一句驗收句。
   3. **預期結果照需求寫,不照程式抄**;程式跟需求對不上的地方標出來問人,不寫成驗收句(否則把錯的行為鎖成對的)。程式只拿來找分支、拿確切文字與元件識別名。
   4. 照需求判這個情境碰哪幾類單向門,寫進 `one_way`。
   5. 另派一個代理,只給需求、驗收句與 `one_way`、**不給程式**,審有沒有漏狀態、有沒有偏向程式、`one_way` 有沒有少標;審過把 `accept_review` 寫成 `{"by": "ai", "who": "<模型>"}`。單向門情境要人點頭,`by` 必須是 `human`(決策 d2)。**人點頭要在跑整套驗收之前做**:簽名會改 e2e 段、讓先跑的紀錄失效。
   6. 新畫面一律開新情境,不塞進既有情境(既有情境不溯及既往、沒寫 `accept` 就不做逐句對照,塞進去等於躲開檢查;既有情境自己補了 `accept` 才逐句對照,見第 5 條)。
   7. e2e.flows 列的是驗收流程,一定要有檢查;只做前置(登入、清資料)的步驟寫成子流程用 runFlow 引進來,不列進 e2e.flows。
3. **流程裡標對應**:每個檢查加 `label: "驗收:<功能>.<情境>#<id>"`;一個檢查只對一句。
4. **judge 記事實**(`_e2e_judge_ui` 兩條路共用,兩條路都算 checks;寫進查證紀錄的只有整套那一份的 `runs.blocks.ui`,按功能跑的紀錄 `feature_runs` 不記,只出現在預覽與本機檢測總表——推送檢查只讀整套紀錄,因為新情境、新流程一定改到 e2e 段、一定要整套):
   - **怎麼找執行紀錄**:取通過的那一次嘗試(第一次紅、第二次過時取第二次)。範本腳本每次嘗試的現場目錄已經記在 steps.json 那次嘗試的 `evidence.dir`(每次嘗試各自一個目錄),debug 目錄固定是它底下的 `debug`(範本腳本就是這樣組的);judge 只讀 `<evidence.dir>/debug` 底下**唯一的那個子目錄**裡的 commands.json。`evidence.dir` 是空(Maestro 太舊沒帶旗標、範本腳本是舊版、不是用範本腳本跑的)、子目錄零個或超過一個、檔不在、讀不懂,都記 `checks: null` 加 `checks_reason`(給人看的字串)與 `checks_reason_code`(下面〈成因與處方〉表裡的代碼之一,判定只看代碼、不比對字串)。judge 不讀 flow 的 YAML、不猜 `name:`。
   - **怎麼數**:commands.json 最外層是**攤平的清單**,子流程、repeat、retry 裡的每一次執行各自一筆、用 `metadata.depth` 標層次;父指令(runFlow、repeat)的內容裡另帶同一批指令的副本,那些副本沒有執行狀態,不算、也不往裡找(往裡找會重複計數)。逐筆看最外層清單:指令是 `assertConditionCommand`(assertVisible、assertNotVisible、extendedWaitUntil、assertTrue 都落在這)或 `assertScreenshotCommand`,而且 `metadata.status` 是 `COMPLETED`;`WARNED`、`SKIPPED`、AI 類檢查(預設 optional、結果不穩定)不算。`count` 是算數的執行次數(repeat 會讓它變大,只用來判「是不是 0」與提醒),`labels` 是去重後的清單,**不截斷**:去重後超過上限(沿用 `E2E_PATH_LIST_MAX` 那一級)就整支記 `checks: null`、代碼 `too_many_labels`——截斷會讓被截掉的句子被誤判成沒對到。讀檔沿用 `_e2e_load_json`,給它加兩個選填參數:巢狀層數(預設維持 20)與 `limit`(檔案大小上限,名稱沿用 `_e2e_tree_json` 的 `limit`;讀之前先看檔案大小,預設不限),這裡傳實作第 0 步量過的值,不另寫讀法;`_e2e_record_update` 讀之前自己看大小的那處不動。超過記 `checks: null`、代碼 `too_deep` 或 `too_big`。實測(2026-11-01,SM-X710、Maestro 2.10.0,S14):一支 18 步的探針(assertVisible、assertNotVisible、extendedWaitUntil、assertTrue 各一,runFlow 檔案子流程一層、repeat 兩次包 runFlow 內嵌一層、assertWithAI 一個)的 commands.json 是 18 筆的攤平清單、13KB、JSON 巢狀 13 層;四種檢查都記成 `assertConditionCommand` 且 label 原樣在,子流程與 repeat 裡的檢查各自一筆(depth 1、2),assertWithAI 記 `assertWithAICommand` 狀態 `WARNED`。據此定上限:巢狀層數 64、檔案大小 16MB(都遠高於實測、只擋病態輸入)。assertScreenshot 這次沒量(要基準圖),指令名照前掃在本機舊樣本看到的 `assertScreenshotCommand`。
   - **寫在哪**:查證紀錄 `runs.blocks.ui` 那支 flow 的新欄位 `checks: {"count": <整數>, "labels": [<字串>…]}`,或 `checks: null` 加 `checks_reason`;`_e2e_record_err` 驗 `checks`、`count`、`labels`、`checks_reason`、`checks_reason_code` 五者的型別(代碼要在表裡)(判定會讀的欄位在那裡驗,跟既有慣例一致;它也是寫入端的把關,寫壞了放行也寫不進去)。**查證紀錄的格式版本跟 steps.json 的拆開**:現在 `E2E_SCHEMA` 同時是兩者的版本,judge 要求 steps.json 的版本完全相等,範本腳本寫死 1;只升這個常數會讓所有還沒更新範本腳本的專案驗收整條失效。所以 `E2E_SCHEMA`(steps.json 的版本)維持 1、範本腳本不動;另開查證紀錄自己的版本號 `E2E_RECORD_SCHEMA`,升到 2,`_e2e_record_err` 收 1 到 2,推送檢查判「這份紀錄比較新」的那一行改用它(不然版本 2 而別處壞掉的紀錄會被誤判成較新、叫人更新 lumos),`E2E_SCHEMA` 的註解改成只講 steps.json;judge 寫紀錄時不論新建或更新一律把版本寫成 2(現在更新既有檔時版本欄不動,要改)。舊版 lumos 讀到 2 的紀錄走既有的「這份紀錄是比較新的 lumos 寫的:更新 lumos,紀錄不要動」,不會把新紀錄覆寫成沒有 `checks` 的舊形狀。
   - judge 的過與不過照原本規則,不因檢查數改判;預覽(零檢查的流程、有 `accept` 的情境沒對到的句子)走 judge 既有的 `notices`,註明「哪些會擋由推送檢查依主線判」。預覽與推送檢查用**同一支**逐句對照函式,不寫兩份。
5. **推送檢查判,只對新開發的情境與流程**(決策 d1):
   - **位置**:放行判斷之後、整套通過那一刻——推送判定現在的順序是先看放行(有就直接放行回傳),再看整套紀錄,整套通過才放行;新規則放在整套通過、宣告放行之前。所以:整套沒跑、整套沒過、紀錄讀不懂這些既有情況照舊由原本的路處理、原本的訊息先講,新規則不搶先(不然會把「要整套驗收」講成別的原因);有放行(人或 AI,AI 放行照舊持續列出)時在放行那一步就回傳,新規則與第 7、8 條的提醒都不算、不印(放行本身已經被列出等人看);CI 裡不判、`LUMOS_SKIP_ANDROID_E2E=1` 整道略過,都跟現行同一條路(決策 d3)。
   - **新舊怎麼認**:流程路徑一律先照既有的正規化(`_e2e_norm`)再比,情境的 flows 對到紀錄裡的 flow 條目也一樣。「新流程」= 主線與分岔點的 `e2e.flows` 都沒有這支檔。「新情境」= 主線與分岔點的 `e2e.features` 都沒有這個 `<功能>.<情境>`;**但主線與分岔點都還沒有 features 表時**(專案第一次導入功能對照表),有 flows、而且 flows 全是舊流程的情境算舊情境;沒有 flows 的情境、或有任一新流程的情境算新情境。用推送檢查既有的挑主線結果;主線判不出來照那道判定原本的規則(判不清就擋);主線根本沒有 e2e 段時那道判定本來就不跑(不需要驗收),新規則也不跑,這是第一次導入 E2E 的分支,沒有主線可比。
   - **舊情境自己補了 `accept`**:只做逐句對照(「A<n> 沒有檢查對到」照擋),不要求 `accept_review` 與 `one_way`、不判單向門——那兩條是新情境的地板,舊情境不溯及既往(決策 d1 寫「照新規則判」,這裡收窄成只做逐句對照,理由同上)。
   - **逐句對照遇到讀不到的 flow**:情境裡任一支 flow 的 `checks` 是 null(不管新舊流程),這個情境的逐句對照判「判不出」,不報「A<n> 沒有檢查對到」,改歸到「沒有檢查」那類、印那支 flow 的原因與處方(見〈成因與處方〉)——不然真正的病因(讀不到執行紀錄)會被講成驗收句沒對到。
   - **逐句對照只對有 flows 的新情境(與補了 `accept` 的舊情境)**:只列截圖、效能或記憶體、沒有 flows 的新情境,沒有可以帶 label 的地方,不要求 `accept`(那幾塊各有自己的判準);`one_way` 照樣必填、單向門照樣要人點頭。
   - 對新的項目,下面任一成立就擋,擋下代碼分三類(同一次推送多類同時成立,訊息全列,`gate_code` 記最前面那類、`extra` 新增一個鍵 `accept_classes` 記全部類別,撤除條件照全部類別數):
     - **沒有檢查**(`e2e_accept_no_checks`):新流程 `checks.count` 是 0 →「這支流程沒有任何檢查」;新流程 `checks` 是 null →「讀不到執行紀錄:<原因>」;紀錄裡這支新流程沒有 `checks` 欄 →「紀錄裡沒有檢查欄:這份紀錄可能是舊版 lumos 寫或覆寫的,更新 lumos 後重跑整套」。
     - **驗收句沒對到**(`e2e_accept_uncovered`):有 flows 的新情境沒有 `accept` →「新情境要先寫驗收句」;沒有 `accept_review` →「新情境的驗收句要先另派代理審過」;某一句在這個情境所有 flow 的 `checks.labels` 聯集裡找不到 `驗收:<功能>.<情境>#<id>` →「A<n> 沒有檢查對到」。label 打錯字的情況由這一條接住(正確的 label 不在聯集裡),不另外檢查多餘或指錯的 label。
     - **單向門沒人點頭**(`e2e_accept_one_way`):新情境沒寫 `one_way` →「新情境要宣告碰哪幾類單向門(一類都不碰寫 [])」;新情境是單向門(第 6 條)而 `accept_review.by` 不是 `human` →印命中的類別與字。
   - **擋下訊息與下一步**:擋下報告帶一個新旗標,`_cl_say_e2e_next` 照它分派(跟既有的 `bad_record`、`newer_schema` 同一種做法),不走整套重跑那一行。各條的處方照下面〈成因與處方〉表印。表把擋下原因分成兩種:**工具類**(讀不到執行紀錄的各種代碼,補內容解不開)附既有的放行指令;**內容類**(零檢查、沒有驗收句、沒有審查紀錄、句子沒對到、沒宣告單向門、單向門沒人點頭)印「改設定或流程再跑整套」,不附放行指令(放行照樣有效,只是不推薦)。同一次推送裡只要有任何一條內容類擋下就不附(先把內容改好);全部是工具類才附。放行指令現在是在擋下訊息外層、照「有指紋、不是讀不懂的紀錄、不是較新版本的紀錄」這個條件另外印的(不在 `_cl_say_e2e_next` 裡),所以要改的是那個條件;新旗標由擋下報告帶,`_cl_say_e2e_next` 的新分派排在按功能判那條之前。
   - **〈成因與處方〉**(judge 寫的 `checks_reason_code` 與推送檢查的處方一對一;新增代碼時這張表與 S5 的測試一起改):
     - `no_evidence`(`evidence.dir` 是空:Maestro 沒有現場旗標、範本腳本是舊版、不是用範本腳本跑的)→「升級 Maestro 到 2.x、跑 lumos update 更新範本腳本,再重跑整套」,附放行。
     - `subdir_count`(debug 底下沒有或超過一個子目錄)、`missing`(commands.json 不在)→「範本腳本與 lumos 版本可能不一致或現場被動過:跑 lumos update 後重跑整套」,附放行。
     - `unreadable`(commands.json 讀不懂或指令形狀認不得)→「Maestro 的執行紀錄格式可能改了:回報工具鏈;確認是工具問題才放行」,附放行。
     - `too_deep`、`too_big`、`too_many_labels`(超過上限)→「把流程拆小再重跑整套;確定合理才放行」,附放行。
     - `no_checks_field`(推送檢查讀到的紀錄裡這支 flow 沒有 `checks` 欄;不是 judge 寫的代碼)→「紀錄可能是舊版 lumos 寫或覆寫的:更新 lumos 後重跑整套」,附放行。訊息裡的 label 與驗收句文字走既有的外來文字出口(`_out_clean`),條數超過上限只印前幾條加總數。
6. **單向門怎麼認**:新情境的 `one_way` 宣告是主要來源,審驗收句的代理看著需求核它;另有一層機械地板——功能名、情境名、每一句驗收句的 `text` 各自當一行,用規格閘的同一支掃描(`_door_keyword_hits`,含它的全形與零寬字元正規化)比對;它回的是中文類名,只留「金流、對外送出、不可逆」三類(對應 payment、external-send、prod-irreversible,用規格閘既有的類名對照表換回英文鍵),不取「守衛面」(self-governance:工具鏈自己的守衛面,跟 App 功能無關)。命中的類別一律併進宣告(作者只能往嚴標),合起來不是空的就是單向門。這張表是為計劃散文寫的,認不得「付款、結帳、刪除、發送」這類 UI 用詞(2026-10-31 實跑全部零命中),所以靠宣告加代理審補;**不為了這裡擴表**:擴表會同時改變規格閘與 pitfalls 對每份計劃的判法,要另案問 Enzo。
7. **檢查數變少只提醒**:推送時,對這次紀錄裡有 `checks` 的 flow,用分岔點那棵樹的 e2e 段算指紋(`_e2e_fingerprint` 現成),在被推送提交的樹裡用既有的讀法(`_e2e_tree_json` 加 `_e2e_record_err`)找 `.lumos/e2e-records/<指紋>.json`;找得到、同一支 flow 也有 `checks`、而且數量比這次多,就列出「<flow> 檢查從 5 個變 2 個」,不擋(刪檢查有時是合理的;repeat 次數改了也會讓數字變)。分岔點那棵樹沒有 e2e 段(分支切出時還沒導入 E2E)時不算指紋;它跟找不到、讀不懂、舊紀錄沒有 `checks` 欄一樣,一律印一行「分岔點沒有可比的紀錄,這次不比」,不擋——分岔點那一版的紀錄常常沒進這棵樹,這行會常出現,只是提醒(Enzo 同意「檢查變少要點名」,所以保留,見 Q5)。
8. **舊項目只列出**:推送時列出主線上已經有、但沒有 `accept` 的有 flows 舊情境,以及紀錄裡 `checks.count` 是 0 的舊流程(各列名字,超過上限只列前幾個加總數),不擋;舊情境自己補了 `accept`,就照第 5 條判。這幾行與第 7 條的行在整套通過時印:以「提醒」開頭,接進推送檢查既有的提醒出口(`_cl_say_e2e_notes` 現在只在 CI、略過、按功能通過與 AI 放行待看時印,要擴到整套通過);有放行時不算也不印(見第 5 條〈位置〉),只有一個算的地方。

## 待決問題

題目、建議答案與自答出處在開頭欄位 `pending_questions`(`lumos show` 看得到);Q1、Q2 的題目文字是當時的建議(裡面的 accept_required、risk 都沒採用),以裁定後的決策 d1(不溯及既往)、d2(單向門要人點頭)為準。d2 原文寫的 `accept_review.by 必須是 human:` 是 r1 的前綴寫法,r2 起改成 `by` 為 `human`(見做法第 1 條),判定照正文;放行規則另見決策 d3。

## 驗收條款

- [S1] 當一支 flow 通過、那次嘗試 `<evidence.dir>/debug` 底下唯一的子目錄裡,commands.json 有兩個 COMPLETED 的 assertConditionCommand(一個帶 label、一個不帶,其中一個在 runFlow 子流程裡)時,judge 寫的整套查證紀錄裡那支 flow 應有 `checks.count` 為 2、`checks.labels` 只含那一個 label;第一次紅、第二次過時取第二次那個目錄 [test:t_android_e2e_checks_recorded]
- [S2] 當檢查加了 `optional: true` 而失敗(WARNED)、在條件不成立的 runFlow 裡沒跑到(不出現),或是 AI 類檢查時,judge 不應把它算進 `checks.count` [test:t_android_e2e_checks_warned_skipped_ai_not_counted]
- [S3] 當通過的那次嘗試 `evidence.dir` 是空、debug 目錄底下沒有或有兩個以上子目錄、commands.json 不在、讀不懂、超過巢狀或大小上限,或去重後的 label 超過上限時,judge 應記 `checks: null` 與寫明哪一種的原因(label 不截斷),UI 那塊的過與不過照原本規則 [test:t_android_e2e_checks_unreadable_null]
- [S4] 當查證紀錄的 `checks` 不是物件也不是 null、`count` 不是整數、`labels` 不是字串清單或 `checks_reason` 不是字串時,`_e2e_record_err` 應判紀錄讀不懂,推送檢查走既有「修好或刪掉紀錄」那條路,不在判定內部出例外;查證紀錄的版本是 2 而 lumos 只認 1 時走既有「更新 lumos、紀錄不要動」那條路;judge 更新既有的版本 1 紀錄時應把版本寫成 2;範本腳本寫的 steps.json 版本 1 照舊被 judge 接受 [test:t_android_e2e_record_checks_type]
- [S5] 當整套紀錄通過、新流程的 `checks.count` 是 0,或 `checks` 是 null(〈成因與處方〉表的每一個代碼各一例),或沒有 `checks` 欄時,推送檢查應以「沒有檢查」擋下並照表印各自的處方;只有工具類擋下時附放行指令,同一次有任一條內容類擋下時不附 [test:t_android_e2e_gate_new_flow_checks]
- [S6] 當有 flows 的新情境沒有 `accept` 或沒有 `accept_review`,或任何新情境沒寫 `one_way` 時,推送檢查應擋下並印對應原因;只列截圖、效能或記憶體的新情境沒有 `accept` 不應因此擋 [test:t_android_e2e_gate_new_case_requires_accept]
- [S7] 當新情境的某一句在它所有 flow 的 label 聯集(flows 路徑正規化後對接)裡找不到時,推送檢查應擋下並列出缺的句子編號;每一句都對到時不因此擋,流程裡多出指到其他情境或不存在情境的 label 也不因此擋;舊情境補了 `accept` 時同樣逐句對照,但不因沒有 `accept_review` 或 `one_way` 而擋;情境裡有任一支 flow 的 `checks` 是 null 時,不報句子沒對到,改照那支 flow 的代碼印讀不到的處方 [test:t_android_e2e_gate_accept_coverage]
- [S8] 當新情境的 `one_way` 非空,或功能名、情境名、驗收句經規格閘同一支掃描命中金流、對外送出或不可逆,而 `accept_review.by` 不是 `human` 時,推送檢查應擋下並印命中的類別與字;只命中守衛面的字不算單向門;全形或夾零寬字元的關鍵字照樣命中 [test:t_android_e2e_gate_one_way_needs_human]
- [S9] 當這一版沒有整套紀錄、或整套沒過時,推送檢查應照原本的路印原本的訊息,新規則不應搶先;有放行(人或 AI)時應在放行那一步放行、不算新規則也不印第 7、8 條的提醒,AI 放行照舊被列為待人看 [test:t_android_e2e_gate_new_rules_order_and_waiver]
- [S10] 當情境或流程在主線與分岔點已經存在(流程路徑正規化後比),或主線與分岔點都沒有 features 表而情境有 flows 且全是舊流程時,推送檢查都不應因此擋,而應在整套通過時印出沒有 `accept` 的舊情境與零檢查的舊流程;第一次導入 features 表時沒有 flows 的情境應算新情境、要寫 `one_way` [test:t_android_e2e_gate_legacy_listed_not_blocked]
- [S11] 當分岔點的紀錄裡同一支 flow 的 `checks.count` 比這次多時,推送檢查應印出前後數量但不擋;分岔點沒有 e2e 段、找不到、讀不懂或舊紀錄沒有 `checks` 欄時,印「分岔點沒有可比的紀錄,這次不比」且不擋、不出例外 [test:t_android_e2e_gate_check_count_drop_notice]
- [S12] 當新規則擋下時,擋下訊息的下一步不應印整套重跑那一行,只有讀不到執行紀錄那支附放行指令(多類同時擋下而有一類不附就不附),治理帳應記對應類別的 `gate_code`;多類同時成立時訊息全列、`extra.accept_classes` 記全部類別 [test:t_android_e2e_gate_new_rules_next_step]
- [S13] 當 `accept`、`accept_review` 或 `one_way` 格式不對(accept 是空清單、缺 id、id 重複或含英數字以外的字、text 空、state 不是字串、by 不是 human 或 ai、who 空、one_way 有三個值以外的字或不是清單)時,`lumos macrobench --check-config` 應回 2 並印出哪一項壞,推送檢查讀到同樣的設定也應擋而不是出例外;三個鍵都不寫的舊設定照舊回 0 [test:t_android_e2e_accept_config_strict]
- [S14] (2026-11-01 已實測,結果見做法第 4 條)當實作開始時,應先在實機上實測 assertNotVisible、extendedWaitUntil、assertTrue、assertScreenshot 在 commands.json 裡的指令名與狀態、runFlow 子流程與 repeat 的巢狀形狀與層數,寫進〈做法〉第 4 條並據此定巢狀與大小上限 [manual:SM-X710 上跑一支探針流程,結果寫進本計劃]
- [S15] 當在 macrobench-lab 開一個新情境、照實測那組重跑(清單頁改壞、流程拿掉檢查)時,推送檢查應擋下;補回帶 label 的檢查、App 改回正常、重跑驗收後應放行 [manual:SM-X710 上跑兩次並各推一次到本機假遠端,結果寫進驗證紀錄]

## 實務隱患

- 已排除:金流:只改驗收判定、推送檢查與設定格式,不碰任何付款或點數程式
- 已排除:對外送出:判定只讀本機的 Maestro 執行紀錄,不送資料到外部服務
- 已排除:不可逆:還原工具鏈的程式就回到現在的行為;專案留著新鍵也無妨(舊版 lumos 忽略)
- 守衛面:命中。推送檢查決定擋不擋;寫錯會放行沒驗過的流程(S2、S3、S5 守),或把好的、舊的流程誤擋(S6 後半、S7 後半、S9、S10 守)。照走設計審。
- 放行蓋得過新規則(決策 d3):單向門情境也能先由 AI 放行,人點頭變成事後確認;AI 放行照舊在推送、開場、體檢持續列出直到人確認。
- 非單向門情境的「另派代理審」,機械上只驗 `accept_review` 存在,不驗真的有另一個代理審過——單人自用、不防刻意偽造的威脅模型下的天花板。
- 單向門的機械地板認不得一般 UI 用詞(付款、結帳、刪除、發送),主要靠 `one_way` 宣告與審驗收句的代理;作者宣告 `[]` 又剛好避開表上的字,機械上擋不到——同一個天花板。反方向,「送出」「對外」這類字在點餐、廚房顯示這種 App 很常見,會讓很多情境要人點頭,這是 Enzo 裁的代價(寧可多問)。
- 不溯及既往的漏洞:把新畫面塞進既有情境、不開新情境、也不補 `accept`,就能躲開逐句對照(補了 `accept` 反而會被逐句對照);機械上分不出「新畫面」,靠程序寫明「新畫面開新情境」與推送時的舊項目清單看得到。
- 本機驗收時與推送時看到的主線可能不同(中間合併過主線):以推送時為準,judge 的預覽只是預覽。
- Maestro 的執行紀錄格式不是公開合約,改版可能改指令名、欄位或目錄;讀不懂一律記 `checks: null`,新流程因此被擋(S5),處方指向升級工具並允許放行。
- 資源:commands.json 可能很大或巢狀很深(repeat、子流程),讀檔有專用的層數與大小上限;labels 去重並設上限,紀錄不會被撐過既有的單檔上限。

## 回退

- 先退專案、後退工具鏈都行,兩層獨立:
  - 工具鏈層:還原 judge 記 `checks` 的一段、推送檢查新增的三類、設定檢查與查證紀錄版本升版;專案裡留著的三個新鍵舊版 lumos 會忽略。代價:升版後寫的紀錄版本是 2,退版的 lumos 讀到會要求「更新 lumos」,所以退版後要把那些紀錄重跑一次(或刪掉重跑)。
  - 專案層:新規則只看新情境與新流程,專案沒辦法用拿掉新鍵來關掉它(有 flows 的新情境不寫 `accept` 會被擋、不寫 `one_way` 也會被擋);專案層的出口只有既有的放行與 `LUMOS_SKIP_ANDROID_E2E=1`。
- 任何改動新鍵的動作都會改 e2e 段、讓既有通過紀錄的指紋失效,要整套重跑實機;拿掉新鍵來回退也一樣。

## 落點

- [[Systems/android-e2e-acceptance]]:新判定、新設定鍵、紀錄的 `checks` 欄與查證紀錄版本 2(steps.json 維持 1)寫進這篇;[[Projects/Android端到端驗收_計劃]] 寫「steps.json 第一版是 1」那句仍成立,不用改;要改的 lumos-android-evidence 的 SKILL.md 實作時加進這篇的 about_code(2026-11-01 已加);lumos-project-notes 的 reference.md 是跨主題的通用參考,只改〈產 maestro UI flow 的派工要求〉一節,不掛進這篇(掛了以後改那份檔的任何一節都會把這篇推到眼前)。
- [[Systems/規格閘]]:補一行「Android 端到端驗收的單向門判定是這張關鍵字表的第三個消費者,改表會同時改變 Android 新情境要不要人點頭」。
- lumos-project-notes 的〈產 maestro UI flow 的派工要求〉:第 1 段(斷言)與第 4 段(完成判準)補驗收句與 label;第 5 段天花板那句(`[kill:]` 第三階在 UI 層走不通、斷言被刪掉不會有任何機械檢查翻紅)保留原句——有檢查的流程刪掉一條檢查仍然不會紅——在它後面另補一句「例外:新流程整支零檢查會被擋、新情境的每一句驗收句要有檢查對到」。

## 不做

- 判斷檢查「有沒有驗到重點」(語意判斷,交給審驗收句的代理與代碼審)。
- 新畫面自動升成代碼審(Enzo 2026-10-31 否決)。
- 截圖比對的門檻與基準圖規則(另有 [[Projects/截圖基準驗收流程_計劃]])。
- 為單向門擴充規格閘的關鍵字表(會改變所有計劃的判法,另案問 Enzo)。

## 審計修正紀錄

- r1(2026-10-31,4 席:正確性、邊界、整合、架構對齊,全 sonnet):41 條(major 15、minor 26,有大量重複)/blocking 15/結論:兩段分工站得住,但新判定的插入位置、執行紀錄怎麼找、紀錄型別驗證、單向門詞表漏報、新舊認定的邊界都沒定;依根因分九組全折;放行 3 條 minor:人名自填不防偽造(單人自用信賴原則)、舊版 lumos 混用(符號連結分發、舊紀錄缺欄已由新流程擋下)、算數指令集待第 0 步實測(本來就排在實作前)。席報告在 governance/review-reports/ui流程驗收句與檢查對照/。
- r1 新增機制前的「最小解為什麼不夠」:
  - `one_way` 必填:不加的話單向門只靠詞表,詞表認不得付款、結帳、刪除、發送(實跑零命中);擴表會改變規格閘對所有計劃的判法,範圍更大。
  - 新規則專用的擋下代碼:不加的話擋下訊息會沿用「整套重跑」的處方(重跑解不開),撤除條件也數不到。
  - (r1 另加的 `evidence.debug` 在 r2 拿掉:既有的 `evidence.dir` 加固定的 `debug` 就推得出來。)
- r2(2026-10-31,4 席:通才、回滾、簡化、架構對齊,全 sonnet,只看 r1 修正差異加全文):28 條(major 7、minor 21)/blocking 7/結論:r1 折入自己帶進新洞——新規則排在整套判定前面會搶先講錯原因、「只有人放行」是第二套放行語意(Enzo 裁沿用現行,決策 d3)、讀不到執行紀錄的處方錯、回退一節漏了指紋全數失效、多餘的「指錯 label」規則會誤擋;另收斂成三類擋下代碼、拿掉 `evidence.debug` 與審查日期、`accept_review` 改用放行紀錄同形的 by/who、紀錄格式升 schema 2、補回 r1 誤刪的〈不做〉;放行 2 條 minor:`one_way` 必填維持(強迫作者與審查代理看一眼,d2 的地板)、檢查數變少的提醒維持(Enzo 同意要點名,雖然常印「不比」)。
- r3(2026-10-31,4 席:正確性、邊界、整合、架構對齊,全 sonnet,末輪驗收,只掃 blocking 級與 r2 修正):22 條(blocker 1、major 4、minor 17)/blocking 5/結論:r2 折入的「紀錄格式升版」誤用了 steps.json 共用的版本號(三席獨立指出,blocker),改成兩個版本號拆開;另修放行路徑提早回傳造成提醒印不出(改成放行時不算不印、只有一個算的地方)、舊情境補 accept 的判法前後矛盾(改成只做逐句對照)、label 截斷造成誤擋(改成不截斷、超過整支記讀不到)、分岔點沒有 e2e 段時算指紋會出例外;其餘 minor 全折(放行指令的印法要改外層條件、by 值改成 human/ai 跟放行紀錄同一套、讀檔加大小參數、d2 原文前綴寫法加註、reference.md 天花板句改成補一句不取代)。達三輪上限;r3 折入沒有再派席審,實作時由代碼審把關。
- r4(2026-11-01,人裁破例加開一輪,2 席:正確性、架構對齊,只審 r3 修正差異):5 條(major 2、minor 3)/blocking 2/結論:兩條 major 是同一族——讀不到執行紀錄的原因有七種、處方只配了兩種,舊流程讀不到時逐句對照會講成句子沒對到;照跑滿回顧的教訓一次改成〈成因與處方〉對照表(原因改成結構化代碼、每個代碼一個處方、工具類附放行、內容類不附),不再逐條補;另修新常數命名與「較新紀錄」判斷改用它、讀檔大小參數沿用 `limit`、程序第 6 點與 d1 收窄的說明、不溯及既往漏洞那句。人裁(選一)寫明折完就停,這輪折入不再派席審,剩下交代碼審。

