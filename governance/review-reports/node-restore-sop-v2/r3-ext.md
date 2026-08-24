1. **blocker**  
   引句:「本迴圈記帳型態走 panel 閘，2026-08-06 後的迴圈 K=2 連續兩輪乾淨、第二輪審全量」  
   問題：現行 design-loop 的正式操作不是 panel，而是 `canary record` 帶處置集合後，以 `loop status --disposal` 問閘；`--disposal` 又與 `--panel` 明確互斥。照現行手冊執行，根本不會進 `_panel_k2_active`，因此可由單輪 disposal gate 結束，沒有 K=2。spec 雖把這稱為「工具鏈文件縫」，卻仍用 panel K=2 推導本案的收尾結論，造成機械判準兩套並存，會直接做出不同的放行行為。  
   查證：`/tmp/node-restore-sop-v2-r3.md:190`；`skills/lumos-design-loop/SKILL.md:27-35`；`scripts/lumos:4527-4534`

2. **major**  
   引句:「以機械閘的實際判定為準：本迴圈記帳型態走 panel 閘，2026-08-06 後的迴圈 K=2 連續兩輪乾淨、第二輪審全量」  
   問題：panel 程式只機械驗「前後兩輪各自通過合取」；沒有欄位或檢查能證明第二輪審查員讀了「全量材料」。“第二輪要審全量”只出現在失敗提示文字，不能據此宣稱是機械閘的實際判定。即使改走 panel，第二輪只審 delta、但記錄乾淨，仍可能 PASS。  
   查證：`/tmp/node-restore-sop-v2-r3.md:190`；`scripts/lumos:3897-3923`；`scripts/lumos:3726-3747`

3. **major**  
   引句:「沙盒的標準照自家探針沙盒先例三層切斷：斷真實外部端點、假憑證、測試身分、資料可重置」  
   問題：repo 的 `make_sandbox` 三層實際是「移除 Git remote、pre-push hook 擋 push、使用 probe 假 Git 身分」，第三層甚至只是事後可辨識，並非切斷；它沒有切 webhook／郵件／簡訊端點、沒有替換服務憑證，也沒有建立可重置資料層。spec 借用了「自家先例」名義，卻換成另一套未實作、未提供操作方式的隔離標準；操作者無法照該先例得到文字宣稱的 runtime 安全性。  
   查證：`/tmp/node-restore-sop-v2-r3.md:119`；`scripts/scenario_probe.py:80-109`

4. **minor**  
   引句:「只認反引號包住的 path[:行號]，且首段須是現存頂層目錄」  
   問題：抽取器遇到非法尾碼仍可能收貨。例如反引號中的 `scripts/lumos:abc` 會把 `:abc` 去掉、以 `scripts/lumos` 且空行號送驗，最後判為有效檔案；因此不是「只認 path[:數字行號]」。另外實作也接受數字範圍 `:10-20`，文字沒有交代。這會讓格式錯誤的報告引用得到假綠。  
   查證：`/tmp/node-restore-sop-v2-r3.md:139`；`scripts/lumos:10757-10776`；`scripts/lumos:10735-10749`

指定的其餘修法核對未見否決級問題：J-c 的 `[src:]`／`[git:]` 確實在每一條 summary 行執行，shallow `[git:]` 確實降為 warning；DocAgent 次序在 spec 已明標為本案設計。

最嚴重 severity：blocker
