# Android 單元測試標準實機演練(2026-11-01)——公開摘要

這是**去識別化之後改寫的摘要**,不是原樣證據:考場是公司私有的消費專案,這裡的類別名、套件名、欄位名換成代稱(`com.example.pos`、`CategoryVm`、`CategorySource`、`Category`、`seq`、`kind`、`name`;考場原有的子套件路徑攤平;剩下的 `com.example.pos.category`、`com.example.pos.drill` 兩層是代稱與演練新增的套件),公開檔不放本機路徑;報告裡的失敗文字也跟著改寫過。不放考場原始碼、代理寫的測試碼、預埋錯誤的 patch 與收據裡的原始碼快照。

`nextSeq`、`voidCategories`、`VoidCategory` 是代稱或演練時另開的資料來源介面裡的名字;測試方法名(`loadAll_…`、`nextSeq_…` 等)是寫測試的代理在演練中寫的,不是考場原有程式。照原樣保留、不算識別字的:一般英文的方法與屬性名(`loadAll`、`add`、`delete`、`addResult`、`deleteResult`、`error`、`loading`、`categories`)、結果包裝的型別名 `Resource`、Gradle 通用的變體名(`devDebug`)與開發用尾碼(`.dev`)、平板的市售型號。

能重跑的完整卷證(含 patch、收據、平板原始報告、重跑腳本、撤回的設計審那一輪)在考場 repo 的本機分支 `drill/android-unit-test-standard` 的 `drill-evidence/`(考場與測試在提交 8a774ca,卷證補到 c66c81b),只留在演練那台機器、不推。這份摘要不能單獨重跑 `lumos test-quality check`(缺原始碼快照),只供核對結果;收據不記收證工具版本,重跑要用工具鏈驗證紀錄寫的那一版。

| 檔 | 內容 |
|---|---|
| `requirements.md` | 給寫測試代理的需求書(去識別化) |
| `fault-matrix-agent-tests.json` | 代理寫的 80 支本機測試:原版、七個錯、還原各跑一次,每次紅了哪幾支 |
| `fault-matrix-bad-tests.json` | 刻意壞測試同樣的矩陣 |
| `fault-checks/M1.json`…`M7.json` | 七個錯各自的 `lumos test-quality check` 結果(fault_evidence 與目標);完整卷證對應 `receipts/M<n>-…/check.json` |
| `bad-test-checks/summary.json` | 五組核對的彙整(rc、fault_evidence) |
| `bad-test-checks/b<n>-M<m>.json` | 五組「壞測試 × 它聲稱要驗的那條需求的錯」的核對結果;完整卷證對應 `receipts-bad/b<n>_…--M<m>-…/check.json` |
| `bad-tests.kt.txt` | 刻意壞測試原文(去識別化) |
| `device/instrumented-summary.json` | 平板全部儀器測試與套一個錯之後的結果摘要(改寫過的);完整卷證對應 `device/baseline-all.xml`、`device/M2.xml` |
| `controls.json` | 零選中、編譯錯、開 `returnDefaultValues`、裝置歸因樣本、平板套件前後對照、考場完整本機測試分組結果 |
| `manifest.json` | 本目錄每個檔的 sha256 |

`bad-tests.kt.txt` 的 B7 示範「預期值照抄實作算法」,那一行算式就是需求書 Q3 的規則(整數最大值加 10);`RecordingSource` 實作的是演練時另開的資料來源介面(去識別化後的 `CategorySource`),不是考場原有程式。

七個錯的改法(文字描述,考場 patch 不公開):M1 建議排序號 `+10` 改 `+1`;M2 清單沒有整數排序號時的起點從 0 改 -10(結果回 "0");M3 新增失敗的分支也呼叫重新載入;M4 作廢成功不發通知;M5 請求結束時 loading 直接設 false、不看計數;M6 載入失敗時把清單清空;M7 新增時名稱與收支別兩個欄位對調。
