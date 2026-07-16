---
type: system
status: done
created: 2026-07-16
updated: 2026-07-16
self_audit: sonnet/2026-07-16
tags:
  - type/system
  - status/done
  - prior-art
related:
  - "[[Systems/canary-audit]]"
  - "[[Systems/verification-rot-eval]]"
summary: |-
  FLAG:ORIGIN
  KEY:PRIOR-ART 對照——langchain-ai/openwiki(2026-06 建、11.6k★、MIT、TS):「CLI 掃 repo→LLM 生成 openwiki/ markdown wiki→CI 排程重生開 PR」的 code 衍生 wiki 原型。同樣往 repo 根 CLAUDE.md/AGENTS.md 塞受管區塊叫 agent「先讀 wiki」——與 lumos 使命重疊、但底層賭注相反
  KEY:定位——openwiki 站在 lumos「圖譜先行後 grep code 驗證」的『grep code 那半(導覽/orientation 層)』,正是 lumos 家規故意不入圖的 code 結構層;兩者是垂直疊(導覽層 vs 合約層)非並排競品
  KEY:相反賭注——openwiki=code 是真相、wiki 是可丟棄投影、重生保鮮;lumos=圖譜是真相(為什麼/邊界/★合約/驗證過沒,code 讀不出)、人手寫+機械閘守。openwiki 結構上裝不下「這條改=breaking」「這條驗證過沒」——頁面隨時被 LLM 重寫,無「不可漂移真相」概念
  KEY:★核心論點★正確性問題——「code 生成的 wiki 憑什麼正確?」openwiki 不保證正確、只保證『新鮮(recent projection)』。它把 lumos 的『staleness 漂移』換成『每輪 synthesis 合成誤差』:另一種失效模式、非消滅。OpenSpec 生成一次都偏,openwiki 連續生成、每輪僅靠 grounding-prompt 當唯一護欄、無 per-cycle oracle
  KEY:實證(2026-07-16 讀 repo)——openwiki 正確性機制全在 prompt 層 grounding 紀律(prompt.ts:「Do not invent…Ground every important claim in source」)=maker 側自律指令、非 checker;test/ 26 檔全是自家單元測試(oauth/env/checkpoint…),0 檔驗 wiki 輸出對 ground truth;無輸出 eval harness。= maker-only、no-checker 的純 maker-bias 案例
  KEY:接 lumos 已錄知識——『驗證層天花板=oracle 品質』(見 [[Systems/canary-audit]] 誠實天花板 + memory pbt-oracle-reliability):openwiki 對生成 wiki 零 oracle,同一 LLM 讀 code 又寫 doc、無獨立查核。這正是 lumos INVARIANT→[test:]→[audit:]→canary 那條 oracle 疊存在的理由
  KEY:為何反證 lumos 核心賭注成立——openwiki 每條優勢(零紀律/全覆蓋/零摩擦/免疫 drift/分發生態)都來自「文件=可丟投影」,代價=裝不下 code 裡沒有的那層;lumos 存在的理由(合約/驗證/drift-proof 真相)恰是 openwiki 結構上放棄的。可疊用:openwiki 跑導覽層、lumos 守合約層
  KEY:openwiki 真優勢(誠實記,非恭維 lumos)——①零維護零紀律(CI 重生,繞掉 lumos 頭號脆弱點『人懶得寫回』)②冷啟動全 repo 覆蓋(lumos 只長在動過處)③開發內圈零摩擦 ④by-construction 免疫 drift(lumos 一大堆 stale/revalidate 機械就為打這場戰)⑤分發:npm/11k★/三家 CI 範本/多 provider/通吃各家 agent
  DEP:[[Systems/canary-audit]]｜[[Systems/verification-rot-eval]]
  DECISION:留痕反例世界解——日後有人問「有自動生 wiki 就夠,幹嘛手寫圖譜?」直接指此節點:答案=openwiki 那套無法承載 code 讀不出的合約/驗證/不可漂移真相,且其新鮮≠正確(無 oracle)
---
# 外部對照-code衍生wiki

