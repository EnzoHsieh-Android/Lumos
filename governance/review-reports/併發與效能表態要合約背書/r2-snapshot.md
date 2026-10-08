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
  WHY:[2026-10-01 本對話裁定]形狀=在既有表態閘上加一層,不另起新閘——只對「併發正確性」與「效能可數化」兩類題,satisfied 必須指向一支有破壞測試強證據、而且配方宣告涵蓋這一題的測試;其他表態(na/todo/tension)照舊可用,誠實說做不到的路永遠在
  WHY:[2026-10-01 本對話裁定]效能只收「次數型」(查詢次數、外呼次數、載入筆數),不收毫秒——毫秒隨機器浮動,推送前會隨機擋;破壞測試把逾時一律記弱證據,「變慢」本來就證不出咬得住
  WHY:[2026-10-01 設計審 r1 六席折入]背書改成「寫表態時在本機對破壞測試紀錄算一次、結果存進表態記錄」——不新增治理帳事件種類(五席抓到新事件寫不進帳、會被 gov 算兩次、CI 讀不到、壓提交後祖先判定失效),推送前檢查只讀表態記錄裡已算好的背書,不再讀帳、不跑 git;過期沿用表態既有的「改碼就要重表態」,不另寫一套過期判定
  RULE:[since:2026-10-01][retire:照 RETIRE-IF 撤掉,或上線 8 週後人裁另開計劃升級成擋]只提醒不擋;專案用 .lumos/config.json 的 stack_questions.contract_evidence 設 off|warn(預設 warn);v1 不做 block
  REVISIT:2026-11-26 上線第 8 週:用 lumos gov --stats 在有觸發的消費專案看被標題目的表態分布與背書比例,依 RETIRE-IF 判撤、留 warn、或另開計劃升擋(升擋前必須先解〈天花板〉三條)
---
# 併發與效能表態要合約背書_計劃

> 白話:推送前,工具會對這次改動丟出「併發會不會壞」「會不會 N+1」等檢核題(本案要管的八題見〈哪些題目要背書〉),要人或 AI 表態。今天回答「已處理」只要附一個檔案行號或測試名字就過了,等於說「我看過了,沒問題」。這份計劃讓其中兩類題目(併發正確性、效能可數化)的「沒問題」要有一條合約背書:合約綁一支測試,這支測試做過破壞測試(故意把保護拿掉,它真的會紅),而且那條壞法宣告過它涵蓋的就是這一題。做不到的就老實表態成「待辦」或「不適用」。v1 只提醒、不擋。

## 緣起與現況

- 使用者的問題(2026-10-01):併發鏡頭說沒問題時,怎麼掛壓測當合約;效能類怎麼辦。
- 查證(獨立 agent 用原始問題查,不帶結論):
  - 審查席交 `severity: clean`:處置閘對零發現輪視同全處置、引句檢查略過(`_loop_status_disposal`);席位編制表 `_TIER_ROSTER` 裡只有資安席是「必派而且處置閘會擋」,其他鏡頭席缺席只提醒。
  - 表態閘的 satisfied:`_dispositions_check_test` 只驗測試名在工作樹與推送樹找得到,不驗它守什麼、會不會紅。技能文件原文:「工具只驗證據存在,不驗答案對不對」。
  - 破壞測試(`cmd_guard_kill`)能證「這支測試咬得住這種壞法」,但只寫 `docs/.kill-log.jsonl`;消費專案 init 時會把這個檔寫進 docs 目錄下的忽略清單(`_scaffold_project` 寫帳檔忽略清單那段),CI 讀不到;本 repo 沒有那份忽略清單、帳檔都被追蹤,但也只有 4 筆紀錄。
  - 綁定測試閘(`_run_bound_tests`)單支預設 180 秒逾時,逾時判紅。
- 已知同源問題:[[Projects/規模影響判斷力假說]] 記「一個自信的『沒問題』會直接餵進收斂帳」;[[Projects/收斂機制優化調研2026-08-14]] 候選④「收斂該錨行為訊號(測試),非對話共識」。
- 用量現況(設計審 r1 簡化席實數):本 repo 治理帳 56 筆表態事件只涵蓋五題 Python 題,被標的八題觸發 0 次;本 repo 是 Python,八題永遠不會在這裡觸發,效用要在消費專案量。

