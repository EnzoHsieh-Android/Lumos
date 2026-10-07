---
type: system
status: doing
created: 2026-10-07
updated: 2026-10-07
responsibility: 跨語言測試品質檢測的邊界與決策；不替代業務判準或宣稱適配器已完成
self_audit: GPT-6-Codex-clean-agent/2026-10-07
aliases: []
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY: 共用規範與證據格式、檢測按語言接入 [出處:2026-10-07 使用者跨語言要求] [因:平台與斷言框架不同且未知結果不得視為乾淨]
related:
  - "[[Systems/test-profile-multiplatform]]"
  - "[[Systems/guard-kill]]"
  - "[[Systems/test-quality-multilang]]"
verified_by:
  - "[[Verification/2026-10-07_跨語言測試品質檢測規劃]]"
  - "[[Verification/2026-10-07_測試品質掃描固定考卷]]"
about_code:
  - scripts/test_quality_scan.py
  - scripts/test_test_quality_scan.py
  - governance/eval/test_quality_pilot.py
---
# test-quality-scan

## 判準與證據邊界

WHY: 候選與品質裁決分開 [出處:2026-10-07 固定考卷與 Lumos 現有測試試掃] [因:穩定性、兩份獨立資料的一致性與來源結構檢查可能各有正當目的]。靜態掃描回答「值得查哪裡」，故障驗證回答「能否抓到這一種退化」，兩者都不證明完整業務正確。

WHY: 故障試行只執行固定 repo 考卷 [出處:[[Projects/測試品質掃描試行_計劃]]] [因:暫存原始碼不會隔離外部資料庫或服務，不能把通用命令 runner 偷渡成安全驗證]。既有功能的故障能力沿 [[Systems/guard-kill]] 的隔離與證據流程，這個工具不自建通用變異 runner。

WHY: 先公布語法範圍再擴充規則 [出處:2026-10-07 跨語言要求] [因:有限局部代入不等於跨檔資料流，更不能把未分析當成沒有問題]。每個適配器用固定壞例與合理反例驗收，真實專案的支援另留驗證紀錄。

## 本篇的檔案邊界

- `scripts/test_quality_scan.py` 的候選／裁決分界與局部判準取捨歸本篇，跨語言 backend 的特殊限制歸 [[Systems/test-quality-multilang]]。
- `scripts/test_test_quality_scan.py` 的獨立 oracle 與合理反例選擇歸本篇，不將測試數量當品質標準。
- `governance/eval/test_quality_pilot.py` 的固定故障與安全執行範圍歸本篇，不能擴張為任意命令的通用變異 runner。
