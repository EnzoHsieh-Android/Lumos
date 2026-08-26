---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:地基盤點第 3 批案 D——新收斂制地基假設「席報告的 severity 標籤↔帳面 --severity 忠實轉錄」至今零機械守衛(僅人工核過 0/18):[S1] severity-check 掃描器(席報告 parse severity 標頭→與該輪該席帳列比對,blocker/major 低報=紅)[S2] 併入 --disposal 輸出(異常才發聲,比照 roster 尾端模式)[S3] 對本日全部 d5 迴圈跑一次歷史掃當首驗
  DEP:[[Systems/loop-convergence-recording]]｜[[Projects/地基盤點2026-08-26_調研]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
---

# 嚴重度綁定機械掃_計劃

> 白話:整套新收斂制信一件事——記帳的人把審查員講的最嚴重等級照實抄。這件事現在靠自律。掃描器把它變機械:報告檔裡寫 blocker,帳上記 minor?當場抓。

PRIOR-ART: borrow——同 repo 的 quote-check/refcheck/seat-check 收貨三道就是「報告↔帳」機械對帳的現成模式,本案是第四道(severity 維度);報告檔已凍結入帳(path+sha256),parse 基礎全在。

## 現況事實

- 帳列有 severity(寫側白名單擋值域)、report{path,sha256};席報告格式慣例=「severity: <值>」行(本 session 全部報告皆此格式,但格式無機械強制)。
- 綁定驗證現況=編排者自律;人工核僅一次(0/18);disposal 閘不驗此維度——低報 severity 可讓 major 變 minor 逃過「code-* major 必折」鐵則。

## 條款

- **[S1] severity-check 掃描器**:`lumos severity-check <帳列|loop+round+席>`——讀該席 report 檔(sha 先驗與帳面一致),parse 全部「severity: <值>」行取最高,與帳列 severity 比:報告最高 > 帳面=★低報,紅★(這是能讓 major 逃折的方向);報告最高 < 帳面=提醒(高報=保守,不紅);報告 parse 不到任何 severity 行=提醒「格式無法機械驗」(不紅,舊報告相容)。值序 clean<minor<major<blocker。
- **[S2] 併入 --disposal(異常才發聲)**:問閘收尾對判定輪逐席跑 [S1],低報→紅字轉述行(advisory 不動 rc——動 rc=改閘語意須另過設計審,本案先轉述+留痕 severity-alerts.log,比照 roster 尾端模式含 try/except 與 __seqN 跳過)。
- **[S3] 歷史首驗**:對 2026-08-25 起全部 d5 迴圈帳列跑一次掃,結果入本案驗證紀錄(0/18 的人工核升級成 n/全量 的機械帳)。
- 邊界:不動記帳寫側、不動閘判定布林;報告格式不強制(掃不出=提醒非紅)。

## 行為斷言

fixture:報告 blocker+帳 minor→紅並指名席;報告 minor+帳 major→提醒不紅;無 severity 行→提醒;sha 不符→拒掃指路 quote-check;disposal 尾端低報轉述行出現且 rc 不變(打樁);歷史掃跑完出統計行。

## 實務隱患

- 守衛面:advisory 首版不動 rc(升級成硬閘=另案過審,本案在驗證紀錄掛回頭條件:若首驗或往後真抓到低報,硬閘案即立)。已排除:金流/對外/不可逆。
- parse 面:severity 行可能出現在引句內(報告引用 spec 原文)——掃描排除引句行(「引句:」開頭行內的不算),fixture 釘。