PRIOR-ART: ①同 repo:表態閘的 satisfied/na/todo/tension 四態、寫表態時先驗形狀再寫帳與標記、改碼後表態過期要重表態([[Projects/棧別提問表態閘_計劃]]);破壞測試的配方與七態判定([[Systems/guard-kill]]);`lumos gov --stats` 已按題目 id 統計表態狀態。②世界解:併發正確性業界靠「強制交錯」而非隨機壓測當證據——Java jcstress、Rust loom、Go `-race`、決定性模擬;效能迴歸在單元層的做法是斷言次數(Django `assertNumQueries`、Rails `assert_queries_count`、Hibernate statistics),絕對延遲交給固定機器的效能 CI 與生產監控;變異測試(mutation testing)證明測試咬得住。③結論:不新建閘、不新建治理帳事件、不新建測試種類;只在寫表態那一刻多查一次破壞測試紀錄,把結果隨表態存下來。

RETIRE-IF: 上線 8 週內出現任一種就撤掉這層(拿掉判定與提醒、保留配方的涵蓋欄位):①被標題目的表態裡,走 na、todo 或 tension 繞開的比例超過八成,而且抽 10 筆看理由多半是「寫合約太貴」而非「真的不適用」——代表成本壓過價值;②使用者回報的誤提醒多過因此補上合約的次數;③所有有觸發的消費專案合計,8 週內被標題目的人工表態少於 5 次——量太小,維護成本大於價值。量法:在各消費專案跑 `lumos gov --stats` 看表態段按題目 id 的狀態分布(本案在該段多印「有背書/沒有背書」兩個數)。

## 做法

用詞:**強證據**=破壞測試七種判定(killed、killed_unattributed、timed_out_weak、survived、drifted、abort、error)裡的 `killed`,也就是綁定測試紅了、而且紅的就是那支測試;**次數型**=斷言某個動作做了幾次(查詢、對外呼叫、載入筆數),不斷言花了多久;**配方**=`lumos guard kill-add` 宣告的一條壞法(改哪支檔、把什麼換成什麼)。

### 哪些題目要背書

在 `_STACK_QUESTION_SPECS` 的題目上加一個欄位 `evidence: "contract"`。入選判準:這題的主問能用「最終狀態斷言」或「次數斷言」寫成測試,而且有一條可以宣告的壞法(拿掉鎖/交易/唯一鍵/冪等檢查,或把批次改回逐筆)。v1 標八題:

- **併發正確性**:`swift-concurrency`、`java-concurrency`、`fe-race`、`sql-transaction`。
- **效能可數化**(N+1、大查詢):`sql-nplus1`、`cs-data`、`node-data`、`java-data`。

