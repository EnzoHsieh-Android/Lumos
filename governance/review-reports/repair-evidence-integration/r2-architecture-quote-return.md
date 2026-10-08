severity: clean

四問覆蓋：

1. 分層與依賴方向：對齊。固定樹只供 `cmd_home_check` 的額外測試路由證據；正式改動清單、設定、圖譜、測試名判定與 fail-open 仍走既有 index 路徑。設計沿用 `_nodehome_list`、`_nodehome_reader`、`_nodehome_side` 的 Git 讀取層，未要求跨層直呼。  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`  
   file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:787`

引句:「索引模式先用write-tree捕獲固定樹，僅用於額外測試路由證據。」

引句:「正式程式的改動清單、設定、圖譜、測試名判定與fail-open仍沿用原index路徑，不宣稱整個home檢查已取得單一原子版本。」

引句:「Git官方write-tree把完整可合併索引寫成不可變樹，沿用現有Git reader而不自建快照引擎」

2. 命名與錯誤處理：設計層對齊。捕獲失敗只撤回額外證據，不改既有正式 fail-open；索引版本變動仍沿用清空 `staged_route_tests` 的責任邊界。尚無實作，故新 helper 的實際名稱、回傳契約及訊息格式未驗。  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`  
   file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:937`  
   file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:988`

引句:「結尾若索引讀不到或版本不同，撤回額外證據；捕獲失敗不借額外證據。」

引句:「當捕獲失敗、來源設定或宣告或模式途中改回、工作樹變動時，額外測試路由應保守撤回且不更改正式程式退路及逐提交核對。」

3. 第二種做法：未見。索引固定化明訂使用 Git `write-tree` 並沿用現有 Git reader，沒有另建快照引擎；四份流程計劃均接回既有共用範本 §3.1、既有 group/finding ID 與同一案例格式，未另造 CLI、欄位或審查閘。bundle/archive 是來源保存媒介，仍以 tree/blob 與可取回 commit 分責核對，未形成第二套行為裁判。  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:26`  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:33`  
   file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:1025`

引句:「Git官方write-tree把完整可合併索引寫成不可變樹，沿用現有Git reader而不自建快照引擎」

引句:「共用範本的留來源指引要求在squash/rebase前保存仍可取回的兩端完整來源，選既有受保護ref或bundle/archive」

引句:「bundle須實際還原commit/tree及必要blob，普通來源壓縮包只能核對tree/blob，提交血緣需另有可取回的完整commit入口。」

4. 落點：語意上對齊。修補證據與來源留存歸 `Systems/每輪修補差異派工`；home-check 固定樹改動歸 `Systems/每支檔有家`；測試假綠控制歸 `Systems/測試假綠形態`。材料未附三篇 Systems 節點全文、目前行數及 `about_code` 清單，因此是否已過大、實作檔家屬是否完整屬未驗邊界，不能反推為缺陷。  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:10`

引句:「落點 Systems/每輪修補差異派工、Systems/每支檔有家、Systems/測試假綠形態。」

未驗邊界：

- 尚無實作 diff，不能驗證實作者是否真的重用現有 reader，或另造重複 helper。
- `_nodehome_route_tests`、`_nodehome_side`、`_vendored_state` 只見呼叫位置，未判其內部行為。
- 未執行測試；既有已綠筆記及收據均未被當成行為已驗。

實際閱讀帳：

- `lumos-design-loop/SKILL.md`：79 行。
- 真 spec：76 行。
- r2-materials：1194 行。
- 凍結副本：76 行，經 `cmp` 確認與真 spec 完全相同，未重複讀正文。
- 計數、相同性與定點搜尋輸出：35 行。
- 實際納入閱讀總量：1384 行。
- 未讀前輪報告、其他席報告或作者修復因果結論。

最高級：clean  
blocking 數：0