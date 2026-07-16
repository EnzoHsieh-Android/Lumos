---
type: project
status: doing
created: 2026-07-16
updated: 2026-07-16
tags:
  - type/project
  - status/doing
related:
  - "[[Systems/design-loop]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/canary-audit]]"
  - "[[Systems/finding-refute]]"
summary: |-
  FLAG:DECISION
  KEY:問題=design-loop 常態跑滿 3 輪 cap 靠人裁,收斂慢。真因兩個結構病:①非定態目標——每輪折入改寫 spec,下輪審的是新文件,新 findings 一半在審上輪補丁,capture-recapture 的封閉族群/獨立捕獲前提偏弱(Codex 診斷);②「你一定找得到」framing 保證每輪必交 minor→G2 發現枯竭永不成立
  KEY:文獻定調——self-refinement 普遍 3 輪 plateau(SELF-REFINE/IMPROVE),cap=3 已是效率前緣;解不在加輪數/換停止規則,在「讓 r1 起點更高+後續輪只審 delta」
  KEY:藥方五條(划算排序):①R2/R3 嚴格 delta-scoped(物理只餵 diff+受影響合約+前輪爭議,留一席便宜全局哨兵)②gate 改 risk-cluster 三態帳(resolved/accepted-minor/disputed-major;停止=canary∧無disputed-major∧高風險claim雙finder覆蓋∧無新cluster;capture-recapture 降 advisory)③pre-flight cascade(機械checklist→小模型→panel)④辯方按共識路由(一致+有證據直折,低共識才開庭)⑤fold 迷你核對
  KEY:不做——SPRT(分布每輪變,不可用)/group sequential(收益極小)/Bayesian 停止(posterior 由 prior 主導,需先累 10+ loops 歷史回放校準,順序不可倒)
  DECISION:②動 loop status gate 語意=改守衛的守衛,高風險面——本計劃進實作前必過 design-loop(用舊 loop 審新 loop);①③④⑤純 skill 編排文字,trivial 級可先行
  DEP:[[Systems/design-loop]]｜[[Systems/loop-convergence-recording]]
---
# design-loop提效_計劃

> **狀態**：三路調研（web 文獻 ×3 + Codex 跨家族研究席）收斂的提效方案，尚未實作。緣起：使用者觀察「跑滿久才能收斂」（2026-07-16）。

## 問題（實測數據）

fromscratch-m1 三輪 9→6→3、T3 三輪 12→6→5——常態跑滿 cap 靠人裁實質收斂。拆 findings 性質：r1 大宗是清單型缺陷（未定義詞/矛盾/touchpoint 漏），r2/r3 一大半在審上一輪折入的補丁。

**兩個結構病**：
1. **非定態目標**（Codex 診斷，比「折入品質」更根本）：折入這個動作本身持續改寫受審對象——下輪的「新發現」可能只是新文字引入的；capture-recapture 的封閉族群＋獨立捕獲兩前提在此偏弱，殘餘估計不可當硬閘。
2. **minor 永續供應**：「你一定找得到」framing（防放水的必要之惡）保證每輪必交 minor → G2 發現枯竭結構上永不成立 → 人裁成為事實出口（T3/fromscratch 皆如此）。

## PRIOR-ART（2026-07-16 真搜：web×3 + Codex 席）

