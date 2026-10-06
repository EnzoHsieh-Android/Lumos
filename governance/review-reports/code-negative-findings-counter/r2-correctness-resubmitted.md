severity: minor

## F1 — 圖譜仍記著舊版紅燈數字

severity: minor  
blocking: 否  
引句:「重現入口 `t_canary_negative_findings_rejected` 在未修入口時14通過/20失敗」  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:223`

輸入：以目前 38 條測試對未修入口重放。  
錯誤：逐項推演結果是 16 pass／22 fail，不是 14／20；同一 delta 的驗證紀錄 file: `docs/lumos-toolchain-knowledge/Verification/2026-10-06_負數發現計數拒收驗證.md:20`與計劃末段 file: `docs/lumos-toolchain-knowledge/Projects/負數發現計數在追加前拒收_計劃.md:65`也都記成 16／22。系統筆記會讓後續重放者誤判收據不一致。

證據：目前測試每種模式有 19 個檢查，normal／`-O` 合計 38；依舊碼分支靜態推演為每種 8 pass／11 fail。本席因唯讀環境沒有可寫暫存目錄，未實際重跑 baseline harness，以上明確屬靜態推論。

### 手工角色卡（standard 通才）

- 核心與邊界：負數守衛位於 report/spec I/O 與 canary append 之前；沒有集合數量等式或 `none` 特判。
- normal／`-O`：不落檔探針均回 rc2，只在 stderr 指出 `--findings` 與 `-1`，stdout 空白；被設成必爆的 I/O／append 都未觸發。
- 合法控制：假 append 擷取到省略／0／2 分別為無鍵／`0`／`2`，兩種模式皆 rc0。
- 相容性：讀側、歷史負數帳、UTF-8／引句／驗後換檔防線未改；沒有新依賴、parser 或 helper。
- 資料狀態：新舊互讀不變；拒收在追加前，不新增半寫；衍生統計不再收到新負數；時間判定未改；既有不可逆帳不遷移或刪除。
- 完整測試：未宣稱全綠；完整 harness 因唯讀 temp 限制未啟動。

### 固定圖譜鏡頭逐項

- `Systems/design-loop`：處置閘第五步未改；新增 PITFALL 有 F1 數字錯誤。
- `Systems/lumos-cli-read`：search／stale／superseded 路徑未改。
- `Systems/bound-tests-gate`：固定席測試執行與 blocked 判定未改。
- `Systems/guard-kill`：rc 優先序及 JSON stdout 合約未改。
- `Systems/授權與歸屬`：vendored、deinit、SPDX 未改。
- `Systems/測試假綠形態`：測試有合法種子前置、bytes 不變與首筆不建帳控制。
- `Systems/loop-convergence-recording`：只收緊非法寫入，讀側收斂算法未改。
- `Systems/lumos-cli-lifecycle`：reinject／sentinel 未改。

已完整讀：`r2-source.patch` 132/132 行、`r2-graph.patch` 300/300 行；七個相關節點 lint 均為 0 問題。snapshot 僅取指紋：`a2d36d520b5316c3602acf355420a9b0139284860b63d969843ee1968901f2f0`。來源／測試 SHA-256 仍為 `52c9c4d7…`／`cc6d8390…`。

最高嚴重度：minor；blocking：0。