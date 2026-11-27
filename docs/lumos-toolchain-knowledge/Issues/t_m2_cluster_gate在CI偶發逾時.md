---
type: issue
status: open
created: 2026-11-28
updated: 2026-11-28
aliases: []
about_code:
  - scripts/test_lumos.py
tags:
  - type/issue
  - status/open
  - scope/evals
summary: |-
  FLAG:TECHNICAL
  PITFALL:t_m2_cluster_gate 在 CI 偶發超過每支測試 180 秒上限而判紅,斷言本身沒錯 [出處:2026-11-28 主線 CI run 46039459166 與 45881353254] [根因:沒查;本機單獨跑約 88 秒且幾乎全是 CPU,CI 分片同跑時機器慢約一倍就貼到上限] [repro:python3.14 scripts/test_lumos.py -k t_m2_cluster_gate 量時間]
  FACT:最近 12 次 Lumos CI 裡這支逾時 2 次(#230 合併那次、#234 合併那次);本機 2026-11-28 單獨跑 real 87.7 秒、user 80.7 秒 [來源:生產] [confirmed:2026-11-28]
---
# t_m2_cluster_gate在CI偶發逾時

## 症狀

主線 CI 的某一份分片印「TIMEOUT t_m2_cluster_gate: 超過 180s 未結束」整份判紅;同一份其他測試全過,前後幾次合併大多不出現。

## 根因

沒查。已知:本機單獨跑約 88 秒、幾乎全是 CPU(user 80.7 秒),40 條斷言;CI 機器較慢、又跟同一份分片的其他測試搶資源,偶爾超過 180 秒。要查的是哪幾條斷言吃掉大部分時間(例如重複建帳或重跑整個閘)。

## 現在怎麼繞

不繞:看到這支逾時、同份其他測試全綠時,照實報「主線 CI 紅,原因是這支偶發逾時」,不當成新改動造成的紅。

## 什麼條件算修好

本機單獨跑降到 60 秒以下,或連續 20 次主線 CI 不再出現這支逾時。

REVISIT:2026-12-15 量一次這支測試各段斷言的耗時,找出最慢的幾段;能在不減斷言的前提下降到 60 秒以下就修,做不到就把撤除條件改成「這支單獨放一份分片」並寫理由。