- **Self-refinement 文獻**（SELF-REFINE arXiv:2303.17651 / IMPROVE arXiv:2502.18530）：迭代精煉普遍 1-2 輪最大收益、3 輪 plateau——**cap=3 已是效率前緣**，實測 9→6→3 完全吻合。解在輸入品質與 delta 化，非輪數與停止規則。
- **軟體審查經典**（Wohlin/Runeson capture-recapture 十年總結 jss04；El Emam DPM）：估計器該用在「要不要開下一輪」的**事前決策**；experience-based 校正因子（誤差 10.5%→7%）＝歷史回放校準路線。DPM（發現速率曲線）需時間戳，選配。
- **LLM cascade/routing**（ICML 2025 dekoninck25a；ICLR 2024 uncertainty routing）：便宜先掃、不確定才升級是正統；成敗核心在 quality estimator 非層數；**路由用可觀測訊號**（席間重疊/severity 分歧/證據座標缺失/辯方翻案史），不用模型口頭 confidence。
- **Debate 負面證據**（EACL 2026 findings.268）：拉長互辯出現 problem drift/無進展——背書現行「禁互辯＋獨立席」設計，並主張更早截斷。
- **統計停止規則裁決**（Codex）：SPRT 不可用（資料生成分布每輪變）；group sequential 形式可做收益極小；Bayesian 最適配但小樣本下 posterior 由 prior 主導——**先累語料後校準，順序不可倒**。
- 裁定＝**borrow-design**：借 inspection 的事前決策思想 + cascade 架構 + cluster 化記帳，全部原生實作於 skill/loop status。

## 藥方（划算排序）

1. **R2/R3 嚴格 delta-scoped + 全局哨兵**（Codex「若只能改一件」）：物理上只餵「折入 diff + 被改 claim 的上下游合約 + 前輪爭議」，另留一席便宜模型全文掃防漏。一石三鳥：省 token/消措辭型重複發現/恢復輪間可比性。改 skill 派工規則。
2. **gate 改 risk-cluster 三態帳**：同根因碎片 findings 合併 cluster，狀態 resolved / accepted-minor / disputed-major。停止＝canary caught ∧ 無 disputed-major ∧ 高風險 claim ≥2 獨立 finder 覆蓋 ∧ 本輪無新 cluster。capture-recapture 降 advisory。**解 minor 永續供應**。動 `loop status --panel` gate 語意 + record 欄位。
3. **pre-flight cascade**：panel 前一道機械 checklist（未定義旗標/欄位/檔名、交叉引用、範圍自違、CLI touchpoint、測試策略對應）+ 小模型掃——清單型缺陷排乾，r1 從 v2 水準起跑，一輪收斂（K=1 本就允許）從理論變可能。
4. **辯方按共識路由 + 免辯方條件明文化**：機械證實（可執行證據+編排者自核）免辯方；席間一致+有獨立證據直折；只有低共識 ≥major 開庭。省每輪 opus pass。
5. **fold 迷你核對**：折完派便宜 agent 只看 delta 問「鏡像段跟了嗎/新舊句打架嗎/新詞有定義嗎」——殺 r3 型「補丁沒同步」findings。
6. **（後續,等語料）** 歷史 replay 校準 Bayesian expected-loss 門檻（golden 語料 10+ 份後）；severity 錨句進派工模板（major=照實作會做錯行為;文件精度/測試枚舉=minor 除非漏合約）。

## 里程碑

- **M1（skill 層,trivial 級可先行）**：①③④⑤ + severity 錨句——全是 SKILL.md/templates.md 文字改動,不動 code。
- **M2（動 gate code,必過 design-loop）**：② risk-cluster 帳——`canary record` 加 cluster 欄位、`loop status --panel` 改停止條件。**改守衛的守衛,高風險面,進實作前本計劃過 design-loop（舊 loop 審新 loop）**。
- 驗收信號：下一個真實 spec 過 loop 的輪數/wall-clock/token 對照本計劃前的基線（fromscratch-m1 ≈3 輪/~2h）。

## 天花板（誠實）

- delta-scoped 有漏看風險——全局哨兵是便宜緩解非保證；哨兵本身是弱檢查器。
- risk-cluster 的「同根因合併」是編排者判斷——cluster 切錯（兩個真問題併一個）會漏；GIGO 同 anchors。
- 這些提效都不改變誠實天花板：收斂仍只證「醒著的審計員沒再找到」，非「沒有更深的洞」。
- 提效後 minor 被 accepted 掉不再擋門——**accepted-minor 帳要留著可查**（不是消失,是記帳),否則變成合法掃地毯。
