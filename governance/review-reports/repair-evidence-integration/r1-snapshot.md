---
type: project
status: doing
created: 2026-10-07
updated: 2026-10-07
tags:
  - type/project
  - status/doing
  - risk/guards
lands_in:
  - Systems/每輪修補差異派工
  - Systems/每支檔有家
  - Systems/測試假綠形態
related:
  - "[[Projects/修復與重構分段驗證_計劃]]"
  - "[[Projects/同類提醒與根因歸因分開_計劃]]"
  - "[[Projects/根因修復與行為保留配對_計劃]]"
  - "[[Projects/跑滿回顧沿用修補因果證據_計劃]]"
---
# 修補驗證與來源留存整合_計劃

本案把既有修補／保留、分段修復、根因歸因與跑滿回顧指引一起交付。原先逐項小範圍人工驗證，不足以代表含CLI與測試裁判變更的整批低風險。本次整合按高風險審設計與代碼；不修改既有審查上限或閘，歷史通過只證原先範圍。

落點 Systems/每輪修補差異派工、Systems/每支檔有家、Systems/測試假綠形態。分兩個功能提交：先CLI輸入與測試路由修正及其脈絡，再審查流程來源及研究脈絡；兩個提交各有完整有效的相依筆記，不借錯誤about_code避開寫回檢查。審查帳與最後版本重新綁定。

PRIOR-ART: Git官方write-tree把完整可合併索引寫成不可變樹，沿用現有Git reader而不自建快照引擎；Git bundle官方允許增量封存，須明記前置提交並實驗驗證可還原。來源 https://git-scm.com/docs/git-write-tree 與 https://git-scm.com/docs/git-bundle ，2026-10-07實讀。
RETIRE-IF: home檢查入口已由正式設計統一接受固定樹且不再直接讀活動索引時，移除本入口重複捕獲；来源留存要求仍保留，直到正式版本庫已提供同等可取回與驗證的固定版本證據。

## 範圍

1. 索引模式先用write-tree捕獲固定樹。可捕獲時，改動清單、設定、圖譜與分類讀同一樹；測試route不再從會動的索引借證。結尾若索引讀不到或版本不同，撤回額外測試路由證據。捕獲失敗不借額外證據，保留原正式程式檢查退路，不修改安家集合、每提交規則或fail-open政策。
2. 新增同一fixture控制：穩定非法、索引非法途中換合法再還原、索引合法途中換非法再還原，普通及最佳化各驗。先確認真實index注入及還原，再獨立驗結果與借證，避免前置條件冒用預期結果。既有worktree競態fixture改指實際讀的固定樹，仍斷言注入確實執行。
3. 共用範本的留來源指引要求在squash/rebase前保存仍可取回的兩端完整來源，選既有受保護ref或bundle/archive；增量bundle明記前置commit與取回入口，核對指紋；bundle須實際還原commit/tree及必要blob，普通來源壓縮包只能核對tree/blob，提交血緣需另有可取回的完整commit入口。不把patch、版本字串或bundle verify單獨當完整來源已還原，不要求每輪產巨大完整歷史封存。
4. 1800行包括派工、操作規則與慣例指引，以及必讀差異及附錄。本輪既有超額席保留報告但不作受控行數試驗成功樣本；下次先核算後拆席，不追改舊結果。
5. 新發現但主線已存在的缺陷，以真實原報告、版本函式雜湊與重現寫Issue。既有缺陷仍然是缺陷，不算本批新增，也不記為上輪修補造成。未判定不變成none。

## 驗收條款

- [S1] 當暫存區途中改动又還原時，home檢查應只用捕獲的固定樹採信測試路由；非法來源仍拒收，合法來源仍通過。 [test:t_nodehome_optional_test_index_aba]
- [S2] 當索引持續變動、工作樹變動或每提交改動不同時，home檢查應維持撤回與版本隔離、逐提交核對的原行為。 [test:t_nodehome_optional_test_index_changed] [test:t_nodehome_optional_test_snapshot_race] [test:t_nodehome_optional_test_home_writeback]
- [S3] 當整理提交使舊版本不再在交付分支上時，範本應要求仍可取得完整來源，增量封存須記前置來源並冷還原核對。 [manual:核對完整與增量bundle的實驗收據及模板]
- [S4] 當派工材料含操作規則及附錄時，範本應計入1800行總量；超額席留證並把未驗範圍列未判定。 [manual:核對code-convergence-input-guards的r3-dispatch.json與原報告閱讀帳，入口見固定材料入口]
- [S5] 當判讀新發現時，交付紀錄應區分主線既有缺陷、本批新增缺陷與有因果證據的修補回歸；主線既有缺陷仍有Issue入口。 [manual:核對固定材料入口的主線與審材版本、同一案例及函式比較收據]

## 實務隱患

已排除:金流:本地審查與Git讀取不處理交易。
對外送出:提交main與CI依使用者2026-10-07授权；不開PR或寄消息。
已排除:不可逆:不刪歷史帳，不強制推送，來源先留存。
守衛面:誤借測試證據會誤放路由，按高風險review及紅綠控制；保留現有正式程式fallback。
併發:write-tree擷取完整索引，讀取期間其他程序改index不會改已存樹；結尾版本不同只撤回额外證據，不宣稱鎖住所有外部程序。
資源:每次staged最多捕獲及核對兩個樹，不建長駐快取。可能寫入Git物件，不改工作樹或索引的內容；Git原有清理負責不可達物件。
相容:Windows暫排除。source取得不代表行為測試通過；原始碼封存未包含外部部署或DB。

## 回退

還原本次cmd_home_check固定樹修改，移除新ABA測試及fixture適配，保留先前功能與所有真實紅綠紀錄；來源留存指引可獨立還原，不刪既有封存。撤回修復會恢復ABA缺口，須明記Issue不能假稱已安全。

REVISIT:2026-10-20 由每輪修補差異派工計劃的真實試行入口核對材料總量、來源可用性與新增缺陷歸因，按實際樣本數寫未判定，不以合成fixture宣稱收斂輪數下降。

## 固定材料入口

本案版本與交付觀測：修後審材為95735eff7f3e17c930d43eecde5dd9d7c4fe9eff，主線起點為c4f2b0cf479ccdff5823524c0b6954113819496b；r3-dispatch.json、r3-file-index.txt及原報告在governance/review-reports/code-convergence-input-guards/。所有18席收齊後才開始改交付來源。最終版本需另綁，不沿用957的結果當新碼全套通過。

來源留存實驗位於本次卷證的來源封存收據；整合時複製增量bundle及其前置/還原收據，而非超過100MB的完整歷史bundle。archive只指保存全部被驗版本tracked原始檔的完整壓縮包，須逐檔還原比對blob/mode並重建Git tree核對；不包含Git提交血緣，不把patch或只收幾支檔當完整archive。增量bundle需前置c4f2b0cf完整物件閉包；未取得前置時verify應拒收。

函式比較收據：governance/review-reports/code-convergence-input-guards/r3-validation/main-inherited-retro-case.json、main-inherited-test-functions.json。增量來源封存與實際冷還原收據為同目錄reviewed-957-incremental.bundle及reviewed-957-incremental-cold.json；完整bundle與來源壓縮包只保留試驗收據，不提交巨大原件，不把它們當交付可取回入口。
