---
type: system
status: doing
created: 2026-10-07
updated: 2026-10-07
responsibility: 重播固定歷史版本與弱強測試以驗考卷鑑別力；不執行模型輸出或推論規範效果
self_audit: GPT-6-Codex-clean-agent/2026-10-07
aliases: []
about_code:
  - governance/eval/historical_test_quality.py
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY:先重播歷史弱強測試確認考卷能分辨，再評估手冊效果 [出處:2026-10-07 使用者要求繼續實驗] [因:合成題兩臂滿分不足以顯示真實漏測]
related:
  - "[[Systems/test-quality-handbook]]"
verified_by:
  - "[[Verification/2026-10-07_歷史弱測試鎖回歸重播]]"
---
# historical-test-quality


## 證據與邊界

WHY:第一個案例選修復引入的退路鎖回歸 [出處:[[Projects/歷史弱測試手冊評估_計劃]]] [因:其弱測試與強測試都有真實歷史版本，直接回應當輪修復導致下一輪新問題]。不是另造業務函式；不把這類情境未成立概括成所有同義測試。

PITFALL:弱測試寫巢狀卻未進入巢狀，漏掉修復引入的自鎖 [出處:歷史代碼審 code-linter送檔進去 的 r2-修正差異-sonnet 報告] [根因:兩個 with 區塊不重疊] [repro:python3 governance/eval/historical_test_quality.py --out /tmp/lumos-historical-new-output]。先確認歷史錯版的強測試只有目標斷言紅、現場前置綠、修復版回綠，才納入模型評估。

本機歷史可信程式重播使用暫存家目錄；這不是任意模型輸出的沙盒。測試函式取原始歷史碼，只將強測試的8秒鬧鐘縮為2秒，正常路徑及被測實作不改。
REVISIT:2026-11-07 在加入生成測試執行前，凍結其允許操作與隔離方案；本機可信歷史碼執行器不直接當模型測試執行器。
