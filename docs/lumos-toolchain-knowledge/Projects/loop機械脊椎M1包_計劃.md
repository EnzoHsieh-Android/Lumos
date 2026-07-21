---
type: project
status: doing
created: 2026-07-21
updated: 2026-07-21
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/全盤外審2026-07_調研]]"
  - "[[Projects/design-loop輕量檔_計劃]]"
  - "[[Projects/lumos-show讀取入口_計劃]]"
  - "[[Systems/convergence-evidence-gate]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/design-loop]]"
summary: |-
  FLAG:DECISION
  KEY:問題=loop 編排的機械脊椎缺四塊(外審 2026-07-21 順位3 一包,使用者裁「一包到底」):①agent 自己當狀態機(輪數/canary 型別/round-id 全靠散文紀律,lumos-show loop 實戰中 round 編號就錯過一次)②light 收斂無機械謂詞(M0 只能人裁攤牌)③收斂帳無 spec 版本綁定(舊乾淨紀錄可掛新內容,[[Systems/convergence-evidence-gate]] 自認 v2 債)④帳本無成本欄(d5 教義無數字可依)
  KEY:#1 loop next——`lumos loop next <id> [--json] [--tier standard|high|light]` 唯讀讀 canary-log,吐唯一下一動作:phase(plant-canary/dispatch/record/gate/converged/cap-reached)+輪數 N+canary 型別(legacy=[(N-1)mod4]/panel=per-slot 輪替)+席數(tier→width:light1/standard3/high5)+record 指令模板字串。**lumos 只出指針不 spawn agent**(維持既有分工);讀側守衛同 status(混用/損壞 rc2);borrow=git status 式 next-action 提示(prior art 普適模式)
  KEY:#2 light 謂詞——`loop status <id> --light --gate`:**單席 caught ∧ 存活 max≤minor ∧ (帶 hash 時)末筆 spec hash=當前 spec → K=1 收斂 rc0**。不含 capture 殘餘(2026-07-21 實證 singleton minor 無資訊量,見[[Projects/design-loop輕量檔_計劃]] M1 前置發現)。**ratchet 機械面**:該 loop 任一輪 severity≥major → --light gate 永久 FAIL、訊息指路「升 standard 開新 panel loop」(只升不降);--light 與 --panel 互斥 rc2。pre-flight 排乾維持散文紀律不進謂詞(無機械 oracle,誠實不裝)
  KEY:#3 spec hash——`canary record --spec <path>` 記錄當下真檔 sha256 入 spec_sha256 欄(record 於 fold 後執行=post-fold hash);gate(legacy/panel/light 三模式)帶 --spec 時驗**末筆** spec_sha256=sha256(當前檔),不符 FAIL 訊息「spec 於末輪審計後被改動,需再過一輪」。不帶 --spec 舊帳不驗(向後相容)但 gate 印 ⚠ 未綁定。v1 單 hash 不做鏈式(append-only jsonl 本地已序;防誤不防惡,誠實天花板)
  KEY:#4 成本欄——`canary record [--tokens N] [--wallclock-min N]` 選配數值欄(非數值 rc2);`loop status` 有欄時尾附成本行(逐輪+總計)。跨 loop 統計/升級率報表**不做**(v1 範圍刀,語料累積後另案;北極星已記[[Projects/loop數據收集_計劃]])
  KEY:與[[Projects/design-loop輕量檔_計劃]] M1 分工——本包交付 light 的 loop-status 面(tier 認得+K=1 謂詞+ratchet 機械面);輕量檔 M1 剩餘=進場硬否決機械化(pitfalls 剝自核段,pitfalls/assess 面)留該計劃,兩包互引不重疊
  KEY:★風險面★self-governance=high——四件全動「判定 spec 能否進實作」的閘;進實作前本 spec 必過完整 design-loop(high tier:panel W=5+跨家族否決席+--need 3 精神),同 M2「舊 loop 審新 loop」前例;實作後 pitfalls 必判 tier=high→full code-loop
  TEST:規劃見 body 測試策略——next 三模式指針/light 謂詞矩陣(caught×severity×hash)/ratchet 永久 FAIL/hash 綁定與相容/成本欄驗證與顯示/既有 legacy+panel gate 全迴歸不變
  DEP:[[Systems/loop-convergence-recording]](record 欄位面)｜[[Systems/convergence-evidence-gate]](gate 合取面)｜[[Systems/design-loop]](編排分工)
  PRIOR-ART:①最小解=全部是既有 record/status 兩指令的欄位與旗標擴充,零新治理層、零新檔 ②世界解=[[Projects/全盤外審2026-07_調研]]本體已裁(#1 Codex 摩擦診斷+git status next-action 普適模式/#3 content-address 綁定=git 血統/#4 OpenAI third-party evals+Anthropic demystifying-evals 把 budget 欄列為 eval 判讀必要上下文) ③裁定=borrow-design 全部(stdlib sha256/argparse 原生)
---
# loop機械脊椎M1包_計劃

> **狀態**：spec 完成，待過完整 design-loop（self-governance=high）。緣起：2026-07-21 全盤外審順位3，使用者裁「一包到底」。四件共用同一批面（`canary record` schema＋`loop status` gate），一份 spec 一次審。

## 問題（全部實戰驗過）

1. **agent 自己當狀態機**：lumos-show loop 四輪全程手工編排——輪數、canary 型別輪替、round-id、severity 記帳全靠散文紀律；實戰中 round 編號（r3/r4）就混過一次。這是日常摩擦最大項（外審 D 類）。
2. **light 收斂無機械謂詞**：M0 首戰收斂只能攤牌人裁——panel gate 要 caught≥2 單席湊不到、legacy G2 被 framing 壓不到底。
3. **spec 版本不綁定**：「審過乾淨」紀錄沒綁「審的是哪一版」——舊乾淨紀錄理論上可掛到改過的新 spec 冒充審訖（gate 節點自認 v2 債）。
4. **成本無帳**：d5「成本平衡」教義沒有數字可依；light 省多少、哪類 spec 審最貴，答不出來。

## 規格

### #1 `lumos loop next <id> [--json] [--tier standard|high|light]`

- **唯讀**：讀該 loop 的 canary-log（同 `loop status` 的讀側守衛：round 混用/損壞 clusters/非連續 round-id → 同款 rc2），不寫任何檔、不 spawn agent——**lumos 只出指針，編排仍是 Claude**（維持 [[Systems/design-loop]]「Claude 編排,lumos 出原語」分工）。
- **輸出（人讀預設；`--json` 機讀）**：
  - `phase`：`plant-canary`（下一輪該開始）/ `record`（該輪已派完待記帳——v1 不可偵測，見範圍刀）/ `gate`（有記錄可問收斂）/ `converged`（gate 已可 rc0）/ `cap-reached`（達 cap 未收斂，指路人裁）。v1 phase 判定只依 log 可觀測事實：無記錄→plant-canary(N=1)；有記錄且 gate FAIL→plant-canary(N=下一輪)；gate PASS→converged；輪數≥cap→cap-reached。
  - `round`：下一輪 N（= 現有輪數＋1，legacy 記錄數／panel round 分組數）。
  - `canary_type`：legacy＝`清單[(N-1) mod 4]`；panel＝per-slot 輪替表（slot i → `清單[(i+N-1) mod 4]`）。
  - `width`：tier→席數（light=1／standard=3／high=5；`--tier` 不給預設 standard；**tier 是編排者宣告非 lumos 判定**——誠實：lumos 沒有 tier 判定能力，只做映射）。
  - `record_cmd`：該輪記帳指令模板字串（含 loop id／round-id／建議旗標——模板是提示非強制）。
- **cap**：legacy=6／panel=3（現行 skill 值；硬編碼進 next 的 cap-reached 判定，與 skill 漂移時以 code 為準並回寫 skill）。

### #2 light K=1 謂詞：`loop status <id> --light --gate`

- **收斂合取（K=1）**：末輪（該 loop 最新一筆）`caught` ∧ 存活 `severity ∈ {clean, minor}` ∧（該筆帶 `spec_sha256` 且 gate 帶 `--spec` 時）hash 相符 → **GATE PASS rc0**。
- **不含 capture-recapture 殘餘**——2026-07-21 實證：singleton minor findings 使殘餘估計恆高（6.0-15.0），對「小 spec 一輪乾淨」場景零資訊量（見 [[Projects/design-loop輕量檔_計劃]] M1 前置發現③）。
- **ratchet 機械面（只升不降）**：該 loop **任一**筆記錄 severity ≥ major → `--light` gate **永久 FAIL**（rc1），訊息指路「light 已 ratchet，升 standard：開新 panel loop id 承接（同 lumos-show 前例）」。不可用後續乾淨輪洗回 light。
- **互斥**：`--light` 與 `--panel` 同給 → rc2。`--light` 對帶 round 的 panel 記錄 → rc2（light=legacy 單席記錄格式，同 lumos-show light r1 實例）。
- **pre-flight 不進謂詞**：排乾與否無機械 oracle（是散文 checklist），謂詞不裝可驗——維持 skill 層紀律，誠實記載此限制。

### #3 spec hash 綁定：`canary record --spec <path>`

- 寫側：record 時計算 `<path>` 檔案 sha256 → 存 `spec_sha256` 欄（record 慣例在 fold 之後執行 → hash = post-fold 版本，正是 gate 要驗的「審完折完的那一版」）。`--spec` 檔不存在 → rc2。
- 讀側：三模式 gate（legacy `--gate`／panel／light）帶 `--spec` 時，驗**末筆記錄**的 `spec_sha256` == sha256(當前 `--spec` 檔)。不符 → FAIL，訊息「spec 於末輪審計後被改動，需再過一輪」。
- 相容：舊帳無 `spec_sha256` 欄→不驗，但 gate 輸出印 `⚠ 末輪未綁 spec hash`（advisory 不擋——存量 loop 不追溯）。
- v1 **單筆 hash、不做鏈式**（reviewed→result 雙 hash 鏈留 v2）：jsonl append-only 本地已有序；本機制**防誤不防惡**（本地檔可改，誠實天花板同 evidence-gate 既有條）。

### #4 成本選配欄：`canary record [--tokens N] [--wallclock-min N]`

- 寫側：兩欄皆選配、皆須非負整數（非數值/負值 → rc2）；不給不寫（鍵不存在，同 `--findings` 慣例）。
- 讀側：`loop status` 任一筆有成本欄時，輸出尾附成本區（逐輪 tokens/分鐘＋總計）；全無則不印（零噪音）。
- **範圍刀**：跨 loop 統計、升級率報表、成本門檻**全不做**——v1 只記帳與單 loop 顯示；北極星與跨 loop 分析歸 [[Projects/loop數據收集_計劃]]（語料累積後另案）。

## 與輕量檔 M1 的分工

本包交付 light 的 **loop-status 面**（`--light` 謂詞＋ratchet 機械面）；[[Projects/design-loop輕量檔_計劃]] M1 剩餘＝**進場硬否決機械化**（pitfalls 剝「light 資格自核」段再掃，pitfalls/assess 面）留在該計劃。兩包互引、無重疊面。

## 明確不做（範圍刀）

- `loop next` 不寫狀態、不 spawn agent、不判 tier（編排者宣告）；phase 不偵測「派了沒記」（log 看不見派工）。
- 不做雙 hash 鏈（v2）；不做跨 loop 成本報表；不做 escape ledger（外審 #5，獨立小 spec 另案）；不動 legacy/panel 既有 gate 合取語意（只加 hash 驗證與成本顯示，皆帶舊帳相容）。

## 測試策略

- **next**：空 loop→plant-canary N=1／有 FAIL 記錄→N+1＋型別輪替正確（legacy mod4、panel per-slot）／gate 可過→converged／達 cap→cap-reached／`--json` 結構完整／混用帳 rc2 同 status／`--tier` 三值→width 映射／不存在 loop id 行為明確。
- **light 謂詞**：矩陣——caught+clean→PASS／caught+minor→PASS／caught+major→FAIL 且此後**永久** FAIL（ratchet，後續乾淨輪不洗回）／missed→FAIL／--light+--panel rc2／--light 對 panel 記錄 rc2／帶 hash 相符 PASS、不符 FAIL、舊帳無欄 advisory 警告不擋。
- **hash**：--spec 記錄 sha256 正確／檔不存在 rc2／三模式 gate 驗末筆／改檔後 gate FAIL 訊息正確／舊帳相容 advisory。
- **成本欄**：數值寫入／非數值/負值 rc2／不給不寫鍵／status 顯示逐輪+總計／全無不印。
- **迴歸**：既有 legacy gate（K-streak∧G1∧G2）、panel 三條合取、cluster 帳、混用守衛——全部現行測試不紅（不動語意）。

## 實務隱患

- **self-governance 循環（最重）**：四件全動「判 spec 能否進實作」的閘——gate 邏輯錯＝系統性放行壞 spec 或永擋好 spec。緩解＝本 spec 過完整 design-loop（high：W=5＋跨家族否決席）＋測試逐條對齊謂詞矩陣＋實作後 full code-loop（pitfalls 必判 high）。
- **loop next 的權威錯覺**：next 吐的是**指針非命令**——editor 若把模板當絕對真相（如 tier 給錯→width 錯），會系統性走錯陣容。緩解＝輸出頭印「advisory：tier 由編排者宣告」＋skill 派工模板仍為權威。
- **light ratchet 的 loop-id 邊界**：ratchet 永久 FAIL 綁 loop id——換 id 就洗掉（同 evidence-gate「換 loop_id 洗紀錄」既有天花板）；hash 綁定收窄但不封死此路。誠實記載，v2 spec-hash 綁 loop 可再收。
- **成本欄 GIGO**：tokens/wallclock 是編排者自報——謊報不可偵測；帳的價值在趨勢非單筆精度（同 anchors GIGO 條）。
- **cap 硬編碼雙源**：next 的 cap 與 skill 文字雙處宣告——漂移風險；以 code 為準、skill 回寫，並列入 cochange 候選。
