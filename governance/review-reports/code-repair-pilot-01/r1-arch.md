severity: minor
審材: `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r1-snapshot.patch`

A1
severity: minor
blocking: 否
引句:「+def _load_probe_module(tag):」
file: `scripts/test_lumos.py:36601`
新 helper 與緊鄰的既有 inline `SourceFileLoader` 流程並存，形成載入 `scenario_probe.py` 的第二種做法；舊測試仍在 `scripts/test_lumos.py:36590` 自行組 spec，新測試則走 helper。最小修法是讓舊測試也呼叫 `_load_probe_module("sp_mt")`。

三問：

1. 分層依賴：對齊。兩個 runner 共用純判分層 `grade()`，各自只處理平台事件與儀器狀態，批次摘要另由 `summarize_results()` 接手。file: `scripts/scenario_probe.py:92`
2. 命名與錯誤處理：對齊。`instrument_fail`、`truncated`、`limit_hit`、`inconclusive` 分別表示執行失敗、截斷、額度限制與批次不可下結論；CLI 仍由 `main()` 回傳狀態碼、入口統一 `sys.exit(main())`，與同層掃描器一致。file: `scripts/scenario_probe.py:446`
3. 是否引入第二種重複做法：不對齊。測試模組載入同時保留 inline 與 `_load_probe_module()` 兩條路。file: `scripts/test_lumos.py:36590`

圖譜固定席：

- `Systems/codex-harness`：對齊；Claude/Codex runner 共用判分，平台差異留在各自 adapter。file: `scripts/scenario_probe.py:468`
- `Projects/探針判準對齊程式碼為主_計劃`：S1–S5 均落在共同判分、截斷標記、摘要／歷史與題庫資料，未跨層。file: `scripts/scenario_probe.py:548`
- `Systems/測試假綠形態`：對齊；截斷測試先證明同一事件正常結束時會判過。file: `scripts/test_lumos.py:36654`
- `Systems/bound-tests-gate`：已讀，改動未碰其執行與阻擋合約。
- `Systems/canary-audit`：已讀，改動未碰 record/readback 或 second telemetry 合約。
- `Systems/design-loop`：已讀，本次為 `code-` 迴圈，未改處置閘。
- `Systems/guard-kill`：已讀，未改 rc 優先序或 JSON 輸出。
- `Systems/lumos-cli-lifecycle`：已讀，未改 re-inject。
- `Systems/slim-get-一行安裝`：已讀，未改 PowerShell 檔。
- `Systems/slim-install-安裝器`：已讀，無 finding。
- `Systems/slim-uninstall-一行卸載`：已讀，無 finding。
- `Systems/lumos-cli-read`：已讀，無 finding。
- `Projects/規格落成可驗收條件_計劃`：已讀，無 finding。
- `Projects/逃逸自動記_計劃`：已讀，無 finding。
- `Systems/lumos-deinit`：已讀，無 finding。
- `Systems/check-r-guard`：已讀，無 finding。
- `Systems/節點範圍與索引守衛`：已讀，無 finding。
- `Systems/cochange-guard`：已讀，無 finding。

最嚴重 severity: minor；blocking: 0
