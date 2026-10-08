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
  - scripts/lumos
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY: 接入來源掃描與明示執行收證，分開機械核對與業務判準 [出處:2026-10-08 使用者要求功能接線與建立測試專案] [因:單純文件與固定示範無法供消費專案直接使用，報告身份和快照須核對]
verified_by:
  - "[[Verification/測試品質工具接線_Node與Laravel原生消費驗證]]"
  - "[[Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證]]"
  - "[[Verification/測試品質分支推送前修復驗證]]"
  - "[[Verification/測試品質分支第二輪修復驗證]]"
  - "[[Verification/測試品質分支第三輪審查停點]]"
  - "[[Verification/測試品質第四輪修補驗證]]"
---
# test-quality-cli

## 判準與收證分工

WHY: 明示執行trusted命令與唯讀核對分開 [出處:[[Projects/測試品質工具接線_計劃]]] [因:暫存來源不隔離外部服務，收證只提供可重放內容，不能讓工具假裝評估業務答案或報告真實性]。呼叫者明示設定、runtime、lock等context；快照不自動證明完整依賴閉包。既有風險放行閘保持原流程。

PITFALL: Node原生無匹配測試仍可退出0，甚至把檔案包裝算作passed [出處:[[Verification/測試品質工具接線_Node與Laravel原生消費驗證]]] [根因:runner整體退出碼與實際named-case選取不是同一件事] [防回歸:test_wrapper_success_without_selected_target_invalid及原生zero-selected卷證]。用capture --target與check --target核對實際身份，不能只看測試數或退出0。

REVISIT:[when-file:scripts/test_quality.py][by:2026-11-08] 擴充reporter或框架前先驗其真實身份與assertion歸因，format支援不等同原生framework資格。

PITFALL: 原生reporter可能抹掉assertion例外型別，單看通用failure無法歸因 [出處:[[Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證]]] [根因:xUnit JUnit logger把型別写成failure，XCTest與AGP instrumentation reporter不填型別] [防回歸:test_xunit_generic_logger_assertion_is_attributed與test_xctest_native_assertion_message_is_attributed、test_android_native_assertion_without_type_is_attributed及原生卷證]。有限辨識必須沿實際訊息結構；一般執行例外只在訊息內提到斷言名稱不構成歸因，用反例守住。

`scripts/test_test_quality_cli.py` 的獨立控制覆蓋收證、原生錯誤歸因與無效結果；不把業務算式抄成預期答案。

## 推送前審查的故障控制

PITFALL: suite總數與逐案例狀態矛盾時曾把失敗基準當全綠 [出處:code-test-quality-native-push/r1-正確性-codex.md] [防回歸:test_suite_failure_summary_cannot_hide_green_case、test_root_failure_summary_cannot_hide_green_case；正常控制test_consistent_suite_summary_retains_green_capture]。解析資格只能授予列出的結果一致性，報告真實性仍由可信runner收證。

PITFALL: 逾時之外的中斷缺少finally清理，且事後才檢查輸出大小會先耗盡磁碟 [出處:code-test-quality-native-push/r1-資源-codex.md] [防回歸:test_cancelled_capture_stops_child、test_output_limit_stops_writer_before_completion]。selectors可能重試InterruptedError，故中斷以既有invalid例外處理通道結束；控制先驗子程序確實進入，再取消並確認停止。本次資格限POSIX本機可信命令，Windows留後續獨立實驗。

WHY: CLI與來源scanner共用參數定義與同一namespace [出處:code-test-quality-native-push/r1-架構-codex.md a3] [因:重建argv形成第二份契約，改旗標時易只接一邊] [防回歸:test_scan_entrypoints_share_options_and_results]。各責任函式分開解析、跨階段驗證與命令執行，避免修復與純重構混成不可比較的一步。


## 第二輪部署與解析邊界

