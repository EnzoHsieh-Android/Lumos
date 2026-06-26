---
type: system
status: rejected
created: 2026-06-26
updated: 2026-06-26
self_audit: sonnet/2026-06-26
tags:
  - type/system
  - status/rejected
summary: |-
  FLOW:gap(單一 judge 不可靠)→設計擾動穩定度測試(關鍵輪換序審兩次、翻盤即不採信)→design-loop r1 折機械 reorder→r2 揭機制堵不住自證(只換藏身處)→人選放棄→改輕方案:可信度報告硬列「迴圈沒檢查到的維度」
  KEY:評估後放棄(2026-06-20)——非未完成,是 design-loop 揭示「用同一 judge 審它自己穩定性逃不出『誰控制擾動』的自證悖論」後的主動不做判斷
  KEY:落地的不是擾動機制而是輕方案——confidence_report.py 把殘留風險升級成「結構上沒能自動檢查的維度」(judge 單一不可靠列首),把放行人的眼睛導到破口[code:governance/autonomous_loop/confidence_report.py]
  KEY:換模型家族(RAND 核心解)在當前工具鏈無實現路徑——claude -p 只路由 Anthropic、OAuth 訂閱再砍到只剩 opus/sonnet,故只能做「同家族內」抗擾動
  DEP:governance/autonomous-loop.sh(RESIDUAL 清單)｜confidence_report.py｜judge-severity-gate(被它推進到的「judge 集中化」是本案要補又會加深的弱環)
  TEST:無(方案放棄、未實作);輕方案的 confidence_report.build_report 在 loop 跑時產報告
  VERIFY:無(放棄決定無功能可驗,design-loop 收斂史見設計稿)
decisions:
  - content: 放棄擾動穩定度測試方案,改用輕方案——可信度報告硬列「這個迴圈沒檢查到的維度(judge 單一不可靠列首)」,把破口誠實標給最後兜底的人,不建 reorder 機制
    context: design-loop r1→r2 每次折修只把自證悖論換個藏身處(agent 產擾動→機械 reorder,但 reorder 由誰執行/種子誰選仍可被被審者操控);且只解「隨機不穩」一半(系統性偏要換家族、$0 OAuth 做不到)、反加深 judge 集中化、為半個解建確定性 reorder+hash+diff 真功能 ROI 低
    why_chosen: loop engineering 洞察——不是每個弱環都該用更多機制堵;有些在當前約束下機制化只會越重越撞自證,最誠實是承認局限、攤給人。機制堵不住的就誠實標給人,別假裝堵得住
    decided: 2026-06-20
    valid: true
  - content: 擾動標的與執行者改用機械 reorder(確定性程序打亂 findings/bullet 順序、逐字不改內容),取代原「orchestrator 自產擾動版+自寫 note 說等價」
    context: design-loop r1 major F3 揪出原方案讓被審者自填擾動=judge-severity-gate 才斷開的「被審者自填」反模式在新位置復發
    why_chosen: 機械 reorder 確定性、可驗證等價、無 agent 自證,作弊面歸零,且更對症(RAND 測的本就是換排版/順序);惟 r2 再揭即使機械化,「由誰執行/種子誰選」未定義時自證仍復活,成為放棄理由之一
    decided: 2026-06-20
    valid: true
---
# judge-perturbation-stability

> **狀態:評估後放棄(2026-06-20)。** 這是一份「決定不做」的節點 —— design-loop 揭示方案堵不住自證悖論後的主動判斷,非未完成的功能。

## 是什麼 / 想解決什麼
為 autonomous design-loop 的 **judge 抗擾動性** 設計的方案:在要判 clean/minor 的**收斂關鍵輪**,把同一份輸入換個呈現再讓**同一個 judge** 審一次;severity 跨越收斂門檻(clean/minor ↔ major/blocker)= 該 judge 這輪不穩 → 不採信、不算收斂。目標是把 judge 從「一次說了算」升到「至少抗得住輕微擾動」。

- **源起:日報 2026-06-20 gap[2] + inspirations[1]** —— RAND JRH「沒有單一 AI 評審穩定可靠、換排版就翻盤」「考官也要被考」。`judge-severity-gate` 把 severity 交給 judge 後,judge 單一不可靠成了新的最弱環。

## 為什麼放棄(關鍵)
design-loop 兩輪揭示方案的根本兩難:
1. **堵不住自證**:r1 把「agent 產擾動」折成「機械 reorder」,r2 再揭 reorder 由誰執行、種子誰選未定義——若是 orchestrator(被審者)就能挑對自己有利的順序,自證悖論原樣復活。每次折修只換藏身處。
2. **只解一半**:擾動只抓「換排版就翻盤」的**隨機**不穩;**穩定的系統性偏見**(對某類 spec 一貫低估)兩次都偏、抓不到——要換模型家族才解,而 `claude -p` 只路由 Anthropic、$0 OAuth 訂閱砍到只剩 opus/sonnet,**根本沒有實現路徑**。
3. **負和**:judge 同輪被呼兩次,權重更集中於單一 judge —— 修一弱環(隨機不穩)反**加深**另一弱環(judge 集中化)。
4. **ROI 低**:為半個解建一套確定性 reorder + 種子=hash + 自動 diff 等價閘的真功能。

## 落地的是輕方案(已實作)
改用日報 inspirations 的更輕路線:`confidence_report.py` 的可信度報告把「殘留風險」升級成 **「⚠ 這個迴圈沒檢查到的維度(品質最可能爛在這、放行請特別盯)」**,judge 單一不可靠列首位;`autonomous-loop.sh` 的 `RESIDUAL` 清單同步攤明(現況該清單還記了「跨家族複核已加(qwen3-max 放行前複核 opus)但 degrade 退回單一 opus」「severity 由 judge 評但同輪判 canary+severity=集中化」等)。把放行的人的眼睛導到機制堵不住的破口。

> loop engineering 洞察:不是每個弱環都該用更多機制堵。有些在當前約束下機制化只會越重越撞自證,最誠實是承認局限、攤給最後兜底的人。design-loop 的價值正在於它沒讓一個 ROI 存疑的方案硬做到收斂,而是逼出「不該做」的判斷。

## 已知限制 / 殘留
- 系統性偏見(同門偏心)仍**未解**——換家族才解,當前工具鏈做不到;只能靠可信度報告誠實標給人。
- judge 集中化(canary + severity 同輪由單一 judge 判)仍在,本案放棄後維持現狀。

## 相關
- 設計稿:`docs/design/2026-06-20-judge-perturbation-stability.md`(含 R1/R2 design-loop 收斂史與〈放棄決定〉全文)。
- 姊妹設計:`docs/design/2026-06-20-judge-severity-gate.md`(把 severity 交給 judge,催生本案要補的弱環)、`docs/design/2026-06-20-autonomous-iteration-loop.md`(judge 機制所在的自主 loop)。
- 落點(輕方案):`governance/autonomous_loop/confidence_report.py`、`governance/autonomous-loop.sh`(`RESIDUAL`)。
