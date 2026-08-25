---
type: issue
summary: |-
  FLAG:TECHNICAL
  KEY:ci-wait/ci-status 認本機 HEAD;HEAD 未推送→報「no-run:此 sha 未觸發 workflow」,實因=commit 沒推,訊息帶人去查 workflow 設定(2026-08-25 實踩,gh 對照才發現推送那顆其實綠)
  DECISION:修法=查詢前驗 sha 在不在遠端,不在→獨立判定值(如 unpushed)+白話訊息「這個 commit 還沒推上去」
status: open
created: 2026-08-25
updated: 2026-08-25
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - priority/P3
---
# ci-wait未推送sha誤導訊息

> 白話:HEAD 還沒推上去時,ci-wait/ci-status 會說「此 sha 未觸發任何 workflow(檢查觸發條件)」——事實是「這個 commit 根本沒推」,訊息把人帶去查 workflow 設定。2026-08-25 實踩:推送後本機又加了一筆 docs commit,再問 CI 就拿到 no-run,差點誤判成 CI 壞了(gh 一查,推上去那顆其實綠)。

## 修法方向
查詢前比對 HEAD 是否存在於遠端(`git branch -r --contains` 或 ls-remote);不在→訊息改「這個 commit 還沒推上去,CI 不會有它的 run」,判定值另立(如 unpushed)不與 no-run 混用。
