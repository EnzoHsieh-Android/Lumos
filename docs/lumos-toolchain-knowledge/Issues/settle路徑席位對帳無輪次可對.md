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
  KEY:觀察單(roster 案 [S4]):settle 結清模式的 canary 記錄結構恆 round-less(帶 round 入口即 rc2),無 rid 與 rN-dispatch 快照可機械對帳——問閘自動席位對帳在此路徑做不到;高風險 spec 恰走 settle,核對靠 skill 指路手動 --roster
  KEY:回頭條件=settle 記錄格式若演進出輪次概念,回來補自動對帳
---
# settle路徑席位對帳無輪次可對

# settle路徑席位對帳無輪次可對

> 白話:結清模式的帳沒有「第幾輪」這個欄位,自動對帳沒東西可對。這張單子記住這個洞,格式哪天演進了再回來補。
