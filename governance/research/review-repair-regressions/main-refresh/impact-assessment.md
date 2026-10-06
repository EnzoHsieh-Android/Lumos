# 最新 main 對本次補強的影響

固定主線：b4637da0fb67a01a476ac672d564b4a918d753cd。整合提交：beb73ba22d8f3e139dabab6dc64158038afa7d1c。

- 主線新增 summary-line、updated-sync，及連結標題的待定詞誤報修正。整合保留 main 所有變動函式與新增測試的完整函式內容，見 source-integration.json；這是內容對照，不代替動態測試。
- 三份本次改動的技能來源，cc032633 到新 main 的 blob 相同。main 沒有改本次所依賴的 fix-check 與 regression_set 語意；此負面結論由 f2_design_rollback 以原始問題獨立唯讀查證。
- 對這次補強的實際影響：改摘要可用新 summary-line 命令，避免手改欄位；doctor 會多日期落後提醒；連結標題誤報減少。沒有因此得到自動回歸因果證明。
- 新查證修正兩處：兩份base一致可能只是共用同一錯值，需核對凍結材料真正的版本來源，不能就此歸因；none 只涵蓋本輪已報 findings，不代表未發現區域沒有回歸。
- 三本帳 append-only 合併：基底+分支新增+主線新增，逐行JSON與occurrence multiset核對；沒有刪行、改行或捏造通過紀錄，見 ledger-merge.json。
- 分支仍攜帶先前兩項未併入main的修正（已宣告測試家寫回、快照拒收）；本次要重驗其相關子集，不能因只修改手冊就忽略這些整合風險。

本次不清理全圖舊提醒、不廣泛執行updated-sync、不更新全域技能安裝，也不開PR。
