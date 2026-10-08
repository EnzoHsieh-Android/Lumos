---
type: project
status: done
created: 2026-10-07
updated: 2026-10-07
self_audit: gpt-5.6-sol/2026-10-07
tags:
  - type/project
  - status/done
  - scope/loop-engineering
lands_in:
  - Systems/每輪修補差異派工
verified_by:
  - "[[Verification/2026-10-07_Claude代碼審公開片段調研]]"
related:
  - "[[Projects/每輪修復副作用驗證調研_計劃]]"
---
# Claude代碼審流程與收斂性對照_計劃


白話：借別人的代碼審做法來檢查我們哪些環節能少返工；看得出原理不代表能直接照搬，少報問題也不算收斂改善。

WHY:依使用者2026-10-07要求，專看Claude相關公開片段對未來代碼審收斂性的幫助，不研究其一般代理架構或復刻產品 [出處:本次對話與governance/research/review-repair-regressions/claude-review-comparison/report.md]
PRIOR-ART: 先讀公開鏡像的review／security-review／遠端入口，再用Anthropic官方code-review外掛、pr-test-analyzer、review-pr與服務文件核對；借用查證與降噪的原理，不新增依賴或直接移植程式。
RETIRE-IF:指定repo或其版本與本次樣本不同、來源不能再核對，撤回對該版本的比較並重查；若後續案例顯示候選以少報真缺陷換輪數下降，撤回該候選。既有合約、未知與完整版本證據保留。
REVISIT:2026-10-21 重新核對使用者指定來源與本次樣本，確認候選實驗是否保留真行為問題及修補回歸；採用前先在獨立計劃列出可翻紅驗收，不把研究候選當規則。

## 成果與界線

對照全文與來源收據見governance/research/review-repair-regressions/claude-review-comparison/report.md及source-receipts.json。已直接查讀固定鏡像及官方公開外掛；鏡像package自報2.1.88，但未獨立認證等同官方发布物。服務端查證引擎未由這些CLI入口片段還原。遞迴樹截斷不作全repo否定結論。使用者未提供精確repo，這次是已辨識樣本的比較，不宣稱找到其心中唯一repo。

最有用的候選是避免修訂輪持續加入非必要風格／自選重構，以及檢查測試能否抓住具體退化。Lumos既有辯方、配對案例、相關壞法抽查與通過後版本固定已有對應，先對照，不再造同功能。不得抑制minor行為缺陷、合約問題或只有特定狀態才出現的真bug；模型信心分數不等於證據。官方外掛與託管服務不混稱，片段中的時間預算／註解不外推事故或成效。

下一個最小實驗候選：選既有純風格、狀態依賴真缺陷、修補退化三類案例，比較只延後非必要建議而不减查證與行為守衛的結果與耗時。尚未執行模型對照或量測實輪輪數；本計劃done只表示完成指定範圍的片段調研，候選另案驗收後才可改流程。

## 選擇與代價

可選①照搬鏡像提示詞與排除清單，省編寫但來源及漏報風險大；②重建其完整查證引擎，片段不足且偏離本次目標；③以第一手片段和官方資料對照現有流程，只保留待驗最小候選。選③，代價是先付案例查證成本，收益及輪數改善仍未判定。

## 回退

撤回本次候選解讀即可；沒有改CLI、技能来源、既有閘、輪數或已核准處置。來源收據保留作歷史研究，不用來追改舊帳。
