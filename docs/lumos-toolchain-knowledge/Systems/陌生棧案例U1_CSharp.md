---
type: system
status: doing
created: 2026-10-16
updated: 2026-10-16
responsibility: 負責CSharp背景作業與request資源生命週期案例，不負責真實DI容器或正式專案判定
aliases: []
about_code:
  - governance/eval/unfamiliar-stack-brief/cases/U1/buggy.cs
  - governance/eval/unfamiliar-stack-brief/cases/U1/fixed.cs
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
# 陌生棧案例U1_CSharp

`governance/eval/unfamiliar-stack-brief/cases/U1/buggy.cs` 保留背景作業閉包捕獲 request-owned 資源的目標故障；`governance/eval/unfamiliar-stack-brief/cases/U1/fixed.cs` 只在作業執行時建立與釋放自己的資源。這兩支是評測原料，不代表某個真實 DI 容器的完整行為。
