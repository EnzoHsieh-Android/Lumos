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
  KEY:#1 loop next——`lumos loop next <id> [--json] [--tier standard|high|light]` 唯讀讀 canary-log,吐唯一下一動作(判 converged 需完整 gate 旗標組 --need/--spec/--repo/--panel/--light 委派既有謂詞,資訊不足 rc2 絕不謊報收斂——r2 Codex C1):phase(**v1 三值** plant-canary/converged/cap-reached,r1 折入砍死值;**判定=cap 短路優先→PASS→其餘**,三分支互斥窮盡,否則 cap-reached 永不可達誘導無限燒)+輪數 N+canary 型別(legacy=[(N-1)mod4]/panel=per-slot 輪替)+席數(tier→width:light1/standard3/high5)+**cap 對照直給(light2/standard3/high3/legacy6,r1 折入)**+record 指令模板字串。**lumos 只出指針不 spawn agent**;讀側守衛同 status(混用/損壞 rc2);borrow=git status 式 next-action 提示
  KEY:#2 light 謂詞——`loop status <id> --light --gate`:**單席 caught ∧ 存活 max≤minor ∧ 欄位互證(clean⇒0/minor⇒≥1,復用 :2710;r2 Codex C5 補) ∧ spec hash 相符(light 強制 fail-closed,缺=FAIL 非 advisory;r2 C3/C5) → K=1 收斂 rc0**。不含 capture 殘餘(2026-07-21 實證 singleton minor 無資訊量)。**ratchet 機械面(r2 C5:只吃 caught)**:任一 **caught** 筆 severity≥major → 永久 FAIL 指路升 standard(missed 筆 severity 不可信不觸發,missed 只使該輪不可收斂);--light 與 --panel 互斥 rc2。pre-flight 排乾維持散文紀律不進謂詞(無機械 oracle,誠實不裝)
  KEY:#3 spec hash——`canary record --spec <path>` 記 sha256 入 spec_sha256 欄;**時序裁定(r2 Codex C4)**:現行「先 record 後 fold」使 post-fold hash 斷言為假——調整 skill 時序(caught 輪 record 移 fold/fold-check/grep 後收尾),列同步義務不假裝既有慣例;**讀檔失敗 OSError 兜底 rc2(r1)**;讀側**末輪級驗證(r2 C2)**:判定輪內全帶-hash 記錄彼此一致∧=sha256(當前檔),輪內漂移即 FAIL(擋補一筆繞過);**定錨式啟用(r2 C3)**:帶過即必須帶到底缺=FAIL,從未帶=advisory(存量不追溯),light 強制,工具鏈模板預設帶 --spec 收窄。v1 單 hash 不做鏈式;byte-level 對行尾敏感(r1,fail-closed 接受);防誤不防惡,誠實天花板
  KEY:#4 成本欄——`canary record [--tokens N] [--wallclock-min N]` 選配數值欄(非負整數,非數值/負值 rc2;不給不寫鍵,同 --findings 慣例);`loop status` 有欄時尾附成本行(逐輪+總計)。跨 loop 統計/升級率報表**不做**(v1 範圍刀,語料累積後另案;北極星已記[[Projects/loop數據收集_計劃]])
  KEY:與[[Projects/design-loop輕量檔_計劃]] M1 分工——本包交付 light 的 loop-status 面(tier 認得+K=1 謂詞+ratchet 機械面);輕量檔 M1 剩餘=進場硬否決機械化(pitfalls 剝自核段,pitfalls/assess 面)留該計劃,兩包互引不重疊
  KEY:落地同步義務(七項,由折入衍生,枚舉寫死)——skills/lumos-design-loop/SKILL.md(record 時序 C4/手算 N 改指 next/light 節人裁改機械 gate)、skills/lumos-design-loop/templates.md(light 附註+模板預設帶 --spec;空帳模板模式由 tier 推導:standard/high→panel 帶 --round、light→legacy)、convergence-evidence-gate KEY「留 v2」清償、loop-convergence-recording 鍵計數、design-loop 手算 N 敘述、輕量檔計劃 M1 標記、Verification 節點
  KEY:★風險面★self-governance=high——四件全動「判定 spec 能否進實作」的閘;進實作前本 spec 必過完整 design-loop(high tier:panel W=5+跨家族否決席+--need 3 精神),同 M2「舊 loop 審新 loop」前例;實作後 pitfalls 必判 tier=high→full code-loop
  TEST:規劃見 body 測試策略——next 三模式指針/light 謂詞矩陣(caught×severity×hash)/ratchet 永久 FAIL/hash 綁定與相容/成本欄驗證與顯示/既有 legacy+panel gate 全迴歸不變
  DEP:[[Systems/loop-convergence-recording]](record 欄位面)｜[[Systems/convergence-evidence-gate]](gate 合取面)｜[[Systems/design-loop]](編排分工)
  PRIOR-ART:①最小解=#2-#4 為既有 record/status 兩指令的欄位旗標擴充;#1 為 loop 子指令組**新增第三個 subparser**(status/capture-counts 之外)——新增一條唯讀查詢介面,**非零新指令**(r1 折入:原「全部零新命令」宣稱與 #1 自相矛盾,自我治理判準不得帶頭失守);仍零新治理層/零新檔 ②世界解=[[Projects/全盤外審2026-07_調研]]本體已裁(#1 Codex 摩擦診斷+git status next-action 普適模式/#3 content-address 綁定=git 血統/#4 OpenAI third-party evals+Anthropic demystifying-evals 把 budget 欄列為 eval 判讀必要上下文) ③裁定=borrow-design 全部(stdlib sha256/argparse 原生)
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
- **gate 參數委派（r2 Codex 折入 C1：next 輸入不足不得宣告 converged）**：next 判 `converged` 需要的 gate 合取取決於 `--need/--spec/--repo/--panel/--light`——next **接受與 status 相同的完整 gate 旗標組並內部委派既有 gate 謂詞**（零新判定邏輯，純 delegation）；帶 `--gate` 級判定而未給必要參數（如缺 `--spec`）→ 同 status 現行為 rc2，**絕不在資訊不足時輸出 converged**。
- **空帳模板模式明定（C1 附帶）**：零記錄 loop 的 `record_cmd` 模板——`--tier standard|high` → panel 格式（帶 `--round`）；`--tier light` → legacy 單席格式（不帶 round）。模板猜錯模式會被現行混用守衛 rc2（:2638），故模式必須由 tier 確定性推導、不留猜。
- **輸出（人讀預設；`--json` 機讀）**：
  - `phase`（**v1 契約=三值**，r1 折入：`record`/`gate` 是 v1 判不出的死值，從契約拿掉留 v2——防 `--json` 消費端寫永遠測不到的死分支）：`plant-canary` / `converged` / `cap-reached`。
  - **判定優先序（r1 折入 major：cap 短路優先，否則 cap-reached 永不可達）**：① `輪數 ≥ cap` 且 gate 未 PASS → `cap-reached`（**短路，先於一切 FAIL 分支**——對齊 skill「到頂停、別無限燒」硬教義）；② gate PASS → `converged`；③ 其餘（無記錄→N=1；有記錄 gate FAIL→N=現有輪數+1）→ `plant-canary`。三分支互斥窮盡。
  - `round`：下一輪 N（= 現有輪數＋1，legacy 記錄數／panel round 分組數）。
  - `canary_type`：legacy＝`清單[(N-1) mod 4]`；panel＝per-slot 輪替表（slot i → `清單[(i+N-1) mod 4]`）。
  - `width`：tier→席數（light=1／standard=3／high=5；`--tier` 不給預設 standard；**tier 是編排者宣告非 lumos 判定**——誠實：lumos 沒有 tier 判定能力，只做映射）。
  - `record_cmd`：該輪記帳指令模板字串（含 loop id／round-id／建議旗標——模板是提示非強制）。
