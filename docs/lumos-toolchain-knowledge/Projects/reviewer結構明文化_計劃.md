---
type: project
status: done
created: 2026-07-10
updated: 2026-07-10
tags:
  - type/project
  - status/done
related:
  - "[[Projects/社群演算法補強_調研]]"
  - "[[Systems/cross-family-audit]]"
---
# reviewer結構明文化_計劃

## 目標

把 [[Projects/社群演算法補強_調研]] §4/§5 的 LLM-judge 可靠度實證寫進 lumos-design-loop / lumos-code-loop skill 的 reviewer 結構規範——現行 panel 已「平行多樣 + 跨家族否決 + 編排者判讀」，但三條紀律只是隱含實踐、未明文，漂移無守衛。

PRIOR-ART: ① 最小解層級：skill 文本明文化即可，panel 機制/原語不動。② 世界解過：Judging with Many Minds（EMNLP 2025 Findings——multi-agent debate 第一輪即劇烈放大 position/verbosity/CoT/bandwagon 偏誤且後續不自癒；meta-judge 聚合對偏誤更抗、pool 越大越好）、PoLL（Cohere 2024——異家族 panel intra-model bias 更低）、Rating Roulette（EMNLP 2025——同 judge 同輸入跨 run α 最好僅 0.563 <0.8；多 run 多數決改善、但只壓 stochastic 變異不壓 correlated 盲點）——真搜真驗見調研節點。③ 裁定 = **borrow-design**（紀律明文化，零碼）。

## 變更規格（skill 文本，三條明文紀律）

1. **禁互辯（新增硬規則）**：reviewer 互不通訊、不得看彼此輸出迭代辯論；發現分歧交 meta-judge（編排者）裁，不回饋給 reviewer 重辯。依據：debate 第一輪即放大偏誤且不自癒。範圍限定誠實寫明：實證測的是「偏誤軸」，另有研究稱 debate 提升「準確率軸」——lumos 選抗偏誤（審計場景假陽/假陰成本不對稱）。
2. **編排者=meta-judge 角色明文化**：判讀段（canary 判定/去重/severity 取 max/辯方裁決聚合）明文標為 meta-judge 聚合——不重審內容、只聚合一級判決；judgment pool 越大越好（W 寬 panel 的理據）。
3. **關鍵單點判決 ≥3 run 多數決**：適用「單一判決要當終局」的窄集合——cap 攤牌前的最後裁定、blocker 級 finding 的辯方裁決有爭議時。≥3 獨立 run（乾淨脈絡）取多數決；並明文「多數決只壓 stochastic 變異、不壓 correlated 系統性盲點——後者靠異家族 panel，兩者不互替」。跨家族 slot 維持現行（qwen 可用時用；不可用時異模型為次佳並註記）。

## 不做（v1）

- 不做 conformal 區間（調研 §5 的 split conformal 需累積校準集——golden 語料 10+ 份後再議，記入 canary-audit 節點未來方向）。
- 不改 loop status 原語/schema。

## 驗收

- 兩份 skill 文本含三條紀律 + 出處；與既有段落（panel 模式、cross-family、判讀規則）無矛盾（合併 panel 審計輪把關）。

## 相關模組

- [[Projects/社群演算法補強_調研]]
- [[Systems/heterogeneous-finder-ensemble]]
- [[Systems/cross-family-audit]]
- [[Systems/design-loop]]
