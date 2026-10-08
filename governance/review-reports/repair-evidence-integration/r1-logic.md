severity: major

logic-F1

severity: major

blocking: 是

觀察：固定樹不變量尚未涵蓋測試名稱分類器。現行 `_nodehome_tag_judge` 先呼叫 `_platform_test_index(repo_root)`，後者以 `load_platforms(repo_root)` 從工作樹載入設定及發現測試；這條路徑並未使用捕獲的 tree。若實作僅把既有 `tip=None` 改傳 tree OID，`_ns_tr_guard` 又會拿 HEAD commit 與 tree OID 比較，落入無 judge 的既有退路，而非讀取固定樹。這不是把「固定樹尚未實作」當現況問題，而是待實作方案沒有定義如何讓這個既有分類入口滿足其固定樹承諾。

file: `/tmp/lumos-future-repair-regression-research/scripts/lumos:14474`

file: `/tmp/lumos-future-repair-regression-research/scripts/lumos:29042`

file: `/tmp/lumos-future-repair-regression-research/scripts/lumos:29043`

獨立判準：凡會影響安家／寫回是否放行的設定、測試存在性與分類結果，都必須來自同一不可變版本；若既有 API 無法讀 tree，spec 必須明定新的 snapshot-aware 讀法或安全退路，並以針對該入口的測試固定行為。只固定 `_nodehome_list`、reader 與 route 檔案內容，不能證明整個裁判只用了固定樹。

具體場景：捕獲的 staged tree 內含設定 P1，Systems 筆記只新增 `[test:t_x]`；未暫存工作樹在檢查期間暫時切成設定 P2／另一組測試，再還原。圖譜與 route 檔案來自固定樹，但 test-name judge 曾從 P2 判定 `t_x`；index tree 始終沒變，因此結尾 tree 比較不會撤回。home check 最終可能依未提交、瞬時的工作樹資料承認寫回或改變分類。現有 S1 ABA 測試只點名 route，既有 worktree fixture又被要求改指固定樹，兩者都未明確命中 `_platform_test_index` 這條旁路。

引句:「可捕獲時，改動清單、設定、圖譜與分類讀同一樹；測試route不再從會動的索引借證。」

file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`

解除 blocking 所需：spec 明定 test-name judge 如何從捕獲 tree 建立平台設定與測試索引；無法判定時不得把只換測試綁定當成有效寫回；另加入工作樹 ABA 與 staged-config 分歧案例，普通及最佳化模式都驗。

覆蓋與未驗邊界：

- 已覆蓋五份計劃、固定樹的 list／reader／changes／home-check、vendored 分類、route 與 test-name judge。
- archive／bundle 依指定材料已區分 tree/blob 與 commit 血緣，未重報前掃已補正問題。
- 未執行測試、Git 實驗、bundle 冷還原或外部程式；綠色筆記及既有驗證紀錄均未當成行為已驗。
- 現行函式只用來辨認待實作方案必須封住的入口，未宣稱固定樹已存在。

實際閱讀帳：技能規則與行數輸出 80 行；指定檔案盤點 4 行；唯一 spec 67 行；凍結副本 67 行；完整材料 1185 行；定位輸出 21 行；必要函式定點上下文 371 行；合計 1795 行。定位輸出中有 18 行僅為路徑與 `def` 命中列，未開啟、未採用其他席或前輪報告正文。

最高級：major；blocking：1。