- **cap（r1 折入：tier→cap 直給對照表，三個 tier 各有明數，不留三種猜法）**：`light=2`（1 輪收斂為設計目標；missed 輪判決不採信可重試 1 次，第 2 輪仍未收斂→指路人裁或升級）／`standard=3`（panel 現行值）／`high=3`（panel 同值；席寬不同不影響輪 cap）／無 `--tier` 且記錄為 legacy 格式=6（legacy 現行值）。硬編碼進 next，與 skill 漂移時以 code 為準並回寫 skill。

### #2 light K=1 謂詞：`loop status <id> --light --gate`

- **收斂合取（K=1；r2 Codex 折入 C5 補全）**：末輪（該 loop 最新一筆）`caught` ∧ 存活 `severity ∈ {clean, minor}` ∧ **欄位互證（復用 :2710 既有檢查：clean⇒findings=0、minor⇒findings≥1，矛盾即擋）** ∧ **hash 相符（light 為新賽道無存量包袱——`spec_sha256` 缺失=FAIL 非 advisory，fail-closed 強制啟用）** → **GATE PASS rc0**。
- **不含 capture-recapture 殘餘**——2026-07-21 實證：singleton minor findings 使殘餘估計恆高（6.0-15.0），對「小 spec 一輪乾淨」場景零資訊量（見 [[Projects/design-loop輕量檔_計劃]] M1 前置發現③）。
- **ratchet 機械面（只升不降；r2 Codex 折入 C5：只吃 caught）**：該 loop 任一筆 **`caught`** 記錄 severity ≥ major → `--light` gate **永久 FAIL**（rc1），訊息指路「light 已 ratchet，升 standard：開新 panel loop id 承接（同 lumos-show 前例；承接時的 id 命名與紀錄歸屬見〈與輕量檔 M1 的分工〉節）」。**missed 筆的 severity 不觸發 ratchet**——missed 輪判決不採信是既有教義（SKILL:43），不可信裁決不得擁有永久否決權；missed 只使該輪不可收斂（light cap=2 內重試，見 cap 表）。不可用後續乾淨輪洗回 light。
- **互斥**：`--light` 與 `--panel` 同給 → rc2。`--light` 對帶 round 的 panel 記錄 → rc2（light=legacy 單席記錄格式，同 lumos-show light r1 實例）。
- **pre-flight 不進謂詞**：排乾與否無機械 oracle（是散文 checklist），謂詞不裝可驗——維持 skill 層紀律，誠實記載此限制。

