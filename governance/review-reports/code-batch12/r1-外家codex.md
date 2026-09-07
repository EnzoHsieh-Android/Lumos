severity: major

1. [major] blocking:是 — 合法 JSON、但不是 object 的帳列會讓整支指令崩潰，違反「壞行跳過」承諾。兩個讀取迴圈只捕捉 `json.loads` 的 `ValueError`，接著立即呼叫 `d.get(...)`；例如帳內一行 `[]`、`null`、`42` 都會拋 `AttributeError`。新增測試只寫入語法不合法的 `{壞掉的行`，沒有覆蓋這類既有已知 JSONL 失效形態。引句:「治理帳 → {loop_id: 最後一次關門事件的 ts}。壞行跳過」 governance/review-reports/code-batch12/r1-snapshot.patch:45；同型審查帳路徑在 governance/review-reports/code-batch12/r1-snapshot.patch:86，測試缺口在 governance/review-reports/code-batch12/r1-snapshot.patch:325。

2. [major] blocking:是 — `--exclude ""` 會匹配所有 loop，並把「全部被排除」誤報成「帳裡從來沒有迴圈」。`startswith("")` 對每個字串都成立；人讀模式接著走 `if not rows`，而且在印出排除數之前提前返回。JSON 模式也不回傳 `n_excluded`，所以呼叫端無法分辨空帳與全部遭排除。這不是正則或跳脫問題，而是空前綴未拒絕。引句:「審查帳裡還沒有任何迴圈。開第一輪:」 governance/review-reports/code-batch12/r1-snapshot.patch:147；根因在 governance/review-reports/code-batch12/r1-snapshot.patch:133。現有測試只驗非空 `auto-`，見 governance/review-reports/code-batch12/r1-snapshot.patch:303。

3. [major] blocking:是 — 關門種類仍是無漂移守衛的人工 allowlist，與註解宣稱「不新增任何要人維護的狀態」相反。治理帳實際枚舉得到 design/code loop 共六種：`converged` 103、`cap-reached` 3、`rewrite` 3、`replay-refreeze` 4、`passed` 121、`skipped` 27；程式只列五種，測試又只真正驗 `converged`、`passed` 兩種，其他三個入選值即使拼錯或刪除也仍會綠。未找到 schema、共享 enum、未知 kind 告警或「所有寫入端 kind 必分類」測試，因此未來新增真正的關門種類會靜默漏列。引句:「那是既有的、寫入當下就落的、可重算的東西,不新增任何要人維護的狀態。」 governance/review-reports/code-batch12/r1-snapshot.patch:11；集合與測試分別在 governance/review-reports/code-batch12/r1-snapshot.patch:13、240。

   `design-loop/replay-refreeze` 本身不算關門：寫入點是在已有 golden 被再次凍結後才記帳，是已結案材料的基準更新，不是收斂或人裁結案。現帳四筆都伴隨真正關門事件，所以今天不造成誤報。全帳沒有第七種 design/code gate；`settle`、`disposal`、panel/light/legacy 成功都統一寫成 `design-loop/converged`。

4. [minor] blocking:否 — 混合格式的 `rounds` 會只數帶 `round` 的相異值，完全忽略所有 round-less 記錄。例如 `r1` 兩筆加上一筆舊格式，顯示仍是 1 輪；如果所有記錄都無 round 才改數筆數。這和 `loop status` 對混合格式 rc2 的策略不一致，會把帳形狀不可信的 loop 顯示成精確輪數。引句:「有 round 欄就數相異值,全沒有就退回數筆數」 governance/review-reports/code-batch12/r1-snapshot.patch:101；輸出採該數字的位置在 governance/review-reports/code-batch12/r1-snapshot.patch:125。它不影響 open/closed 判定，故列 minor，但應至少顯示未知或警告混用。

5. [minor] blocking:否 — 錯誤與降級訊息沒有全面符合三段式。`--now` 壞值只說發生什麼，沒有說為何在意，也沒有獨立一行給可執行修正指令；壞帳提醒同樣只說可能少列，沒提供定位或檢查命令。成功清單尾端的 `loop next` 則有做到指令獨立一行。引句:「擋下:--now 要給 YYYY-MM-DD 這種格式的日期,你給的是」 governance/review-reports/code-batch12/r1-snapshot.patch:111；壞帳訊息在 governance/review-reports/code-batch12/r1-snapshot.patch:141。

補充核驗：

- 效能：直接對現有 26,465 行治理帳呼叫 `_loop_close_stamps` 20 次，median 53.47 ms、p95 55.70 ms、max 55.98 ms；完整 `cmd_loop_list --json` 10 次 median 64.59 ms、max 66.74 ms。以互動式唯讀命令而言可接受，目前不值得為效能加索引或快取。
- 時區修正的翻紅釘有效：測例刻意構造 `10:00+08:00` 與稍後的 `03:00Z`；退回原本字串比較會把已關門判成開著。
- `--now` 的翻紅釘也有效：移除 `ValueError` 攔截後，`上禮拜` 會吐 traceback，無法同時滿足 rc2 與無 traceback 兩條斷言。不過 Python `date.fromisoformat` 還接受 `20260907` 等基本 ISO 形式，實作比錯誤訊息所稱的嚴格 `YYYY-MM-DD` 更寬；沒有看到會造成日期判定錯誤，因此未另列 finding。
- 18 條斷言中，最明顯「宣稱大於實際驗證」的是：五種關門訊號只驗兩種，以及「壞行」只驗 JSON 語法錯誤、沒驗合法非 object。`--all`、`--stale` 的人讀輸出、混合 round、空 exclude 也完全沒有覆蓋。
- 目標測試在此唯讀 sandbox 無可用暫存目錄，測試 runner 於建立隔離環境前即失敗；上述效能與帳本枚舉均以不寫檔的直接函式／讀取方式完成。
