severity: minor

審材核對：

- 正式 snapshot：`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-snapshot.patch`
- 程式材料：`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-code.patch`
- 圖譜／流程材料：`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-context.patch`
- 歷史帳本／卷證：`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-archive-arch.patch`

四份皆已核對；未讀其他 r3 席報告。`r3-archive-arch.patch` 與 `r3-code.patch` 分別是正式 snapshot 第 6067–7441、7442–8340 行的逐字連續切片；`r3-context.patch` 與正式 snapshot 對應檔案的 stable patch-id 同為 `6f23353013c2fabcffa99a96a29035104c237055`。目前真正程式為 HEAD `4a60b231`，程式差異與 `r3-code.patch` 一致。

finding A1：新結果解析器跨過既有 runner adapter 邊界，且已超過專案複雜度上限

severity: minor  
blocking: 否  
材料: `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-code.patch`  
引句:「只信成功工具的回傳；缺串流前提為 unknown，完整但沒讀到為 absent。」

`source_evidence` 重新解析 Claude、Codex 兩套原始 JSON；相同事件格式知識原本已分別由 `tool_calls_from_stream`、`tool_calls_from_codex_json` 持有。這不是因「同一函式裡有分支」就算第二套，而是同一份 runner 格式現在有兩條獨立解析路徑，日後事件格式更新可能只修到一般工具摘要、漏掉讀碼證據。該函式目前圈複雜度 34，也明確超過本專案上限 10。

外部佐證 file: `scripts/scenario_probe.py:27`  
外部佐證 file: `scripts/scenario_probe.py:55`  
外部佐證 file: `scripts/scenario_probe.py:92`  
外部佐證 file: `governance/review-reports/code-repair-pilot-01/r3-pitfalls.json:1`

具體輸入：解析 `r3-pitfalls.json`，篩選 `file == scripts/scenario_probe.py` 且 `line == 92`。  
執行路徑：pitfalls 的 Ruff claim → 目前 `source_evidence` → 對照既有兩個 runner adapter。  
可重現輸出：

```text
{'file': 'scripts/scenario_probe.py', 'line': 92, 'end_line': 92,
 'source': 'lint:ruff', 'rule': 'C901',
 'message': '`source_evidence` is too complex (34 > 10)'}
```

沒有重現錯誤判分，因此只列 minor、非 blocking。收斂方向是讓兩家事件解碼仍留在各自 adapter，將共同部分限縮為 `present/absent/unknown` 狀態歸納。

原問題驗收：

- R2C1 的 README 搜尋、`find` 列檔與 `cat README.md` 不再取得標記；R2C2 的直接 `cat`、先 `cd` 後 `cat`、`grep`、`sed` 保持通過。卷證為 `r3-paired-cases.json`；本席未冒稱重跑其暫存 Git fixture。
- 只有成功工具回傳含一次性標記才會得到 `present`；失敗工具即使含標記仍為 `absent`。
- 本席純記憶體重現結果：Claude/Codex 的成功命中均為 `present`，完整但未命中均為 `absent`，Claude 已發出支援工具卻缺結果為 `unknown`，完整零呼叫為 `absent`。
- v04 每次嘗試都由 `_run_source_attempt` 新建含標記且已提交的乾淨副本；用量重試會重新進入該函式，不沿用前一副本。清理失敗走專用 fatal、停止整批。
- `_git_env` 已延伸到兩個 runner 及共享副本的 Git 清理；來源 Git 目錄不在來源內仍於 `make_sandbox` 停手。真 repo 污染路徑未發現回歸。
- C2 非零退出排除與 C3 逐題有效分母仍保留在原 runner／摘要路徑，沒有另造計分流程。

圖譜與固定席影響：

- `Systems/codex-harness`、`Systems/測試假綠形態`：直接受影響；驗證範圍誠實標為 fixture／本機 shell、未跑真模型或部署。除 A1 外一致。
- `Systems/lumos-cli-lifecycle`、`Systems/bound-tests-gate`、`Systems/canary-audit`、`Systems/design-loop`、`Systems/guard-kill`：已核對，乾淨快照、錯誤分類與既有合約語意未被改壞。
- `Systems/lumos-cli-read`、`Systems/slim-get-一行安裝`、`Systems/slim-install-安裝器`、`Systems/slim-uninstall-一行卸載`、`Projects/規格落成可驗收條件_計劃`、`Systems/lumos-deinit`、`Projects/逃逸自動記_計劃`、`Systems/節點範圍與索引守衛`、`Systems/cochange-guard`、`Systems/check-r-guard`：沒有直接行為影響或新增衝突。
- `Issues/探針以工作樹為來源會改到本體`：既有正面 Git 目錄檢查保留，runner 繼承定位變數的缺口已補。
- `Issues/探針讀碼證據不足`：本次方案覆蓋其兩個反例及合法相對路徑，狀態仍維持 open、續辦 Verification 維持 pending，沒有在第三輪完成前冒稱結案。
- `r3-test-layers.txt` 為空，沒有 UI 或其他額外驗收層。
- `py-eventloop: na`：本程式是同步 CLI，沒有 async event loop；pitfalls 只因字面命中 `subprocess`／`json` 而觸發此題。

驗證限制：唯讀沙盒禁止建立 `/tmp` fixture，所以未重跑會寫暫存 repo 的 157／177 項測試，也未跑真模型探針或網路寫入；那些綠燈只作凍結卷證一致性核對。本席另完成純記憶體狀態重現、AST 解析及指定 production/context 差異的 whitespace 檢查，均通過。