### #3 spec hash 綁定：`canary record --spec <path>`

- **時序裁定（r2 Codex 折入 C4——原「record 在 fold 後」斷言與現行 skill 步驟順序相反，必須明講）**：現行權威流程是**先 record（步驟5）後 fold（步驟7）**——照此 hash 必在每個有折入的 caught 輪後失配，機制在最常見成功路徑上先壞。**本包裁定：調整 skill 時序**——caught 輪的 record 移至「fold 完成＋fold-check 過＋canary token grep=0」**之後**當輪次收尾（record 是純 append 記帳，移位無機械依賴；missed 輪無 fold，record 即收尾不變）。此為 skill 文字改動，列入同步義務（見下）；spec 不假裝這是既有慣例。
- 寫側：record 時計算 `<path>` 檔案 sha256 → 存 `spec_sha256` 欄（依上述新時序＝post-fold hash）。**讀檔/hash 失敗一律 rc2（r1 折入 major）**：不存在/是目錄/無權限等統一 `OSError` 兜底——沿 G1 refcheck 讀 `--spec` 的既有 catch 慣例（scripts/lumos:2687-2691）；只查 `exists()` 會對目錄裸 traceback。
- **讀側（r2 Codex 折入 C2——「末筆」升級「末輪」，防補一筆繞過）**：三模式 gate 帶 `--spec` 時，以**判定輪（round 分組）為單位**驗：該輪**所有帶 `spec_sha256` 的記錄必須彼此一致**且 == sha256(當前 `--spec` 檔)。輪內 hash 不一致 → FAIL（「輪內版本漂移——各席審的不是同一版」）；一致但≠當前檔 → FAIL（「spec 於末輪審計後被改動，需再過一輪」）。Codex 反證場景（往已有效輪補 append 一筆新 hash 記錄）被輪內一致性擋死。legacy/light 單席輪＝該輪唯一一筆，退化為單筆驗證。
- **相容（r2 Codex 折入 C3——「舊帳 advisory」不得成為永久逃生門）**：**定錨式啟用**（同 cluster 帳定錨前例）——該 loop 首個帶 `spec_sha256` 的記錄出現後，loop 定錨 hash 模式，後續記錄缺 hash → gate FAIL（非 advisory）；**從未帶過**的 loop → advisory `⚠ 本 loop 未啟用 hash 綁定`（存量舊帳不追溯）。**light 例外：強制**（新賽道無存量，缺=FAIL，見 #2）。殘餘誠實記載：legacy/panel 新 loop 整條不帶仍只有 advisory——機械上無法區分「舊帳」與「拒用」，靠 skill 派工模板預設帶 `--spec`＋loop next 的 record_cmd 模板內建 `--spec` 收窄（工具鏈預設路徑帶上，偷懶要主動刪旗標）。
- v1 **單筆 hash、不做鏈式**（reviewed→result 雙 hash 鏈留 v2）：jsonl append-only 本地已有序；本機制**防誤不防惡**（本地檔可改，誠實天花板同 evidence-gate 既有條）。