> **這是什麼**：一筆 **PRIOR-ART 留痕**（非 lumos 子系統）。記錄 [langchain-ai/openwiki](https://github.com/langchain-ai/openwiki) 這個「code 衍生 wiki」世界解，以及它為什麼**反證了 lumos「圖譜即真相、非 code 衍生」核心賭注的必要性**。CLAUDE.md〈PRIOR-ART 三問〉的世界對照留痕。

## openwiki 是什麼（2026-07-16 讀 repo）

LangChain 官方出的 CLI，2026-06-22 建、11.6k★、MIT、TypeScript、爆紅新專案。`npm i -g openwiki`：
- **code mode**：掃 repo → LLM 合成 `openwiki/` 一疊 markdown（架構/工作流/領域/測試/source map）；往 repo 根 `CLAUDE.md`+`AGENTS.md` 塞 `<!-- OPENWIKI:START -->` 受管區塊，叫 coding agent「先讀 wiki 再找 context」。
- **personal mode**：接 Gmail/Notion/X/Web Search/HN/git-repo connector → 本機個人大腦 wiki。
- **靠 CI 保鮮**：附 GitHub Actions/GitLab/Bitbucket 範本，排程重跑、自動開 PR 更新文件。「別手改生成頁，改 code 讓它重生。」

## 它站在 lumos 的什麼位置

lumos 進場紀律＝「先 `lumos` 讀圖譜（為什麼/邊界/合約）→ **再 grep code 驗證細節**」，且家規**故意不把 code 結構入圖**。**openwiki 做的正是那第二步（grep code 那半＝導覽層）**。所以兩者**垂直疊**、非並排競品：

| | openwiki | lumos |
|---|---|---|
| 層 | 導覽 orientation | 合約 contract/rationale/verification |
| 真相源 | code 是真相，wiki 是投影 | 圖譜是真相，code 讀不出 |
| 保鮮 | LLM 重生 | 人手寫 + 機械閘擋漂移 |
| 裝什麼 | code 摘得出的 | code 摘不出的（★合約/驗證過沒/為什麼） |
| 保證 | recency（新鮮） | correctness（[test:]/[audit:]/canary） |

## ★核心論點：code 生成的 wiki 憑什麼正確？

**它不保證正確——只保證新鮮。** 這是這筆留痕的技術重點：

- **重生 = recency，不等於 correctness**。openwiki 把 lumos 的「staleness 漂移」（doc 落後 code）換成「每輪 **synthesis 合成誤差**」（doc 是新鮮但可能誤讀 code 的 LLM 詮釋）。是**換一種失效模式、不是消滅它**。
- **OpenSpec 生成一次都偏**（使用者洞見）；openwiki **連續**生成，每輪唯一護欄是 **grounding-prompt**（maker 側自律），**無 per-cycle oracle、無人逐輪查**——因為它的賣點正是「沒人手維護」。
- **實證**（讀 repo）：正確性機制全在 prompt 層——`src/agent/prompt.ts` 明寫「Do not invent files/APIs/business rules… Ground every important claim in source files/git evidence」。這是 **maker 指令、不是 checker**。`test/` 26 個檔全是自家單元測試（oauth/env/checkpoint/redaction…），**0 個驗「生成 wiki 對不對」**。無輸出 eval harness。
- 結論：openwiki 是 **maker-only、no-checker** 的純 maker-bias 案例——同一個 LLM 讀 code 又寫 doc，沒有獨立 oracle 查核輸出。

**接 lumos 已錄知識**：「驗證層天花板 = oracle 品質」（見 [[Systems/canary-audit]] 誠實天花板、memory `pbt-oracle-reliability`）。openwiki 對生成 wiki **零 oracle**——這正是 lumos `★INVARIANT★→[test:]→[audit:]→[kill:]` 那條 oracle 疊、和 canary loop（test-the-tester）存在的理由。openwiki 沒有這一層，所以它的內容**只能是 advisory/可丟棄**：一頁錯了下輪重生、且沒有任何合約依賴它為真、讀的 agent 反正也會去讀真 code——它靠「低風險」而非「已驗證」活著。

## openwiki 真正的優勢（誠實記，非恭維 lumos）

1. **零紀律零維護**（最深一條）：lumos 全部價值押在人的紀律（退場必寫/圖譜先行/實時更新）+ 機械閘逼；頭號失效＝人懶得寫回。openwiki **結構上把人移出維護迴圈**，CI 重生天生不爛。
2. **冷啟動全覆蓋**：第一天攤平整個 repo；lumos 只長在動過的地方（真圖稀疏）。上手陌生 repo 完勝。
3. **開發內圈零摩擦**：lumos 每次改 code 加稅過閘；openwiki 對寫 code 當下零摩擦。
4. **by-construction 免疫 drift**：lumos 一大堆機械（`stale`/`revalidate_when`/`valid_under`/doctor 同步檢查）存在的**唯一目的就是打漂移**；openwiki 重生天生免疫。lumos 花大力工程對抗的，它天生沒有——**但這是 lumos 內容不可重生所付的內生代價**（決策理由/驗證結果無法從 code 重生）。
5. **分發生態**：npm/11k★/三家 CI 範本/多 provider（OpenAI/Anthropic/Gemini/Bedrock…）/同時寫 CLAUDE.md+AGENTS.md 通吃各家。lumos 是零依賴單作者手工精品。

## 為何這反證 lumos 核心賭注成立

openwiki 每條優勢都來自同一個賭注：「文件應是 code 的衍生投影、可丟可重生」。**代價是它裝不下任何 code 裡沒有的東西**——沒有「這條是合約、改＝breaking」、沒有「這條驗證過沒」、沒有「當初為什麼這樣選」。lumos 押相反的賭：**真正值錢的知識恰恰是推導不出來的那半**，所以必須手寫 + 機械閘保護。使用者付的維護稅，是這個更難問題的**內生**成本。

**可疊用**：openwiki 跑導覽層、lumos 守合約層，連注入 CLAUDE.md 的手法都一樣。真正威脅不是功能，是它會讓人問「有自動生 wiki 就夠了吧？」——而此節點就是那問題的存檔答案：**新鮮 ≠ 正確；無 oracle 的衍生 wiki 承載不了合約/驗證/不可漂移的真相。**

## 誠實邊界
- 未親跑 openwiki 生成一份 wiki 實測其誤差率（結論建立在讀 prompt.ts + test/ 結構 + README 機制）；「無輸出 oracle」是**機制推斷**，非跑出來的量測。日後若要硬化此對照，可跑一次 openwiki 對已知 repo、人工抽查生成頁對 code 的偏差當語料。
- openwiki 仍在高速迭代（今日還在更新），未來版本可能加輸出校驗——此節點記的是 2026-07-16 當下狀態。
