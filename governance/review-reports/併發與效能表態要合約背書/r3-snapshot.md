---
type: project
status: doing
created: 2026-10-01
updated: 2026-10-01
aliases:
  - 表態要合約背書
  - 沒問題要有證據
  - 併發效能合約背書
  - contract-backed disposition
related:
  - "[[Projects/棧別提問表態閘_計劃]]"
  - "[[Systems/棧別提問表態閘]]"
  - "[[Systems/guard-kill]]"
  - "[[Systems/bound-tests-gate]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Projects/規模影響判斷力假說]]"
  - "[[Projects/收斂機制優化調研2026-08-14]]"
lands_in:
  - Systems/棧別提問表態閘
  - Systems/guard-kill
tags:
  - type/project
  - status/doing
  - scope/guards-gates
summary: |-
  WHY:[2026-10-01 Enzo 問「審查鏡頭的併發鏡頭聲稱沒有問題的話,我想掛壓測當合約應該怎麼做?」,接著問「效能類呢?」]查證結果:審查席交 clean 只驗格式與留痕、不驗證據;棧別提問表態的 satisfied 只驗 path:line 或測試名存在。「沒問題」這句話今天沒有任何行為層證據
  WHY:[2026-10-01 本對話裁定]形狀=在既有表態閘上加一層,不另起新閘——只對「併發正確性」與「效能可數化」兩類題,satisfied 要指向一支在「這一版程式」上做過破壞測試、每條涵蓋這題的壞法都被抓到的測試;其他表態(na/todo/tension)照舊可用,誠實說做不到的路永遠在
  WHY:[2026-10-01 本對話裁定]效能只收「次數型」(查詢次數、外呼次數、載入筆數),不收毫秒——毫秒隨機器浮動,推送前會隨機擋;破壞測試把逾時一律記弱證據,「變慢」本來就證不出咬得住
  WHY:[2026-10-01 設計審 r1 六席折入]背書改成「寫表態時在本機對破壞測試紀錄算一次、結果存進表態記錄」——不新增治理帳事件種類,推送前檢查只讀表態記錄裡已算好的背書,不讀帳、不跑 git
  WHY:[2026-10-01 設計審 r2 六席折入]背書要綁程式版本:破壞測試那次的 HEAD 必須就是被表態的版本,或兩者之間只動了簿記檔——直接用表態與審查留痕共用的 `_codeloop_record_valid` 判,不另寫一套;配方要有身分(invariant、檔、原文三者的雜湊),同一配方在有效版本上只要有一次不是強證據就不算;拿掉 off/warn 開關,只跟著表態閘開關走
  RULE:[since:2026-10-01][retire:照 RETIRE-IF 撤掉,或第 8 週人裁另開計劃升級成擋]只提醒不擋;v1 沒有獨立開關,`stack_questions.gate` 關掉表態閘時一起不提醒
  REVISIT:2026-11-26 上線滿 8 週(日期照今天估;實作推上主線晚於 2026-10-01 就照上線日順延):Enzo 在手上有觸發這八題的消費專案各跑一次 lumos gov --stats,看被標題目的表態分布與背書數,依 RETIRE-IF 判撤、留、或另開計劃升擋(升擋前必須先解〈天花板〉)
---
# 併發與效能表態要合約背書_計劃

> 白話:推送前,工具會對這次改動丟出「併發會不會壞」「會不會 N+1」等檢核題(本案要管的八題見〈哪些題目要背書〉),要人或 AI 表態。今天回答「已處理」只要附一個檔案行號或測試名字就過了,等於說「我看過了,沒問題」。這份計劃讓其中兩類題目(併發正確性、效能可數化)的「沒問題」要有一條合約背書:合約綁一支測試,這支測試在這一版程式上做過破壞測試(故意把保護拿掉,它真的會紅),而且那條壞法宣告過它涵蓋的就是這一題。做不到的就老實表態成「待辦」或「不適用」。v1 只提醒、不擋。

## 緣起與現況