### #4 成本選配欄：`canary record [--tokens N] [--wallclock-min N]`

- 寫側：兩欄皆選配、皆須非負整數（非數值/負值 → rc2）；不給不寫（鍵不存在，同 `--findings` 慣例）。
- 讀側：`loop status` 任一筆有成本欄時，輸出尾附成本區（逐輪 tokens/分鐘＋總計）；全無則不印（零噪音）。
- **範圍刀**：跨 loop 統計、升級率報表、成本門檻**全不做**——v1 只記帳與單 loop 顯示；北極星與跨 loop 分析歸 [[Projects/loop數據收集_計劃]]（語料累積後另案）。

## 與輕量檔 M1 的分工

本包交付 light 的 **loop-status 面**（`--light` 謂詞＋ratchet 機械面）；[[Projects/design-loop輕量檔_計劃]] M1 剩餘＝**進場硬否決機械化**（pitfalls 剝「light 資格自核」段再掃，pitfalls/assess 面）留在該計劃。兩包互引、無重疊面。

## 落地同步義務（同 commit；由折入內容衍生，比照 lumos-show 前例枚舉寫死）

1. `skills/lumos-design-loop/SKILL.md`：〈每一輪〉record 時序改動（C4——caught 輪 record 移 fold/fold-check/grep 之後收尾）；步驟 1「N=status 輪數+1 手算」改指 `lumos loop next`；〈light 檔〉步驟 4 的「人裁實質收斂出口」改寫為 `loop status <id> --light --gate` 機械謂詞（本包 #2 交付的正是這件）。
2. `skills/lumos-design-loop/templates.md`：§1 light 附註同步（人裁→機械 gate）；派工/記帳模板預設帶 `--spec`（C3 收窄）。
3. `Systems/convergence-evidence-gate`：KEY 行「--spec 無綁定向量**留 v2**」——#3 落地即清償，同 commit 拿掉「留 v2」改記落地指針。
4. `Systems/loop-convergence-recording`：record 選用鍵計數與清單（+spec_sha256/tokens/wallclock_min）。
5. `Systems/design-loop`：〈每一輪〉手算 N 敘述同步 loop next。
6. `Projects/design-loop輕量檔_計劃`：M1 的 loop-status 面標記由本包交付。
7. Verification 節點（plan_refs 回指本計劃）。

