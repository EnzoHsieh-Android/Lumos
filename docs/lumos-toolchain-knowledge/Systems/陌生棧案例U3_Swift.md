---
type: system
status: doing
created: 2026-10-16
updated: 2026-10-16
responsibility: 負責Swift actor重入與陳舊結果覆蓋案例，不負責真實UI架構或取消政策
aliases: []
about_code:
  - governance/eval/unfamiliar-stack-brief/cases/U3/buggy.swift
  - governance/eval/unfamiliar-stack-brief/cases/U3/fixed.swift
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY:保留同一缺陷的壞版、修復版與正常反例，讓陌生棧審查有可執行外部答案 [出處:2026-10-16五案資格預檢] [因:不能拿 reviewer 自己的判斷當 oracle] [不選:只有文字壞例]
  SEE:[[Systems/陌生棧不變量簡報評測]] [[Projects/陌生棧不變量簡報五案評測_計劃]]
verified_by:
  - "[[Verification/2026-10-16_陌生棧五案資格預檢]]"
---
# 陌生棧案例U3_Swift

`governance/eval/unfamiliar-stack-brief/cases/U3/buggy.swift` 保留 actor 方法跨 `await` 後讓舊請求覆蓋新結果的目標故障；`governance/eval/unfamiliar-stack-brief/cases/U3/fixed.swift` 以 revision 確認完成的工作仍是最新一份。案例只隔離 actor 重入，不包含真實 UI 擁有者與取消策略。
