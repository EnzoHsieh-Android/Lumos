# 測試證據互補性固定實驗

最終證據為 run-v2：Python3.14.6／Node24.16.0，各25矩陣格與3次錯誤規則基準→故障→還原循環，全部事前結果吻合；不是56個獨立樣本。manifest保存需求、預期與runner SHA；results保存每格來源SHA、測試結果與stdout/stderr；來源檔可重放。

run-v1是中間版本，未增加明確錯版還原循環，對應當時runner而非最終runner；不得混加作效果分母。

唯讀乾淨agent於2026-10-08核對最終runner、全部來源hash、圖譜、手冊與結果一致，沒有剩餘finding。沒有模型效果、真專案輪數或各棧原生framework資格宣稱。各棧接入標準：skills/lumos-project-notes/commands/test-quality-standard.md。

歸檔形式：逐格程式是可信固定實驗的原始來源卷證，以原始檔名加 `.txt` 保存，不作專案可維護程式入口。results 的 artifact 保存執行時原名；查檔在相應資料夾加 `.txt`。內容未改，source SHA 可直接核對；重放時複製到暫存原名，執行固定 runner亦可重新產生。改 runner 或需求須重新跑，不直接編輯卷證。
