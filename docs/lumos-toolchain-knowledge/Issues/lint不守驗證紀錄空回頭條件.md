---
type: issue
status: done
created: 2026-08-26
updated: 2026-08-26
aliases: []
about_code: []
tags:
  - type/issue
  - status/done
  - scope/node-content
summary: |-
  FLAG:TECHNICAL
  KEY:守衛缺口(code-batch2 conf-f1 順帶抓到):lumos lint 對 Verification 的 valid_under/revalidate_when 空欄不警——同一天五篇驗證全把回頭條件寫進正文、欄位空白,stale --match 全掃不到,lint 全綠放行;鐵則四被靜默架空而無機械提醒
  KEY:建議修法=lint 對 type verification 且 status pass 的節點,兩欄空=warning(不擋舊帳,cutoff 起算);第 5 批清債候補
---
# lint不守驗證紀錄空回頭條件

- ★2026-09-16 已做★:`lumos lint` 對 `type: verification` 且 `status: pass` 的節點，兩個條件欄任一空著就出一句提醒（只提醒不擋）。訊息講明「空著＝掃描工具永遠掃不到這篇，這個結論會一直被當成還有效」。
- **只提醒不擋是刻意的**：真語料上量到 **20 篇**會被叫到（都是舊帳）。擋了等於每個提交都紅，而提醒的作用是讓**寫的時候**看到，不是逼人回頭清舊帳。
- **只對 pass 的**：其他型別沒有這兩個欄位；標成待重驗或失敗的本來就還在處理中，不必催。
- 守衛拆掉驗證過會翻紅。

# lint不守驗證紀錄空回頭條件

> 白話:驗證筆記的「什麼時候要回頭重驗」欄位空著,lint 不會叫——這次五篇同天全空、機械掃描全盲,是審查席抓到的。這張單子排進清債批,給 lint 加一聲警告。
