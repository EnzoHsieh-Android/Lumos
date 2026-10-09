severity: clean

ID: C1 — AST grammar、fixture 隔離與歷史 controls  
severity: clean  
blocking: 否  
引句:「def validate_node_access(node):」  
file: `governance/eval/historical_handbook_trial.py:49`  
已讀,無 finding。舊、新版對照 15 組 import/call/name/attribute/標準 footer 案例，接受結果完全相同；historical controls 通過，weak/survived、strong/detected、錯誤 baseline 與不支援語法仍判 invalid。

ID: C2 — handbook grammar、scenario budget 與行為計分  
severity: clean  
blocking: 否  
引句:「def validate_node_access(node, scopes):」  
file: `governance/eval/test_quality_handbook.py:91`  
已讀,無 finding。18 組舊、新 grammar 差分無差異；15 個 grader controls 全綠。holdout 的 shipping、calendar 各三個固定 fault 均 detected，baseline 各跑 3 tests 且通過；lane 數量維持 all=10、behavior=4、trigger=6、native-trigger=6。

ID: C3 — model_command timeout cleanup  
severity: clean  
blocking: 否  
引句:「def model_command(cmd, directory, timeout):」  
file: `governance/eval/test_quality_handbook.py:226`  
已讀,無 finding。假 Claude 確認 worker 實際啟動後，逾時會終止整個 POSIX process group；正常完成、Popen 失敗及逾時三條路徑都恢復原 SIGTERM handler。未呼叫真 Claude。Windows 行為未驗，與圖譜明示的 POSIX 範圍一致。

ID: C4 — scanner bindings、模型範圍與雙入口  
severity: clean  
blocking: 否  
引句:「def comparison_rule(expr, models, aliases):」  
file: `scripts/test_quality_scan.py:138`  
已讀,無 finding。7 組舊、新 scanner 輸出完全相同；21 個 scanner controls 與 CLI 整合控制全綠。模型仍只收頂層、同步、無 decorator/default、單一 return 且算式節點的函式；async、巢狀、多敘述與有 default 的函式仍列為 unmodeled。

ID: C5 — Semgrep 結果映射重構  
severity: clean  
blocking: 否  
引句:「def backend_findings(result, source, path, raw):」  
file: `scripts/test_quality_semgrep.py:23`  
已讀,無 finding。抽函式保留 rule、snapshot、line shape 驗證及 candidate 欄位；假 backend 的 error、漏掃 snapshot、缺 executable 控制均維持 incomplete。未跑真 Semgrep。

因果核對：`r1-intake.md` 的 r2 對應到 model worker 逾時殘留，現有假程序控制可翻紅且修後通過；a3 對應 scanner/CLI 共用參數與 namespace，雙入口結果一致。其餘 helper 抽取屬複雜度拆分，差分檢查未見放寬、收窄或 bindings 漂移。`r2-repair-binding.json` 的 base/head 對上 `5d8f0ec7…`／`598e41b2…`，其 `r2-repair.patch` SHA-256 `0dcdc6f2…f988f3a` 相符。

手動圖譜鏡頭前 8 篇逐條：

1. `Issues/vendored測試套件在消費端假紅.md`：本席兩份 patch 未碰 vendor/deployment 程式，無新增牽連。
2. `Systems/lumos-cli-lifecycle.md`：未碰 re-inject 或 CLAUDE sentinel，合約不受影響。
3. `Systems/lumos-deinit.md`：未碰 deinit，風險面不受影響。
4. `Systems/lumos-cli-read.md`：未碰 search/superseded/stale 篩選，合約不受影響。
5. `Systems/bound-tests-gate.md`：未碰 code-loop check 或 bound-tests 判定，合約不受影響。
6. `Systems/guard-kill.md`：未碰 rc 優先序或 JSON purity，兩條合約均不受影響。
7. `Systems/授權與歸屬.md`：未改 `_VENDORED_TOOLKIT`、LICENSE 清理或 SPDX 內容，兩條合約均不受影響。
8. `Systems/測試假綠形態.md`：timeout 控制先確認 worker PID 已產生，再驗證 worker 消失；historical controls 也分 baseline/fault，未見「現場未成立」假綠。file: `scripts/test_test_quality_cli.py:477`

已讀：`r2-history.patch`、`r2-scanner.patch` 共 949 行、`r2-repair-binding.json`、`r1-fix.json`、`r1-intake.md`、`r1-history.patch`、`/tmp/lumos-r2-manual-lens.txt`、`Systems/test-quality-handbook.md`、`Systems/historical-test-quality.md`、`Systems/test-quality-scan.md`。AGENTS.md 指定的「代碼審修復穩定性試行」與「2026-10-04_代碼審改道生效驗證」在凍結副本中以三組同義詞查找仍不存在，因此該兩篇狀態未知；不影響上述程式與指定合約核對。

驗證：handbook 15/15、scanner 21/21、CLI focused 1/1、historical controls 通過；四支 Python 檔可編譯，相關 diff 無 whitespace error。未跑全套 3700+ 測試、真 Claude、真 Semgrep或 Windows。

總結: 最嚴重 severity clean；blocking 0 條。