說明:
- `sql-*` 兩題的證據用應用程式那一端的測試(例如在 Java 或 C# 測試裡數查詢次數),寫成 `test:<平台>:<名>`;SQL 本身不必是測試平台。
- `sql-transaction`、`cs-data`、`java-data` 是複合題(一題問好幾件事)。背書只證明「配方宣告涵蓋的那一面」咬得住,不代表整題都答完——派工單上會同時列出配方的壞法說明,讓審查席看得到涵蓋了哪一面(見〈天花板〉)。
- 設計審 r1 整合席列了其他同類候選(`py-parallel`、`node-parallel`、`kt-coroutines`、`cs-async`、`py-memory`、`vue-watch`、`dart-async`):v1 不收,因為它們的主問是「有沒有並行、有沒有上限、記憶體」,多半寫不成最終狀態或次數斷言;8 週量完再決定要不要擴。

判定端用 `_stack_spec_by_id(<題目id>)` 查這個欄位,不改 `_stack_applicability` 產生的 meta 形狀。沒標的題目行為完全不變。

### 配方宣告它涵蓋哪一題

`lumos guard kill-add` 多一個選填參數 `--covers <題目id>[,<題目id>…]`,存進配方;`cmd_guard_kill` 寫 `.kill-log.jsonl` 時,每筆多三個欄位:
- `covers`:配方宣告涵蓋的題目 id 清單(沒宣告就是空清單)。
- `file`:配方改到的檔(相對平台根)。
- `method`:實際跑的測試方法名,照 `cmd_guard_kill` 現行的正規化(有平台時去掉平台前綴、去掉 Kotlin 反引號)。

同時修一個既有小問題:`commit` 改成每筆記它那一組平台跑的當下 HEAD(現行多平台時整批只記最後一組)。其他欄位與寫法不變;`--json` 模式 stdout 仍只印一行 JSON。

### 寫表態時算背書,存進表態記錄

`lumos code-loop dispositions <檔>`(`_cmd_codeloop_dispositions`)驗完形狀、寫帳之前,對每一題「被標、而且 status=satisfied」的表態:

1. evidence 不是 `test:` 開頭 → 背書=`none`,原因「讀程式碼不算行為證據」。
2. 用 `_dispositions_split_test` 把 evidence 拆成(平台, 方法名),方法名照 kill 同一套正規化。
3. 讀本機 `docs/.kill-log.jsonl`(讀不到或沒有這個檔 → 背書=`none`,原因「本機沒有破壞測試紀錄」)。逐行 `json.loads`,壞行略過。
4. 取「platform 與方法名都對得上、而且 `covers` 含這一題」的紀錄,按配方分組(配方=同一 node、同一 invariant、同一 file),每組取檔案順序最後一筆。
5. 至少有一組,而且**每一組**的最後一筆都是 `killed` → 背書=`strong`,記下各組的 node、invariant、commit、ts 與配方的壞法說明(note);否則背書=`none`,原因寫明是「沒有涵蓋這題的配方」「最後一次不是強證據(是 killed 以外的六種判定之一)」還是「平台或名字對不上」。

算出來的結果以 `backing` 欄位存進該題的表態(樣板裡若已帶 `backing`,一律丟掉重算,不信任手填或 `--carry` 帶過來的值)。之後照既有流程先寫治理帳的 `kind=dispositions` 事件、再原子寫標記——CI 讀得到,因為它本來就讀這筆事件。

### 推送前檢查只讀記錄好的背書

`_dispositions_verdict` 在 satisfied 分支(不是共用的 `_ev`,所以 tension 不受影響),對被標題目看表態記錄裡的 `backing`:
- `strong` → 不多說。
- `none` 或沒有這個欄位(舊記錄) → 放進 `out["warnings"]`(獨立於 `problems`,不改 `blocked`、不改回傳碼),code-loop check 印成「提醒:」,附原因與補救指令(寫次數或併發測試 → `guard kill-add --covers <題目id>` → `guard kill` → 重表態)。

這一步不讀治理帳、不讀破壞測試紀錄、不跑 git,所以不增加推送前的時間,也碰不到 `_DISP_BUDGET` 超時放行的問題。

### 過期

不另寫過期判定。表態記錄本來就綁提交:改了程式,表態依 `_codeloop_record_valid` 的既有規則失效,要重表態(`--carry` 只沿用答案、背書照第 3 步重算)。所以背書最舊只到「最後一次重表態時本機破壞測試紀錄的狀態」。殘留缺口見〈天花板〉第 1 條。

### 開關

- `.lumos/config.json` 的 `stack_questions.contract_evidence`:`off` / `warn`,預設 `warn`;只認這兩個小寫字串,其他值(大小寫不同、布林、數字、null)照預設 warn,並照 `_stack_questions_config` 既有慣例把說明放進回傳的 warnings。回傳 dict 用鍵 `contract_evidence`。
- 這個開關附屬於整個表態閘:`stack_questions.gate` 為 `off`,或為 `high-only` 且這次不是高風險時,`_dispositions_verdict` 本來就提早結束,背書提醒也不印。
- `off`:寫表態時不算背書、檢查時不提醒。
- v1 不做 block。

### 派工鏡頭

表態記錄已經帶著 `backing`,派工鏡頭照現行只讀標記(`_lens_dispositions_lines` 讀到的就是含背書的記錄),每筆被標題目的 satisfied 行尾多印「背書:強證據(配方:<note 前 40 字>)」或「背書:沒有(<原因>)」。快取鍵照舊用表態記錄的 sha256——背書改變時記錄內容就變,鍵自然跟著變,不用改 `_lens_cache_path`。

### 教人怎麼寫測試

要同步改的文件(上線後舊說法會變錯的都列進來):
- `skills/lumos-code-loop/SKILL.md` 表態那段、`skills/lumos-code-loop/reference.md` 兩處「工具只驗證據存在,不驗答案對不對」:補一句「被標的八題 satisfied 另外看破壞測試背書,v1 只提醒」。
- `skills/lumos-project-notes/reference.md` 的 `guard kill-add` 說明與 `commands/06-代碼審與推送.md` 指令表:加 `--covers` 與 `stack_questions.contract_evidence`。
- 同一份 reference 寫合約那節加一小段怎麼寫測試:併發用同步起跑讓請求同時撞進來、斷言最終狀態不斷言時間、最穩是在讀與寫之間留測試用暫停點強制交錯,配方拿掉鎖、交易、唯一鍵或冪等檢查;效能斷言查詢或外呼次數、資料量從 10 變 100 時次數不變,配方把批次改回逐筆;絕對延遲不收,寫成 `RULE:` 加 `FACT:[來源:生產]` 交給效能 CI 或監控。
- `Systems/棧別提問表態閘`、`Systems/guard-kill` 兩篇的現況行。
- 全域紀律範本(`scripts/templates/graph-discipline.md`)不提表態與破壞測試,不用改(r1 整合席查過)。

## 天花板(v1 承認、不處理)

1. **表態之後才改弱測試**:背書在重表態時才重算;表態之後、推送之前若把測試改弱但沒動到會讓表態失效的檔,背書仍是舊的。重表態時會重算,但破壞測試紀錄本身不會自己重跑——紀錄可能是很久以前跑的。v1 只在提醒與派工單印出那次破壞測試的提交與日期,讓人判斷要不要重跑。
2. **偶發才紅的測試**:破壞測試只跑一次,機率性才紅的併發測試可能剛好紅而拿到 killed(誤放行),也可能剛好綠而 survived(誤提醒)。技能文件要求強制交錯以降低;重跑機制屬於破壞測試本身,另案。
3. **涵蓋是作者宣告的**:`--covers` 是寫配方的人自己宣告的,工具不判那條壞法跟題目真的有關;派工單印出壞法說明,交審查席看。
4. 以上三條任一條沒解,就不升級成擋。

## 不做

- 不驗審查席的 clean 報告本身(那是處置閘的事,另案)。
- 不在推送前自動跑破壞測試;不在推送前讀破壞測試紀錄或治理帳。
- 不新增治理帳事件種類、不改 `_KNOWN_GATES`。
- 不收毫秒、吞吐量這類時間斷言當證據。
- 不新增測試種類或 profile。
- 不做 block;升級另開計劃。
- tension 選 suggested 時附的 evidence 不要求背書(tension 本來就印 ⚠ 交人裁);RETIRE-IF 把 tension 算進繞開比例。

## 實務隱患

- 併發:寫表態時只讀 `.kill-log.jsonl`,不寫;破壞測試對它的寫法不變(同一次 open 批次寫)。讀到半行(另一個破壞測試正在寫)照第 3 步略過壞行,結果是少算背書、只會多提醒。治理帳多個寫入者的問題([[Issues/治理帳多個寫入者都沒上鎖]])本案不新增寫入點。
- 效能:推送前檢查不增加任何讀取;寫表態時多讀一次 `.kill-log.jsonl`(本 repo 4 行;就算上千行也是一次讀完)。
- 資源:無新檔案、無新行程。
- 相容:舊表態記錄沒有 `backing` 欄位 → 當成「沒有背書」只提醒;舊配方沒有 `covers` → 不涵蓋任何題,只提醒;舊 kill-log 紀錄沒有新欄位 → 對不上,只提醒。`lumos gov` 讀 kill-log 只取既有欄位,多出來的欄位不影響。
- 沒有圖譜的專案:[[Issues/沒有圖譜的專案答不完表態題]] 記了既有死結(沒有 docs/ 時表態根本寫不進去)。本案只在寫表態的路徑上加一步,不改那個死結,也不讓它更糟。
- 輸出純度:破壞測試的 `--json` 模式成功時 stdout 必須恰好一行 JSON(既有合約,[[Systems/guard-kill]]);多寫欄位不改變輸出。

## 驗收條款

- [S1] 題目規格 應 能標 `evidence: "contract"`,v1 標上面八題;沒標的題目,寫表態與推送前檢查的結果 應 與改動前一致 [test:t_contract_evidence_marked_questions]
- [S2] 當 `guard kill-add` 帶 `--covers`,配方 應 存下涵蓋的題目 id 清單 [test:t_guard_kill_add_covers]
- [S3] 當破壞測試判完配方,kill-log 每筆 應 多出 covers、file、method 三欄,且 commit 是該筆所屬平台的 HEAD [test:t_guard_kill_log_new_fields]
- [S4] 若以 `--json` 跑破壞測試,stdout 應 仍只有一行 JSON [test:t_guard_kill_json_purity]
- [S5] 當被標題目的 satisfied 附 `path:line`,寫表態 應 記背書為 none 並寫明原因 [test:t_contract_backing_rejects_path_line]
- [S6] 當 kill-log 裡對得上的紀錄都沒宣告涵蓋這一題,寫表態 應 記背書為 none [test:t_contract_backing_needs_covers]
- [S7] 當同一配方先 killed、後來最後一筆是 survived,寫表態 應 記背書為 none [test:t_contract_backing_latest_per_recipe]
- [S8] 當兩個平台有同名測試、只有另一個平台的紀錄是 killed,寫表態 應 記背書為 none [test:t_contract_backing_platform_match]
- [S9] 當涵蓋這題的每一組配方最後一筆都是 killed,寫表態 應 記背書為 strong 並附配方資訊 [test:t_contract_backing_strong]
- [S10] 當樣板或 `--carry` 帶了 backing 欄位,寫表態 應 丟掉並重算 [test:t_contract_backing_recomputed]
- [S11] 若背書為 none 或缺欄位,code-loop check 應 印提醒、放進 warnings、不改 blocked 與回傳碼 [test:t_contract_evidence_warn_only]
- [S12] 若 `stack_questions.contract_evidence` 為 off,寫表態 應 不算背書、code-loop check 應 不提醒 [test:t_contract_evidence_off_mode]
- [S13] 當設定值不是 off 或 warn,設定讀取 應 照預設 warn 並在 warnings 說明 [test:t_contract_evidence_bad_config]
- [S14] 若 `stack_questions.gate` 為 off,code-loop check 應 不印背書提醒 [test:t_contract_evidence_follows_gate]
- [S15] 當派工鏡頭附上表態,被標題目的 satisfied 行 應 帶背書註記 [test:t_dispatch_lens_shows_contract_backing]
- [S16] 當 `lumos gov --stats` 印表態段,被標題目 應 多列有背書與沒有背書的次數 [test:t_gov_stats_contract_backing]
- [S17] 技能文件與兩篇 Systems 筆記 應 照〈教人怎麼寫測試〉列的位置更新 [manual:逐一打開列出的六個位置,確認新說法在、舊的「只驗證據存在」句旁已補被標題目的例外、範例不含毫秒斷言]

## 回退

- 最快:專案把 `.lumos/config.json` 的 `stack_questions.contract_evidence` 設成 `off`,寫表態不算背書、檢查不提醒,其他表態照舊。
- 整個撤:還原實作那個功能提交即可。已寫進治理帳的表態事件多出的 `backing` 欄位、kill-log 多出的三個欄位,舊程式讀不到也不會壞(都是只增不改的紀錄、讀者只取自己認得的欄位);只提醒不擋,還原前不會有人被擋住,沒有外部要收拾的東西。

## 合約候選

- 寫表態時,背書一律重算,不信任樣板或 `--carry` 帶來的值。
- 推送前檢查的背書提醒不改變 blocked 與回傳碼(v1 只提醒)。

## 審計修正紀錄

- r1(2026-10-01,5 席+架構對齊):62 條/blocking 45 條/原設計「破壞測試寫新的治理帳事件、推送前讀帳判祖先與過期」被五席從不同角度打穿(事件寫不進帳、gov 算兩次、CI 讀不到、壓提交後失效、背書沒綁題目、只看配方檔),改成「寫表態時本機算背書、存進表態記錄、推送前只讀」;過期改沿用表態既有失效規則;砍 block 模式;配方加 `--covers` 綁題目;派工鏡頭改讀記錄內的背書、不動快取。席報告:`governance/review-reports/併發與效能表態要合約背書/`。
