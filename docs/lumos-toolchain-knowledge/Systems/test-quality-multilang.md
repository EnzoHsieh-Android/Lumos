---
type: system
status: doing
created: 2026-10-07
updated: 2026-10-07
responsibility: 選配本機 Semgrep 的來源自比辨識與失敗狀態；不執行來源、不保證完整測試框架或算法同源分析
self_audit: GPT-6-Codex-clean-agent/2026-10-08
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
  - "[[Verification/測試品質工具接線_Node與Laravel原生消費驗證]]"
  - "[[Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證]]"
  - "[[Verification/測試品質分支推送前修復驗證]]"
  - "[[Verification/測試品質分支第二輪修復驗證]]"
  - "[[Verification/測試品質第四輪修補驗證]]"
---
# test-quality-multilang

## 選配 backend 的決策

WHY: 本機固定規則掃暫存快照，而不沿用來源專案設定 [出處:2026-10-07 測試品質掃描試行] [因:要讓重跑範圍可確認且不受 ignore 或遠端規則變動影響]。核心與 Python 分析仍只依賴標準庫；選配工具由明確路徑指定、版本從結果留痕。

WHY: 未收到快照已掃描的證據就回報不完整 [出處:固定 backend 反例考卷] [因:零結果也可能是工具缺失、解析錯、逾時或整支檔被略過]。此層只驗來源自比候選，方法身份、算法同源與執行情境仍須其他證據。

PITFALL: 同一 Swift 規則混入 #expect 會令 XCTest 掃描也失敗 [出處:Semgrep CE 1.179.0 固定考卷實跑] [根因:該版本不能解析 #expect 的規則語法] [防回歸:test_swift_testing_macro_is_not_claimed_supported]。分開公布 XCTest 與 Swift Testing 的介面能力；後者接入時須新增原始樣本、解析失敗與抓錯案例，不能僅看 Swift 語言名稱就啟用。

## 本篇的檔案邊界

- `scripts/test_quality_semgrep.py` 的選配依賴、快照隔離與有限介面支援決策歸本篇，候選通用語義歸 [[Systems/test-quality-scan]]。
- `governance/eval/test_quality_corpus.py` 的獨立固定標註、未知／未分析結果與跨語言外推限制歸本篇，不把考卷符合率當真實專案品質。

WHY: PHP先沿成熟parser辨識明示斷言自比 [出處:[[Projects/測試品質工具接線_計劃]]] [因:PHPUnit與Pest介面可有限接入，不能從介面匹配推論Laravel框架情境或演算法同源]。原生PHPUnit與框架證據見[[Verification/測試品質工具接線_Node與Laravel原生消費驗證]]，Pest執行資格另驗。

## 推送前結果形狀修復

WHY: 結果映射抽成同責任函式以維持複雜度上限 [出處:code-test-quality-native-push/r1-fix.json] [因:沿固定 backend 結果合約拆分，沒有增加第二個 parser；配對控制與 [[Verification/測試品質分支推送前修復驗證]] 分開記錄來源掃描與原生執行資格]。

PITFALL: check_id 非字串會在 split 拋未收斂例外，失去結構化不完整報告 [出處:code-test-quality-native-push/r2-邊界-codex.md 與 r2-資安-codex.md] [防回歸:test_invalid_semgrep_rule_has_structured_shape_error]。反例走真 CLI 與無害假 backend，驗輸出不完整而非重抄結果映射算法。

PITFALL: Semgrep 每筆 finding 重複 decode/split 同一份來源，finding 增加時會把純呈現成本線性重做；第四輪改成每份來源只解碼一次，並在取 snippet 前驗行號界線 [出處:[[Verification/測試品質第四輪修補驗證]]] [防回歸:test_semgrep_backend]。這項修補只改固定 backend 的結果轉換，不擴張支援語法或品質裁決範圍。
