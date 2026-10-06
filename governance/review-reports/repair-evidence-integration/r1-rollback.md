severity: major

accept-repro-F1  
severity: major  
blocking: 是  
觀察：設計明定固定樹捕獲失敗時不得借用額外測試證據，但驗收矩陣只有穩定與 ABA 變動案例，沒有令 `write-tree` 明確失敗並驗證退路的案例。  
獨立判準：會改變守衛採信證據範圍的失敗分支，必須以可控制的失敗注入驗證「額外 route 證據為空、正式程式退路不變」，並涵蓋普通及最佳化執行。  
具體場景：索引含未合併項目或 Git reader 被注入錯誤，`write-tree` 失敗；實作若仍從活動索引建立 `staged_route_tests`，可能以未固定的測試寫回證據放行違規，而目前列出的 ABA 測試仍全部通過。  
引句:「捕獲失敗不借額外證據，保留原正式程式檢查退路，不修改安家集合、每提交規則或fail-open政策。」  
file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`  
佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:966`

accept-repro-F2  
severity: major  
blocking: 是  
觀察：範圍宣告改動清單、設定、圖譜與分類都讀同一固定樹，但列出的注入案例及 S1 只驗測試 route；沒有分別擾動設定、安家圖譜或分類輸入，不能驗出只固定部分 reader 的實作。  
獨立判準：凡能獨立改變最終 rc 的資料面，都須在捕獲後被改動再還原，並斷言結果及實際讀取來源仍來自捕獲樹。  
具體場景：捕獲時 `.lumos/config.json` 為 `gate=on` 且某檔無家；檢查途中活動索引短暫改成 `gate=off` 再還原。若設定 helper 仍讀活動索引，會錯誤回傳 rc0；只擾動 route 的 ABA 測試無法抓到。圖譜 ownership 或提交分類仍讀活動索引時亦同。  
引句:「可捕獲時，改動清單、設定、圖譜與分類讀同一樹；測試route不再從會動的索引借證。」  
file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`  
佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:943`

attribution-F3  
severity: major  
blocking: 是  
觀察：主線既有缺陷的判定只明列原報告、函式雜湊與「重現」，S5 也只指向版本、同一案例及函式比較收據；沒有明定同一案例必須在主線與審材兩個固定版本各自執行，且證明實際載入版本及環境可比。  
獨立判準：只有兩端同題、同預期、可比環境的實際觀測，並具實際載入來源證據，才能把缺陷歸為「主線已存在」；函式內容相同只能證明該函式未改，不能證明完整可達行為相同。  
具體場景：被比較函式在 `c4f2b0cf` 與 `95735eff` 雜湊相同，但 957 的呼叫者或設定新增了會觸發缺陷的輸入。若只在 957 重現再用函式同雜湊歸因，會把本批新增缺陷錯記成主線既有缺陷。  
引句:「新發現但主線已存在的缺陷，以真實原報告、版本函式雜湊與重現寫Issue。」  
file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:35`  
佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:1040`

rollback-F4  
severity: minor  
blocking: 否  
觀察：回退段描述要撤哪些內容，但沒有固定回退基線、回退後測試集合或驗收結果；同時要求刪除 ABA 測試及 fixture 適配，使「保留先前功能」缺乏可重現證明。  
獨立判準：回退應指定可唯一定位的功能提交／差異範圍，並列出回退後仍須通過的既有測試與已知缺口重現入口。  
具體場景：fixture 適配同時服務既有 worktree 競態測試；回退時按文字整段移除，ABA 測試亦被刪除，CI 可以綠燈，但舊競態覆蓋已被一併移除。  
引句:「還原本次cmd_home_check固定樹修改，移除新ABA測試及fixture適配，保留先前功能與所有真實紅綠紀錄。」  
file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:57`

閱讀帳：

- `lumos-design-loop/SKILL.md`：79 行。
- `r1-materials.md`：1185 個唯一行；因首次輸出截斷補讀 20 行，計費 1205 行。
- 唯一真 spec：67 行。
- 凍結副本：67 行。
- `wc`、輸出標籤及截斷提示：保守計 9 行。
- 總計：保守計 1427 行，未超過 1800 行。

未驗邊界：未執行任何外部代碼或測試，未讀其他席／前輪報告、作者因果結論或實驗收據；現行函式僅作待實作設計的資料流對照。版本簡稱與 archive 無法自行還原 commit 血緣已在 spec 補正，本席未重報；prose-lint 詞表項亦未列 finding。

最高級：major；blocking：3。