- 使用者的問題(2026-10-01):併發鏡頭說沒問題時,怎麼掛壓測當合約;效能類怎麼辦。
- 查證(獨立 agent 用原始問題查,不帶結論):
  - 審查席交 `severity: clean`:處置閘對零發現輪視同全處置、引句檢查略過(`_loop_status_disposal`);席位編制表 `_TIER_ROSTER` 裡只有資安席是「必派而且處置閘會擋」,其他鏡頭席缺席只提醒。
  - 表態閘的 satisfied:`_dispositions_check_test` 只驗測試名在工作樹與推送樹找得到,不驗它守什麼、會不會紅。技能文件的說法(`skills/lumos-code-loop/SKILL.md` 表態那段):工具只驗證據存在,不驗答案對不對。
  - 破壞測試(`cmd_guard_kill`)能證「這支測試咬得住這種壞法」,但只寫 `docs/.kill-log.jsonl`;消費專案 init 時會把這個檔寫進 docs 目錄下的忽略清單(`_scaffold_project` 寫帳檔忽略清單那段),CI 讀不到;本 repo 沒有那份忽略清單、帳檔都被追蹤,但也只有 4 筆紀錄。
  - 綁定測試閘(`_run_bound_tests`)單支預設 180 秒逾時,逾時判紅。
- 已知同源問題:[[Projects/規模影響判斷力假說]] 記「一個自信的『沒問題』會直接餵進收斂帳」;[[Projects/收斂機制優化調研2026-08-14]] 候選④「收斂該錨行為訊號(測試),非對話共識」。
- 用量現況(設計審 r1 簡化席實數):本 repo 治理帳 56 筆表態事件只涵蓋五題 Python 題,被標的八題觸發 0 次;本 repo 是 Python,八題永遠不會在這裡觸發,效用要在消費專案量。

PRIOR-ART: ①同 repo:表態閘的 satisfied/na/todo/tension 四態、寫表態時先驗形狀再寫帳與標記、改碼後表態過期要重表態,以及表態與審查留痕共用的版本有效性判定 `_codeloop_record_valid`([[Projects/棧別提問表態閘_計劃]]);破壞測試的配方與七態判定([[Systems/guard-kill]]);`lumos gov --stats` 已按題目 id 統計表態狀態。②世界解:併發正確性業界靠「強制交錯」而非隨機壓測當證據——Java jcstress、Rust loom、Go `-race`、決定性模擬;效能迴歸在單元層的做法是斷言次數(Django `assertNumQueries`、Rails `assert_queries_count`、Hibernate statistics),絕對延遲交給固定機器的效能 CI 與生產監控;變異測試(mutation testing)證明測試咬得住。③結論:不新建閘、不新建治理帳事件、不新建測試種類、不新寫版本有效性判定;只在寫表態那一刻多查一次破壞測試紀錄,把結果隨表態存下來。

RETIRE-IF: 上線 8 週內出現任一種就撤掉這層(拿掉判定與提醒、保留配方的涵蓋欄位):①被標題目的表態裡,走 na、todo 或 tension 繞開的比例超過八成,而且抽 10 筆看理由多半是「寫合約太貴」而非「真的不適用」——代表成本壓過價值;②使用者回報的誤提醒多過因此補上合約的次數;③所有有觸發的消費專案合計,8 週內被標題目的人工表態少於 5 次——量太小,維護成本大於價值。量法:REVISIT 那天由 Enzo 在手上有接 Lumos、而且會觸發這八題的消費專案各跑一次 `lumos gov --stats`,人工加總。分母=上線後、被標題目、人工表態(不含自動記的未觸發)的事件;「有背書」只算其中 status=satisfied 且 backing=strong 的,缺 backing 欄位的(上線前寫的)不算進分母。

## 做法

