---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/每支檔有家
---
# 已宣告測試家的同次寫回_計劃


## 問題與最小範圍（實作前）

一批同時修程式及測試，將測試教訓寫回已宣告的測試家，卻被當成寫到無關節點，會逼人拆帳、刪掉教訓或重開審查。這是本批快照拒收修復的真實home拒收入口，不是用舊圖譜摘要推論缺功能。乾淨查證席及獨立Git fixture已確認：混合提交rc1，未改測試卻寫測試家rc1（應保留），只改測試rc0。source52與整合sourcecc929的兩個判定函式字節完全相同。

[[Projects/每支檔有家_計劃]] 原規則三只在改需要家的程式檔時啟動；[[Projects/只換測試綁定不算寫說明_計劃]] 的「不做:讓測試檔可以當家」是該案範圍，沒有相關decisions或硬合約。程式與歷史設計相符，不把舊案寫成違反規格。本案明定擴展：混合提交的路由核對，可採信已由有效家宣告、且同一提交實際改動的測試檔。測試仍免强制安家，純測試/純筆記提交的原規則三啟動條件不變，不擴成全圖整治。

落點 [[Systems/每支檔有家]]；測試來源由既有測試家及Verification留證。只修路由證明，不改安家要求、內容判定、測試識別、foreign-ref或忽略政策。

PRIOR-ART: Git官方diff文件區分索引/兩個提交/工作樹，--name-status給實際改動類型，-z避免特殊檔名被引用/拆錯；沿用既有提交快照與每提交g_paths，不讀目前工作樹來猜另一版本。責任仍用現有about_code而非CODEOWNERS副本。來源 https://git-scm.com/docs/git-diff ，2026-10-06實讀；同repo既有_nodehome_required/side/route_groups是借用入口，不新建解析器。
RETIRE-IF: 正式決策未來取消測試免安家、預設需要家的集合已覆蓋本案全部路由控制時，於_nodehome_required改動入口移除本案可驗路由視圖；在免安家仍成立時不以關掉守衛退場。

## 最小候選

在既有_nodehome_required新增預設關閉的include_tests選項，只供規則三計算「可核對的路由檔」。兩版各用同一個既有分類器形成較廣視圖：一般檔/程式副檔名或shebang、UTF8、忽略清單、自裝未修改檔等限制完全沿用，只讓測試排除可關閉。不另寫一份測試辨認或檔案模式算法。

原reqN/reqB、code_touched/g_code啟動條件、安家與S13b全部不改。只有S13寫回路由用同次g_paths與較廣視圖的交集；about_code前後版及每提交content_notes仍是原算法。這個較廣集合不是新的需要家集合，不得拿來要求測試有家，也不得跨提交借測試變更通行。刪除/改名仍查快照兩版；仍不把symlink、資料JSON、ignore檔作程式寫回證明。

## 驗收條款

- [S1] 當混合提交包含有效家宣告且同次改動的測試檔，路由檢查器應允許向該測試家寫回，提交索引與單提交diff、普通與最佳化皆成立。 [test:t_nodehome_optional_test_home_writeback]
- [S2] 當改動沒有碰測試檔或測試路徑已排除，路由檢查器應繼續拒收向其家寫回，不以symlink或資料JSON冒充測試程式。 [test:t_nodehome_optional_test_home_writeback]
- [S3] 當測試沒有宣告家，安家檢查器應保持測試免安家且不連帶放過新增需安家的程式檔。 [test:t_nodehome_optional_test_home_writeback] [test:t_nodehome_check_blocks_new_homeless_file] [test:t_nodehome_write_back_requires_every_changed_file_homed]
- [S4] 當測試改動與程式/節點改動分屬兩個提交，路由檢查器應依每提交實際g_paths判斷、不借整段範圍的測試變更通行。 [test:t_nodehome_optional_test_home_writeback] [test:t_nodehome_diff_route_per_commit]
- [S5] 當本案落地，內容判定與foreign-ref檢查器應保留純測試綁定豁免、只改測試的啟動條件、責任範圍及原有外來引用拒收。 [test:t_nodehome_test_tag_only_edit_is_not_write_back] [test:t_nodehome_diff_test_tag_only_edit_is_not_write_back] [test:t_nodehome_check_blocks_new_foreign_ref]

## 已有最小紅燈

新增方法24控制，舊碼16通過/8失敗/0略過。混合、刪測試、改名及單提交diff的正向路由各普通/-O翻紅；未碰測試、ignore、symlink、JSON、無家測試、純測試、跨提交及新增無家程式控制維持原結果。整支共用方法紅不代表通過的負控制退化。原JSON/log與source-bind留版；正式生產尚未改、反向故障未擴成壞報告格式。

## 回退

只移除include_tests可驗路由視圖與S13採用較廣視圖的局部分支，保留舊安家集合與舊測試辨認、內容/tag-only算法、每提交快照、全部原帳及測試。回退後混合提交測試家寫回會恢復原拒收，先確認本批快照修復如何保存測試教訓；不以skip、加錯誤about_code或刪除驗證帳補洞。

## 實務隱患

已排除:金流:只判本機版本與節點落點，不傳款或處理金額。
已排除:對外送出:本案判定不送網路请求，發布仍在外部流程。
已排除:不可逆:不遷移資料、不刪帳，只擴容有證據的路由核對。
守衛面:不能排除，路由集合可能誤放，設計審及正反控制過後才實作。
併發:只讀已捕獲的索引/提交快照，不用工作樹分類，保留原逐提交語意與模式判定。
效能與資源:候選兩版各多一次既有分類掃描；shebang沿用side快取、不新增程序或持久資源。以現有nodehome子集與單案例耗時收據確認，不宣稱零成本。
回退與相容:不擴成全部測試強制安家，不改只換測試綁定舊案的歷史範圍；Windows排除。

REVISIT:2026-10-20 在home check提交/推送入口核對五份真實混合提交寫回紀錄，逐份保存CLI/提交SHA、命令、前後rc與原診斷、實際改動路徑/家；同一案例重試不重複計數，fixture/人工注入不計真實數，不足五份就記實際數。測試通過不代表真實審查輪數下降。