## 明確不做（範圍刀）

- `loop next` 不寫狀態、不 spawn agent、不判 tier（編排者宣告）；phase 不偵測「派了沒記」（log 看不見派工）。
- 不做雙 hash 鏈（v2）；不做跨 loop 成本報表；不做 escape ledger（外審 #5，獨立小 spec 另案）；不動 legacy/panel 既有 gate 合取語意（只加 hash 驗證與成本顯示，皆帶舊帳相容）。

## 測試策略

- **next**：空 loop→plant-canary N=1／有 FAIL 記錄→N+1＋型別輪替正確（legacy mod4、panel per-slot）／gate 可過→converged／達 cap→cap-reached／`--json` 結構完整／混用帳 rc2 同 status／`--tier` 三值→width 映射／不存在 loop id 行為明確。
- **light 謂詞**：矩陣——caught+clean→PASS／caught+minor→PASS／caught+major→FAIL 且此後**永久** FAIL（ratchet，後續乾淨輪不洗回）／missed→FAIL／--light+--panel rc2／--light 對 panel 記錄 rc2／帶 hash 相符 PASS、不符 FAIL、舊帳無欄 advisory 警告不擋。
- **hash**：--spec 記錄 sha256 正確／檔不存在 rc2／三模式 gate 驗末筆／改檔後 gate FAIL 訊息正確／舊帳相容 advisory。
- **成本欄**：數值寫入／非數值/負值 rc2／不給不寫鍵／status 顯示逐輪+總計／全無不印。
- **迴歸**：既有 legacy gate（K-streak∧G1∧G2）、panel 三條合取、cluster 帳、混用守衛——全部現行測試不紅（不動語意）。

## 審計修正紀錄

**pre-flight（2026-07-21，haiku checklist）**：0 命中（六項全過——今天實戰紀律直接反映在 spec 起點）。

**r1（2026-07-21，high panel W=4 sonnet 異鏡頭＋Codex 否決席；loop id `loop機械脊椎M1包`）**：canary slot1=a 型（近名假節〈分工與邊界〉，probe 重植 1 次後 pass）✗ missed；slot2=b 型（測試單憑空旗標，probe 重植 1 次後 pass）✗ missed；slot3=c 型（憑空分塊常數）✓ **精準抓**（grep 零命中＋反先例 :6382/:6414 整檔讀無分塊）；slot4=d 型（憑空狀態表檔名，probe 直接 pass）✗ missed。**caught 1/4=輪無效**；三 missed 席 findings 依規則全數剔除（其中含貌似高值貨——ratchet 被 missed-severity 毒化、panel 末筆語意——不走後門撿，留醒席與否決席浮回）。護欄觸發（連 2 筆 missed 條件在本 loop 帳成立）→ r2 升 opus。**編排者偏離自省（記入 M1 回饋）**：slot2/slot4 的 canary 植在該席鏡頭責任田之外——missed 率混入 lens-scoping 因素非純放水訊號；panel canary 植入紀律應加「型別異段＋落在該席專攻範圍內」雙條件。
slot3（醒席）7 條折入 v2：
- **F1 phase 判定順序（major）**：cap 檢查改短路優先＋三分支互斥窮盡——原字面 if/elif 順序使 cap-reached 永不可達、next 誘導無限燒（違「到頂停」硬教義）。
- **F2 `--spec` 讀檔失敗面（major）**：只查存在性會對目錄裸 traceback——統一 OSError 兜底 rc2，沿 G1 :2687-2691 慣例。
- **F4 PRIOR-ART 自相矛盾（minor）**：「零新命令」與 #1 新 subparser 打架——自我治理判準不得帶頭失守，改誠實版。
- **F5 hash 行尾敏感（minor）**：CRLF/正規化觸發無資訊量重審——v1 接受並記載。
- **F6 phase 死值（minor）**：record/gate 從 v1 契約拿掉（防消費端死分支）。
- **F7 light cap 缺數（minor）**：補 tier→cap 直給對照（light=2/standard=3/high=3/legacy=6）。
- **F8 loop id typo 不可分辨（minor）**：既有結構限制記入隱患。

