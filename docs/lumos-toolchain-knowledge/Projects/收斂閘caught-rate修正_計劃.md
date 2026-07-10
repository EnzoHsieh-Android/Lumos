---
type: project
status: done
created: 2026-07-10
updated: 2026-07-10
tags:
  - type/project
  - status/done
---
# 收斂閘caught-rate修正_計劃

## 目標

把 [[Projects/社群演算法補強_調研]] §1 的 mutation score 文獻教訓（3-0 高信度）落進收斂閘：caught-rate 只有近滿分才有強訊號、冗餘 canary 灌水指標、missed 類別必須分帳追蹤。

PRIOR-ART: ① 最小解層級：panel gate 一行條件強化 + gov 彙整段，無新機制。② 世界解過：Papadakis et al. survey（Advances in Computers 2019——very high mutation score levels 才有顯著效益、中段分數相關弱；冗餘識別不可判定、灌水指標）、Just et al. FSE 2014——真搜真驗見調研節點 §1。③ 裁定 = **borrow-design**。

## 變更規格

1. **near-perfect 輪有效（gate 代碼）**：`_loop_status_panel` 的輪有效從「caught ≥2」強化為「caught ≥2 **且該輪 0 missed**」（近滿分＝全 caught；5 人 panel 2/4 caught 的中段分數不再算有效輪）。訊息同步改。風險：更多輪無效 → 更快到 cap 攤牌——這是特性不是缺陷（弱訊號輪本就不該背書收斂）。
2. **missed 分帳（gov 彙整）**：`lumos gov` 的 canary 段加分帳：per-auditor 與 per-loop 的 caught/missed 計數 + missed-rate；note 含 `type=X` 者 best-effort 抽 type 分佈。missed-rate 從異常事件升為一級可觀測指標。
3. **冗餘 canary 紀律（skill 文本一行）**：panel 多樣化三軸加「同輪 W 個 canary 不得同型同段——殺 A 必殺 B 的重複難度 canary 不算獨立注意力票」（冗餘識別不可判定 → 靠紀律不靠機械）。

## 不做（v1）

- 不做 canary 難度自動分層（FLAWS 生成者難度校準 claim 查證被否決 1-2；等 golden replay 語料）。
- 不動 legacy（非 panel）K-streak 判準——序列模式向後相容。

## 驗收

- 測試：panel 輪含 1 missed（即使 caught ≥2）→ gate FAIL 輪無效；全 caught → 其餘條件不變。gov 輸出含分帳段。
- 審計：本計劃三項變更以實現 diff 為對象跑 panel 一輪（與 canary生成硬化/reviewer結構明文化 的 skill diff 合審——同批文本、單輪覆蓋；偏離「先審 spec 再實作」以「審真落地物」代之，理由：變更皆小而機械、審 diff 嚴於審散文）。

## 相關模組

- [[Projects/社群演算法補強_調研]]
- [[Systems/convergence-evidence-gate]]
- [[Systems/loop-convergence-recording]]
