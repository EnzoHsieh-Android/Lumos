# R1 收貨、重現與處置

preflight-4: ran

七席fresh xhigh原始報告收齊後才改碼。高風險五個finder＋架構＋資安；同模型家族、沒有外家交叉背書。原報5宣告皆major（logic1/resources2/rollback2），其中一條規則判準不成立；另外編排者機械補充一條，不冒稱獨立席。四個不同根因：測試盲點、完整樹快取保留、工作樹競態、分組失敗跨提交。

| ID | 觀察 / 判準 | 處置 |
| correctness-F1 | HIT：只核rc會被其他擋項代答；正式前置現場合約也成立 | folded：索引/版本變更、宣告家、啟動/排除/連結/首行前置與特定拒收種類持續斷言 |
| rollback-F1 | HIT：端點-onlymutant原三案例普通/-O6/0；修正同壞版本36通過6失敗 | folded：移除端點污染，多次改名混合提交只有中間測試；與correctness-F1同一測試可信度根因，不當兩個產品缺陷 |
| rmax-resources-F1 | HIT：4/12提交全樹容器peak5/13，单次O(KP)保留，非跨呼叫洩漏或RSS实測 | folded：兩版LRU父版先讀、候選逐家交集；實際容器生命週期控制先紅後綠 |
| rmax-resources-F2 | HIT：借舊reader新消費路徑在讀取前换磁碟雙向誤放/誤擋；辯方agree | folded：僅新增借用首行固定Git版本；staged/diff、普通/-O、合法/非法8控制先紅後綠 |
| operator-F1 | HIT：分組故障current0/baseline1且正常current1，故障入口原2控制紅；辯方agree | folded：明確分開staged與diff故障；故障不添加不確定測試證據，保留原正式程式退路 |
| rollback-F2 | MISS：有来源/回歸資訊，v1.0未規定WHY/PITFALL一律方括號；lint三篇实跑0，帳指紋未變 | refuted：乾淨field-defender精確程式證據，原major報告保留，不將新增更嚴規則當修復 |

correctness/rollback兩席同一oracle盲點直接折；resources單席低共識兩條與operator由乾淨辯方實跑agree保留major。field-defender在原版本定點證明rollback-F2判準不成立，file/line與實跑界線原報完整保留；不因換模型就丟發現。

原報normalize/refcheck/seat-check接收收據保留；logic原跨diff加號引句錨不到，交乾淨格式退回席讀真材料重送，finding/major/判準不改，quote/ref/seat全部0，raw未覆寫。其餘positive引句全錨，clean零條quote rc2是N/A不假稱通過。seat-check幾席未逐路徑列材料的unreported提示原樣保留，不冒稱它們逐檔已讀；派工內嵌固定鏡頭及source/graph材料，下一輪要求顯式列出材料。

原整合4f全套10921/1/0、CLI/test来源未變；失敗是角色計算逾時，單獨同版重跑7/0/0，保留失敗，不稱原全套綠、不斷言一定是並行負載造成。本次修補247/0/0是在N獨立root固定source；相關子集、再整合及新席回歸另留實際收據。第一次red缺json匯入、第一次green的rename前置查舊路徑錯誤都保留原收據，沒有列為產品缺陷／真翻紅。

修復摘要：不改快照拒收H生產修法；N借用路由只新增from_git預設關閉參數、沿同分類器的局部side、兩版快取及group_fallback語意，不擴強制安家／啟動／foreign-ref或整閘fail-open政策。程式碼類5ID合為4根因，沒有minor承認風險代替修復。真實輪數改善仍以計劃REVISIT收五份实际收據，未宣稱已下降。

補充：第一次修復在原nodehome子集543/1被既有架構釘攔住——evaluate不能間接建Git reader。該釘原樣保持，提交索引證據移回cmd入口、只傳staged_route_tests，推送分組故障不提供集合；中間group_fallback版撤掉。架構專項11/0、新控制247/0先驗，整組相關重跑正在完成。這是R1修正自產回歸被機械守衛接住，不把它算成原七席已看到的finding或另洗迴圈編號。
