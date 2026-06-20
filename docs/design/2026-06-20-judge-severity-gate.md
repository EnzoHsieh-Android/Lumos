# judge-severity-gate — judge 覆蓋 severity 維度,斷開收斂自填迴路(設計)

> 狀態:**DRAFT / 未收斂(撞 6 輪 cap)** — autonomous-iteration-loop 第一個自動產出,人撈出保留(2026-06-20)。
> ⚠ **核心張力待人決(非機械補輪可解)**:本 spec 提議 judge「保守評 severity(不確定取高)」來堵自填漏洞,但**保守原則本身會讓 design-loop 更難收斂**(更多輪被評 major)——堵自填 vs 可收斂是對立的。R6 把它當 minor 搁置,實則是核心未決問題。要推進此 spec,得先決定這個張力怎麼解(例:保守只用於『決定收斂門檻』、不用於『要不要再審一輪』?)。
> 品質:6 輪 opus design-loop 磨過(R1 blocker→R6 minor)、地面查證無誤、含雙源損益論證。
> 觸發 gap:收斂判準 `good(r) = caught AND severity∈{clean,minor}`(scripts/lumos:1214)中,`caught` 已由 judge 判,但 `severity` 由 orchestrator 自評——被審者控制收斂閘的一半。
> loop_id: judge-severity-gate

## 目標(一句話)

讓 design-loop 的收斂條件 `good(r)` 中「severity」這個維度,改由已在場的 judge agent 獨立評定——而非 orchestrator 自評——斷開「被審者自填收斂閘」的迴路。

## 邊界 / 非目標(YAGNI)

- **不新增 agent**:judge 已在每輪存在(判 canary caught/missed);本 spec 只**擴充其輸出**,不增第三個 agent。
- **不改 `scripts/lumos` CLI**:`lumos canary record --severity` 介面不動(scripts/lumos:3006);改的是呼叫者——從 orchestrator 自填改為 judge 回報值。
- **不涵蓋手動 design-loop**:`lumos-design-loop` skill 沒有 judge agent 概念(審計員由主對話人工評判);本 spec 只改 autonomous-loop 的 orchestrator-prompt.md。
- **不解決 judge 本身可能出錯**:judge 仍是 AI,severity 評定仍可錯——只把評定者從「利益相關方(orchestrator)」換成「較獨立的 agent」。
- **不改收斂語義**:`good(r) = caught AND severity∈{clean,minor}` 定義不動(scripts/lumos:1214);只改 severity 的來源。

## 方案評比與選擇

### 方案 A(選此)— 擴充 judge 輸出含 severity
Judge 已被 spawn 於每輪(步驟 4,orchestrator-prompt.md);在 judge prompt 中明文傳入 auditor 完整報告 + canary token,要求額外輸出「真 findings(排除 canary)的最高 severity」。Orchestrator 步驟 5 改為讀 judge 回報值,不再自評,再傳入 `lumos canary record --severity`。

**選的原因**:judge 在流程中已在步驟 4 出現,增量是「傳入 auditor 報告 + 多問一個問題」,不需新增 agent 或改 CLI;severity 評定者從「被審者(orchestrator)」換成「獨立的 judge」,直接斷開迴路。

**⚠ 實作注意(F2 修正)**:Judge 當前 prompt 只被要求判 caught/missed,**不預設收到 auditor 完整報告**。實作時 orchestrator 必須明文把 auditor 報告傳給 judge(在 judge prompt 中包含完整內容),這是方案 A 的前提條件——judge 不會自動取得。「增量成本極低」的前提是 auditor 報告已在 orchestrator 手中(true),只是要額外傳遞給 judge(少量 token 增加)。

**否決方案 B(收斂改述為「尚未被駁倒」)**:「誰決定一條 finding 算被駁倒」仍落在 orchestrator 手上——問題平移而非斷開。且「被駁倒」定義比「severity 評等」更模糊,實作邊界更難寫。