用詞:**強證據**=破壞測試七種判定(killed、killed_unattributed、timed_out_weak、survived、drifted、abort、error)裡的 `killed`,而且那次不是「整套測試一起跑」(沒法確認紅的就是那支測試)也不是有 `flaky_risk` 的平台;**次數型**=斷言某個動作做了幾次(查詢、對外呼叫、載入筆數),不斷言花了多久;**配方**=`lumos guard kill-add` 宣告的一條壞法(改哪支檔、把什麼換成什麼);**配方身分**=invariant、file、old 三者合起來的雜湊,跟 `cmd_guard_kill_add` 判「同一條配方」用的鍵相同;**有效版本**=破壞測試那次的 HEAD,經 `_codeloop_record_valid` 判定對被表態的版本有效(同一版,或是它的祖先且中間只動簿記檔)。

### 哪些題目要背書

在 `_STACK_QUESTION_SPECS` 的題目上加一個欄位 `needs_backing: True`(不叫 evidence,避免跟表態記錄裡的 evidence 同名不同義)。入選判準:這題的主問能用「最終狀態斷言」或「次數斷言」寫成測試,而且有一條可以宣告的壞法(拿掉鎖/交易/唯一鍵/冪等檢查,或把批次改回逐筆)。v1 標八題:

- **併發正確性**:`swift-concurrency`、`java-concurrency`、`fe-race`、`sql-transaction`。
- **效能可數化**(N+1、大查詢):`sql-nplus1`、`cs-data`、`node-data`、`java-data`。

