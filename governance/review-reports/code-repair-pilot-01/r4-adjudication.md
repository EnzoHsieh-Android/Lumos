# 第4輪判讀（編排者，非審查席原稿）

原稿分別保存於 r4-correctness.md、r4-boundary.md、r4-measurement.md、r4-security.md、r4-arch.md；本篇只記五席全收齊後的機械重現與判準。凍結程式為8922c3c9，全分支審材SHA256見r4-dispatch.json。使用者只授權一個追加輪次，所以即使主要缺陷仍存活，也不作r5或偷改r4審材。

- R4-C1／B2／M2／S1: 設定來源殘留是同一根因組。include及worktree兩形狀均在本機暫存repo成對重現，頂層有效remote與hook可繞，維持blocker。安全席S1原只作唯讀推論，實檔佐證由編排者和辯方後補；不能把父代理實驗歸給安全席。B2以`--no-verify`展示殘留remote，本身可跳hook不當作獨立洞；S1不帶跳hook選項仍dry-run成功，足以證有效防線失效。沒有真專案或網路push。
- R4-B1／S2: 正常子模組在副本保留remote，父代理臨時bare實際新增ref，維持blocker。S2另推測絕對巢狀gitfile可能寫回來源，但未跑該特定變體，不另計已證缺陷。
- R4-B3: 第一題破壞臨時副本Git資料後，清理命令失敗卻執行下一題，主入口rc0。維持major。
- R4-B4: Claude空字串ID會把畸形工具回傳當成功讀碼，維持major。這是新S3兩runner規則補齊問題，但修前版本也重現，並非r4修補新引入。
- R4-M1: 原席觀察成立。另席辯方核對後，unknown並未進內部valid/failed；`scored=total`是2026-09-30起明文保留的不足半數通知相容邏輯。可確認的剩餘問題是history_record把顯示分母存成歷史total且不存inconclusive，人工直接讀passed/total可看成假0%。目前沒有下游自動按該歷史率裁決的證據，編排者按minor資料口徑缺口留在Issue，不以其原稿major做額外blocker；原席報告與canary原始severity不改。辯方表態為evidence降級，依據`summarize_results`的valid/failed路徑、`history_record`及計劃S3。若後續找到下游以歷史total作自動裁決，從Issue重啟重驗嚴重度。
- R4-A1: 前輪已知C901品質告警，未見本輪新增錯誤行為，保留minor、待重估架構時處理；不拿測試綠取代全分支lint閘。

低共識的R4-S1經辯方與父代理實驗同意blocker；R4-M1經辯方有程式與合約反證降為minor。其餘成立項由父代理修前修後配對，未因多席重複報告而多計。所有五席原始報告之quote-check/refcheck通過，seat-check的measurement有1個未逐字寫完整snapshot檔名的觀測提醒，未改席報告。29670行整分支材料超出建議審材上限，分派只對新程式與上下文高密度審查；本輪找到真缺陷足以判FAIL，不能據此推論別處沒有漏網。

raw五筆canary均不帶假處置集合；r4-gate.txt記`DISPOSAL GATE FAIL`。沒有code-loop pass、freeze verdict或push。結論：局部三項修補的測試通過，但本案第4輪仍未收斂，按這次授權停止。沒有第五輪權限或額外名額變更。
