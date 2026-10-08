---
type: project
status: doing
created: 2026-10-08
updated: 2026-10-08
tags:
  - type/project
  - status/doing
  - scope/evals
lands_in:
  - Systems/codex-harness
  - Systems/ablation-lumos-first
related:
  - "[[Projects/探針隔離與清理收斂_計劃]]"
---

# 探針持久用量帳

## 原問題與範圍

父計劃 [[Projects/探針隔離與清理收斂_計劃]] 第三輪 G10、G11 原始反例見 governance/review-reports/code-probe-postreview-dispatch-ledger/r3-intake.md：失敗結果歸檔後窗口用量回到零，換日期輸出目錄也回到零。本案只修本機同一帳路徑的五小時派工限制，不把它說成供應商帳號／跨機全域用量。模型正式結果是否可計分仍由消融讀取器裁定，不因記用量而變有效。

PRIOR-ART: 採 Python sqlite3 標準庫及 SQLite BEGIN IMMEDIATE 的持久交易，借既有交易序列化而不自寫多檔鎖或結算協定。官方來源 https://docs.python.org/3/library/sqlite3.html 、https://www.sqlite.org/lang_transaction.html 。sqlite3 是 CPython 可選模組；缺模組、壞帳或鎖逾時均在模型前停止，不退回從结果檔估算。
RETIRE-IF: 下一個完整真模型窗口若顯示持久帳的保守誤擋／維護成本高於省下呼叫成本，由使用者裁決撤回硬額度；修改 [[Projects/探針隔離與清理收斂_計劃]] S18 與 CLI 承諾後再移除，不靜默旁路。

## 設計

- 用量帳位於共用本機預設路徑 `~/.local/state/lumos/probe-attempts.sqlite3`，探針命令 scripts/scenario_probe.py 與父派工命令 governance/eval/ablation_lumos_first.py 均可用 `--attempt-ledger` 指定同一絕對路徑。不同路徑、使用者、機器是不同額度域；CLI 明示此邊界。`--max-per-window 0` 仍明示不設限制。
- SQLite helper 放入探針模組，父派工器 run_job import 同一實作；不新增第三方依賴。run_one 與 run_one_codex 兩個真模型 runner 在題目及副本驗證完成後、呼叫 subprocess 前，以一個 BEGIN IMMEDIATE 交易核對窗口並寫入一次 launch-intent。核帳用同一個 now；已達限不插入且rollback，未達限插入並commit；commit成功才啟動模型。SQLite鎖等待上限固定五秒，超時fatal、不啟動。
- 每次重試重新 claim；失敗、取消、解析失敗及結果歸檔都不刪 launch-intent。啟動 OS 例外也保守占一筆，文案稱啟動意圖額度而非已付費呼叫數；不做不可證的退款。
- 初始化交易寫 initialized_at（Unix epoch秒）；新建帳自動從 initialized_at 保守封住首五小時，使新工具上線前或遺失帳後的舊呼叫先過期，避免把不可得舊用量當零。既有帳以每筆 claimed_at（同為Unix epoch秒）計算；恰滿五小時的紀錄已過期；偵測系統時鐘早於已記時間時停止，避免回撥後低估。壞帳包含損壞、非一般檔、既有schema/version不符或不可讀寫；時計錯誤包含 now 小於 initialized_at 或已記 claimed_at。初始化、時計與鎖錯誤使用專用 fatal 例外，探針產生 fatal=true、inconclusive=true、rc3 的候選結果並停止所有後題／重試；父程序停止派工並保留正式事故、候選及pending。
- 父程序只用帳的剩餘量作提前提醒及本批 max-attempts；探針新增 --max-per-window 接收父派工器原始窗口上限；--max-attempts 仍只限本批。每個實際 launch 前仍在同一交易重驗，其他輸出目錄不能競爭超額。日期與評分結果 mtime 不參與硬額度。

## 驗收條款

- [S1] 當同一帳已有四筆啟動意圖且窗口上限為五筆時，兩個獨立程序競爭剩餘一筆應只有一個 claim 成功且總数五；鎖逾時不得呼叫模型。[manual:暫存SQLite帳加兩個程序競爭，核對成功數一及持久行數五]
- [S2] 當模型啟動後失敗或父程序死亡，且操作者歸檔三份結果或改跨午夜輸出目錄時，重跑仍應讀到原用量並拒絕超限。[manual:故障注入後歸檔三檔及切换日期輸出，核對同帳剩餘量與模型啟動計數]
- [S3] 當帳缺失、損壞、不可讀或時鐘回撥時，派工器應在模型前停止；新帳首五小時只保守等待且五小時後可 claim。[manual:固定時鐘與壞資料庫反例，核對模型零啟動及新帳跨窗口結果]
- [S4] 當題目預驗失败、或首次撞供應商上限已記啟動意圖、且本批額度已滿時，該筆意圖保留；其後被本機額度拒絕的重試應零新增 launch-intent，且不再先等待300秒。[manual:缺expect及最後一筆limit結果兩案例，核對意圖行數與sleep零次]

## 實務隱患

已排除:金流:只控制本機模型啟動意圖，不計價，不當供應商帳務來源。
對外送出:本案正式驗證用假模型子程序與暫存帳，真模型窗口量測另記驗證，不在設計閘啟動。
已排除:正式環境不可逆:不改使用者業務資料，持久帳只追加啟動意圖。
守衛面:本案會改派工額度與故障停止條件，須過完整設計審與修後代碼審。

## 回退

回退實作先停真模型派工並保留持久帳及原始事故；若仍宣稱五小時限制，不可恢復以可歸檔結果檔反推硬額度。需要撤回硬額度時先裁決並修改 S18／CLI 說明，保留歷史三輪FAIL。

REVISIT:[when-file:scripts/scenario_probe.py][by:2026-11-08] 下一個完整真模型窗口核對持久帳保守誤擋與維護成本，觀測到保守誤擋／維護成本高於省下呼叫成本時由使用者按RETIRE-IF裁決撤除。
