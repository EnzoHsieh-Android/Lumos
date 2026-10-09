# 探針隔離修補：使用者授權的例外第四輪處置

使用者 2026-10-04 明示「開第四」，僅限樣本外儀器修補；不重算 `code-repair-pilot-01` 第1案四輪 FAIL。首派審材 `r4-snapshot.patch`，SHA-256 `aba46af10824bc3bf4f9f1a49ed81c8971be92012aba4d63da5541e4f9b5eb42`，742行。三席獨立讀該版：正確性 clean、架構兩 minor、邊界三 major。所有發現先由編排者在臨時結果目錄重現，再修補；沒有使用真模型或網路。

| id | 原席／實路徑重現 | 處置 |
|---|---|---|
| R4A1 | 架構 minor；HIT：新 [[Systems/ablation-lumos-first]] 沒有 MOC 入口。 | folded：在 MOC 的 `scope/evals` 加新家入口；`lumos lint MOC/index` 0 問題。 |
| R4A2 | 架構 minor；HIT：doctor 回報新家缺本案 Verification 的 typed `verified_by` 反向邊。 | folded：`lumos append Systems/ablation-lumos-first verified_by` 加邊，doctor 回到 0 issues。 |
| R4B1 | 邊界 major；HIT：只有舊 `skills_health_bad` 或逐場 `fatal` 的事故檔，真 `load_results` 仍載入成功列、`needed(a)=0`、`merge` 分母1；後者失效掃描還回空。 | folded：讀取、掃描、live 派工共用 `invalid_batch_evidence`；`t_probe_boundary_review4_legacy_poison_not_reused` 兩種舊格式修前紅修後綠。 |
| R4B2 | 邊界 major；HIT：out-dir 已有 fatal 檔，真 `main` 先呼叫 `run_job`，末尾才顯示失效，且 rc0。 | folded：派工前先掃舊檔、有事故則不建 jobs 並回3；`t_probe_boundary_review4_existing_poison_stops_dispatch` 修前紅修後綠。 |
| R4B3 | 邊界 major；HIT：真 `run_job` 在 rc1 且缺檔／半檔時 `stop=False`，回「有效0/1」並可續派。 | folded：結果不可讀、格式錯誤或非預期退出一律 set stop；`t_probe_boundary_review4_partial_output_stops_batch` 兩個事故紅綠，另以有效 JSON 的普通 rc1 作不誤擋對照。 |
| R4B4 | 原邊界席續驗 major；HIT：語法完整但缺 `fatal`／`inconclusive`／`skills_health_bad` 的結果可讓 live `run_job` 回有效1/1且不設 stop；原普通失敗對照 fixture 正好缺這三欄，形成假綠。 | folded：live 本版結果必須有三個型別正確的健康欄位；普通 rc1 對照改成真 schema，另以缺欄及錯型兩種資料作紅綠。原稿 `r4-boundary-recheck.md`。 |
| R4D1 | 全新差異席 major；HIT：live 子程序完全缺結果檔時 `run_job` 已停派，但 `main` 最後只掃磁碟，沒有檔可掃，summary 未標事故且 rc0。 | folded：`main` 保留 live stop 訊號，磁碟掃不到時補一筆本輪失效原因、回3；真 `main` 的 stub 子程序缺檔反例紅綠。原稿 `r4-delta.md`。 |

邊界前三條的修前輸出是 `r4-boundary-pre-fix-red.txt`（4 passed、5 failed），首修後全 `probe_` 260 passed、消融既有 23 passed，輸出是 `r4-boundary-postfix-*.txt`。續驗與新席的兩條追加反例在首修版 9 passed、3 failed，見 `r4-delta-pre-fix-red.txt`。最終修後全 `probe_` 263 passed、消融既有 23 passed，`py_compile` 與 `git diff --check` 通過。第四輪首派報告 `r4-correctness.md`、`r4-architecture.md`、`r4-boundary.md` 經 `lumos report-normalize` 只搬格式；`r4-boundary-recheck.md` 只複查原席發現，`r4-delta.md` 是新席看369行追加差異。最後又派全新席審235行修補差異，`r4-last.md` 回報 clean、blocking 0。至此首派五項、續驗與 delta 兩項共七項全折，正式處置閘仍待機械判定；舊三輪 FAIL 不改寫。
