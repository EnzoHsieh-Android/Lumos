---
type: project
status: doing
created: 2026-07-09
updated: 2026-07-09
tags:
  - type/project
  - status/doing
related:
  - "[[design-loop]]"
  - "[[canary-audit]]"
  - "[[convergence-evidence-gate]]"
  - "[[risk-tiered-review]]"
summary: |-
  FLAG:DECISION
  KEY:把 design-loop/code-loop 從「6 輪同族循序」壓到「≤3 輪:1 輪平行多樣 panel + 條件式精修」,同準確度、砍 token+wall-clock。動機=6 輪跑在文獻有用邊界外(2-3 輪抓絕大部分增益)、且同族循序=相關信號(9 judge 只值 2 票)、framing「你一定找得到」對抗 G2 收斂逼跑滿 cap
  PRIOR-ART:搜過三線文獻(非憑印象):多智能體辯論 2-3 輪報酬遞減(arxiv 2506.00066)/同族 panel 錯誤相關「9 judge 2 票」(2605.29800)/平行廣度常勝循序深度、最優比按難度(2408.03314、2502.20379)/自適應穩定停(2510.12697)。裁定 borrow-design 原生實作,不引依賴
  KEY:核心洞=買獨立廣度而非相關深度——1 輪 3 個「多樣」審計員(canary 型別 a/b/c 各異 + 鏡頭各異 + ≥1 跨家族 qwen)的獨立信號 > 6 輪同族循序;canary per-auditor 平行做(注意力檢查更強非更弱)
  KEY:結構=Round1 平行 panel(覆蓋一次買齊)→ Round2-3 條件式循序精修(只在存活 ≥major 才跑,只重審 delta)→ 收斂判準改 verdict 穩定非輪數;tier=standard 只跑 R1、tier=high 才 R1+≤2 精修(複用 risk-tiered-review)
  KEY:誠實天花板=canary 注意力測試正交於辯論共識,壓縮須保留 per-auditor canary;「2 票」定理反對天真擴 panel→多樣性(型別+鏡頭+家族)是關鍵非數量;本計劃自己該用新規則 dogfood
  DEP:[[design-loop]]
  TEST:待實作;本計劃以「用新 ≤3 輪規則跑自己收斂」為第一驗證
---
# loop 三輪壓縮_計劃

> 把 canary-護的對抗審計 loop(design-loop + code-loop)從 6 輪同族循序壓到 ≤3 輪,同準確度、砍成本與時間。緣起:使用者指出 6 輪太耗;PRIOR-ART 搜證 6 輪跑在有用邊界外。

## 背景:為什麼 6 輪是浪費
- **文獻**:多智能體辯論 2-3 輪抓絕大部分增益、超過 3 輪報酬遞減甚至退化(arxiv 2506.00066)。
- **相關信號**:審計員同族(sonnet/opus)+ 同 framing + 循序 → 「9 judge 只值 2 票」(2605.29800)的相關性,6 輪 ≪ 6 份獨立信號。
- **framing 對抗收斂**:`skills/lumos-design-loop/SKILL.md` 的「你一定找得到至少一個」保證每輪必交 minor,G2 發現枯竭壓不到底,逼跑滿 cap(exec-anchor-gate 空燒、claude-reinject 撞 glue 天花板同根)。

## 方案(borrow-design,零依賴原生)
### Round 1 — 平行多樣 panel(一次買齊覆蓋)
同時派 **3 個多樣審計員**(平行,非循序):
- **canary 型別各異**:a(壞章節引用)/b(未定義旗標)/c(未定義常數)各植一份工作副本 → 型別覆蓋一輪買齊,不攤 4 輪。
- **鏡頭各異**:正確性 / 邊界與可執行性 / 整合與知識同步。
- **≥1 跨家族**:複用 `governance/autonomous_loop/cross_audit.py` 的 qwen 路徑(從「終審才用」提前到 R1),破同門盲點。
- 每審計員**各自 canary**,注意力檢查平行 3 份(比 1 份強)。findings 去重 → 對存活 ≥major 派 opus 辯方(`skills/lumos-design-loop/templates.md` §2)。

### Round 2-3 — 條件式循序精修
- 只在 R1 有存活 ≥major 才跑;fix → **只重審 delta**(borrow PR-Agent 增量審)。
- R1 回 clean/minor → 立即收斂(多樣 panel 一輪的獨立信號 > 6 輪同族循序,K 降到 1)。

### 收斂判準:verdict 穩定,非輪數
- 沒有新 ≥major 即停(borrow adaptive stability detection 2510.12697),配既有「實質收斂 early-exit」。
- **tier 分配**(複用 `Systems/risk-tiered-review`):standard 只跑 R1;high 才 R1 + ≤2 精修(對上文獻「最優平行/循序比按難度」)。

