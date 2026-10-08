severity: major

design3-logic-F1  
severity: major  
blocking: 是

引句:「額外路由應只用捕獲樹及起點作證；各來源分別驗合法，不借途中內容。」

暫存區的固定樹先由 `write-tree` 捕獲，但「哪些路徑有改動」隨後仍從活動索引計算。若另一程序在這個窗口暫時修改一支合法測試、讓差異讀取看見它，再於結尾前還原，該測試會進入 `changed_paths`；捕獲樹可提供合法內容，結尾樹又與原樹相同，因此額外寫回路由不會被撤回。結果是一支在捕獲樹相對起點其實未改動的測試，仍能成為放行證據，直接違反 S1。

現有 ABA 測試是在 `_nodehome_route_tests` 開始後才注入索引變動，沒有覆蓋 `write-tree` 與 `_nodehome_changes` 之間的窗口。

修補要求：正式裁判若仍需讀活動索引，可以保留；但額外路由必須另以 `HEAD → index_tree` 算自己的固定改動集合，不能共用活動索引算出的 `changed_paths`，並新增此窗口的 ABA 測試。

file: `/tmp/lumos-seat-materials/repair-evidence-integration-r3/plans.md:41`  
file: `scripts/lumos:29994`  
file: `scripts/lumos:29996`  
file: `scripts/lumos:30050`  
file: `scripts/lumos:29479`  
file: `scripts/lumos:30068`  
file: `scripts/test_lumos.py:49171`

design3-logic-F2  
severity: major  
blocking: 是

引句:「額外路由的測試內容、設定、安家宣告與普通檔案模式均從捕獲樹核對，並可讀既有起點；兩個來源分別驗合法後聯集」

實作沒有讓兩個來源各用自己的設定驗合法。它只從捕獲樹讀一次 `.lumos/config.json` 與 vendored 排除集，接著把同一組 `cfg`、`skip` 同時套在捕獲樹及既有起點。

具體反例：起點設定排除某測試；終點取消排除，但把該測試刪除或改成 symlink。終點本身因檔案非法不能作證，起點本身則因當時設定排除也不能作證；目前程式卻會用終點較寬鬆的設定驗起點普通檔，錯誤形成合法聯集。反方向也可能保守誤拒。

現有 `input_snapshots` 只測「讀取途中暫時換設定又還原」，沒有測起點與捕獲樹本來就具有不同設定的案例。

修補要求：捕獲樹與起點各自讀取並套用自己的 config、vendored state、檔案模式與安家宣告，先分別產生合法集合，再聯集。

file: `/tmp/lumos-seat-materials/repair-evidence-integration-r3/plans.md:33`  
file: `scripts/lumos:29494`  
file: `scripts/lumos:29498`  
file: `scripts/lumos:29499`  
file: `scripts/lumos:29500`  
file: `scripts/lumos:29501`  
file: `scripts/test_lumos.py:49265`

三類風險逐類結論：

- 錯誤放行：未通過。F1 可把未真正變動的測試借為寫回證據；F2 可把兩份各自非法的來源拼成合法證據。
- 錯誤拒收／可用性：設計允許競態時保守撤回並要求重跑，方向合理；但 F2 共用終點設定也會造成非預期拒收，應隨同修補。
- 來源取回、版本綁定與回退：未發現新的 blocking。增量 bundle 的實檔雜湊與收據一致；收據記錄空庫拒收、取得前置閉包後 `bundle verify` 成功、還原到指定 tree 和 blob。計劃也明確要求最後功能 HEAD 重新綁定，不把 `95735eff…` 當最終通過版本。

逐篇覆蓋：

- `修補驗證與來源留存整合_計劃`：F1、F2。
- `根因修復與行為保留配對_計劃`：已讀，未發現新增 blocking 或 minor。
- `修復與重構分段驗證_計劃`：已讀，分段版本、不可分離及整理提交後重驗邏輯一致。
- `同類提醒與根因歸因分開_計劃`：已讀，分類、根因與修補因果沒有互相代填。
- `跑滿回顧沿用修補因果證據_計劃`：已讀，`fix-induced`、`other`、`attribution-undetermined`、`regression_set` 的引用均存在，未發現新增 finding。

固定合約以實際查詢為準：五個相關 Systems 節點中，只有 `Systems/測試假綠形態` 登記一條 ★INVARIANT★，要求翻紅釘具備「現場成立」前置斷言；本案測試確有注入是否執行的前置檢查。其餘四節點沒有登記固定合約。

查證限制：

- 目前唯讀環境沒有可寫暫存目錄，指定測試子集啟動即因 `No usable temporary directory` 中止，因此未把歷史綠燈當成本輪實跑結果。
- 派工限定的 Git 工作目錄不存在，無法在本輪用 `git cat-file` 重驗四個短 SHA；來源收據中的具體 Git 命令及旗標曾以 rc0 執行，但屬既有收據。
- 沒有讀任何前輪席報告；搜尋曾帶出少量非目標審計檔的命中摘要，未開啟或採用其結論。
- 未驗 Windows；計劃本身亦明列暫時排除。
- 未改 repo，未執行任何提交或其他狀態變更。

實際閱讀量約 4,100 行顯示輸出，包含 AGENTS 97、CLAUDE 101、兩份 skill 173、指令手冊29、五篇計劃348及重讀、定點程式／測試、收據與搜尋輸出；已超過派工所述1800行，因此沒有再擴張到全套測試、18席報告或非必要程式區域。最高等級為 major，blocking 共2條。