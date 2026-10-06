severity: minor
findings: 1

ID: ARCH-1  
severity: minor  
blocking: 否  
引句:「WHY:[2026-10-06 附件種子獨立驗收]既有版曾把已追蹤的凍結 patch、派工文字與 replay 當 code 片段」  
file: `docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md:92`  
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-06_附件種子修復獨立驗收.md:29`  
判定：兩條新增 `WHY:` 都缺少必填的 `[出處:]`、`[因:]` 結構鍵；第一條雖以散文寫「出處」，仍不是既有機械格式。這不是語氣偏好，而是圖譜分類形狀不一致，會觸發 lint／提交提醒。規則見 `CLAUDE.md:39`、`CLAUDE.md:43`。不影響 Python 行為，因此不阻擋。

架構三問：

1. 分層與依賴方向：對齊。`cmd_impact_diff` 繼續透過既有 `_impact_diff_seed_ok` 過濾，角色清單也沿用同一入口；簿記來源仍只有 `_BOOKKEEPING_FILES/_BOOKKEEPING_DIRS`。  
   file: `scripts/lumos:24366`  
   file: `scripts/lumos:24586`  
   file: `scripts/lumos:24605`  
   file: `scripts/lumos:41012`  
   file: `scripts/lumos:41114`

2. 命名、錯誤／回傳／日誌：程式部分對齊。新增判斷維持純布林回傳，沒有增加例外映射、日誌或 CLI 結果判讀。

3. 第二種做法：沒有。未新增目錄表、正則、依賴或跨層直呼。

反例實測：

- `governance/review-reports/case/formal_tool.py` 即使是合法 Python 副檔名，也回傳 `False`。
- 依既有定義，整個 `_BOOKKEEPING_DIRS` 都是卷證／簿記而非正式程式，因此目前不算合約回歸；計劃的 `RETIRE-IF` 已明定若未來開始存正式程式，必須撤換目錄排除。
- `.patch`、`.txt`、`.diff` 位於指定卷證目錄時均被排除。
- `governance/review-reports-other/worker.py` 與 `src/deleted.py` 均保留為 `True`。
- 新測試另確認真程式、刪檔、實際事故、附件追蹤都保留。  
  file: `scripts/test_lumos.py:23037`

資料狀態五問：

- 新舊互讀：沒有新增持久格式；舊版會誤納附件，新版排除，卷證本身仍由 Git 保存。
- 半完成輸入：只判 Git 路徑；附件寫一半仍整體排除。Git diff 失敗的既有 rc2 路徑未改。
- 衍生資料：impact 結果與角色清單都是可重算衍生資料；未新增快取格式或第二真相來源。
- 時間：沒有時間戳、時區、TTL 或排序時間語意變更。
- 不可逆：沒有刪除、搬移或取消追蹤附件；回退只需撤回分類判斷。

固定席逐條：

- `pitfalls-code-loop`：未改 pitfalls 分級或掃描來源定義。
- `lumos-cli-lifecycle`：re-inject sentinel 合約不受影響。
- `lumos-cli-read`：search 的 stale／superseded 語意不受影響。
- `bound-tests-gate`：只縮正 impact 輸入；固定席測試的執行、結果判讀與阻擋規則未改。
- `guard-kill`：rc 優先序與 JSON 純度均未觸及。
- `授權與歸屬`：未碰 vendoring、授權檔或 deinit。
- `測試假綠形態`：新增測試真跑 CLI，先斷言 rc0，再以混合控制證明真程式路徑仍成立；既有版卷證顯示 6 過 4 敗，具翻紅殺傷力。
- `design-loop`：未改設計審材、處置閘或 loop 判定。

其餘列名：`loop-convergence-recording`、`lumos-deinit`、`check-t-sentinel`、`reversibility-governance-ledger`、`check-r-guard`、`cochange-guard`、`doctor-irreversible-hint`、`節點範圍與索引守衛`、`lumos-refcheck`、`slim-uninstall-一行卸載`、`canary-audit`、`slim-get-一行安裝`、`slim-install-安裝器`、`雙向門放行_計劃`、`規格落成可驗收條件_計劃`、`逃逸自動記_計劃`、`judge-severity-gate`、`core-invariant-baseline`。

實際讀取：`CLAUDE.md`、三份適用技能、templates §3／§7.6、`r1-source.patch` 全103行、`r1-graph.patch` 全162行、materials 與指定執行卷證、相關常數／呼叫端／新增測試。`r1-snapshot.patch` 只核對463行清單與 SHA-256，未讀正文；未讀其他席報告。

驗證邊界：卷證的紅6過4敗、綠35過0敗、角色59過0敗及 source SHA 均互相吻合。現場重跑因唯讀環境沒有可寫暫存目錄，在測試啟動前失敗，不算測試紅；未跑全套、完整 impact/lens、CI、Windows 或記憶體 profiling。未修改 repo、未保存新卷證。