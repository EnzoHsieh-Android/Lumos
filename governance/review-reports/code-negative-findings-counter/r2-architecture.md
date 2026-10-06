severity: clean

零 finding。

### 架構三問

1. 分層依賴方向：符合。argparse 將 `--findings` 轉為整數（`scripts/lumos:46330`），dispatch 傳入既有 `cmd_canary`（`scripts/lumos:47421`），命令邊界先驗證（`scripts/lumos:9201`），最後才呼叫既有追加 helper（`scripts/lumos:9679`）；沒有跨層直呼。

2. 命名與錯誤返回：符合。`--findings` 的負值診斷指出欄位與原值並回 rc2（`scripts/lumos:9202`），與 `tokens`、`wallclock_min`、`scope_lines` 的既有守衛形狀一致（`scripts/lumos:9245`）。檢查早於 report IO（`scripts/lumos:9526`）及成功訊息（`scripts/lumos:9682`）。

3. 是否第二套做法：否。只在既有 `findings is not None` 分支加入三行守衛，沒有新 parser、helper、資料模型或讀側規則。測試經完整 CLI subprocess 進入同一入口（`scripts/test_lumos.py:278`）。

### 固定圖譜鏡頭逐條對照

- `Systems/design-loop`：未改處置閘第五步或設計／代碼迴圈分類。
- `Systems/lumos-cli-read`：未改 search 三路濾網。
- `Systems/bound-tests-gate`：未改固定席測試執行或 rc 規則。
- `Systems/guard-kill`：未改 kill rc 優先序或 JSON stdout。
- `Systems/授權與歸屬`：未改 vendored 集合、授權標頭或 deinit。
- `Systems/測試假綠形態`：新測試具現場前提與反向控制，包括未有帳不建檔、已有帳逐位元不變、雙非法輸入先診斷負數，以及合法省略／0／正數控制（`scripts/test_lumos.py:294`、`:300`、`:305`、`:326`、`:335`）。
- `Systems/lumos-cli-lifecycle`：未改 re-inject 或 sentinel 外內容。
- 新 PITFALL 有出處及重現測試（`docs/lumos-toolchain-knowledge/Systems/design-loop.md:223`）；新 WHY 有出處（同檔 `:226`），符合本次 AGENTS v1.0。

### 驗證邊界

- AST 解析及 `git diff --check` 通過。
- 本席嘗試只跑 `t_canary_negative_findings_rejected`，但唯讀沙盒沒有可用暫存目錄，測試在收集前退出；不冒稱本席實跑 38 條全綠。
- 未跑全套或正在執行的 16 分片；材料所載 472/0/0 未被本席改寫成完整測試全綠。
- 已完整讀 `r2-source.patch` 132 行、`r2-graph.patch` 300 行；完整 snapshot 僅核對 SHA-256 `a2d36d520b5316c3602acf355420a9b0139284860b63d969843ee1968901f2f0`。
- 最高級：clean；blocking 數：0。