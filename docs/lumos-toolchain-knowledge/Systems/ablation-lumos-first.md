---
type: system
status: doing
created: 2026-10-04
updated: 2026-10-04
responsibility: 負責探針消融結果檔的有效性篩選、缺場補跑與統計合併；不負責探針沙盒本身的隔離與健康檢查執行
aliases: []
about_code:
  - governance/eval/ablation_lumos_first.py
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY: 2026-10-04 第三輪代碼審證明探針整批 fatal 時仍可能保留逐場成功列；消融讀取端須再查整批有效性。出處 [[Verification/2026-10-04_探針隔離與清理收斂]] 與 r3-reproduction.json。
  PITFALL: 只按逐場 reason 判有效會把健康不可判的批次計入統計且抵掉缺場。出處 [[Issues/探針健康檢查不可判資料仍被重用]]。[test:t_probe_boundary_review4_fatal_batch_not_reused]
  PITFALL: 新頂層 fatal 不能涵蓋舊輸出只標 skills_health_bad 或逐場 fatal 的事故，且失效檔若在補跑後才掃會先啟動模型。出處 r4 邊界席 [[Verification/2026-10-04_探針隔離與清理收斂]]。[test:t_probe_boundary_review4_legacy_poison_not_reused]
  PITFALL: 子程序缺檔／半檔時只停派仍不夠，末尾若只重掃磁碟會把無檔事故消掉；語法正確但缺健康欄位的本版 live 結果也不能證明健康。出處 r4 續驗與差異席 [[Verification/2026-10-04_探針隔離與清理收斂]]。[test:t_probe_boundary_review4_missing_output_main]
  WHY: 2026-10-04 後續設計選擇單路派工與同目錄互斥，因 Python 已啟動的 future 無法靠取消排隊工作停止；恢復並行要先證明事故後所有在途模型均已停。出處 [[Projects/探針隔離與清理收斂_計劃]] S9-S10 與 Python concurrent.futures、fcntl 官方文件。
  PITFALL: 子程序啟動例外可能跳過摘要，且先寫出的有效外觀結果會在重跑時被採信；失敗嘗試須留可供下次合併辨認的致命紀錄，不能只靠本次記憶中的 stop 旗標。出處 [[Issues/探針批次停止後的剩餘工作與落檔邊界]] 與 [[Verification/2026-10-04_探針停派與失敗留痕]]。[test:t_probe_boundary_postreview_launch_exception_summary]
  PITFALL: 先歸檔舊結果再寫 fatal 會留下中斷空窗；代碼審故障注入證明下次純合併會漏掉事故。出處 [[Verification/2026-10-04_探針停派與失敗留痕]]。[test:t_probe_boundary_postreview_archive_interrupt]
  PITFALL: 鎖檔路徑被移除後另一進程可鎖到新 inode；只看鎖檔名稱會誤認仍有互斥。出處 [[Verification/2026-10-04_探針停派與失敗留痕]] 與 Linux flock(2) 官方手冊。[test:t_probe_boundary_postreview_lockfile_replacement]
  PITFALL: 摘要既有符號連結可把直接寫檔導出目錄外，長題號再加奈秒時間戳會使檔名超過檔案系統上限。出處 [[Verification/2026-10-04_探針停派與失敗留痕]]。[test:t_probe_boundary_postreview_symlink_outputs]
  PITFALL: 只以 import 載入被測 CLI 會避開 __main__ 的執行順序；helper 若定義在入口後方，測試全綠而實際命令必定 NameError。出處 [[Verification/2026-10-04_探針停派與失敗留痕]]。[test:t_probe_boundary_postreview_cli_entry_and_modes]
  PITFALL: 目錄鎖修掉可刪鎖檔競態後，仍在跑的舊版若只持鎖檔，新版只鎖目錄就會在版本交接時同時派工。出處 [[Verification/2026-10-04_探針停派與失敗留痕]]。[test:t_probe_boundary_postreview_legacy_lock_interop]
verified_by:
  - "[[Verification/2026-10-04_探針隔離與清理收斂]]"
  - "[[Verification/2026-10-04_探針停派與失敗留痕]]"
---
# ablation-lumos-first

這篇是 `governance/eval/ablation_lumos_first.py` 的家，負責消融結果檔的有效性、缺場與合併判定。

