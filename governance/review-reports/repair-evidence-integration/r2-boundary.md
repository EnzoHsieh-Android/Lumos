severity: major

boundary-F1

severity: major

blocking: 是

觀察：驗收條款要求「工作樹變動」時撤回額外證據，但設計只定義捕獲及前後比較索引；現行補助 reader 在 `from_git=True` 時刻意不讀工作樹，結尾也只比較索引。規格沒有工作樹版本快照、變動偵測或撤回入口，因此照字面實作無法兌現 S2。

獨立判準：每個會使安全證據失效的輸入變動，都必須有可觀測版本、明確比較點及 fail-closed 處置；驗收條款不能要求現有資料流刻意忽略、且設計未另行捕獲的狀態。

具體場景：索引保持不變，`write-tree` 捕獲有效測試及安家宣告；檢查途中另一程序只修改工作樹檔案。補助 reader 仍從捕獲樹取證，末尾索引比較也相同，因此額外路由不會撤回；這直接違反 S2。若為滿足 S2 改回讀工作樹，又違反額外證據固定讀樹的核心邊界。

引句:「當捕獲失敗、來源設定或宣告或模式途中改回、工作樹變動時，額外測試路由應保守撤回且不更改正式程式退路及逐提交核對。」

佐證：

- file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:40`
- file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`
- file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:829`
- file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:988`

覆蓋與未驗邊界：

- `write-tree` 捕獲失敗：規格已要求不借額外證據並保留正式 index 路徑；僅判讀設計，未把待實作測試視為已驗。
- 索引 ABA、設定／宣告／模式 ABA：已檢查固定樹來源與末尾索引撤回要求，除上述工作樹矛盾外未見獨立缺陷。
- 特殊路徑：現行清單採 NUL 分隔，普通檔模式與 symlink/gitlink 有區分；NFC 碰撞及 Windows 已明列不在本次修復範圍，未另列 finding。
- 相容性：正式改動清單、設定、圖譜、測試名及 fail-open 保持原 index 路徑；未推導其行為已通過。
- 來源留存：已覆核 bundle 前置來源、archive 的 blob/mode/tree 重建要求；未執行還原實驗。

實際閱讀帳：

- `lumos-design-loop/SKILL.md`：79 行。
- `wc -l` 輸出：5 行。
- 唯一真 spec：76 行。
- r2 凍結副本：76 行；與真 spec 逐行內容一致。
- `r2-materials.md`：1–400、401–800、801–1000、1001–1194；另因工具截斷補讀 130–180、490–600，重疊照實計入。
- 總計：1592 行，未超過 1800 行。

最高級：major；blocking 數：1。