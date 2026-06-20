# judge-perturbation-stability — 讓 design-loop 的 judge 判斷抗得住輕微擾動(設計)

> 狀態:草稿(待 design-loop 收斂)｜日期:2026-06-20
> 觸發 gap(日報 2026-06-20 gap[2]):design-loop 每輪只靠單一 judge,但 RAND 實測(arXiv 2603.05399)『沒有單一 AI 評審穩定可靠』——同一份答案換排版判斷就翻盤。judge-severity-gate 把 severity 交給 judge 後,judge 單一不可靠成了新最弱環。
> loop_id: judge-perturbation-stability

## 目標(一句話)

design-loop **關鍵輪**(要判 clean/minor 的收斂輪),把同一份 spec 換個說法再讓 judge 審一次;severity 判斷翻盤 = 該 judge 這輪不穩 → 該輪不採信、不算收斂。把 judge 從「一次說了算」升到「至少抗得住輕微擾動」。

## 邊界 / 非目標(YAGNI + 誠實約束)

- **不換模型家族(做不到,$0 OAuth 約束)**:能用的只有 Claude opus/sonnet(fable-5 被禁),真「換家族(GPT/Gemini)避免同門偏心」要 API key。**RAND 的核心建議在當前約束下實現不了**,硬寫=假設做得到的破口。本 spec 只做「同家族內」抗擾動。
- **不做真多數決**(每輪多個 opus judge 投票成本翻倍,autonomous loop 已夠燒)。
- **只補關鍵輪**(要判 clean/minor 的那輪),不是每輪——成本。前面 blocker/major 輪本來就不收斂,不需擾動測試。

## 方案評比與選擇

### 方案 A(選此)— 關鍵輪擾動穩定度測試
要判 clean/minor 時,把 spec **換個說法/換段落順序**(語意不變),讓**同一個 judge** 再審一次。兩次 severity 跨越收斂門檻(clean/minor ↔ major/blocker)= 不穩 → 該輪記 missed-equivalent、不採信、不算收斂。
**選的原因**:直接對應 RAND「換排版就翻盤」實測;不需換模型、只多一次審(成本可控);只在關鍵輪觸發。

### 方案 B(否決)— judge 改 sonnet、與 opus auditor 隔離
讓 judge 用 sonnet(跟 opus auditor 不同 tier),弱版「評審與被評隔離」。**否決**:sonnet 評 severity 比 opus 糙、可能更不準;且 sonnet/opus 同家族,「隔離」是假的(同門);換來的隔離度 < 失去的判準度。不如把 judge 留 opus + 加擾動測試。

### 方案 C(否決)— 真多數決(N 個 judge 投票)
成本翻倍,且同家族 N 個 opus 投票仍同門偏心(RAND 的問題沒解、只是平均)。ROI 低。

## 組件

### C1 — 關鍵輪擾動測試(改 orchestrator-prompt.md design-loop sub-step)
- 觸發條件:judge 回報的 severity ∈ {clean, minor}(=這輪可能讓收斂窗前進)時才做;major/blocker 輪跳過(本來就不收斂)。
- 動作:orchestrator 產一份 spec 的**擾動版**(換段落順序 + 關鍵句換句話說,語意嚴格不變),用**同一個 judge prompt** 再審一次,只問 severity。
- 判定:兩次 severity 是否**同在收斂側**(都 ∈{clean,minor})。跨越門檻 = 不穩 → 該輪 severity 取較嚴格者(=不採信這次 clean/minor)、不算進收斂窗;orchestrator note 記「擾動翻盤」。

### C2 — 擾動版怎麼產(防作弊)
擾動版由 **orchestrator** 產(它非評定者),不是 judge 自己改;且必須**語意等價**(只換措辭/順序,不增刪 finding、不改數據)。orchestrator note 附「擾動版做了什麼改動」供 dry-run 抽查擾動是否真等價(否則 orchestrator 可做一個「故意更難讀」的擾動版逼翻盤、或「幾乎沒動」的假擾動)。

### C3 — 收斂語義不變、只多一道閘
`good(r) = caught AND severity∈{clean,minor}` 定義不動;C1 只是在「judge 回報 severity」與「record」之間插一道「擾動複審」,讓據實評的 severity 多一層抗擾動驗證。

## 誠實天花板

1. **同家族抗不了「系統性偏」,只抗「隨機不穩」**:擾動測試是同一個 judge 審兩次。它若有**穩定的系統性偏見**(對某類 spec 一貫低估),兩次都偏、都不翻盤——擾動只抓「換排版就翻盤」的隨機不穩,抓不到穩定的系統性偏。RAND 的「同門偏心」核心在 $0 OAuth 下**沒解**(換家族才解),本 spec 只補了一半。
2. **擾動等價性靠 orchestrator 自律**:擾動版由 orchestrator 產,「語意是否真等價」沒有機制校驗(同 judge-severity-gate 的「規範非機制」)——靠 dry-run 人工抽查擾動 diff。
3. **成本**:關鍵輪多一次 judge 審(只在 severity∈{clean,minor} 時觸發,即每個 loop 收斂前的少數輪),單日增量有限但非零。
4. **自指**:本 spec 是用「現在這個單一 judge 的 design-loop」審的——用不可靠的單一評審,審「修單一評審不可靠」的方案。不可避免,放行的人是最後兜底。

## 測試策略

- 合成:同一 spec 兩種說法,judge 給不同 severity(一 clean 一 major)→ 驗 C1 判「不穩、不採信」。
- 同一 spec 兩種說法 severity 一致 → 驗 C1 判「穩、採信」。
- major 輪 → 驗跳過擾動測試(不觸發)。
- 擾動版非等價(偷改 finding)→ 人工抽查能否從 note 看出(C2 揭露)。

## 知識同步影響(dogfood 2026-06-20 新機制)

此改動若實作,需同步:
- **`governance/autonomous_loop/orchestrator-prompt.md`**(主改):design-loop sub-step 加「關鍵輪擾動複審」。
- **`docs/design/2026-06-20-autonomous-iteration-loop.md`** §組件3:judge 那條補「關鍵輪還要過擾動穩定度測試」。
- **`docs/methodology/圖譜即合約.md`** §四「自主迭代 loop」節:judge 機制補一句抗擾動;§誠實天花板「judge 集中化」可註「已加抗隨機不穩、但系統性偏未解」。
- **`docs/methodology/圖譜即合約-對外論述.md`**:白話段「派 AI 審設計」可補一句「同一份東西換個說法再審一次,判斷翻盤就代表這個 AI 沒看穩」。
- skills:**無**(judge/擾動是 autonomous-loop 獨有;`lumos-design-loop` 手動 loop 人在場、不受影響)。

## 審計修正紀錄

(design-loop 跑完後補)
