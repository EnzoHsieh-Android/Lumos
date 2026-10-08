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
  WHY:[2026-10-01 本對話裁定]形狀=在既有表態閘上加一層,不另起新閘——只對「併發正確性」與「效能可數化」兩類題,satisfied 必須指向一支有破壞測試強證據的合約測試;其他表態(na/todo/tension)照舊可用,誠實說做不到的路永遠在
  WHY:[2026-10-01 本對話裁定]效能只收「次數型」(查詢次數、外呼次數、載入筆數),不收毫秒——毫秒隨機器浮動,推送前會隨機擋;破壞測試把逾時一律記弱證據,「變慢」本來就證不出咬得住
  RULE:[since:2026-10-01][retire:照 RETIRE-IF 撤掉,或上線 8 週後人裁升級成 block]預設只提醒(warn)不擋;專案用 .lumos/config.json 的 stack_questions.contract_evidence 設 off|warn|block
  REVISIT:2026-11-26 上線第 8 週:看觸發次數、提醒被照做的比例、誤擋回報,依 RETIRE-IF 判撤、留 warn、或另開計劃升 block
---
# 併發與效能表態要合約背書_計劃

> 白話:推送前,工具會對這次改動丟出「併發會不會壞」「會不會 N+1」等檢核題(本案要管的八題見〈哪些題目要背書〉),要人或 AI 表態。今天回答「已處理」只要附一個檔案行號或測試名字就過了,等於說「我看過了,沒問題」。這份計劃讓其中兩類題目(併發正確性、效能可數化)的「沒問題」必須有一條合約背書:合約綁一支測試,而且這支測試做過破壞測試(故意把保護拿掉,它真的會紅)。做不到的就老實表態成「待辦」或「不適用」,不准用「已處理」矇過去。

## 緣起與現況

- 使用者的問題(2026-10-01):併發鏡頭說沒問題時,怎麼掛壓測當合約;效能類怎麼辦。
- 查證(獨立 agent 用原始問題查,不帶結論):
  - 審查席交 `severity: clean`:處置閘對零發現輪視同全處置、引句檢查略過(`_loop_status_disposal`);席位編制表 `_TIER_ROSTER` 裡只有資安席是「必派而且處置閘會擋」,其他鏡頭席缺席只提醒。
  - 表態閘的 satisfied:`_dispositions_check_test` 只驗測試名在工作樹與推送樹找得到,不驗它守什麼、會不會紅。技能文件原文:「工具只驗證據存在,不驗答案對不對」。
  - 破壞測試(`cmd_guard_kill`)能證「這支測試咬得住這種壞法」,但只寫 `docs/.kill-log.jsonl`;消費專案 init 時會把這個檔寫進 docs 目錄下的忽略清單(`_scaffold_project` 寫帳檔忽略清單那段),CI 讀不到;本 repo 沒有那份忽略清單、帳檔都被追蹤,但也只有 4 筆紀錄。
  - 綁定測試閘(`_run_bound_tests`)單支預設 180 秒逾時,逾時判紅。
- 已知同源問題:[[Projects/規模影響判斷力假說]] 記「一個自信的『沒問題』會直接餵進收斂帳」;[[Projects/收斂機制優化調研2026-08-14]] 候選④「收斂該錨行為訊號(測試),非對話共識」。

PRIOR-ART: ①同 repo:表態閘的 satisfied/na/todo/tension 四態與「只驗證據存在」的錨點([[Projects/棧別提問表態閘_計劃]]);破壞測試的配方與七態判定([[Systems/guard-kill]]);治理帳是 CI 唯一讀得到的帳(init 的 `.gitignore` 註解與 `_codeloop_read_from_ledger`)。②世界解:併發正確性業界靠「強制交錯」而非隨機壓測當證據——Java jcstress、Rust loom、Go `-race`、決定性模擬;效能迴歸在單元層的做法是斷言次數(Django `assertNumQueries`、Rails `assert_queries_count`、Hibernate statistics),絕對延遲交給固定機器的效能 CI 與生產監控;變異測試(mutation testing)證明測試咬得住。③結論:不新建閘、不新建測試種類;只把「已處理」的證據要求從「存在」提高到「有破壞測試強證據」,並讓破壞測試的強證據進治理帳。

RETIRE-IF: 上線 8 週內出現任一種就撤掉這層(拿掉判定、留治理帳事件):①觸發的題目裡,表態改走 na/todo 繞開的比例超過八成,而且抽 10 筆看理由多半是「寫合約太貴」而非「真的不適用」——代表成本壓過價值;②誤擋或誤提醒的回報多過真的因此補上合約的次數;③8 週總觸發少於 5 次——量太小,維護成本大於價值。

## 做法

