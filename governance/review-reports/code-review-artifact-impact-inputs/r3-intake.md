# R3 收貨與修復處置

兩個正式唯讀席收齊後才修改來源，兩席原報告保持原樣。代理執行額度耗盡後改用新建唯讀 CLI 席，版本仍為 9a6e21e49a96677db09286a63beaf38f381a0104。normalize、quote、ref、seat 收貨紀錄見 r3-report-checks.json。

| ID | 重現 | 處置 | 根因與控制 |
| --- | --- | --- | --- |
| R3-COR-1 | HIT | folded | 兩席相同根因，固定帳檔與未知首行終點均可漏算舊角色；r3-repair-red.json 10過4敗。共用分類函式保留未知，補償只問新側是否已確認程式。r3-role-count-green.json 的17條包含固定帳檔、未知、確認程式三種真Git改名，各 backend=1，避免重複計數。 |
| R3-GRAPH-1 | HIT | folded | 家節點 verified_by 原為普通字串，改用 CLI 寫正式連結，r3-graph-link-fixed.json 真解析確認。屬文件缺陷，不增程式入口。 |
| ORCH-R3-UTF8 | HIT | folded | 編排者另行真Git重現，非第三個獨立席。保留原始檔名字節後直接輸出非ASCII JSON，造成UTF編碼無效。r3-nonutf8-red-rerun.json 1過7敗；最早缺os匯入的一次不是產品反例。以JSON標準escaping與既有顯示函式修復；測試核對原始位元組可逆、真事故仍命中、嚴格stdout可呈現。 |

三個ID、兩個程式根因與一個連結格式缺陷；均不接受、不降級、不反駁。第一個根因為前一輪邊界補償尚不完整；UTF8問題是前一輪改為保留原始檔名後引入，regression-set 記 ORCH-R3-UTF8。兩席一致且實際控制翻紅的程式條目不再派辯方。185條相關子集綠與另外17條角色控制有重疊，不能相加當作202條。

維持 standard 第三輪，不重置輪次，不冒稱零發現重審。須在最後提交上再跑修正關卡、處置與推送閘才可放行。原混合分支的Python證據歸屬問題與Windows不在此驗收範圍。