此篇管消融結果的「能不能拿來算」這道邊界。[[Systems/codex-harness]] 管探針如何產生與隔離樣本；兩邊都要守住整批失效的訊號，否則即使探針退出碼正確，重開消融或只做合併時仍可能吃到事故資料。

第四輪修補採整檔排除：fatal 檔案保留原始逐場紀錄供事故分析，但不能抵掉缺場或進入統計；掃描失效檔時同時辨認全域連結損壞與未能完成健康／清理檢查的 fatal。沿用既有彙總欄位以免舊讀取器漏看，呈現文字改為「探針失效」，不把所有 fatal 都叫作 skills 連結損壞。若未來新增消費端，先以 [[Verification/2026-10-04_探針隔離與清理收斂]] 的致命批次反例驗證整批欄位有被讀到。

第四輪邊界席又證出三種舊/壞資料入口：沒有頂層 fatal 的舊事故檔、事後才掃失效檔、模型程序留下缺檔或半檔但仍續派。處置是同一份整批失效判定供讀取、掃描與 live 派工共用；舊列只要明示 skills 損壞或逐場 fatal，就拒收整檔，普通因有效場不足的 inconclusive 不因此整批作廢。先掃舊檔才派模型；本輪產物不可讀或程序異常退出也停批。反例為 `t_probe_boundary_review4_legacy_poison_not_reused`、`t_probe_boundary_review4_existing_poison_stops_dispatch`、`t_probe_boundary_review4_partial_output_stops_batch`；若改結果 schema 或派工順序，從這三項重驗。

原席續驗發現語法完整但缺健康欄的 live 檔可被當普通模型失敗，故同 checkout 的 producer/consumer 要求三個整批健康欄位及型別；歷史舊檔仍由 `invalid_batch_evidence` 做相容判定，不回頭強求新 schema。全新差異席另發現「完全缺檔」時 `run_job` 雖停派，`main` 的磁碟重掃卻把事故訊號洗掉；本輪停止旗標要傳到 summary/退出碼。兩條反例為 `t_probe_boundary_review4_partial_output_stops_batch` 的 schema 分支及 `t_probe_boundary_review4_missing_output_main`，均先紅後綠。下次改 live 結果的可採信條件，兩項要一起跑。

後續修補的取捨見 [[Projects/探針隔離與清理收斂_計劃]] S8-S10：單路派工把「事故後還有另一個已開始的模型」排除在同一次 CLI 外，同目錄互斥則防另一個 CLI 同時啟動；子程序啟動例外要留下持久的 fatal 嘗試，讓下次純合併仍拒收。反例為 `t_probe_boundary_postreview_serial_dispatch`、`t_probe_boundary_postreview_cross_process_lock`、`t_probe_boundary_postreview_launch_exception_summary`。這是本機 POSIX 及受控 stub 的驗證，真模型吞吐與跨機共享檔案系統鎖效力沒有由此推出；要恢復多路時依計劃的 RETIRE-IF 先驗在途取消。

代碼審續驗證明鎖檔名稱不能代表同一 inode，故互斥目標改為輸出目錄本身；這仍是合作進程的本機 advisory 鎖。若輸出目錄改為不受信任者可任意改名的共用空間，入口是該部署／權限變更，須重驗目錄身分與所有讀寫路徑，不能沿用本機互斥結論。歸檔前先原子取代 fatal 記錄；摘要、meta 亦以原子替換避免跟隨目標符號連結到目錄外。長題號改用固定長度檔名摘要，完整題號保留在結果或失敗紀錄。對應四條先紅後綠反例在 [[Verification/2026-10-04_探針停派與失敗留痕]]；變更落檔或鎖身分時一起重跑。

真 CLI 子程序測試補了 import 測試看不到的執行順序；新版還要同時持有舊鎖檔，直到不再可能與只鎖舊檔的程序交接。若將來確定所有舊程序已退出且不再從舊版啟動，入口是部署版本清查，才可考慮撤掉舊鎖相容；撤前重跑 `t_probe_boundary_postreview_legacy_lock_interop` 並更新計劃退場條件。摘要原子替換沿用既有普通檔的權限，目標是符號連結時不抄其模式；反例同由 `t_probe_boundary_postreview_cli_entry_and_modes` 與 `t_probe_boundary_postreview_symlink_outputs` 釘住。
