severity: major

repro-F1

severity: major

blocking: 是

觀察：同一個 ABA 場景有互斥驗收結果。S1 與範圍第 1、2 點要求暫存區改動後還原時，額外路由仍依捕獲樹判定；S2 卻要求設定、宣告或模式「途中改回」時撤回額外證據。實作者無法同時滿足兩者。

獨立判準：同一時間序列只能有一個預期結果；若某類輸入例外地必須撤回，spec 必須明訂其與一般 index ABA 不同的原因及優先順序。

具體場景：捕獲時宣告合法；檢查途中改成非法再逐字還原。依 S1 應使用合法捕獲樹而通過；依 S2 又必須撤回額外證據，可能改變最終裁定。

引句:「當捕獲失敗、來源設定或宣告或模式途中改回、工作樹變動時，額外測試路由應保守撤回且不更改正式程式退路及逐提交核對。」

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-snapshot.md:31`

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-snapshot.md:39`

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-snapshot.md:40`

acceptance-F2

severity: major

blocking: 是

觀察：S6–S9 的 manual 綁定主要核對子計劃及既有實驗，沒有要求在最終版本直接核對真正承載行為的共用範本、手冊與速查來源。這會讓「計劃寫對、舊實驗已綠，但交付來源漏改」仍可被判通過。

獨立判準：文字指引功能的驗收必須綁最終提交中的權威來源，逐項核對實際文字或重放使用情境；已綠計劃與實驗只能當歷史證據，不能替代最終來源驗收。

具體場景：最終共用範本漏掉「沒有中間版本就未判定」，但子計劃與先前兩段實驗仍完整存在；照目前 S7 manual 可核對成功，實際派工卻會產生錯誤歸因。

引句:「manual:核對修復與重構分段驗證計劃的前後版本與兩段實驗」

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-snapshot.md:46`

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-snapshot.md:49`

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:690`

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:1025`

rollback-F3

severity: major

blocking: 是

觀察：回退後保留新測試且明訂 ABA、input_snapshots 應重新翻紅，但沒有定義 expected-failure、隔離套件或其他可讓回退版本通過標準推送閘的方式。現行專案規則會在推送前跑程式測試，因此此回退狀態本身不可正常交付。

獨立判準：可操作的回退版本必須通過既有交付閘；若刻意保留已知紅測試，必須明訂如何隔離、如何防止被誤列通過，以及哪一組命令構成回退成功收據。

具體場景：撤除固定樹 helper 後，`t_nodehome_optional_test_index_aba` 如預期失敗；推送前完整套件因該失敗擋下，操作者只能跳過閘或臨時改測試，兩者都不在設計內。

引句:「ABA及input_snapshots預期重新翻紅，不能列為交付通過。」

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-snapshot.md:66`

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:192`

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:202`

attribution-F4

severity: major

blocking: 是

觀察：S5 要區分「主線既有、本批新增、修補回歸」三類，但 manual 只綁主線起點與 957 審材；固定材料入口又明說最終版本必須另綁。這兩端只能證明缺陷是否已存在於主線，不能驗最終交付新增了什麼，也不能把混合區間中的退化歸因給某次修補。

獨立判準：本批新增必須以主線起點對最終 HEAD 的同案例證據判定；修補回歸必須另有修補前後固定版本及隔離因果證據。混入其他可達變更時只能記未判定。

具體場景：c4f2 與 957 同題皆通過，但 957 之後的最終 HEAD 才失敗；目前 S5 manual 仍可能判「非本批新增」。另一情況是 c4f2 通過、957 失敗但區間混入測試裁判與路由變更，兩端紅綠只能證明區間退化，不能證明是修補造成。

引句:「交付紀錄應區分主線既有缺陷、本批新增缺陷與有因果證據的修補回歸；主線既有缺陷仍有Issue入口。」

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-snapshot.md:43`

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-snapshot.md:72`

file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r2-materials.md:1053`

閱讀帳：`lumos-design-loop/SKILL.md` 79 行、真 spec 76 行、凍結副本 76 行、R2 materials 1194 行；補讀截斷區 51 行、`wc` 5 行及截斷提示 2 行。按請求範圍保守計 1483 行。未讀其他席、前輪報告或作者修復因果結論；未執行外部代碼。

覆蓋：S1–S10、回退、未判定／歸因、來源留存，以及材料所附現行函式與共用範本。行為執行結果未驗，本席不從既有綠筆記推導已通過。

最高級：major；blocking 數：4。