說明:
- `sql-*` 兩題的證據用應用程式那一端的測試(例如在 Java 或 C# 測試裡數查詢次數),寫成 `test:<平台>:<名>`;SQL 本身不必是測試平台。
- `java-concurrency`、`sql-transaction`、`cs-data`、`node-data`、`java-data` 是複合題(一題問好幾件事)。背書只證明「配方宣告涵蓋的那一面」咬得住,不代表整題都答完;提醒與派工單都寫成「涵蓋一面」並列出壞法說明。v1 仍收這幾題,因為應用程式裡的 N+1 是在 `java-data`、`cs-data`、`node-data` 觸發,只收單一面向的題會漏掉最常見的情況。
- 設計審 r1 整合席列了其他同類候選(`py-parallel`、`node-parallel`、`kt-coroutines`、`cs-async`、`py-memory`、`vue-watch`、`dart-async`):v1 不收,因為它們的主問是「有沒有並行、有沒有上限、記憶體」,多半寫不成最終狀態或次數斷言;8 週量完再決定要不要擴。

判定端用 `_stack_spec_by_id(<題目id>)` 查這個欄位,不改 `_stack_applicability` 產生的 meta 形狀。沒標的題目行為完全不變。

### 配方宣告它涵蓋哪一題

- `lumos guard kill-add` 多一個選填參數 `--covers <題目id>[,<題目id>…]`,存進配方的 `covers`(清單)。每個 id 用 `_stack_spec_by_id` 驗:不存在或沒標 `needs_backing` 的擋下並列出可用的 id;重複的去重;空字串擋下。
- **補既有配方**:`kill-add` 遇到同一條配方(invariant、file、old 都相同)時,現行是擋下要人先手動拿掉;改成「這次有帶 `--covers`、其他欄位完全相同」就只更新那條的 `covers`,印出更新前後,其餘情況照舊擋。
- `cmd_guard_kill` 寫 `.kill-log.jsonl` 時,每筆多四個欄位,其他欄位(含既有的 `commit`)語意不變:
  - `covers`:配方宣告的題目 id 清單(沒宣告就是空清單)。
  - `recipe`:配方身分雜湊。
  - `head_sha`:那一組平台跑破壞測試時的完整 HEAD(存在每一筆自己身上,不是迴圈外的共用變數);這一筆若在建沙盒前就出錯,記空字串。
  - `weak`:那次是整套測試一起跑(run_cmd 沒有 `{method}`)或平台有 `flaky_risk` 時為 true。
- 寫 kill-log 前,檔案若不是以換行結尾(上次寫到一半被中斷),先補一個換行,免得新的一批接在殘行後面整行壞掉。
- 讀 kill-log 的解析抽成一支共用函式(放在破壞測試那一帶),寫表態用它;`Systems/guard-kill` 記明 kill-log 有兩個讀者(gov 統計與這支)。

### 寫表態時算背書,存進表態記錄

`lumos code-loop dispositions <檔>`(`_cmd_codeloop_dispositions`)驗完形狀、寫帳之前,先把每一題表態裡的 `backing` 欄位全部拿掉(不信任手填或 `--carry` 帶來的值),再對每一題「標了 needs_backing、而且 status=satisfied」的表態算一次。整段包在 try 裡:任何例外都記 `backing={"status":"none","reason":"讀取失敗"}`,照常寫帳,不讓一個只提醒的功能擋住寫表態。

1. evidence 不是 `test:` 開頭 → none,原因「讀程式碼不算行為證據」。
2. 用 `_dispositions_split_test` 把 evidence 拆成(平台, 方法名),方法名用 kill 同一套正規化(去平台前綴、去 Kotlin 反引號)。
3. 讀本機 `docs/.kill-log.jsonl`:沒有檔或空檔 → none,原因「本機沒有破壞測試紀錄」;逐行解析,不是合法 JSON 或不是物件的行略過;`covers` 不是清單就當空清單。
4. 留下「platform 對得上、`test` 正規化後的方法名對得上、`head_sha` 經 `_codeloop_record_valid` 對這次表態的版本有效」的紀錄;一筆都沒有 → none,原因「沒有在這一版程式上跑過的破壞測試」(若平台或名字都對不上,原因改成「平台或名字對不上」)。
5. 把留下的紀錄按配方身分分組,每組看**最後一筆**的 `covers` 有沒有這一題;沒有任何一組涵蓋 → none,原因「沒有涵蓋這題的配方」。
6. 涵蓋這一題的每一組,組內**每一筆**都要是 `killed` 且 `weak` 不是 true;任一筆不是 → none,原因「有一次不是強證據」(同一版程式上重跑到碰巧紅,也洗不掉先前的 survived)。
7. 都過 → `backing={"status":"strong","recipes":[…]}`,每組記 node、invariant、head_sha 前 8 碼、ts、配方的壞法說明(note 截到 80 字、去掉換行)。

之後照既有流程先寫治理帳的 `kind=dispositions` 事件、再原子寫標記。CI 讀得到這筆事件,但 CI 只能相信記錄下來的結果、不能自己重算(見〈天花板〉第 3 條)。

### 推送前檢查只讀記錄好的背書

`_dispositions_verdict` 在 satisfied 分支(不是共用的 `_ev`,所以 tension 不受影響),對標了 needs_backing 的題看表態記錄裡的 `backing`,整段包在 try 裡、例外一律當「沒有背書」處理,絕不丟到外層被接成擋下:
- `status` 是 `strong` → 不多說。
- 其他(`none`、缺欄位、形狀壞)→ 放進 `out["warnings"]`(不進 `problems`、不改 `blocked`、不改回傳碼),code-loop check 印成「提醒:」,附原因與補救步驟(見〈教人怎麼寫測試〉的順序)。

這一步只讀已經載入的表態記錄,不增加推送前的時間。

### 過期

版本綁定在第 4 步:破壞測試那次的 HEAD 必須對被表態的版本有效。之後改了測試或受測程式,破壞測試紀錄就不再有效,要重跑破壞測試再重表態。表態記錄本身也照 `_codeloop_record_valid` 在改碼後失效。kill-log 自己是簿記檔,之後把它提交不會讓紀錄或表態失效。

### 開關

v1 沒有獨立開關:`stack_questions.gate` 為 `off`,或為 `high-only` 且這次不是高風險時,`_dispositions_verdict` 本來就提早結束,背書提醒也不印;寫表態時照樣算背書(成本是讀一次本機檔)。嫌提醒吵又不想關表態閘,就是 RETIRE-IF ② 要量的訊號。

### 派工鏡頭

表態記錄已經帶著 `backing`,派工鏡頭照現行只讀標記。`_lens_dispositions_lines` 每行現在會截到 200 字;背書註記接在截斷**之後**另起一段,不佔那 200 字:「背書:強證據,涵蓋一面(N 條配方;第一條:<note 前 40 字>)」或「背書:沒有(<原因>)」。表頭那句「答案對不對沒人驗」改成「被標的八題另看破壞測試背書(只提醒)」。快取鍵照舊用表態記錄的 sha256——背書改變時記錄內容就變,鍵自然跟著變。

### 教人怎麼寫測試

補救順序(提醒與技能文件照這個寫):寫次數或併發測試 → `guard kill-add --covers <題目id>`(既有配方同一指令只更新 covers)→ 把測試、程式、含配方的筆記一起提交(要壓提交就先壓)→ `guard kill` → 重表態。筆記不是簿記檔,破壞測試之後才提交筆記,紀錄就對不上這一版。

要同步改的位置(上線後舊說法會變錯的都列進來,共九處):
1. `skills/lumos-code-loop/SKILL.md` 表態那段「工具只驗證據存在…不驗答案對不對」旁補被標八題的例外。
2. `skills/lumos-code-loop/reference.md` 兩處同義句(「工具驗證據存在、不驗答案對錯」那句與表態流程那句)。
3. `skills/lumos-project-notes/reference.md` 的 `guard kill-add` 說明:加 `--covers` 與「同一配方只更新 covers」。
4. 同一份 reference 寫合約那節加一小段怎麼寫測試:併發用同步起跑讓請求同時撞進來、斷言最終狀態不斷言時間、最穩是在讀與寫之間留測試用暫停點強制交錯,配方拿掉鎖、交易、唯一鍵或冪等檢查;效能斷言查詢或外呼次數、資料量從 10 變 100 時次數不變,配方把批次改回逐筆;絕對延遲不收,寫成 `RULE:` 加 `FACT:[來源:生產]` 交給效能 CI 或監控;以及上面的補救順序。
5. `skills/lumos-project-notes/commands/06-代碼審與推送.md` 指令表與 `commands/INDEX.md` 的 guard 那列。
6. `scripts/lumos` 裡 `kill-add` 的參數說明與派工鏡頭表頭字串。
7. `Systems/棧別提問表態閘`、`Systems/guard-kill` 兩篇的現況行。
8. `Systems/效能檢核目錄` 的消費專案設定段:補一句被標八題會看背書。
9. 全域紀律範本(`scripts/templates/graph-discipline.md`)不提表態與破壞測試,不用改;`slim/` 已凍結,不用改(r2 整合席查過)。

## 天花板(v1 承認、不處理)

1. **偶發才紅的測試**:同一版程式上,破壞測試若每次都碰巧紅,仍會拿到強證據;只要有一次 survived 就不算(第 6 步),但從沒碰巧綠過的偶發測試抓不出來。技能文件要求強制交錯以降低;重跑機制屬於破壞測試本身,另案。
2. **涵蓋是作者宣告的**:`--covers` 是寫配方的人自己宣告的,工具只驗 id 存在,不判那條壞法跟題目真的有關;派工單印出壞法說明,交審查席看。
3. **CI 只能相信記錄**:背書是在本機算的,CI 讀到的是記下來的結果,不能重算;手改治理帳就能偽造(跟其他表態內容一樣)。消費專案的 kill-log 不進版控,換一台機器或新 clone 重表態會算成「沒有背書」。升級成擋之前,要先設計 CI 自己能驗的方式。
4. **多平台的兩個邊角**:平台根在另一個 repo 時,那邊的 HEAD 在本 repo 驗不了版本,一律算沒有背書;多平台專案的配方若測試名帶平台前綴卻沒給 `--platform`,破壞測試會在預設平台跑,紀錄的平台對不上,算沒有背書——提醒原因會寫「平台或名字對不上」。
5. **已刪掉的配方**:在同一版程式上跑過、之後才從筆記刪掉的配方,它的紀錄仍會被算進去,直到程式再改一版。
6. 以上任一條沒解,就不升級成擋。

## 不做

- 不驗審查席的 clean 報告本身(那是處置閘的事,另案)。
- 不在推送前自動跑破壞測試;不在推送前讀破壞測試紀錄或治理帳。
- 不新增治理帳事件種類、不改 `_KNOWN_GATES`、不改 kill-log 既有欄位(含 `commit`)的語意。
- 不收毫秒、吞吐量這類時間斷言當證據。
- 不新增測試種類或 profile。
- 不做擋下;不加獨立開關;升級另開計劃。
- tension 選 suggested 時附的 evidence 不要求背書(tension 本來就印 ⚠ 交人裁);RETIRE-IF 把 tension 算進繞開比例。

## 實務隱患

- 併發:破壞測試跑完整批才一次寫入,寫表態當下看不到正在跑的那一批——可能讀到同版程式上較早的 killed 而判 strong;這跟天花板第 1 條同源(同一版程式上一次 survived 就不算,但要等那一批寫進來)。寫到一半被中斷的殘行,下一批寫入前補換行,不會連累新紀錄。治理帳多個寫入者的問題([[Issues/治理帳多個寫入者都沒上鎖]])本案不新增寫入點。
- 效能:推送前檢查不增加任何讀取;寫表態時多讀一次 `.kill-log.jsonl`,並對每一筆對得上名字的紀錄跑一次 `_codeloop_record_valid`(同一個 head_sha 只跑一次)。
- 資源:無新檔案、無新行程。
- 相容:舊表態記錄沒有 `backing` 欄位 → 只提醒;舊配方沒有 `covers` → 不涵蓋任何題,只提醒,用 `kill-add --covers` 補;舊 kill-log 紀錄沒有 `head_sha` → 驗不了版本,不算。`lumos gov` 讀 kill-log 只取既有欄位,`commit` 語意不變,去重不受影響。
- 沒有圖譜的專案:[[Issues/沒有圖譜的專案答不完表態題]] 記了既有死結(沒有 docs/ 時表態根本寫不進去)。本案只在寫表態的路徑上加一步,不改那個死結,也不讓它更糟。
- 輸出純度:破壞測試的 `--json` 模式成功時 stdout 必須恰好一行 JSON(既有合約,[[Systems/guard-kill]]);多寫欄位與補換行都不印東西。

## 驗收條款

- [S1] 題目規格 應 能標 `needs_backing`,v1 標上面八題;拿一份觸發到未標題目的既有表態測試資料,寫表態與推送前檢查的結果 應 與改動前一致 [test:t_contract_backing_marked_questions]
- [S2] 當 `guard kill-add` 帶 `--covers`,配方 應 存下驗過的題目 id 清單,不存在或沒標 needs_backing 的 id 應 被擋下 [test:t_guard_kill_add_covers]
- [S3] 當 `guard kill-add` 遇到同一條配方且只多帶 `--covers`,工具 應 只更新那條的 covers [test:t_guard_kill_add_covers_update]
- [S4] 當破壞測試判完配方,kill-log 每筆 應 多出 covers、recipe、head_sha、weak 四欄,兩個平台 HEAD 不同時各記各的,既有 commit 欄 應 不變 [test:t_guard_kill_log_new_fields]
- [S5] 當 kill-log 結尾是半行,破壞測試 應 先補換行再寫新的一批 [test:t_guard_kill_log_repairs_partial_line]
- [S6] 若以 `--json` 跑破壞測試,stdout 應 仍只有一行 JSON [test:t_guard_kill_json_purity]
- [S7] 當寫表態時計算背書,結果 應 符合〈寫表態時算背書〉七步:path:line、沒有紀錄、版本無效、平台或名字不符、沒有涵蓋、同一配方有一次 survived、weak 為 true、兩條同檔不同原文的配方一條 survived,各判 none 並寫對原因;全數強證據判 strong [test:t_contract_backing_cases]
- [S8] 當樣板或 `--carry` 帶了 backing 欄位,寫表態 應 先全部拿掉再只為標了 needs_backing 的 satisfied 重算 [test:t_contract_backing_recomputed]
- [S9] 當算背書時發生例外,寫表態 應 記 none(讀取失敗)並照常寫帳與標記 [test:t_contract_backing_error_is_none]
- [S10] 若背書不是 strong、缺欄位或形狀壞,code-loop check 應 印提醒、放進 warnings、不改 blocked 與回傳碼 [test:t_contract_evidence_warn_only]
- [S11] 若 `stack_questions.gate` 為 off,code-loop check 應 不印背書提醒 [test:t_contract_evidence_follows_gate]
- [S12] 當派工鏡頭附上表態,被標題目的 satisfied 行 應 在 200 字截斷之後帶背書註記 [test:t_dispatch_lens_shows_contract_backing]
- [S13] 當 `lumos gov --stats` 印表態段,被標題目 應 依 RETIRE-IF 的分母定義多列有背書與沒有背書的次數 [test:t_gov_stats_contract_backing]
- [S14] 技能文件、指令表與筆記 應 照〈教人怎麼寫測試〉列的九處更新 [manual:逐一打開列出的九處,確認新說法與補救順序在、舊的只驗證據存在說法旁已補被標題目的例外、範例不含毫秒斷言]

## 回退

- 最快:專案把 `.lumos/config.json` 的 `stack_questions.gate` 設成 `off`,整個表態閘連同背書提醒都不跑(代價是其他表態也不檢查);或什麼都不做——它只提醒,不會擋住推送。
- 整個撤:還原實作那個功能提交即可。已寫進治理帳的表態事件多出的 `backing` 欄位、kill-log 多出的四個欄位與配方多出的 `covers`,舊程式都不讀(讀者只取自己認得的欄位);沒有外部要收拾的東西。

## 合約候選

- 寫表態時,背書一律重算,不信任樣板或 `--carry` 帶來的值。
- 背書只認在有效版本上跑的破壞測試,且涵蓋該題的每條配方在有效版本上的每一筆都是非弱的 killed。
- 推送前檢查的背書提醒不改變 blocked 與回傳碼(v1 只提醒)。

## 審計修正紀錄

- r1(2026-10-01,5 席+架構對齊):62 條/blocking 45 條/原設計「破壞測試寫新的治理帳事件、推送前讀帳判祖先與過期」被五席從不同角度打穿(事件寫不進帳、gov 算兩次、CI 讀不到、壓提交後失效、背書沒綁題目、只看配方檔),改成「寫表態時本機算背書、存進表態記錄、推送前只讀」;過期改沿用表態既有失效規則;砍 block 模式;配方加 `--covers` 綁題目;派工鏡頭改讀記錄內的背書、不動快取。席報告:`governance/review-reports/併發與效能表態要合約背書/`。
- r2(2026-10-01,5 席+架構對齊):57 條/blocking 24 條/新設計的核心洞是「背書是本機快照、沒綁程式版本」(四席各自抓到:舊紀錄、別的分支、測試改弱後重表態、CI 只能照單全收),改成用 `_codeloop_record_valid` 判破壞測試那次的 HEAD 對被表態版本有效;配方加身分雜湊(同檔不同原文不再併組)、改成「組內每一筆都要是非弱的 killed」(重跑洗不掉 survived、整套跑與 flaky 平台算弱);kill-add 同一配方可只更新 covers 並驗 id;背書計算與讀取都包 try,只提醒的功能不再可能擋住寫表態或推送;kill-log 補殘行換行、改成新增 head_sha 而不改 commit 語意;拿掉 off/warn 開關;補救順序補上「先提交再跑破壞測試」;同步清單改成九處;〈天花板〉改寫成五條(含 CI 只能相信記錄)。席報告:`governance/review-reports/併發與效能表態要合約背書/`。
