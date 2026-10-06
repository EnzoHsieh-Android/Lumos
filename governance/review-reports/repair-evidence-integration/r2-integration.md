severity: blocker

integration-F1

severity: blocker

blocking: 是

觀察：S1 與 S2 對同一個索引 ABA 情境給出相反結果。若捕獲時來源合法，途中改成非法再還原，S1 要依捕獲樹通過；S2 卻要求設定、宣告或模式「途中改回」時撤回額外證據。起終點 `write-tree` 又無法觀察已還原的中間狀態，因此 S2 不只與 S1 衝突，正式實作也無從判定。

獨立判準：同一受控輸入必須只有一個預期結果，而且驗收條件必須能由正式程式可觀察的狀態判定。

具體場景：先捕獲含合法安家宣告與測試的樹 T；另一程序暫時移除宣告，再恢復成 T。依 S1 應通過，依 S2 應撤回證據並可能擋下，普通與最佳化路徑會被迫選擇不同契約。

引句:「當暫存區途中改动又還原時，home檢查的額外測試路由應只用捕獲樹及起點作證；非法來源仍拒收，合法來源仍通過。」

引句:「當捕獲失敗、來源設定或宣告或模式途中改回、工作樹變動時，額外測試路由應保守撤回且不更改正式程式退路及逐提交核對。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:39`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:40`

integration-F2

severity: major

blocking: 是

觀察：計劃要求新增三類提交後再做高風險代碼審，但 S10 唯一具名的代碼審閘仍是新來源開始修改前、綁在 `95735eff…` 的既有 `code-convergence-input-guards` 閘；「最終範圍收據」不能替代最終 HEAD 的獨立代碼審處置帳。計劃沒有指定新的 loop、其凍結快照、或必須等於最終功能 HEAD 的 `reviewed` 指紋。

獨立判準：高風險提交的驗收證據必須包含直接綁定最終功能 HEAD 的代碼審處置紀錄；舊版本審查加測試收據不能證明後加程式碼已受審。

具體場景：保留舊 `95735eff…` 處置閘，接著加入測試裁判、固定樹路由及來源留存提交，再產生一次全範圍測試收據。S10 所列三項材料表面俱全，但新 helper 與提交相依關係沒有任何席位審過。

引句:「本次整合按高風險審設計與代碼；不修改既有審查上限或閘，歷史通過只證原先範圍。」

引句:「核對本案design處置閘、code-convergence-input-guards處置閘與最終範圍收據」

引句:「所有18席收齊後才開始改交付來源。最終版本需另綁，不沿用957的結果當新碼全套通過。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:22`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:50`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:72`

integration-F3

severity: major

blocking: 是

觀察：回退設計要求保留新增測試，同時明定 ABA 與 `input_snapshots` 應重新翻紅，卻沒有指定它們轉為非閘測試、預期失敗或只保留歷史紅燈收據。現行推送規則對程式變更會跑相關或全套測試，因此這個回退本身無法通過未修改的既有閘。

獨立判準：回退路徑必須能在現行提交與 CI 契約下交付；不得以永久活躍紅測試作為回退後狀態，除非明確定義不影響既有閘的保存方式。

具體場景：固定樹 helper 在正式使用後出現事故，需要依本節回退。既有三項守衛通過，但保留下來的 ABA 與 `input_snapshots` 測試按規格失敗，pre-push／CI 因此拒絕唯一允許的回退提交。

引句:「新ABA／設定宣告模式控制與紅綠紀錄保留為已知缺口。回退後跑t_nodehome_optional_test_home_writeback、t_nodehome_optional_test_snapshot_race、t_nodehome_optional_test_index_changed確認既有守衛；ABA及input_snapshots預期重新翻紅，不能列為交付通過。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:66`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:202`

integration-F4

severity: major

blocking: 是

觀察：交付只保留增量 bundle，並明知它依賴 `c4f2b0cf…` 的完整物件閉包；完整 bundle 與 archive 又只留試驗收據。計劃沒有為該前置閉包指定實際受保護 ref、可抓取位置或一併交付的基底封存。提交碼及冷還原收據只能證明曾經存在，不能讓接手者取得物件。

獨立判準：增量封存的每個 prerequisite 都必須有耐久、可操作的取回入口；否則不能聲稱兩端完整來源在 squash/rebase 後仍可還原。

具體場景：交付分支經 squash/rebase，暫存 clone 被清理，接手者只取得 `reviewed-957-incremental.bundle` 與 JSON 收據。其物件庫沒有 `c4f2b0cf…` 閉包，bundle 按計劃自行拒收，修前與修後來源均無法完成冷還原。

引句:「增量bundle需前置c4f2b0cf完整物件閉包；未取得前置時verify應拒收。」

引句:「完整bundle與來源壓縮包只保留試驗收據，不提交巨大原件，不把它們當交付可取回入口。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:74`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:76`

實際閱讀帳：

- `r2-materials.md`：1–1194，完整閱讀。
- `lumos-design-loop/SKILL.md`：1–79，完整閱讀。
- 唯一真 spec：1–76，完整閱讀並取行號。
- 凍結副本未重複展開；與真 spec 的 SHA-256 相同，`cmp_rc=0`。
- `wc`、雜湊／比較及兩次定點搜尋輸出：20 行。
- 合計實際顯示 1369 行，未超過 1800 行。

未驗邊界：未讀其他席或前輪報告，未開原收據、bundle 或作者因果結論；沒有把 `verified_by`、既有綠筆記或歷史通過當成行為已驗；未運行或安裝外部代碼，未修改任何檔案、帳號或 Git 狀態。

最高級：blocker  
blocking 數：4