用詞:**強證據**=破壞測試七種判定(killed、killed_unattributed、timed_out_weak、survived、drifted、abort、error)裡的 `killed`,也就是綁定測試紅了、而且紅的就是那支測試;**推送版本**=這次被推送的提交(程式裡的 `at_sha`);**次數型**=斷言某個動作做了幾次(查詢、對外呼叫、載入筆數),不斷言花了多久。

### 哪些題目要背書

在 `_STACK_QUESTION_SPECS` 的題目上加一個欄位 `evidence: "contract"`,v1 只標這兩類(清單本身是審查對象):

- **併發正確性**:`swift-concurrency`、`java-concurrency`、`fe-race`、`sql-transaction`。
- **效能可數化**(N+1、大查詢):`sql-nplus1`、`cs-data`、`node-data`、`java-data`。

沒標的題目行為完全不變。

### satisfied 要什麼證據

被標的題目表態成 satisfied 時,`evidence` 必須是 `test:<名>`(不收 `path:line`,讀程式碼不算行為證據),而且治理帳裡要有一筆「這支測試的破壞測試是強證據」的紀錄,且沒過期:

1. 破壞測試寫治理帳事件:`cmd_guard_kill` 現行在所有配方判完後、迴圈外批次寫 `.kill-log.jsonl`;在同一處,再用既有的治理帳寫入(`_gate_event_or_warn`,不改變呼叫端判定)為每條配方各寫一筆 `kind=guard-kill`,欄位 `node`、`invariant`、`test`、`platform`、`verdict`、`commit`(跑的當下 HEAD)、`files`(配方改到的檔)。只有 `killed` 算強證據;`killed_unattributed`、`timed_out_weak`、`survived` 都不算。
2. 表態檢查(`_dispositions_verdict` 走到被標題目的 satisfied)讀治理帳,找同一個測試名、`verdict=killed` 的最新一筆:
   - 找不到 → 「沒有背書」。
   - 那筆的 `commit` 不是被推送版本的祖先 → 「沒有背書」(在別的分支跑的不算)。
   - 從那筆的 `commit` 到被推送版本之間,`files` 裡任一支檔有改動 → 「背書過期,要重跑破壞測試」。
3. 檢查只讀治理帳與 git,不載圖譜——沿用表態閘「推送前檢查不載圖譜」的既有限制。

### 擋不擋

- `.lumos/config.json` 的 `stack_questions.contract_evidence`:`off` / `warn` / `block`,預設 `warn`。跟既有的 `stack_questions.gate`(控制整個表態閘 all/high-only/off)並列、互不影響。設定寫壞照預設,並照 `_stack_questions_config` 既有慣例把說明放進回傳的 warnings,由 code-loop check 印成「提醒:」。
- `warn`:沒有背書或背書過期時,`code-loop check` 印提醒並寫一筆治理帳 `kind=contract-evidence` 事件(題目 id、原因),不改回傳碼。
- `block`:同樣情況當成表態不完整,照表態閘既有路徑擋。
- 錯誤處理照表態閘現行分層:單題驗不了(例如讀帳或 git 指令失敗),warn 模式印提醒、block 模式照 `_dispositions_verdict` 內單題的既有做法擋下;整道檢查的外層例外與超時才走 `_gate_failopen` 放行。

### 其他表態照舊

na(理由 ≥10 字)、todo(連 Issue)、tension 不受影響——包括 tension 選 suggested 時附的 evidence,v1 也不要求背書(tension 本來就印 ⚠ 交人裁)。這是刻意的:做不到就老實說,例如 todo 連一篇「補壓測」的 Issue。

### 派工鏡頭多一行

表態會附進審查席的派工單(既有行為)。被標題目的每筆 satisfied 旁邊加註「背書:強證據(提交 <短編號>)/沒有背書/過期」,讓併發或正確性席知道這個「沒問題」有多硬。現行附表態的 `_lens_dispositions_lines` 只讀表態標記、不讀治理帳,所以要多讀一次治理帳的 `guard-kill` 事件,並用跟表態檢查同一支函式算狀態;派工鏡頭的快取鍵(`_lens_cache_path`)要把背書狀態算進去,否則補跑破壞測試後舊快取不會失效。

### 教人怎麼寫測試

技能文件(lumos-project-notes 寫合約那節、lumos-code-loop 表態那段)各加一小段:

- 併發:用同步起跑讓請求同時撞進來;斷言最終狀態不斷言時間;最穩的是在讀與寫之間留測試用暫停點強制交錯;配方拿掉鎖、交易、唯一鍵或冪等檢查。
- 效能:斷言查詢或外呼次數,且資料量從 10 變 100 時次數不變;配方把批次改回逐筆。
- 絕對延遲不收:寫成 `RULE:` 加 `FACT:[來源:生產]`,交給效能 CI 或監控。

