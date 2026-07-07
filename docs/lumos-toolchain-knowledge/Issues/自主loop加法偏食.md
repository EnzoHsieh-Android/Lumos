---
type: issue
status: open
created: 2026-07-07
updated: 2026-07-07
related:
  - "[[autonomous-iteration-loop]]"
tags:
  - type/issue
  - status/open
summary: |-
  FLAG:DECISION
  KEY:結構性偏誤——自主 loop 的任務是「從 gap 產 spec」,所以它永遠提「加一個機制」,從不提「這題該在別層用更便宜的既有手段解」或「該刪什麼」。治理面只有生長壓力、沒有修剪壓力 → overcheck 的來源
  KEY:實證=exec-anchor-gate(2026-07-07):$30/6輪/5組件的 G3 執行錨設計,動機 gap(測試紅了溜進 main)為真,但成比例解法=pre-push 補跑測試一段(事件點閘,~32s);6 輪對抗審計把設計磨到自洽,無一環節問「這題該不該用這個解」——審計員審的是 spec 內部品質,不審解法層級選擇
  KEY:對照組=人的修剪動作(2026-07-06 撤 Stop nag ADR)——loop 自己永遠不會做這種事
  DECISION:[2026-07-07] exec-anchor-gate gap 標 covered(covered.jsonl,防 requeue 再燒);撿走 spec 真值錢的兩樣:runner -k 0案例假綠洞修 + pre-push 測試閘(皆已落地);G3 本體不做(使用者裁定 overcheck)
  KEY:守衛模型原則(使用者提出):守衛該長在「事件源」上——每種漂移向量在發生那刻被對應的閘接住;對已有事件閘的東西做收斂期輪詢=overcheck。唯一合法的重驗=無事件可掛的向量(世界變了 code 沒變 → 人)
  KEY:改進方向(未實作):gap 選題評估加一問「這 gap 有沒有更便宜的既有層解法?」;或 orchestrator prompt 給 brainstorm 階段加「先評估最小解在哪一層」步驟
---
# 自主 loop 加法偏食(結構性偏誤)

## 現象
自主迭代 loop 的產出永遠是「新增一個機制」——它的任務定義(gap → spec → design-loop)天生不會產出「這題該用既有層的便宜解」或「該刪掉什麼」。**治理面只有生長壓力,沒有修剪壓力**,日積月累 = overcheck。

## 實證:exec-anchor-gate(2026-07-07)
- 動機 gap 為真:repo 無 CI、pre-push 不跑測試 → 紅測試 48 小時內兩度溜進 main。
- loop 的解:G3 執行錨(config schema + 機械選集鏈 + injection 白名單 + 進程組 timeout + skipped 語意),$30、6 輪、今日射程 1 個測試。
- 成比例的解:pre-push 補跑全量測試(~32s,一段 shell)——**事件點閘**。
- 6 輪對抗審計(canary/judge/辯方全 opus)把 spec 磨到內部自洽,**沒有任何環節質疑解法的層級選擇**——審計器只審「這份設計好不好」,不審「該不該是這個設計」。

## 對照組
人的修剪動作:2026-07-06 撤除 Stop nag(ADR 在 [[code-loop必用守衛_計劃]])——「太擾民,pre-push 單點就夠」。loop 永遠不會自發做這種減法。

## 處置(2026-07-07,使用者裁定)
1. exec-anchor-gate gap → `governance/covered.jsonl`(永不再選,防 requeue 再燒 $30)。
2. 撿走 spec 的兩樣真價值(已落地):runner `-k` 選中 0 案例假綠洞(rc 0→1)、pre-push 源 repo 測試閘。
3. G3 本體不做。

## 待議(open 的原因)
gap 選題/brainstorm 階段加「最小解在哪一層」評估——讓 loop 至少會說「這 gap 的成比例解是 X,不需要新機制」。實作前先觀察:這類「解法層級錯配」再發生幾次、什麼形態,再決定機械化的形式。