**r2-Codex（2026-07-21，否決席 gpt-5.6-sol high，108k tokens，無 canary 約束）**：**VETO，5 major 全折入 v3**——其中 C2/C4/C5 後半＝被剔除 missed 席真貨的跨家族獨立再發現（機制二度自證：剔除規則不吞真信號，真貨從可信通道浮回）：
- **C1 next 輸入不足不得宣告 converged（major）**：gate 合取依賴 --need/--spec/--repo/--panel——next 改為完整 gate 旗標組委派既有謂詞，資訊不足 rc2 絕不輸出 converged；空帳模板模式由 tier 確定性推導（standard/high→panel、light→legacy）。
- **C2 末筆→末輪 hash（major）**：append 補一筆可繞過整輪重審——升級為判定輪內全帶-hash 記錄彼此一致∧=當前檔，輪內漂移即 FAIL。
- **C3 advisory 永久逃生門（major）**：新 loop 可永不啟用——定錨式啟用（帶過即必須帶到底）＋light 強制 fail-closed＋工具鏈模板預設帶 --spec 收窄；殘餘（整條不帶）誠實記載。
- **C4 record/fold 時序顛倒（major）**：現行為先 record 後 fold，原 spec 斷言相反——裁定調整 skill 時序（caught 輪 record 移 fold 後收尾），列同步義務，不假裝既有慣例。
- **C5 light 謂詞漏欄位互證＋ratchet 吃 missed（major）**：補 clean⇒0/minor⇒≥1 互證（復用 :2710）；ratchet 改只吃 caught 筆 severity（missed 判決不採信教義）。

## 實務隱患

- **self-governance 循環（最重）**：四件全動「判 spec 能否進實作」的閘——gate 邏輯錯＝系統性放行壞 spec 或永擋好 spec。緩解＝本 spec 過完整 design-loop（high：W=5＋跨家族否決席）＋測試逐條對齊謂詞矩陣＋實作後 full code-loop（pitfalls 必判 high）。
- **loop next 的權威錯覺**：next 吐的是**指針非命令**——editor 若把模板當絕對真相（如 tier 給錯→width 錯），會系統性走錯陣容。緩解＝輸出頭印「advisory：tier 由編排者宣告」＋skill 派工模板仍為權威。
- **light ratchet 的 loop-id 邊界**：ratchet 永久 FAIL 綁 loop id——換 id 就洗掉（同 evidence-gate「換 loop_id 洗紀錄」既有天花板）；hash 綁定收窄但不封死此路。誠實記載，v2 spec-hash 綁 loop 可再收。
- **成本欄 GIGO**：tokens/wallclock 是編排者自報——謊報不可偵測；帳的價值在趨勢非單筆精度（同 anchors GIGO 條）。
- **cap 硬編碼雙源**：next 的 cap 與 skill 文字雙處宣告——漂移風險；以 code 為準、skill 回寫。
- **hash 對行尾/編碼敏感（r1 折入）**：byte-level sha256——跨機器 autocrlf/編輯器正規化會使「語意未變」的檔判成「被改動」觸發無資訊量重審。fail-closed 方向（誤擋非誤放）；v1 接受不緩解（單機工作流為主），記載此成本。
- **loop id typo 不可分辨（r1 折入，既有結構限制）**：無 loop 註冊表——打錯 id 與開新 loop 在 next 眼裡同為「零記錄→plant-canary N=1」，無法提醒。`loop status` 現況同病，非本包引入；記載防「權威指針」錯覺加重此坑。
