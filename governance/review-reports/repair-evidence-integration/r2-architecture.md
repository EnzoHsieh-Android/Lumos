severity: clean

四問覆蓋：

1. 分層與依賴方向：對齊。固定樹只供 `cmd_home_check` 的額外測試路由證據；正式改動清單、設定、圖譜、測試名判定與 fail-open 仍走既有 index 路徑。設計沿用 `_nodehome_list`、`_nodehome_reader`、`_nodehome_side` 的 Git 讀取層，未要求跨層直呼。  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`  
   file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:787`

2. 命名與錯誤處理：設計層對齊。捕獲失敗只撤回額外證據，不改既有正式 fail-open；索引版本變動仍沿用清空 `staged_route_tests` 的責任邊界。尚無實作，故新 helper 的實際名稱、回傳契約及訊息格式未驗。  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`  
   file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:937`  
   file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:988`

3. 第二種做法：未見。索引固定化明訂使用 Git `write-tree` 並沿用現有 Git reader，沒有另建快照引擎；四份流程計劃均接回既有共用範本 §3.1、既有 group/finding ID 與同一案例格式，未另造 CLI、欄位或審查閘。bundle/archive 是來源保存媒介，仍以 tree/blob 與可取回 commit 分責核對，未形成第二套行為裁判。  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:26`  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:33`  
   file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:1025`

4. 落點：語意上對齊。修補證據與來源留存歸 `Systems/每輪修補差異派工`；home-check 固定樹改動歸 `Systems/每支檔有家`；測試假綠控制歸 `Systems/測試假綠形態`。材料未附三篇 Systems 節點全文、目前行數及 `about_code` 清單，因此是否已過大、實作檔家屬是否完整屬未驗邊界，不能反推為缺陷。  
   file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:10`

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