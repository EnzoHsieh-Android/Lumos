---
type: system
status: doing
created: 2026-10-04
updated: 2026-10-08
responsibility: 負責探針消融結果檔的有效性篩選、缺場補跑與統計合併；不負責探針沙盒本身的隔離與健康檢查執行
self_audit: gpt-5.6-sol/2026-10-08
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
  - "[[Verification/2026-10-04_消融派工正式審查修正]]"
  - "[[Verification/2026-10-08_消融結果與恢復控制驗證]]"
  - "[[Verification/2026-10-08_持久用量帳暫存控制驗證]]"
  - "[[Verification/2026-10-08_持久用量帳第四輪代碼審停點]]"
  - "[[Verification/持久用量帳第五輪修補驗證]]"
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

PITFALL: 正式代碼審多席找到「非零退出只停本輪、下次合併卻採信成功外觀列」；父程序被殺時，原本只由父程序持有的鎖也無法代表子程序已停。出處 [[Verification/2026-10-04_消融派工正式審查修正]] 與 `r1-formal-correctness.md`、`r1-formal-concurrency.md`。重現／防回歸：`t_probe_boundary_formal_dispatch_fail_closed`。未完成標記以先建立、驗證成功後才清理的順序封住此洞；標記殘留表示人工要先查日誌與在途程序，不能直接採信同名結果。

PITFALL: 單工作場數可超過窗口剩餘額度，`--only` 的逗號／前綴語意又可能將一題展成多題；相對輸出路徑曾令鎖住的目錄與子程序落檔目錄不同。出處 [[Verification/2026-10-04_消融派工正式審查修正]] 與 `r1-formal-security.md`。重現／防回歸：`t_probe_boundary_formal_input_validation`、`t_probe_boundary_formal_dispatch_fail_closed`。若將來更換選題或批次編排介面，先重驗精確一題與同目錄互斥。

WHY: 結果檔 schema 採讀取端保守拒收，因錯誤字串 `passed: "false"` 可被 Python 視為真值並抬高 M1；報表 Markdown 必須直接顯示整批不可採信，因人可能只看這份檔案。出處 [[Verification/2026-10-04_消融派工正式審查修正]] 的正式 r1 資料席與邊界席，反例 `t_probe_boundary_formal_dispatch_fail_closed`。這是輸出可信度邊界，不將低有效場數的普通 inconclusive 一概判 fatal。

PITFALL: r2 指出只歸檔 `.pending` 會讓原先由子程序直寫的成功外觀 JSON 復活。子程序現在寫候選檔，父程序驗證精確列數、題號、組別、schema 與退出碼後才升格；殘留候選檔本身也是失效訊號。出處 [[Verification/2026-10-04_消融派工正式審查修正]] 與 `r2-external-finder-v2.txt`；防回歸 `t_probe_boundary_formal_second_round_regressions`、`t_probe_boundary_formal_parent_killed_child_continues`。若改結果落地協定，先重驗只歸檔標記仍不能採信未驗證列。

PITFALL: 結果欄位錯型、非物件逐場元素及 A 題多跑遮掉 B 題缺場，都曾讓讀取端報出虛高數字。現在按檔拒收錯型結果，缺場逐題計算；旁邊的無關 JSON 不再當探針事故。出處同篇 Verification 的 r2 intake；防回歸 `t_probe_boundary_formal_second_round_regressions` 與 `test_load_results_skips_bad_json`。結果 schema 或檔名規則變更時重跑。

WHY: [status:superseded] 2026-10-04 曾以正式結果與重試次數近似「實際模型呼叫」；2026-10-08 持久帳設計已推翻這個權威來源，改記模型啟動前提交且失敗不退還的 launch-intent。舊近似只保留為決策歷史，現況與驗證入口見 [[Projects/探針持久用量帳_計劃]]、[[Verification/2026-10-08_持久用量帳暫存控制驗證]]。

PITFALL: 上段只是 r2 修法的意圖，r3 證明現碼沒有做到帳號級五小時額度：`runs_in_window` 只掃當前日期目錄內正式 JSON；子程序失敗時真正用量留在候選檔，歸檔後歸零，跨午夜也歸零。出處 [[Verification/2026-10-04_消融派工正式審查修正]] 的 r3 FAIL 與 `r3-intake.md` G10–G11；重現指令與輸出在同一 intake。若保留硬額度，先建不隨結果歸檔消失的權威用量帳，不能再從 M1 計分結果推回實耗。

PITFALL: r3 另證明逐題缺場修好後，重複同題列仍可灌高 M1–M4；`calls` 只驗外層 list，錯型元素仍能被當無 lumos 呼叫。出處同篇 Verification 的 r3 G12–G13；重現指令與輸出見 `r3-intake.md`。結果計分前要先驗每題場數和每個呼叫元素形狀，不能以 `missing=0` 推論分母正確。

PITFALL: 消融題庫去重的舊測試只在測試內複寫去重迴圈，沒有呼叫真正派工讀題函式；實作改壞仍可能維持綠燈。r2 改用實際 `load_ids` 載入含重複題號的暫存題庫，斷言派工前拒絕。出處 [[Verification/2026-10-04_消融派工正式審查修正]]、`r2-external-finder-v2.txt`；防回歸 `test_load_ids_rejects_duplicates`。若再寫協定測試，先確認斷言經過正式入口。

PITFALL: 歸檔中斷測試只驗「最後有 fatal」，卻沒驗注入點真的觸發；既有或新加的其他 fatal 標記可讓整支測試假綠。正式代碼審指出後補上注入計數斷言。出處 [[Verification/2026-10-04_消融派工正式審查修正]]、`r1-formal-correctness.md`；防回歸 `t_probe_boundary_postreview_archive_interrupt`。改故障注入時先讓斷言證明注入有發生，再驗收結果。