PITFALL: 檔案都存在仍可能新舊混裝，同時間戳同大小的 bytecode 也曾讓新來源執行舊判讀 [出處:code-test-quality-native-push/r2-正確性-codex.md 與 r2-controls-red.txt] [防回歸:test_mixed_sidecars_refused_before_false_green、test_source_bytes_not_stale_bytecode_authorize_capture；正常 scan/capture/check/capabilities 與既有來源保持控制]。配套校驗的取捨見 [[Projects/測試品質部署配套校驗_計劃]]；只證本機配套一致，不證業務答案或報告真實性。

PITFALL: ASCII bytes 搜尋漏掉 UTF-16 的 DTD，suite 失敗標記不在 testcase 內亦曾被忽略 [出處:code-test-quality-native-push/r2-資安-codex.md 與 r2-邊界-codex.md] [防回歸:test_utf16_dtd_is_not_a_valid_receipt、test_plain_utf16_report_retains_valid_capture、test_orphan_failure_refused]。拒收依標準 XML parser 的宣告事件；正常 UTF-16 不跟著被擋。

PITFALL: 另看 argv 首項會漏掉合法 --vault 全域選項 [出處:code-test-quality-native-push/r2-架構-codex.md] [防回歸:test_global_vault_option_retains_structured_deployment_error、test_mixed_scanner_retains_legacy_help]。命令身份沿正式 argparse，不維護第二份命令解析。

PITFALL: 只在 launcher 本身仍存活時清理程序群，會漏掉「launcher rc1、worker 繼續跑」；worker 繼承 stdout/stderr 時還會讓已退出的 launcher 被誤判逾時。CLI capture 與 handbook model runner 都建立獨立 POSIX 程序群，必須採同一項返回前清理政策 [出處:code-test-quality-r4-repair/r1-architecture-report.md A1 與 r2-boundary-report.md B1] [防回歸:test_failed_capture_stops_stream_detached_worker、test_failed_capture_stops_worker_that_inherits_streams、test_cancelled_capture_stops_child]。可信測試 runner 正常使用 worker 仍屬本程序群責任；子程序主動 setsid 逃逸不在可攜式保證內。CLI capture、選配 Semgrep backend 與 handbook 模型命令三個入口共用本檔同一個 runner，不各自保留清理實作；繼承管線的控制要先證明 worker 確實寫進同一條管線，再斷言它已被清掉。

WHY: 共用 runner 用 CaptureTimeout 與 CaptureInterrupted 兩個 ValueError 子型別回報逾時與 SIGTERM 中斷，呼叫端按型別分類，中斷一律往上傳、不收成單一輸入的錯誤 [出處:code-test-quality-r4-repair/r3-邊界-sonnet.md BND-1、r3-架構對齊-sonnet.md ARC-2] [因:改用訊息字串比對時，Semgrep backend 把 SIGTERM 收成單檔 unavailable 後繼續掃下一檔，多拖一整段 backend 逾時；字串一改，逾時也會悄悄變成 unavailable] [不選:各呼叫端比對例外訊息字串] [代價:直接執行 scanner 收到 SIGTERM 時以 traceback 非零結束，經 lumos 入口才轉成結構化不完整結果] [test:t_test_quality_scan_cli]。控制方法為 test_sigterm_during_semgrep_stops_scan_and_backend；子型別保留原訊息，CLI capture 的 receipt reason 不變；逾時例外帶著已讀到的部分輸出，供 handbook 保存原始事件。

PITFALL: 逾時邊界上 launcher 剛退出時，macOS 對只剩殭屍 leader 的程序群 killpg 回 EPERM，權限錯誤從 finally 蓋掉原本的回傳或逾時 [出處:code-test-quality-r4-repair/r4-邊界資源-sonnet.md BND4-1] [根因:清理只容忍 ProcessLookupError] [防回歸:test_zombie_only_group_permission_error_is_not_fatal]。leader 被 reap 之前 PGID 不會被別人重用，所以 EPERM 一律視為已無可清；控制用注入的 EPERM 驗呼叫仍正常回傳，因為真實競態 300 次只出現十幾次、不能當穩定測試。

WHY: `scripts/lumos` 在此節點只負責測試品質子命令的部署完整性與註冊入口；CLI其他子命令仍各歸原家。來源：第二輪部署低風險計劃與混裝控制。
