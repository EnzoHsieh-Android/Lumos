---
type: system
status: doing
created: 2026-10-07
updated: 2026-10-07
responsibility: 跨語言測試品質檢測的邊界與決策；不替代業務判準或宣稱適配器已完成
self_audit: GPT-6-Codex-clean-agent/2026-10-08
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
  - "[[Verification/測試品質工具接線_Node與Laravel原生消費驗證]]"
  - "[[Verification/測試品質分支推送前修復驗證]]"
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

WHY: 掃描入口隨consumer更新部署但語義不升級 [出處:[[Projects/測試品質工具接線_計劃]]] [因:方便日後實作時直接掃，不把安裝可用等同業務品質通過]。PHP有限介面自比歸[[Systems/test-quality-multilang]]；可信本機命令收證歸[[Systems/test-quality-cli]]，固定試行不變成通用mutation engine。

WHY: 來源與安裝入口共用掃描參數，選配適配器延後載入 [出處:code-test-quality-native-push/r1-邊界-codex.md b1與r1-架構-codex.md a1/a3] [因:遞移缺檔不應使既有CLI的help失效，測試品質命令則須明確回不完整及更新指引]。保留控制见 [[Systems/test-quality-cli]]；局部bindings、算式模型、檔案解析各有獨立責任，有限語法掃描不裁決獨立業務答案。

WHY: scanner 只在帶 `--semgrep` 時才載入 Semgrep adapter，純 Python 掃描不需要共用程序 runner [出處:code-test-quality-r4-repair/r3-架構對齊-sonnet.md ARC-3] [因:adapter 改用 [[Systems/test-quality-cli]] 的共用 runner 後，模組頂層匯入會讓只掃 Python 的 scanner 也必須帶著 runner 檔，形成 core 到 scan 到 adapter 再回 core 的依賴圈] [不選:另抽一個共用底層模組，會在 bundle 裡多一種模組角色] [test:t_test_quality_scan_cli]。控制方法為 test_python_scan_does_not_need_semgrep_runner_bundle；帶 `--semgrep` 時仍要整組 bundle 與指紋一致。