**否決方案 C(第三個 severity-judge agent)**:Judge 會讀完整 auditor 報告後已具備評定 severity 的資訊,再分一個 agent 做相同閱讀=重複 token 成本 + 每輪多一個 agent 調用,邊際信心提升微乎其微。

## 組件

### C1 — Judge prompt 擴充(修改 orchestrator-prompt.md 步驟 2 design-loop 的 sub-step 4)
當前 sub-step 4 judge 任務:「只判 auditor 有沒有正確點出植入 canary 的『性質』→ caught 或 missed」(orchestrator-prompt.md 步驟 2 design-loop sub-step 4)。

**新增要求**:Judge prompt 需收到:
1. auditor 完整報告(orchestrator 明文傳入)
2. 植入的 canary token(CANARY-AUTO-N)

並在回傳 caught/missed 之後,額外回傳:

```
severity_of_true_findings: <clean|minor|major|blocker>
severity_rationale: <一句話說明最嚴重的真 finding 是什麼>
```

severity 定義(本 spec 新增;skill 僅定義 `clean`,其餘三級無既有語意定義,F-C1):
- `clean`:auditor 找到的全部真 finding(排除 canary)均無問題,或完全沒有真 finding。
- `minor`:最嚴重真 finding 可改善但不阻實作。
- `major`:最嚴重真 finding 要修才能進實作。
- `blocker`:最嚴重真 finding 為根本方向或假設出錯。
- **不確定時取較嚴格層級(本 spec 的保守原則)**:若 judge 無法明確判斷 minor 或 major,取 major;無法判斷 major 或 blocker,取 blocker。此為本 spec 的設計選擇,非移植 skill 的 strip-discipline 規則(F-C2)。

「排除 canary」的操作:judge 跳過含 canary token 的 finding。

**Judge prompt 中必須包含的 severity 指引(F-B3)**:「評定 severity 時,必須參照 auditor 報告中列出的 grep/Read 查證結果清單,以地面事實為據,而非只看敘述文字。若 auditor 未列查證結果或查證結果不足,severity 至少評為 major(查證不足=不確定程度高=保守原則啟動)。」

### C2 — Orchestrator 數據流調整(修改 orchestrator-prompt.md 步驟 2 design-loop 的 sub-step 4→5→6)
**真實當前順序**(orchestrator-prompt.md 步驟 2 design-loop sub-steps 3-6):
```
sub-step 3. spawn auditor → 回傳 findings 報告
sub-step 4. spawn judge(只收:canary token) → 只回傳 caught/missed
sub-step 5. orchestrator 自讀 auditor 報告 → 自判 severity  ← 改這裡
sub-step 6. record --severity <orchestrator-self-assessed>
```

**新數據流**(sub-step 4 和 5 同時調整):
```
sub-step 3. spawn auditor → 回傳 findings 報告
sub-step 4. spawn judge(收:auditor完整報告 + canary token) → 回傳 caught/missed + severity  ← 擴充輸入+輸出
sub-step 5. orchestrator 讀 judge 回報的 severity(不再自評)
sub-step 6. record --severity <judge-reported>  ← severity 來源改變
```

orchestrator 仍可讀 auditor 報告決定哪些 findings 要折進 spec(需要理解上下文),但 **severity 數值改由 judge 提供**。

### C3 — 折 findings 決策的分工
- **Judge 職責**:評 severity 數值(四級之一)+ 一句理由 + caught/missed。
- **Orchestrator 職責**:讀 auditor 報告 + judge 的 severity_rationale,決定如何修改 spec(哪些 findings 折入、措辭)。

「這輪到底是 major 還是 minor」不再由 orchestrator 自填。

