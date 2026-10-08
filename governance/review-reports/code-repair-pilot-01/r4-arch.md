severity: minor

finding: R4-A1
severity: minor
blocking: false
引句:「+def source_evidence(lines, harness, token):」
file: `scripts/scenario_probe.py:92`
類型: 品質警告，沒有行為反例。
說明: 新增的 `source_evidence()` 同時承擔兩種事件格式、呼叫生命週期、成功狀態、內容正規化與完成判定，圈複雜度為 34，超過專案門檻 10。兩個 runner 又會重複拆行與解析同一份 JSON 串流：
- Codex：`tool_calls_from_codex_json()`、thread-id 迴圈、`source_evidence()` 三次走訪。
- Claude：`tool_calls_from_stream()`、result 迴圈、`source_evidence()` 三次走訪。
重現:
`ruff check --no-cache --select C901 --output-format concise scripts/scenario_probe.py`
輸出:
`scripts/scenario_probe.py:92:5: C901 source_evidence is too complex (34 > 10)`
靜態路徑:
- Codex：`scripts/scenario_probe.py:667`、`:669`、`:677`
- Claude：`scripts/scenario_probe.py:744`、`:747`、`:761`
判準: 這是同一 CLI／runner 層內的重複事件解析，沒有引入第二種互斥的業務機制，也沒有跨層直呼，因此不升 major。未重現錯誤判分、安全隔離失效或其他行為反例。合理修法是一次解碼事件，再由既有 harness adapter 產出統一結果，供 calls、final、thread/result 與 source evidence 共用。
歸因:
- 舊漏報: false；archive 已記錄相同 C901／雙份事件格式知識告警。
- 本輪回歸: false；r4 delta 沒有新增或加劇這個結構。
- 未判定: false；複雜度與重複走訪可由現況程式及靜態檢查直接確認。

固定席合約逐條:
- `Systems/codex-harness`: 分層一致；sandbox、runner、判分與測試仍在原有 harness 邊界內。除 R4-A1 外無架構分叉。
- `Systems/測試假綠形態`: patch 有前置條件、正反例與故障形狀測試；本席未在唯讀環境重跑，故不把 frozen 綠燈當成獨立驗證。
- `Systems/lumos-cli-read`: 沒有修改 search／superseded／stale 路徑。
- `Systems/lumos-cli-lifecycle`: 沒有修改 re-inject 或 sentinel 外內容。
- `Systems/bound-tests-gate`: 沒有修改合約測試執行或 rc 判定。
- `Systems/canary-audit`: 沒有修改落盤 readback 或 second telemetry。
- `Systems/design-loop`: 沒有修改處置閘或計劃材料判定。
- `Systems/guard-kill`: 沒有修改 rc 優先序或 JSON stdout 純度。
- `Systems/slim-get-一行安裝`: 無跨層呼叫或行為改動。
- `Systems/slim-install-安裝器`: 無跨層呼叫或行為改動。
- `Systems/slim-uninstall-一行卸載`: 無跨層呼叫或行為改動。
- `Projects/規格落成可驗收條件_計劃`: 無新增互斥驗收機制。
- `Systems/lumos-deinit`: 無跨層呼叫或行為改動。
- `Projects/逃逸自動記_計劃`: 無行為改動。
- `Systems/節點範圍與索引守衛`: 無行為改動。
- `Systems/cochange-guard`: 無行為改動。
- `Systems/check-r-guard`: 無行為改動。
- `py-eventloop`: na；程式是同步 CLI，沒有 async／await 或事件迴圈，串行執行仍保留逐場隔離與重試語意。
- 第二種互斥做法: 未發現。
- 跨層直呼: 未發現。
- 錯誤語意: `present`／`absent`／`unknown`、儀器例外與致命清理失敗仍沿用既有語彙。
- `r4-test-layers.txt`: 0 bytes，沒有額外 UI／device 測試層要求。

讀過材料:
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`
- `CLAUDE.md`
- `docs/lumos-toolchain-knowledge/MOC/index.md`
- `governance/review-reports/code-repair-pilot-01/r4-code.patch` 全文
- `governance/review-reports/code-repair-pilot-01/r4-context.patch` 全文
- `governance/review-reports/code-repair-pilot-01/r4-delta.patch` 全文
- `governance/review-reports/code-repair-pilot-01/r4-archive-arch.patch` 全文；只作歷史證據
- `governance/review-reports/code-repair-pilot-01/r4-snapshot.patch` 完整檔案雜湊；SHA256 為 `2e8dae39bcabc1d4793e43e096995d79e84bbcf4edb9c83dea009bdfeb0c2734`
- `/tmp/r4-lens.txt` 全 50 行
- `/tmp/r4-test-layers.txt`，空檔
- HEAD `8922c3c9c11e4234554d94695c31c93973679a99` 的 `scripts/scenario_probe.py` 與相關測試區段

限制:
- 沒有讀其他 r4 席報告。
- 沒有改檔、push、network 或根 repo Git 狀態操作。
- 未執行會建立暫存檔的測試；沒有需要交父代理做 filesystem 重現的行為 finding。
- `lumos impact --diff 2db51cc4..HEAD` 連續 60 秒沒有輸出後中止；視為環境／工具限制，不列產品 bug。
- 完成唯讀 AST／靜態路徑檢查及 C901 重現；archive 的舊綠燈未當作現況權威。