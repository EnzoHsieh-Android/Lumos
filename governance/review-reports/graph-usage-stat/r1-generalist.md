# graph-usage-stat r1 通才席(light 單席)

**L-1**|blocker|blocking:是——被審材料缺可執行機械定義本體
引句:「M2 切片「席報告引圖譜率」先行:讀側純觀測掛 gov --stats,d8 前後兩桶分層」
grep 正規化/NFC/stem/型別資料夾路徑於被審材料全 0 命中;r1-intake 宣稱「已修真檔」的內容從未落地(後經主對話驗證:python replace 括號全半形不合靜默沒中,切片章節本身缺席)。且「d8」跨節點有三個互斥候選(design-loop 08-29/autonomous-iteration-loop 08-30/節點還原SOP 08-24),單看材料無法錨定。

**L-2**|major|blocking:是——806 筆 ts 實測 100% 帶 +08:00,naive datetime 比對直接 TypeError。
**L-3**|major|blocking:否——d8 後桶僅 22 筆(<2 天),無小樣本但書。
**L-4**|blocker|blocking:是——實帳第 446 筆 report_path 指向 repo 外權限 600 私有逐字稿 .jsonl;掃描器無值域守衛會讀錯或炸。
**L-5**|major|blocking:是——單檔 205 個 [[...]](外家席貼注入樣板)可主導平均;現行 444 筆中位數 0、最大 7。
**L-6**|minor:「席報告」無分母判準;--stats 既有兩種口徑,新分母須自標。1 筆帳列缺 auditor 去留未交代。
**L-7**|minor:查過沒事——金流/不可逆/併發回滾與現況相符(抑噪)。
**L-8**|major|blocking:是——實務隱患缺「讀取穩定性/可攜性」類;單檔讀失敗炸不炸整支未定義(severity-check 有 nofile/shafail 慣例可循)。

severity: blocker
