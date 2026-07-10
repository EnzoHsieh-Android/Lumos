---
type: project
status: done
created: 2026-07-10
updated: 2026-07-10
tags:
  - type/project
  - status/done
decisions:
  - content: 難度過濾用 haiku 弱模型探針(反向適配 FLAWS difficulty filter),上限重植 2 次
    context: FLAWS 原版丟棄『生成模型自己抓得到』的錯;lumos 情境生成者=編排者(知道答案不能自測),需外部探針
    why_chosen: 弱模型不腦補、它都抓到=真太明顯,同 [audit:] 用 sonnet 的哲學;haiku 成本可忽略;強模型當探針會把難度推到審計員也抓不到(canary 變不公平)
    decided: 2026-07-10
    valid: true
related:
  - "[[Projects/社群演算法補強_調研]]"
  - "[[Systems/canary-audit]]"
---
# canary生成硬化_計劃

## 目標

解 [[Projects/社群演算法補強_調研]] 缺口 a（canary 對技術密集 spec 審計員易漏）的生成側：現行 canary 由編排者憑手感植入，「認真審就抓得到、但不一眼看穿」的校準全靠自律，無機械信號。借兩條已驗證的生成硬化路線改 **lumos-design-loop / lumos-code-loop skill 的植入程序**（純程序變更，無 CLI 新面）。

PRIOR-ART: ① 最小解層級：改 skill 植入步驟即可，無需新 CLI/新機制（canary record/loop status 原語不動）。② 世界解過：FLAWS（arXiv 2511.21843——抽核心可證偽 claim → 生成使其失效的概念級錯 → **difficulty filter 丟棄生成模型自己就能偵測的**，存活率僅 7-39%）、IBIR（ACM TOSEM 2022——bug report 定位 + 修復 pattern 反轉植錯，偵測率能區分有效/無效 test suite，plain mutant 不能）——真搜真驗見調研節點 §2/§3。③ 裁定 = **borrow-design**：兩者都是「生成程序設計」借用，零依賴零新碼。

## 變更規格（skill 程序，三條）

1. **載重錨定（借 FLAWS 步驟①）**：植入位置從「隨機挑段」改為「先掃 spec 抽 3-5 條載重最高的可證偽 claim（演算法定義/門檻數字/整合接點），canary 植在其中一條的失效變體上」——canary 測的是「審計員有沒有讀懂核心」而非「有沒有掃過周邊」。
2. **難度過濾（借 FLAWS 步驟③，反向適配）**：植完 canary 後、派審計員前，先派一個 **haiku 探針**（弱模型、只給被植段落 ±20 行、prompt「這段有沒有內部不一致/未定義引用？」）：
   - haiku **一眼抓到** → canary 太明顯（訊號弱）→ 重植更藏的變體再探。
   - haiku **沒抓到** → 難度合格，進正常審計。
   - 上限 2 次重植（防無限調難）；探針結果記入該輪 canary note（`probe:pass|recraft×N`）。
   - 理由：FLAWS 實測「生成者自己抓得到的錯」存活率過濾掉 61-93%——不過濾，caught 就會灌水（mutation score 冗餘教訓同源）。**弱模型當探針而非強模型**：同 `[audit:]` 的哲學——弱模型不腦補，它都能抓到的就是真太明顯。
3. **事故反轉（借 IBIR，機會性）**：植入型別輪替前，先查事故語料（`lumos search --path Issues` + `pitfall_when` 命中 spec 主題域）：有匹配事故 → **把該事故的「修法」反轉成 canary**（如事故修了「hook 卸載殘留註冊」→ canary = spec 裡塞一段「卸載只刪 symlink 即可」的錯誤宣稱），取代該 slot 的通用型別；無匹配 → 照舊輪替 a/b/c/d。事故反轉的 canary 標 `type=incident-inv`。
   - 理由：IBIR 實證事故驅動的植錯比盲 mutation 寫實、有區分力；lumos 事故語料現成（Issues + pitfall_when）。

## 不做（v1）

- 不做自動生成 canary 的 CLI（生成仍是編排者+LLM 的手工藝，工具只記錄）；
- 不動 canary record/loop status 原語（探針結果進 --note 自由文字，不加 schema 欄位——等語料累積再議機械化）；
- code-loop 的 bug canary 同樣適用三條（載重錨定=植在 diff 主題的核心邏輯型別上、難度探針、事故反轉），寫進 code-loop skill 對應段。

## 驗收

- skill 文本更新後，下一個真實 design-loop（Task #3 收斂閘修正的 spec 審計）實際走新程序：haiku 探針至少跑一次、留 probe 註記於 canary note。
- 事故反轉路徑：語料目前僅 2 篇 pitfall_when Issue（hook卸載殘留註冊、init-force-slug），主題不匹配時走 fallback 輪替——驗收「無匹配 → 照舊」的路徑即可，匹配路徑等語料成長後自然觸發。

## 相關模組

- [[Projects/社群演算法補強_調研]]
- [[Systems/canary-audit]]
- [[Systems/design-loop]]
- [[Systems/pitfalls-code-loop]]
