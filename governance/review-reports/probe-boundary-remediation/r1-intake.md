# 探針隔離與清理修復：代碼審首輪

審材 `r1-snapshot.patch`，sha256 `09bf4aa0cdfbaae297e274250d66887dc8898b832e24be23b3c282a2b5e64b9b`，1307 行，對應功能提交 2854d961。`pitfalls --diff 88752a29..HEAD` 分級 standard；三席代碼審與架構席同時獨立讀這一版，四份報告收齊後才動程式。表態 `py-eventloop` 為同步 CLI 不適用。各報告 quote-check、refcheck、seat-check 均通過。

| id | 原席 | 編排者核對及處置 |
|---|---|---|
| C1 | 正確性 blocker | HIT：巢狀 bare repo 無 `.git` 入口仍有自身 remote；臨時 bare repo dry-run/實驗外 ref 證據見原席報告。folded：識別工作樹中的 bare Git 形狀，加入 `t_probe_boundary_review1_git_shapes`。 |
| C2 | 正確性 major | HIT：封閉重建 config 後沒有假身分，模型提交取本機帳號。folded：副本 config 明訂 probe 假身分，加入 `t_probe_boundary_review1_trace_identity`。 |
| C3 | 正確性 major | HIT：普通題後接讀碼題時 `--keep` 留零份。folded：逐場更新「最後普通題」保留副本，加入 `t_probe_boundary_review1_keep_retry`。 |
| B1 | 邊界 blocker | HIT：macOS 大小寫不敏感檔案系統中 `.GIT` 漏過精確字串比較，前置測試已證現場。folded：大小寫折疊拒絕巢狀 Git 入口，同一 `git_shapes` 測試。 |
| B2 | 邊界 major | HIT：父環境 `GIT_TRACE` 指向來源檔時，儀器自己的 Git 呼叫從9 bytes追加至4577 bytes。folded：Git 環境清掉 `GIT_TRACE*`，同一 `trace_identity` 測試。 |
| M1 | 量測 major | HIT：與 C3 同一混合題序問題，不重算根因。folded：同 C3。 |
| M2 | 量測 major | HIT：用量上限重試第一次模型時間只在批次總數，逐次結果遺失。folded：正式結果帶 `retry_attempts` 的每次時間，加入 `keep_retry` 測試。 |
| M3 | 量測 minor | HIT：故障注入在刪除前拋錯，測試遺留臨時副本。folded：測試用真實清理函式補收殘留。 |
| A1 | 架構 minor | HIT：普通題與基線都叫 `_remove_source_sandbox`，名稱與責任不合。folded：改成 `_remove_sandbox`。 |
| A2 | 架構 major | HIT：舊 `_run_source_attempt` 無生產呼叫，main 另有完整生命週期。folded：刪掉舊 helper，原直接測試改驗 main 或真實副本路徑。 |

去重後九組發現，其中兩組為巢狀 Git 形狀、兩組為環境／身分設定；C3/M1 為同一組。新反例在舊版確實翻紅；`git_shapes` 初版 fixture 因巢狀 repo 沒有 commit 讓 `git add` 自己失敗，補前置 commit 後才算有效紅燈。修後 `probe_` 243項斷言、0失敗，輸出在 `r1-postfix-regression.txt`。這是本輪折入自測，不等於第2輪獨立驗收或分支放行。

所有 Git 外逸實驗限臨時 repo 與本機 bare；沒有真遠端 push、真模型或完整測試套件。本修復是原五案試行之外的儀器介入，原 `code-repair-pilot-01` 四輪FAIL仍保留。輪次成本：首輪派工與每席收卷的精確牆鐘起訖沒有完整打點，總耗時／新增步驟耗時記未知，不把席位分鐘相加。
