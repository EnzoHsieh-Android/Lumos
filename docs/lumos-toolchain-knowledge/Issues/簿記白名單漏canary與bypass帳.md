---
type: issue
status: resolved
created: 2026-08-26
updated: 2026-08-26
aliases: []
about_code: []
tags:
  - type/issue
  - status/resolved
summary: |-
  FLAG:TECHNICAL
  KEY:死結型缺口(batch2 CI 紅實錘):_BOOKKEEPING_FILES 白名單漏 docs/.canary-log.jsonl 與 .bypass-log.jsonl——記審查帳/跳過帳這個動作本身把 code-loop pass 打失效;本機有未 commit marker 可救、CI 端只看推上去的帳=gate 紅。修法=白名單補兩檔(一行,但改的是守衛面要過審);第 5 批清債候補
---
# 簿記白名單漏canary與bypass帳

> ✅ **已結案(2026-08-27,root-fixed)**:`_BOOKKEEPING_FILES` 補 canary-log+bypass-log,死結拔除。詳見文末〈已根治〉。

# 簿記白名單漏canary與bypass帳

> 白話:審查記帳的檔案不在「簿記豁免」名單裡,於是「記帳」這個動作會讓「審過了」的留痕失效——自己咬自己。CI 上今天真的紅了一次。

## 乾淨繞法(2026-08-26 再撞,實測驗過)
根治=把 docs/.canary-log.jsonl 加進 `_BOOKKEEPING_FILES`(scripts/lumos:11315)——但那是 code 改動、要自己過 code-loop(死結套死結)。在根治前的正確推送順序:**先把 canary-log 連同 code/卷證一起 commit → 再跑 `code-loop pass`(此時 canary-log 已定稿在 pass 綁的那個 sha)→ 之後只 commit 白名單檔(governance-log/code-loop marker)→ push**。踩坑順序=pass 先、canary-log 後 commit → canary 那筆不在白名單 → pass 自失效。本次 code-batch3 收官即照繞法過關(re-pass 綁 canary-log 已入的 HEAD)。

## ★已根治(2026-08-27)★
Enzo 指示「優化這些部分」——`_BOOKKEEPING_FILES`(scripts/lumos)補 `docs/.canary-log.jsonl` + `docs/.bypass-log.jsonl`,死結拔除:pass 後提交審計記帳不再讓留痕失效。測試 `t_codeloop_pass_survives_bookkeeping_commits` 擴含 canary/bypass 案例+突變驗(拔掉→死結重現 rc1)。上方繞法段轉歷史帳(根治後不需先提 canary-log 再 pass 的手動繞法,但守著也無害)。本 Issue 可結案。