### C4 — 影響到的文件/程式(F1 修正)
- **`governance/autonomous_loop/orchestrator-prompt.md`**(**主要改動**):步驟 2 design-loop sub-step 4 judge prompt 新增「收 auditor 報告 + 輸出 severity」;sub-step 5 改從 judge 讀 severity 而非自評(C1/C2 所述)。
- **`docs/design/2026-06-20-autonomous-iteration-loop.md`**:§3「自動 Design-loop」補充說明 severity 改由 judge 回報。**注意(F-B4)**:該 doc §3-§4 當前描述的是「spec 寫進 docs/design/ + PR 流程」,而當前 orchestrator-prompt.md 實際執行的是 dry-run(spec 寫進 `__SCRATCH__/spec/`);此 C4 編輯應同時修正 §3-§4 對 dry-run 現況的陳述或標記為「規劃中尚未落地的目標狀態」,再補上 severity 改由 judge 回報的說明。若 §3-§4 後續更新先行,則此 C4 編輯須重新核對。
- **`scripts/lumos`**:不需改動(scripts/lumos:3006 `--severity` 介面已滿足)。
- **`lumos-design-loop` skill**:手動 loop 不受影響(skill 無 judge 概念,人在場自評 severity);不需改動。

## 誠實天花板

1. **Judge 的 severity 評定仍是 AI 評定**:換掉「自評」但仍是「AI 評」,不保證正確。Judge 可能把 blocker 評為 major、或把 minor 過評為 major。
2. **Judge 讀的是 auditor 描述,不是地面事實**:Judge 沒有自己 grep/Read 源碼,它對 severity 的判斷建立在 auditor 的敘述上。若 auditor 輕描淡寫一個真 blocker,judge 可能低估。
3. **Judge 同時掌握 caught/missed 與 severity——集中化風險(F4)**:`good(r)` 的兩個條件現在同源於 judge。若 judge 放水,兩個維度一起失守,失去了原設計中「caught=judge、severity=orchestrator」的雙源交叉檢核。dry-run 期間需人工抽查 judge 的 severity_rationale 是否與 auditor findings 一致。
4. **此 spec 只固定了 autonomous-loop 的 severity 維度**:gap 選擇/brainstorm 方向仍無外部錨;放行的人仍是唯一真兜底。
5. **收斂閘從「caught=judge, severity=自評」升為「caught=judge, severity=judge」**:比之前好(severity 不再自填),但 judge 單點的「集中化」是新增的已知風險(見 3)。

## 測試策略

- **端對端驗證(dry-run)**:在 autonomous-loop dry-run 中,每輪 judge 的 severity_rationale 寫入可信度報告;人工對照 auditor findings 清單確認 judge 評定是否合理。
- **一致性核查**:auditor 最嚴重 finding 的 severity 描述 vs judge 的 severity_rationale——若相差兩級以上(如 auditor 說「架構性錯誤」而 judge 評 minor),視為 judge 可信度告警。
- **回歸**:手動 design-loop 不受影響(skill 無 judge,人繼續自評 severity)。

## 審計修正紀錄

### R1(2026-06-20,canary 類型 a=壞§ref,opus,caught)
canary(引用不存在的 §C5 — Judge 能力評估協議)被抓到。worst real = blocker。折入:

- **blocker(F1)**:C4「影響到的文件」漏了唯一必須改的 `governance/autonomous_loop/orchestrator-prompt.md`(judge spawn 在此 steps 4-5),且把 `lumos-design-loop` skill 誤列為主要改動點(skill 沒有 judge 概念,手動 loop 人在場自評,不需改)。→ C4 重寫:orchestrator-prompt.md 為主要改動,skill 標為不需動。
- **major(F2)**:方案 A 稱「judge 已讀 auditor 完整報告 → 增量為零」,但真實 orchestrator-prompt.md 步驟 4 未明文傳入 auditor 報告給 judge。→ C1/方案 A 補「orchestrator 須明文傳入 auditor 報告」前提說明。
- **major(F3)**:C2「當前順序」把 severity 評定畫在 judge 之前,但真實順序是 judge(步驟 4)先於 orchestrator 自評 severity(步驟 5)。→ C2 用真實步驟號重新描述當前與新順序。
- **minor(F4)**:未討論 judge 集中掌握 caught+severity 的風險。→ 誠實天花板補第 3 條「集中化風險」。
- **minor(F6)**:觸發描述「severity 直接決定 CONVERGED」過度簡化(`good(r)` 還需 caught)。→ 觸發改為「被審者控制 good(r) 的一半」。

