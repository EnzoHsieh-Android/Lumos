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
  KEY:守衛缺口(code-batch2 conf-f1 順帶抓到):lumos lint 對 Verification 的 valid_under/revalidate_when 空欄不警——同一天五篇驗證全把回頭條件寫進正文、欄位空白,stale --match 全掃不到,lint 全綠放行;鐵則四被靜默架空而無機械提醒
  KEY:建議修法=lint 對 type verification 且 status pass 的節點,兩欄空=warning(不擋舊帳,cutoff 起算);第 5 批清債候補
---
# lint不守驗證紀錄空回頭條件

- REVISIT:2026-09-12 房務批開工:lint 對空 valid_under/revalidate_when 出 warning(欄位層可讀,免正文管線;Enzo 2026-09-01 委任裁辦)

# lint不守驗證紀錄空回頭條件

> 白話:驗證筆記的「什麼時候要回頭重驗」欄位空著,lint 不會叫——這次五篇同天全空、機械掃描全盲,是審查席抓到的。這張單子排進清債批,給 lint 加一聲警告。
