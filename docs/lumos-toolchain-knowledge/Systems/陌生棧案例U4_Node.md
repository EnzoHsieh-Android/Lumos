---
type: system
status: doing
created: 2026-10-16
updated: 2026-10-16
responsibility: 負責Node非同步扇出與有界並行案例，不負責真實服務容量或連線池設定
aliases: []
about_code:
  - governance/eval/unfamiliar-stack-brief/cases/U4/buggy.js
  - governance/eval/unfamiliar-stack-brief/cases/U4/fixed.js
  - governance/eval/unfamiliar-stack-brief/cases/U4/buggy-v2.js
  - governance/eval/unfamiliar-stack-brief/cases/U4/fixed-v2.js
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY:保留同一缺陷的壞版、修復版與正常反例，讓陌生棧審查有可執行外部答案 [出處:2026-10-16五案資格預檢] [因:不能拿 reviewer 自己的判斷當 oracle] [不選:只有文字壞例]
  SEE:[[Systems/陌生棧不變量簡報評測]] [[Projects/陌生棧不變量簡報五案評測_計劃]]
verified_by:
  - "[[Verification/2026-10-16_陌生棧五案資格預檢]]"
  - "[[Verification/2026-10-16_陌生棧評測儀器修正]]"
---
# 陌生棧案例U4_Node

舊 v1 的 fixed 曾遺失 worker 回傳值，峰值 oracle 卻仍通過；舊凍結檔與舊紀錄保留以供查證，不再作完整 S2 通過依據。新版以回傳結果、輸入順序與空集合補強正常路徑；詳見 [[Projects/陌生棧不變量簡報五案評測_計劃]]。

`governance/eval/unfamiliar-stack-brief/cases/U4/buggy.js` 保留對輸入集合直接 `Promise.all` 的無界扇出；`governance/eval/unfamiliar-stack-brief/cases/U4/fixed.js` 用固定數量的 consumer 將峰值限在三。這個三是案例 oracle，不是真實服務容量建議。