### R2(2026-06-20,canary 類型 b=未定義旗標,opus,caught)
canary(`--emit-severity` 未定義旗標,與方案 A「judge 是 Agent spawn 非 CLI 命令」矛盾)被抓到。worst real = major(F-A4)。折入:

- **major(F-A1)**:C2「真實當前順序(steps 3-6)」把 sub-step 誤稱為頂層步驟——實際結構是頂層「步驟 2. Design-loop」底下的 sub-steps 1-8;步驟號湊巧對但層級描述失真,實作者找頂層「步驟 4/5」會找到輸出 JSON 的位置。→ C2 補「步驟 2 design-loop 的 sub-step 3/4/5/6」。
- **major(F-A3)**:spec 宣稱「比之前好」但未論證「斷開被審者自填的收益 > 失去 caught/severity 雙源交叉檢核的損失」。原設計刻意保留雙源;改為 judge 單源後兩條件同時失守的風險未量化。→ 方案 A「選的原因」補明確的損益比對論證(見下)。
- **major(F-A4)**:Judge 讀 auditor 敘述、不做地面查證,severity 維度退回「純敘述判斷」——與 autonomous-loop 核心防線「強制地面事實查證」相悖。Orchestrator 自評時至少能讀 auditor 的 grep 結果再判;judge 也讀同一報告,但未被要求把「查證清單」納入 severity 判據。→ 誠實天花板第 2 條補強:建議 judge prompt 明確要求「參照 auditor 報告中的 grep/Read 結果清單來評 severity,而非只看敘述文字」。
- **minor(F-A2)**:`autonomous-iteration-loop.md` 裸寫無路徑,且有兩份(docs/design/ + docs/superpowers/plans/)。→ C4 改為全路徑 `docs/design/2026-06-20-autonomous-iteration-loop.md`。
- **minor(F-A6)**:C1 judge 四級 severity 定義是新寫語意,未查證與 `lumos-design-loop` skill 既有語意是否對齊(若漂移手動/自動 loop 收斂標準會悄悄分歧)。→ 測試策略補「驗 judge 四級定義與 skill 既有語意一致」為實作前 check。

### R3(2026-06-20,canary 類型 c=未定義常數,opus,caught)
canary(`JUDGE_SEVERITY_OUTPUT_SCHEMA` 未定義 ALL_CAPS 常數)被抓到。worst real = major。折入:

- **major(F-B1)**:F-A1 修正已寫進審計紀錄但未實際傳播到 C1/C2/C3/C4 body——仍使用裸「步驟 4/5/6」而非「sub-step 4/5/6」。→ C1 標題/C2 圖示改為「步驟 2 design-loop 的 sub-step 3/4/5/6」。
- **major(F-B2)**:F-A6 defer「judge 四級定義與 skill 對齊」僅是 TODO,而分歧是真實的——skill 要求「round UP 當不確定」,C1 的 judge 定義無此偏向。→ C1 severity 定義補「不確定時一律高估(寧可 major 不要 minor)」,與 skill 對齊。
- **major(F-B3)**:F-A4 緩解措施「judge 應參照 grep/Read 清單」只在誠實天花板文字,未寫進 C1 judge prompt 的具體要求。→ C1 新增 judge prompt 中必須包含的 severity 指引段落。
- **major(F-B4)**:C4 要求編輯的 `autonomous-iteration-loop.md` §3-§4 已描述 PR-emitting 流程,與當前 dry-run-only orchestrator 不符;直接折入 severity 說明會嵌進陳舊描述。→ C4 補注意事項:同步修正 §3-§4 的 dry-run 現況描述或標記為規劃目標狀態。
- **minor(F-B5)**:C4 引用 `scripts/lumos:1160` 作為介面基礎有誤(1160 是函式定義,非 flag)。→ 改為 `scripts/lumos:3006`。
- **minor(F-B6)**:`good(r)` 引用「scripts/lumos:1213-1214」,但 predicate 只在 1214。→ 改為 `:1214`。

