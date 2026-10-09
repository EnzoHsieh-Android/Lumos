severity: major

## Finding 1

severity: major

blocking:是

逐字引句:「初始化、時計與鎖錯誤使用專用 fatal 例外，探針產生 fatal=true、inconclusive=true、rc3 的候選結果並停止所有後題／重試；父程序停止派工並保留正式事故、候選及pending。」

佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:31`

佐證 file: `governance/eval/ablation_lumos_first.py:235`

佐證 file: `governance/eval/ablation_lumos_first.py:240`

佐證 file: `governance/eval/ablation_lumos_first.py:259`

具體輸入：以 `--max-per-window 5` 執行父派工器，指定帳是損壞 SQLite，或由另一程序持有寫鎖超過五秒。

推導：現有 `run_job` 在建立 `out`、`candidate`、`pending`，以及進入子程序例外處理之前，就先於 235–239 行查剩餘量。提案只說父派工器匯入同一實作，未規定必須把帳本查詢移到事故標記建立之後，也未定義此處例外如何轉成 `stop.set()`、正式事故與候選結果。因此最直接的實作會在前置查詢拋出，既沒有 promised artifacts，也未必停止其餘工作。S3 目前只核對零模型啟動及新帳跨窗口，抓不到這個父程序恢復證據缺口。驗收需加入 `run_job` 前置查帳失敗案例，明確斷言停止旗標、rc3／等價失敗結果及三種恢復路徑的狀態。

## Finding 2

severity: major

blocking:是

逐字引句:「不同路徑、使用者、機器是不同額度域；CLI 明示此邊界。`--max-per-window 0` 仍明示不設限制。」

佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:28`

佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:29`

佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:31`

具體輸入：同一本機有效帳已完成初始化且窗口內零筆；先用 `--max-per-window 0` 啟動十次模型，再於五小時內改用 `--max-per-window 5`。

推導：設計同時說 `0` 不設限制、兩個 runner 每次啟動前都寫 launch-intent，以及新帳首五小時封鎖，但沒有定義 `0` 是否仍寫帳。若 `0` 略過帳本，前十次不會進入後續有限窗口的計數，有限模式仍可再啟動五次；若 `0` 仍必須 claim，則帳缺失、損壞或新建帳的五小時封鎖會阻止宣稱「不設限制」的相鄰正常路徑。S1–S4 沒有覆蓋 `0→有限值` 切換或預設直跑。需先定義 `0` 是「只取消拒絕、仍記 intent」還是「完全停用帳本」，並加入切換驗收；否則無法同時判定正常路徑與硬額度是否正確。

## 實際覆蓋

- 凍結 spec：`r1-snapshot.md:1-52`
- `scripts/scenario_probe.py:711-1203`，重點為 `run_one_codex`、`run_one`、`main`
- `governance/eval/ablation_lumos_first.py:232-405,499-547`，重點為 `run_job`、`main`
- 未讀其他報告、作者 intake 或秘密；未寫檔、未呼叫模型或外部服務。

## 未驗資格

- 未執行 SQLite 併發、五秒鎖逾時、固定時鐘或跨午夜測試；這是凍結設計審，不是現況實作審。
- 跨機共享額度未驗，且 spec 已限定為各機器各自的本機帳，不能外推成跨機或供應商帳務保證。
- 回退只有程序性文字，未驗證舊版程式、排程或其他入口確實會先停用；亦未驗證歷史 FAIL 的保存流程。