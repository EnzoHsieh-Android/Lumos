severity: major

design3-rollback-F1

severity: major  
blocking: 是

引句:「兩個來源分別驗合法後聯集」

捕獲樹與起點沒有真正「分別」套用各自設定。實作只從捕獲樹讀一次 `cfg`／`skip`，接著拿同一份設定判斷捕獲樹與起點；若兩端的 ignore、測試分類或 vendored 狀態不同，合法起點可能被誤撤回，違反 S1/S2。

佐證 file: `scripts/lumos:29494`、`scripts/lumos:29498`、`scripts/lumos:29501`

修補驗收：起點與捕獲樹須各自建立 `cfg`、`skip`、reader，再聯集各自合法的結果；新增「起點合法、終點改成 ignore」及反向案例，普通與 `-O` 都驗。

design3-rollback-F2

severity: major  
blocking: 是

引句:「另在隔離副本重放封存中的ABA及input_snapshots，預期重新翻紅」

回退驗證沒有定義如何讓封存測試載入「已回退的 CLI」。測試的 `GRAPHCTL` 固定指向測試檔旁的 `lumos`；直接還原並執行封存版本，實際載入的是修補後 CLI，預期會綠而不是紅。計劃也未列出回退的確切 helper、呼叫點或可套用差異，無法可靠重放。

佐證 file: `scripts/test_lumos.py:30`、`scripts/test_lumos.py:49151`、`scripts/test_lumos.py:49260`、`scripts/lumos:29470`、`scripts/lumos:30067`

修補驗收：明定回退版本指紋與精確符號；建立可重放入口，把封存測試來源和已回退 CLI 明確分離並記錄兩者指紋，先證實載入回退 CLI，再要求 ABA／input snapshots 翻紅。

design3-rollback-F3

severity: major  
blocking: 是

引句:「若遠端入口改寫或前置不可得，來源驗收保持未判定，須先改用可取得的完整封存」

目前增量 bundle 不是自足來源，依賴可改寫的遠端 `main` 提供 `c4f2b0cf…` 完整閉包。若在 squash/rebase 後才發現遠端前置消失，屆時可能已無來源可建立「完整封存」；把狀態改成未判定不能恢復已失去的來源。

佐證 file: `governance/review-reports/code-convergence-input-guards/r3-validation/reviewed-957-incremental-cold.json:63`、`governance/review-reports/code-convergence-input-guards/r3-validation/remote-prerequisite-cold.json:127`

修補驗收：在任何歷史改寫前，把前置閉包放入不可變、受保護且實際驗證可取得的 ref，或保存自足封存；再從空物件庫還原「前置＋增量＋最終重新綁定版本」，成功後才准改寫。

三類風險逐類結論：

- 回退與遷移：未通過，F2 blocking。
- 來源取回與版本綁定：未通過，F3 blocking；bundle 指紋本身吻合，但長期前置來源未被固定。
- 可執行性、內部一致性與未定義引用：未通過，F1 blocking。五篇計劃的 `[[節點]]` 均存在；六個測試名及 `lumos loop retro-stats --json/--repo` 入口存在。實際固定合約中，三個落點只有 `Systems/測試假綠形態` 登記「翻紅釘須有現場前置斷言」，相關測試確有注入／還原前置檢查；另外兩個落點沒有登記固定合約。

未驗範圍：

- 指定 git 工作目錄不存在，因此未重新執行任何 git 指令；Git 旗標只核對了既有冷還原收據，未確認本機當下版本。
- 未執行會在其他臨時目錄進行 git 操作的測試。
- 未驗 Windows、遠端 ref 保護設定、未來最終 HEAD 重新綁定。
- 實際閱讀約 2,700 行（包含重讀、搜尋命中與收據，不只計 348 行審稿），超過 1,800 行上限；因此未宣稱完成全 repo 的全面性排除。未主動開啟前輪席報，但一次廣域搜尋回傳了前輪報告命中片段；上述 findings 未採用那些結論。

全程未修改 repo，未執行 git 寫入或狀態操作。