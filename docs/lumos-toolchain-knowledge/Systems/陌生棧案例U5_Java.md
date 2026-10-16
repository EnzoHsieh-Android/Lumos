---
type: system
status: doing
created: 2026-10-16
updated: 2026-10-16
responsibility: 負責Java代理式交易入口與部分寫入案例，不負責載入Spring或真實資料庫
aliases: []
about_code:
  - governance/eval/unfamiliar-stack-brief/cases/U5/buggy.java
  - governance/eval/unfamiliar-stack-brief/cases/U5/fixed.java
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
# 陌生棧案例U5_Java

`governance/eval/unfamiliar-stack-brief/cases/U5/buggy.java` 保留同一類內部調用繞過交易包裝、失敗後留下第一筆寫入的目標故障；`governance/eval/unfamiliar-stack-brief/cases/U5/fixed.java` 讓兩步寫入從交易入口進入。這是零依賴的 proxy 語意模型，不證明 Spring 或資料庫的其他行為。