## 誠實天花板
- canary 注意力測試正交於辯論共識;壓縮**保留 per-auditor canary**(每平行審計員各自誘餌),不為省而砍。
- 「9 judge 2 票」反對天真擴 panel:3 個 sonnet 不算 3 票 → **多樣性(型別+鏡頭+家族)是關鍵,非數量**。
- 平行 R1 的 3× auditor 呼叫換掉 3-4 輪循序:token ≈ break-even 或更省,**wall-clock 大降**;最好情況(R1 乾淨)~2.5× 省。
- 文獻是 benchmark 準確度,非 canary/辯方構件;移植的是「輪數 vs 廣度」與「收斂點」,不是 1:1。

## 知識同步影響
落地須改:`skills/lumos-design-loop/SKILL.md`(每一輪流程 → R1 平行 panel + R2-3 條件)、`skills/lumos-code-loop/SKILL.md`(同構)、`skills/lumos-design-loop/templates.md`(加平行 panel 派工模板)、`governance/autonomous_loop/orchestrator-prompt.md`(自主 loop 步驟 3-8 改平行)、`Systems/design-loop.md`(收斂判準 KEY)。cross_audit.py 從終審提前到 R1 的接線。

## 實務隱患
- 平行 3 審計員讀 3× spec:token 與 6 輪循序讀 6× 相比仍省;但單輪峰值並發高。
- qwen 跨家族在 R1 每輪都用 → 成本從「終審一次」變「每 spec 一次」,仍 ~$1/月級,可接受;無 key/API 掛 → degrade 成純 Claude panel(fail-open)。
- 判讀 3 份平行報告的去重與 severity max 由編排者一次做,比循序逐輪判省事但單次認知負荷高。
- 自主 loop 無人攤牌:early-exit 走 unconverged requeue,tier=high 仍需硬證據閘。

## 審計修正紀錄

### R1(2026-07-09,新規則 dogfood:平行多樣 panel × 3,sonnet A正確性/B邊界/C整合;無跨家族 qwen——手動 Agent tool 限 Claude,此軸未驗)
- **canary 3/3 caught**(a=§4.2壞引用 / b=--stability-window / c=PANEL_WIDTH_DEFAULT,三審計員各抓各的)——一輪平行完成舊機制需 3 輪循序的注意力覆蓋。
- **存活 blocker(三鏡頭獨立收斂 + 真 code 佐證,非假陽性,不折入即修——需重設計)**:
  - **B1 收斂機制正面衝突(致命)**:本設計「1 輪平行 panel + K=1」與剛落地的 `convergence-evidence-gate` G2 衝突——G2「findings 枯竭」是**序列語意**(單調不增、末輪≤1,`scripts/lumos:1685-1689`);need=1 退化成「findings==0 才收斂」,與本設計「clean/**minor** 即收斂」(minor⇒findings≥1)矛盾,閘永遠 FAIL。**根因**:壓縮不能只改 skill——平行 panel 用**廣度**產生獨立信號,但 G2 的收斂信號建在**深度序列**上;兩者拓樸不合。
  - **B2 canary-record 資料模型**:`cmd_canary` 1輪1筆,裝不下 3-auditor panel;平行 canary missed 無「下一輪」可作廢。
  - **B3 tier 不驅動寬度**:`difficulty.params()` 只回 {need,maxr},無「並行寬度」維度;`PANEL_WIDTH_DEFAULT` 憑空(且是 canary,但真設計確實缺此常數與能力)。
- **major**:去重演算法未定義(影響 G2 計數)/ cross_audit 提前 R1 時 evidence 空退化 + qwen 無 canary 能力破「per-auditor canary」/ 成本 model per-spec vs per-round 差 3× / 知識同步漏列 `convergence-evidence-gate.md` + `templates.md`(平行需新派工模板)+ `scripts/lumos` G2 code 改動。
- **裁定**:R1 severity=blocker,**不收斂**。但**實驗本身成功**——機制(平行 panel、3 canary 一輪全抓、獨立收斂真 blocker)驗證了「廣度取代相關深度」;而它抓到的 B1 是真設計缺陷,證明壓縮的正確 scope 比原設想大。
- **redesign 方向(B1 的解,實驗浮現)**:平行 panel 的收斂信號**不能沿用 G2 的序列枯竭**——改為 **cross-auditor 獨立同意**(adaptive stability / 多樣 panel 都判無 ≥major = 收斂),這才配平行拓樸。故壓縮**必須同時改** `convergence-evidence-gate`(G2 語意)+ `scripts/lumos` cmd_loop_status,非 skill-only。待使用者裁定是否進此擴大 scope。
