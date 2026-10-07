---
type: system
status: doing
created: 2026-10-07
updated: 2026-10-07
responsibility: 選配本機 Semgrep 的來源自比辨識與失敗狀態；不執行來源、不保證完整測試框架或算法同源分析
self_audit: GPT-6-Codex-clean-agent/2026-10-07
aliases: []
about_code:
  - scripts/test_quality_semgrep.py
  - governance/eval/test_quality_corpus.py
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY: 選配固定版本的本機語法工具，避免自建多語言 parser [出處:2026-10-07 跨語言測試品質計劃] [因:保持核心零依賴，缺工具或未掃快照時明確回報不完整]
related:
  - "[[Systems/test-quality-scan]]"
verified_by:
  - "[[Verification/2026-10-07_測試品質掃描固定考卷]]"
---
# test-quality-multilang

## 選配 backend 的決策

WHY: 本機固定規則掃暫存快照，而不沿用來源專案設定 [出處:2026-10-07 測試品質掃描試行] [因:要讓重跑範圍可確認且不受 ignore 或遠端規則變動影響]。核心與 Python 分析仍只依賴標準庫；選配工具由明確路徑指定、版本從結果留痕。

WHY: 未收到快照已掃描的證據就回報不完整 [出處:固定 backend 反例考卷] [因:零結果也可能是工具缺失、解析錯、逾時或整支檔被略過]。此層只驗來源自比候選，方法身份、算法同源與執行情境仍須其他證據。

PITFALL: 同一 Swift 規則混入 #expect 會令 XCTest 掃描也失敗 [出處:Semgrep CE 1.179.0 固定考卷實跑] [根因:該版本不能解析 #expect 的規則語法] [防回歸:test_swift_testing_macro_is_not_claimed_supported]。分開公布 XCTest 與 Swift Testing 的介面能力；後者接入時須新增原始樣本、解析失敗與抓錯案例，不能僅看 Swift 語言名稱就啟用。

## 本篇的檔案邊界

- `scripts/test_quality_semgrep.py` 的選配依賴、快照隔離與有限介面支援決策歸本篇，候選通用語義歸 [[Systems/test-quality-scan]]。
- `governance/eval/test_quality_corpus.py` 的獨立固定標註、未知／未分析結果與跨語言外推限制歸本篇，不把考卷符合率當真實專案品質。
