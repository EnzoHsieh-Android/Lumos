severity: major

integration-F1

severity: major

blocking: 是

觀察：唯一真 spec 宣稱四項人工方案一起交付，但 S1–S5 僅驗固定樹、來源封存、1800 行限制與缺陷歸因；沒有驗收條款分別約束修補／保留配對、修補／重構分段、同類／根因分離、跑滿回顧因果證據。四份相關計劃雖各有條款，但不是本輪唯一真 spec，不能代替整合驗收。

獨立判準：高風險整合案聲稱交付的每項行為，都必須在唯一真 spec 有可驗證條款；否則照 spec 實作可漏交功能仍全數驗收通過。

具體場景：第二提交只加入來源留存與行數計算文字，漏掉修前 `repair/preserve` 選例和跑滿回顧的兩版因果核對。固定樹、bundle、行數與三類缺陷歸因仍可讓 S1–S5 全過，但四項方案並未完整交付。

引句:「本案把既有修補／保留、分段修復、根因歸因與跑滿回顧指引一起交付。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:22`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:548`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:614`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:691`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:757`

integration-F2

severity: major

blocking: 是

觀察：高風險升格只出現在敘述；S1–S5 沒要求既有卷證證明 design-loop 與 code-loop 都以 high 執行，也沒把兩個功能提交的完整 `base/head` 範圍列入驗收。「最後版本重新綁定」只能證版本欄位，不能單獨證 tier、材料或實際受審範圍。

獨立判準：宣稱高風險審查是交付合約；必須用現有派工、報告與版本綁定收據，驗明 high tier 且範圍覆蓋兩個功能提交。補此條款不需要修改任何既有閘。

具體場景：CLI 提交曾接受 high 審查，之後再加入四項人工方案提交；最終帳只更新到新 SHA，或完整版本僅走 standard code-loop。產品面的 S1–S5 仍可通過，但「整批高風險設計與代碼審」實際未完成。

引句:「本次整合按高風險審設計與代碼；不修改既有審查上限或閘，歷史通過只證原先範圍。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:22`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:37`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:63`

integration-F3

severity: major

blocking: 是

觀察：spec 把四項具有各自條款、RETIRE-IF、試行週期與獨立回退方式的人工方案，全部塞進同一個「審查流程來源及研究脈絡」功能提交。這與必讀規則「一個功能一個提交」衝突，也使四份計劃承諾的單項回退無法由提交邊界直接完成。

獨立判準：可以獨立驗收、退役或回退的功能應有獨立提交；若確實必須原子交付，spec 必須明定不可分依賴，並同步改寫各方案的獨立回退合約。

具體場景：同類／根因說明在試行後決定撤除，但其提交同時包含修補／保留配對、分段驗證和跑滿回顧。直接 revert 會誤刪其餘有效方案；手工挑除則失去原本宣稱的獨立提交、驗證與回退邊界。

引句:「分兩個功能提交：先CLI輸入與測試路由修正及其脈絡，再審查流程來源及研究脈絡。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:24`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:74`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:561`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:627`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:704`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:769`

覆蓋與未驗邊界：已覆蓋四項人工方案的整合合約、高風險升格、兩提交邊界、獨立回退及最終版本綁定。依指示未讀其他席／前輪報告，未執行程式、測試或外部代碼；固定樹仍按待實作設計判讀。未重報版本簡稱及 archive 還原 commit 問題，也未把既有綠筆記當行為已驗。

實際閱讀帳：`lumos-design-loop/SKILL.md` 79 行；真 spec 67 行；凍結副本 67 行；`r1-materials.md` 1185 行；行數盤點輸出 5 行；合計 1403 行。額外定點搜尋 0 行。

最高級：major；blocking：3。