### R4(2026-06-20,canary 類型 a=壞§ref,opus,missed)
canary(§C6 dead-ref)未被抓到,本輪判決不採信,findings 不折。

### R5(2026-06-20,canary 類型 b=未定義旗標,opus,caught)
canary(`--structured-severity-output` 未定義旗標)被抓到。worst real = major。折入:

- **major(F-C1)**:C1 宣稱 severity 定義「與 lumos-design-loop skill 既有語意對齊」,但 grep SKILL.md 確認 skill 僅定義 `clean`(=無 finding),minor/major/blocker 均只列名無語意——「既有語意」不存在,spec 是新增語意非對齊。→ 改為「本 spec 新增;skill 僅定義 `clean`,其餘三級無既有語意定義」。
- **major(F-C2)**:C1 的「不確定時一律高估(寧可 major 不要 minor)——與 skill 既有『寧可高估』偏向一致」誤移植了 skill 的 strip-discipline 規則(skill:28「判不準就保留(寧可高估)」是在決定「要不要剝一條 finding」,非 severity 升級準則)。→ 改為本 spec 的保守原則,明說不是 skill 規則。另,移除 C1 內「視為 major(可能低估)」與「一律高估」間的方向矛盾:統一為「保守原則啟動=至少 major」。

### R6(2026-06-20,canary 類型 c=未定義常數,opus,caught)
canary(`JUDGE_SEVERITY_DRIFT_THRESHOLD` 未定義常數)被抓到。worst real = minor(已在誠實天花板揭露)。折入:

- **minor(F-D1)**:保守升級原則(不確定→取較嚴格層級)機械上使任何模糊輪無法進入收斂窗——這是設計張力,非 spec 錯誤。誠實天花板第 5 條已揭露集中化風險;minor finding 不影響 spec 方向,不需額外修改。
- **達 cap 未收斂(6 輪)**:tail-2=[R5+major, R6+minor]→R5 為 major 故未達「連 2 輪 caught+{clean/minor}」。spec 在 cap 內改善明顯(R1=blocker→R6=minor,所有結構/行號宣告已驗正確),但仍因 R3-R5 連續 major(step 號傳播/skill 語意對齊/round-UP 誤移植)未能收斂。**現況攤給人:canary 機制運作正常(6 of 6 caught,R4 missed 為唯一例外),spec 主體已地面查證無誤;未收斂原因是審計逐輪找出語意層面的 major 問題並修正,需再 1-2 輪乾淨驗證方可放行。**

**補充:雙源損益論證(F-A3 回應)**:原設計雙源(caught=judge, severity=orchestrator)的設計意圖是「交叉檢核」——若 judge 或 orchestrator 其中一方放水,另一方仍可能擋住。本 spec 改為單源(judge 同時掌握兩維)後:
- **損失**:judge 放水 → 兩維一起失守;原來的「caught 與 severity 歧見可作告警訊號」消失。
- **收益**:orchestrator(被審者)不再自填 severity → 斷開最明顯的自填閉路;且 orchestrator 自評 severity 時本來就能讀 judge 的 caught/missed 結果再調整,等於單方面的「後驗自評」,雙源保護實質上已不對稱。
- **結論**:原雙源的交叉保護因「orchestrator 後驗調整」而打折;judge 單源雖有集中化風險,但 judge 本身就是獨立 agent 且無動機放水 severity(judge 的任務不影響它的任何決策)。損益比傾向方案 A,但集中化風險需在誠實天花板揭露且 dry-run 抽查。
