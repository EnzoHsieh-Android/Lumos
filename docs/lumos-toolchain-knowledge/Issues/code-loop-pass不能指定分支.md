---
type: issue
status: open
created: 2026-09-11
updated: 2026-09-11
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - scope/guards-gates
summary: |-
  FLAG:TECHNICAL
  KEY:在沒有掛在分支上的工作目錄(detached worktree)做完代碼審,推 HEAD:main 會被推送前檢查擋
  DECISION:還沒修;碰 code-loop 守衛的讀寫兩側、屬高風險,修要走設計審
  KEY:code-loop pass 把「審過了」記在目前 checkout 的分支名下,detached 就記成 HEAD;推送前按遠端目的地分支名(main)查,只找到別人上一次在 main 記的那筆,判「留痕過時」。表態(dispositions)與判定(check)都有 --branch,pass 沒有
  KEY:目前的繞法:另開 --shared 私有 clone,讓它的 main 指向功能提交,在那裡 pass、只提交帳本、推 main:main;★要設 core.hooksPath 指向那份 clone 的 scripts/hooks★,不設的話那份 clone 沒有任何掛鉤,推送前檢查全沒跑
  KEY:修的時候要守住:讀側曾刻意不認分支別名(別的分支的留痕不能拿來用),pass 加旗標之後留痕仍只能綁被推的那個版本
---
# code-loop-pass不能指定分支

> 白話：在「沒有掛在分支上」的工作目錄做完代碼審，記下的「審過了」會掛在一個叫 HEAD 的名字底下；推到 main 時，推送前檢查按 main 找，找不到。

## 經過

2026-09-11 推「每支檔有家」：本機 main 上有別的會談還沒推的提交，所以在另一個工作目錄（detached）做。
`lumos code-loop pass` 記成「分支 HEAD，版本 dcd5c9dd」；推 HEAD:main 時推送前檢查印「tier=high 且留痕 sha 過時（留痕=c769b746…）」——它找到的是別的會談上一次在 main 記的那筆。
另開私有 clone、讓它的 main 指向功能提交重記一次，推上去（3a59166c），CI 綠。

## 為什麼沒當場修

碰的是 code-loop 守衛的讀寫兩側，屬高風險，要先過設計審；而且讀側曾刻意拿掉分支別名（別的分支的留痕不能拿來用），加旗標要先想清楚不重開那個洞。

REVISIT:2026-10-11 數這一個月治理帳裡分支記成 HEAD 的 pass 有幾筆；有就代表又有人踩到，排進修

## 相關

- [[Systems/pitfalls-code-loop]]：代碼審閘本身
- [[Issues/code-loop-pass自失效追尾]]：同一道留痕的另一個縫（pass 自己寫帳讓留痕失效，後來用簿記豁免解）
