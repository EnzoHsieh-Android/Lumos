severity: major

審查材料：

- formal snapshot：`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-snapshot.patch`
- code：`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-code.patch`
- context：`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-context.patch`
- archive-boundary：`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-archive-boundary.patch`

四份材料已逐 hunk 讀完；formal snapshot SHA-256 為 `582475fb21b83d3cc1672257ead7d5b77905691f4e7b118b32c79ecb558c5f9a`，與 dispatch 相符。未讀其他 r3 席報告。

### Finding R3-B1：Git command-scope config 可繞過副本隔離

severity: major  
blocking: 是  
引句:「當呼叫端環境含Git定位變數時，兩runner與所有副本Git操作應使用既有_git_env清洗，外部暫存repo的設定與檔案應不變。」  
材料: `governance/review-reports/code-repair-pilot-01/r3-context.patch:202`  
file: `scripts/scenario_probe.py:385`  
file: `scripts/scenario_probe.py:617`  
file: `scripts/test_lumos.py:36978`

`_git_env()` 只清除 `GIT_DIR`、`GIT_WORK_TREE` 等六個路徑變數，仍完整保留 Git 的 command-scope config 注入入口，例如：

```text
GIT_CONFIG_COUNT
GIT_CONFIG_KEY_0
GIT_CONFIG_VALUE_0
GIT_CONFIG_PARAMETERS
GIT_CONFIG_GLOBAL
```

具體輸入：

```sh
GIT_CONFIG_COUNT=2
GIT_CONFIG_KEY_0=remote.r3escape.url
GIT_CONFIG_VALUE_0=https://example.invalid/r.git
GIT_CONFIG_KEY_1=core.hooksPath
GIT_CONFIG_VALUE_1=/tmp/r3-no-hooks
```

執行路徑：

```text
父程序環境
→ _git_env() 未移除上述欄位
→ run_one_codex/run_one 把環境交給模型
→ 副本內 git remote、commit、push 解析被注入的 remote/hooksPath
```

唯讀解析輸出：

```text
r3escape https://example.invalid/r.git (fetch)
r3escape https://example.invalid/r.git (push)

/tmp/r3-no-hooks
```

這會重新生出已被副本初始化流程移除的 remote，並覆蓋副本內的硬擋 pre-push hook。現有 `t_probe_source_probe_git_env` 只測 `GIT_DIR` 與 `GIT_WORK_TREE`，因此會假綠。

依禁令未實際執行 push、外部 hook 或真模型；目前環境也禁止建立 `/tmp` fixture。因此將原本可能造成外部寫入的 blocker 下調一級為 major。修復需隔離 Git config 注入面，並以臨時 repo 驗證注入 remote 與 `core.hooksPath` 均無法進入兩個 runner。

### 原問題驗收

- 成功工具內容才證明讀到目標片段：通過。
- Codex/Claude 的 pending、失敗、非零退出不能算取得證據：通過。
- 缺串流前提為 `unknown`、完整串流確定沒讀到為 `absent`：通過。
- v04 每次 attempt 建立獨立副本並在 `finally` 清理：通過。
- 清理失敗轉 fatal、停止批次並回傳 3：通過。
- symlink、hardlink、路徑逸出及注入後語法一致性：通過。
- C2 非零退出排除與 C3 分母／全排除 inconclusive：保留。
- 不污染真 repo／不能向外推送：未通過，受 R3-B1 阻擋。
- `r3-archive-boundary.patch` 與 r2 已處置事項一致，未重開舊 finding。

### 圖譜與測試層影響

- `Systems/codex-harness`：直接受 R3-B1 影響，副本的 remote／hook 隔離仍可被環境 config 繞過。
- `Systems/測試假綠形態`：直接受影響；現有測試只覆蓋兩個 Git 路徑變數。
- `Issues/探針以工作樹為來源會改到本體`：工作樹來源拒絕仍正確；本 finding 是另一條環境注入路徑。
- `Issues/探針讀碼證據不足`：成功結果證據、`unknown`／`absent` 分流已符合修復目標。
- `Systems/lumos-cli-read`、`Systems/lumos-cli-lifecycle`、`Systems/bound-tests-gate`、`Systems/canary-audit`、`Systems/design-loop`、`Systems/guard-kill`：本批改動未改變其行為或既有 invariant。
- `py-eventloop`：`na`。本程式是同步 CLI，沒有 `async def` 或事件迴圈；命中來自同步 `subprocess.run`／JSON 處理。
- `r3-test-layers.txt` 為空。`r3-paired-cases.json` 的 4 個 valid green→green、3 個 broken red→green 已核對邏輯，但受唯讀環境限制未獨立重跑會寫入 `/tmp` 的測試。