## 不做

- 不驗審查席的 clean 報告本身(那是處置閘的事,另案)。
- 不在推送前自動跑破壞測試(太慢、要沙盒);只讀它留下的紀錄。
- 不收毫秒、吞吐量這類時間斷言當證據。
- 不新增測試種類或 profile;次數斷言與併發測試用既有單元、整合測試寫。
- 不做 block 預設;升級另開計劃。

## 實務隱患

- 併發:治理帳多個寫入者同時寫的問題已有 [[Issues/治理帳多個寫入者都沒上鎖]];本案新增兩種事件走同一個寫入函式,不另開寫入點,不加重也不修它。
- 效能:表態檢查每題多一次讀治理帳加一次 `git diff --name-only`;治理帳大時讀取成本要量,沿用表態閘既有的預算與 `_gate_failopen`。
- 資源:無新檔案、無新行程。
- 相容:舊專案沒有 `guard-kill` 事件,被標題目的 satisfied 在 warn 下只會多提醒;block 要專案自己打開。
- 沒有圖譜的專案:[[Issues/沒有圖譜的專案答不完表態題]] 記了既有死結(沒有 docs/ 時表態寫不進去、閘卻照擋),同一篇也記了合約測試那一關遇到同樣情況會標成「沒有圖譜」而不擋。本案在沒有 docs/ 的專案比照合約測試那一關、不做背書判定,不加重那個死結。
- 輸出純度:破壞測試的 `--json` 模式成功時 stdout 必須恰好一行 JSON(既有合約,[[Systems/guard-kill]]);新增的治理帳寫入不得印任何東西到 stdout。
- 誤判:機率性才紅的壓測,破壞測試可能剛好綠而判 survived——這會讓人「證不出背書」,方向是誤提醒而非誤放行;技能文件要求強制交錯以降低。

## 驗收條款

- [S1] 題目規格 應 能標 `evidence: "contract"`,v1 標上面八題;沒標的題目,表態判定 應 與改動前一致 [test:t_contract_evidence_marked_questions]
- [S2] 當破壞測試判完一條配方,cmd_guard_kill 應 寫一筆欄位齊全的治理帳 `guard-kill` 事件,並照舊寫 `.kill-log.jsonl` [test:t_guard_kill_writes_ledger_event]
- [S3] 當被標題目的 satisfied 附 `path:line`,表態檢查 應 判「沒有背書」 [test:t_contract_evidence_rejects_path_line]
- [S4] 當附的 `test:<名>` 在治理帳沒有 `killed` 事件或只有弱證據,表態檢查 應 判「沒有背書」 [test:t_contract_evidence_needs_strong_kill]
- [S5] 當 `killed` 事件的提交不是推送版本的祖先,表態檢查 應 判「沒有背書」 [test:t_contract_evidence_kill_must_be_ancestor]
- [S6] 當配方改到的檔在事件之後被改過,表態檢查 應 判「背書過期」 [test:t_contract_evidence_stale_after_recipe_file_change]
- [S7] 若啟用 warn 模式,code-loop check 應 只印提醒、寫 `contract-evidence` 事件、不改回傳碼 [test:t_contract_evidence_warn_mode]
- [S8] 若啟用 block 模式,code-loop check 應 把沒有背書當成表態不完整而擋下 [test:t_contract_evidence_block_mode]
- [S9] 若設定為 off,code-loop check 應 完全不做背書檢查 [test:t_contract_evidence_off_mode]
- [S10] 當設定值寫壞,設定讀取 應 照預設 warn 並印一句說明 [test:t_contract_evidence_bad_config]
- [S11] 當派工鏡頭附上表態,被標題目的 satisfied 應 帶背書狀態註記 [test:t_dispatch_lens_shows_contract_backing]
- [S12] 技能文件 應 在兩處加上寫併發與次數型效能測試的做法 [manual:讀 lumos-project-notes 寫合約那節與 lumos-code-loop 表態那段,各有一小段且範例不含毫秒斷言]

## 回退

- 最快:專案把 `.lumos/config.json` 的 `stack_questions.contract_evidence` 設成 `off`,背書檢查整段不跑,其他表態照舊。
- 整個撤:還原實作那個功能提交即可。治理帳裡已寫下的 `guard-kill` 與 `contract-evidence` 事件是只增不改的紀錄,留著不影響任何閘(讀它的只有本案的檢查與 `lumos gov` 統計);預設是 warn,還原前不會有人被擋住,沒有外部要收拾的東西。

## 合約候選

- 被標題目的 satisfied,在 block 模式下,沒有未過期的強證據就不放行。
- 只有 `killed` 算強證據。

## 審計修正紀錄

(設計審開始後逐輪記)
