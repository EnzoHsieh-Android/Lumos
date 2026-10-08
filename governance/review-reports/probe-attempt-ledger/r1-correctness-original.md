severity: major  
blocking: 是  
逐字引句:「已達限不插入且rollback，未達限插入並commit；commit成功才啟動模型」

設計沒有定義「本機額度拒絕」的回傳型別、結果列、退出碼與父程序處置。

佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:29`  
佐證 file: `scripts/scenario_probe.py:1115`  
佐證 file: `governance/eval/ablation_lumos_first.py:296`

具體輸入與推導：

1. 上限 5，父程序讀到剩餘 1，派出一題。
2. 另一程序先 claim 第五筆。
3. 本程序交易重驗時必須拒絕啟動。
4. 若沿用 `limit_hit`，現有重試分支會先睡 300 秒；若拋 fatal，會把正常達限判成整批事故、rc3；若不產生結果列，`run_job` 又會因 `len(rows) != n` 判定輸出無效。
5. 三種處置皆與部分條款衝突，但 spec 未指定第四種可辨識的「本機額度耗盡、非供應商上限、非事故」結果契約。

需明定其結果欄位、是否加入 `results`、退出碼、是否停止後題，以及父程序如何保留 candidate/pending；並明定此狀態不得走供應商 `wait_on_limit`。

severity: major  
blocking: 是  
逐字引句:「新建帳自動從 initialized_at 保守封住首五小時，使新工具上線前或遺失帳後的舊呼叫先過期」

初始化隔離只涵蓋 `initialized_at` 之前的舊呼叫，沒有排除仍存活的舊版程序在初始化之後啟動模型。

佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:31`  
佐證 file: `scripts/scenario_probe.py:1119`

具體輸入與推導：

1. T0 建立新帳並開始五小時隔離。
2. 一個 T0 前已進入既有 300 秒重試迴圈、尚未升級的程序，在 T0+4:59:59 啟動模型；它不會寫新帳。
3. T0+5:00:00，新版程序依 `initialized_at` 解封並可 claim 完整上限。
4. 此時最近五小時仍包含那筆舊版啟動，帳卻將它視為已過期，可能多啟動一筆。

需把「初始化前必先確認沒有舊探針存活／停派滿五小時」列為前置條件，或提供能阻止舊版程序在 `initialized_at` 後啟動的 rollout 機制；否則「舊呼叫先過期」不成立。

severity: minor  
blocking: 否  
逐字引句:「恰滿五小時的紀錄已過期」

`initialized_at`、`claimed_at` 雖指定為 Unix epoch 秒，但未指定儲存型別、精度及邊界比較式，恰界行為仍有兩種相容實作。

佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:31`

具體輸入與推導：

- 真實初始化時間為 `1000.9` 秒。
- 若先轉整數 `1000`，以 `now - initialized_at >= 18000` 解封，會在實際經過 `17999.1` 秒時提前開放。
- 若保存 REAL `1000.9`，則會在完整五小時後開放。

應明定欄位為 REAL epoch seconds，並使用 `claimed_at <= now - 18000` 視為過期；或明定整數取整規則及接受的一秒誤差。

實際覆蓋：完整初讀 52 行凍結 snapshot；精讀 `scripts/scenario_probe.py` 的 `run_one_codex`、`run_one`、`main`，以及 `governance/eval/ablation_lumos_first.py` 的 `run_job`。未讀其他審查報告、作者 intake、秘密或外部服務，未呼叫模型，未寫檔。

未驗資格：未檢查未指定函式、實際 schema/helper 實作、跨機或供應商帳務；後兩者依固定邊界不納入本席結論。