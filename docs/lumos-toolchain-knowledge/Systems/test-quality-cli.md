---
type: system
status: doing
created: 2026-10-08
updated: 2026-10-08
responsibility: 測試品質CLI的明示本機命令收證與JUnit一致性核對；不裁決業務答案或驗證報告真實性
self_audit: GPT-6-Codex-clean-agent/2026-10-08
aliases: []
about_code:
  - scripts/test_quality.py
  - scripts/test_test_quality_cli.py
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY: 接入來源掃描與明示執行收證，分開機械核對與業務判準 [出處:2026-10-08 使用者要求功能接線與建立測試專案] [因:單純文件與固定示範無法供消費專案直接使用，報告身份和快照須核對]
verified_by:
  - "[[Verification/測試品質工具接線_Node與Laravel原生消費驗證]]"
  - "[[Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證]]"
---
# test-quality-cli

## 判準與收證分工

WHY: 明示執行trusted命令與唯讀核對分開 [出處:[[Projects/測試品質工具接線_計劃]]] [因:暫存來源不隔離外部服務，收證只提供可重放內容，不能讓工具假裝評估業務答案或報告真實性]。呼叫者明示設定、runtime、lock等context；快照不自動證明完整依賴閉包。既有風險放行閘保持原流程。

PITFALL: Node原生無匹配測試仍可退出0，甚至把檔案包裝算作passed [出處:[[Verification/測試品質工具接線_Node與Laravel原生消費驗證]]] [根因:runner整體退出碼與實際named-case選取不是同一件事] [防回歸:test_wrapper_success_without_selected_target_invalid及原生zero-selected卷證]。用capture --target與check --target核對實際身份，不能只看測試數或退出0。

REVISIT:[when-file:scripts/test_quality.py][by:2026-11-08] 擴充reporter或框架前先驗其真實身份與assertion歸因，format支援不等同原生framework資格。

PITFALL: 原生reporter可能抹掉assertion例外型別，單看通用failure無法歸因 [出處:[[Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證]]] [根因:xUnit JUnit logger把型別写成failure，XCTest與AGP instrumentation reporter不填型別] [防回歸:test_xunit_generic_logger_assertion_is_attributed與test_xctest_native_assertion_message_is_attributed、test_android_native_assertion_without_type_is_attributed及原生卷證]。有限辨識必須沿實際訊息結構；一般執行例外只在訊息內提到斷言名稱不構成歸因，用反例守住。

`scripts/test_test_quality_cli.py` 的獨立控制覆蓋收證、原生錯誤歸因與無效結果；不把業務算式抄成預期答案。