PITFALL: r2 再指出同一測試只要 `.pending` 還在，`load_results` 就會拒收同名成功檔；即使 fatal 正式檔根本沒寫，也可假綠。現在注入點後直接檢查 fatal 正式 JSON 已落地，再看整批拒收。出處 [[Verification/2026-10-04_消融派工正式審查修正]]、`r2-external-finder-v2.txt`；防回歸 `t_probe_boundary_postreview_archive_interrupt`。修改事故落地順序時要同時檢查標記、正式檔與候選檔。

PITFALL: r3 的額度測試在空目錄給 `max_per_window=50`，就算把「剩餘額度」誤改成「整個上限」，測試仍綠；橫幅測試只查文字存在，移到報表最後也會綠。出處 [[Verification/2026-10-04_消融派工正式審查修正]]、`r3-external-finder.txt`；重現方法及觀測在 `r3-intake.md` G20。下次寫額度和顯示測試，先用「已有 45、剩 5」及「警示必在第一屏」作前置斷言，再做移除守衛的翻紅檢查。

PITFALL: 第三輪證實同題超額結果可灌高通過率、錯型 calls 可被當成沒用工具，事故文字也漏了未完成檔。修後保留原始資料但每題只採前 runs 個有效場；calls 逐項驗兩個字串；事故列三個恢復路徑且先確認無在途探針。出處 [[Verification/2026-10-08_消融結果與恢復控制驗證]]；防回歸 [test:t_probe_boundary_fourth_round_result_contracts][test:t_probe_boundary_fourth_round_recovery_recipe]。

PITFALL: 純合併把壞meta覆寫成來源未知會抹掉救援證據，報表不一致題清單、健康檔名與版本來源也曾漏轉義。修後metadata只作輸入，未知只呈現在報表，來源byte及metadata符號連結保留；摘要仍原子取代且不寫到連結目標。出處 [[Verification/2026-10-08_消融結果與恢復控制驗證]]；防回歸 [test:t_probe_boundary_fourth_round_report_and_provenance][test:t_probe_boundary_postreview_symlink_outputs]。

PITFALL: 可封存的結果檔與日期目錄不是硬額度來源；失效候選被排除計分後，舊計數會讓已啟動模型的額度消失。[根因:把計分視圖混當啟動用量帳][出處:code-probe-postreview-dispatch-ledger r3 G10/G11][test:test_attempt_ledger_failed_launch_archive_and_cross_date_keep_quota] [[Verification/2026-10-08_持久用量帳暫存控制驗證]]

PITFALL: 備註檔與探針同用組別前綴，健康掃描曾將操作者備註視為事故，造成無效停批。[根因:僅依組別前綴辨認正式結果][出處:code-probe-postreview-dispatch-ledger r3 G14][test:test_ablation_notes_are_not_results_but_legacy_shards_are]

WHY: 用量帳控制案例保留在既有探針消融測試群，使用外部模型邊界假替身與暫存帳，避免驗證本身觸碰真模型或使用者額度。[出處:Projects/探針持久用量帳_計劃] [[Verification/2026-10-08_持久用量帳暫存控制驗證]]

WHY: 用量帳控制從真探針 CLI 與消融派工入口驗輸出協定及副作用計數，不用重抄計數公式來製造綠燈。[出處:Projects/探針持久用量帳_計劃] [[Verification/2026-10-08_持久用量帳暫存控制驗證]]

PITFALL: HTML escape 不會阻止 Markdown 圖片／連結語法，也不會移除 ESC、BEL 等終端控制字元；報表在 Markdown 預覽或直接印到終端時仍會把外部 meta 當控制內容。第五輪改為先將不可列印字元轉成可見序列，再轉義會啟動行內 Markdown 的字元；同時保留既有事故檔名字面。防回歸 [test:t_probe_boundary_fourth_round_report_and_provenance][test:t_probe_boundary_formal_dispatch_fail_closed]，紅綠證據見 [[Verification/持久用量帳第五輪修補驗證]]。

PITFALL: 只轉義 `[]()!` 時，GitHub 類 Markdown 仍會把報表裡的裸網址、`www.` 與 email 自動變成可點連結、`~~` 變刪除線；而先轉控制字元再轉義反斜線，會讓真的 ESC 與原本就寫著 `\x1b` 的文字呈現成同一個樣子 [出處:code-probe-postreview-dispatch-ledger r5 BND5-03/BND5-04/SEC5-02] [根因:轉義集合只依當時見過的語法挑選，且字面反斜線沒有先加倍] [test:t_probe_boundary_fourth_round_report_and_provenance]。證據 [[Verification/持久用量帳第五輪審查修補驗證]]。

WHY: 原子寫入不在消融腳本另留一份，改從探針匯入同一份實作，跟本檔對判準採「單一實作來源」的做法一致 [出處:code-probe-postreview-dispatch-ledger r5 ARCH5-01] [因:兩份逐行相同的實作在第五輪已經開始分岔（權限與裝置處理只修了一邊）] [不選:兩邊各修一次（下次仍會漂移）] [test:t_probe_boundary_postreview_cli_entry_and_modes]

WHY: 報表裡的外部文字把不可列印字元轉成看得見的 `\xNN` 序列，不像 lumos 主程式清理注入內容那樣換成空白 [出處:code-probe-postreview-dispatch-ledger r5 ARCH5-02] [因:消融報表是事後追查的證據，要能從報表看出原值是哪個字元；注入清理的目的只是不讓內容控制版面，原值不重要] [不選:沿用換空白（追查時看不出是 ESC 還是 BEL）] [test:t_probe_boundary_fourth_round_report_and_provenance]
