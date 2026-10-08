severity: major

## Finding F1 — 缺少事件 ID 被誤判成確定未讀

severity: major  
blocking: 是

引句:「+                if isinstance(ident, str):
+                    pending.add(ident)
+                continue」

file: scripts/scenario_probe.py:115  
file: docs/lumos-toolchain-knowledge/Projects/探針讀碼結果證據_計劃.md:33  
file: scripts/test_lumos.py:36885

Codex 的 `item.started`／`item.updated` 若是 `command_execution`、但缺少字串 ID，程式會直接 `continue`，沒有把格式標成 `unknown`。

具體輸入：

```json
{"type":"item.started","item":{"type":"command_execution","command":"cat scripts/lumos"}}
{"type":"turn.completed"}
```

執行路徑：

```text
run_one_codex → source_evidence → grade → summarize_results
```

唯讀 in-process 重現輸出：

```text
source_evidence: absent
grade: [False, "未取得目標程式片段", True]
summary: passed=0, scored=1, inconclusive=False, failed=["v04-where-used"]
```

控制組中，加入 ID 但不給完成結果會正確回傳 `unknown`；成功完成且輸出含標記則回傳 `present`。

這直接違反 S3「已發出支援呼叫卻缺結果、格式無法識別應記儀器例外、不進有效分母」。目前會把不完整或版本不相容的串流算成模型確定未讀，製造假紅。建議缺少合法 ID 時設 `unknown = True`，並為 `item.started`、`item.updated` 各補一個缺 ID 的回歸案例。

## 其餘重點驗收

- 成功工具內容才建立正證據：保留；未發現命令文字、答案或失敗結果可形成 `present`。
- v04 每次嘗試／重試使用獨立副本：保留；`_run_source_attempt` 每次建立新標記及新沙盒，`finally` 清理。
- 不污染真 repo：副本內注入、Git 定位環境清洗及來源 Git 目錄檢查均保留；本席未跑真模型。
- C2/C3：非零退出／截斷仍優先成為儀器例外，有效分母排除規則仍保留。
- 歷史卷證：所列歷史報告檔 SHA 與實檔相符；沒有重開前兩輪已處置的舊發現。
- `py-eventloop`: na。本程式是同步 CLI，沒有 async event loop；pitfalls 僅因 `subprocess`／JSON 字樣命中，不構成事件迴圈問題。
- `r3-test-layers.txt` 為空，沒有額外測試層指示。

固定席影響：

- 直接受 F1 影響：`Systems/codex-harness`、`Systems/測試假綠形態`、`Issues/探針讀碼證據不足`。
- 真 repo 隔離未見退步：`Issues/探針以工作樹為來源會改到本體`。
- 未見語意影響：`Systems/lumos-cli-read`、`Systems/lumos-cli-lifecycle`、`Systems/bound-tests-gate`、`Systems/canary-audit`、`Systems/design-loop`、`Systems/guard-kill`。
- 超額鏡頭未見直接影響：`Systems/slim-get-一行安裝`、`Systems/slim-install-安裝器`、`Systems/slim-uninstall-一行卸載`、`Projects/規格落成可驗收條件_計劃`、`Systems/lumos-deinit`、`Projects/逃逸自動記_計劃`、`Systems/節點範圍與索引守衛`、`Systems/cochange-guard`、`Systems/check-r-guard`。

## Seat-check 材料

正式完整 snapshot：

`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-snapshot.patch`  
8435 行，SHA-256 `582475fb21b83d3cc1672257ead7d5b77905691f4e7b118b32c79ecb558c5f9a`

逐 hunk 讀完的三份分工材料：

- `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-code.patch`  
  899 行，SHA-256 `0c699d826e64f1ded04e8413fa462222a402240aeccc304748afee9b1bf7fdb9`
- `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-context.patch`  
  661 行，SHA-256 `9eafa8047a774e70f047aa064bfdd287b5060d353a675d424caf707db492cdb2`
- `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-archive-correctness.patch`  
  1375 行，SHA-256 `4ce26456b4c1cb43986b1ebdafaa84624ba5ce6cf9cd42ddf4c9aa37f96af878`

未讀其他 R3 席報告，未修改 repo 或圖譜。正式測試子集因唯讀環境無法建立任何臨時目錄而未啟動；上述 major 由不落盤的實際函式重現支持，沒有依賴封存測試結果冒充當前驗證。