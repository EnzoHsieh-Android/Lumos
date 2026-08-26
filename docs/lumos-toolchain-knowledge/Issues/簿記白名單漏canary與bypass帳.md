---
type: issue
status: open
created: 2026-08-26
updated: 2026-08-26
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
summary: |-
  FLAG:TECHNICAL
  KEY:死結型缺口(batch2 CI 紅實錘):_BOOKKEEPING_FILES 白名單漏 docs/.canary-log.jsonl 與 .bypass-log.jsonl——記審查帳/跳過帳這個動作本身把 code-loop pass 打失效;本機有未 commit marker 可救、CI 端只看推上去的帳=gate 紅。修法=白名單補兩檔(一行,但改的是守衛面要過審);第 5 批清債候補
---
# 簿記白名單漏canary與bypass帳

# 簿記白名單漏canary與bypass帳

> 白話:審查記帳的檔案不在「簿記豁免」名單裡,於是「記帳」這個動作會讓「審過了」的留痕失效——自己咬自己。CI 上今天真的紅了一次。
