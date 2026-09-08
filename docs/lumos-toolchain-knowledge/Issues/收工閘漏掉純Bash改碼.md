---
type: issue
status: open
created: 2026-09-07
updated: 2026-09-07
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
summary: |-
  FLAG:TECHNICAL
  KEY:症狀=收工 hook(check-graph-sync.py,Stop)的「改了 code 沒動筆記→擋一次」對**純 Bash 改碼**(sed -i / heredoc > / python 寫檔)完全看不到:閘門 1/2 只從逐字稿收 Edit/Write/MultiEdit 檔路徑與 Bash 的 rm/mv/cp/git rm/git mv 五種,src_files 空就 return 0——連 stderr 提醒都不印
  KEY:★git 腿(impact --diff HEAD --sync-check)存在但接錯位置★——只在「圖譜已被動過」分支被呼叫、用途是列缺哪些筆記,從不參與「改了 code 沒」的判斷;逐字稿版本認不得時整支 hook 略過,不是退回 git 腿
  KEY:發現於 [[Projects/進度從提交推導_計劃]] v4 前掃(2026-09-07);v3 邊界席實測本 repo 逐字稿 Bash 43,481 次 vs Edit/Write 886 次、≥13,712 次疑似改檔——★這個閘對本 repo 大多數改碼動作是盲的★
  KEY:修法方向=閘門 1/2 的 src_files 改由 git diff --name-only HEAD 過 is_code_file 取得(git 優先),逐字稿腿降為輔助(判「哪些是這輪的」);★該 hook 在 ANCHOR_FILES(2026-09-07 補進),改必走 anchor approve★;安裝版與 repo 源檔行號自 :468 起錯開 132 行(源檔多一段 _trusted_lumos),實作對源檔
  KEY:未量:純 Bash 改碼在「該擋卻沒擋」的實際比例(要拿逐字稿對 git diff 重算)
---
# 收工閘漏掉純Bash改碼

> 白話:收工時那道「改了程式碼但知識筆記沒跟著動」的擋門,**只看得到用改檔工具做的改動**。用 Bash 跑 sed、用腳本整檔寫回——這些在本 repo 是常規做法——它一個都看不到,而且不是「看到但不擋」,是**根本不知道你改了東西**。

## 怎麼發現的
[[Projects/進度從提交推導_計劃]] v4 想借這道門當「記任務」的入口,前掃獨立重開 hook 程式碼逐條驗,發現 git 那條腿接錯位置。

## 為什麼之前沒人發現
它的失效是**靜默的**:src_files 空→`return 0`,不印任何東西。而本 repo 改碼大宗是 Bash(v3 邊界席實測)——所以這道門大多數時候其實沒在守,但沒有任何訊號。

## ★活樣本(2026-09-07,同日另一個 session 現場示範,對造自報)★

另一個 session 修兩支排程 shell 腳本(`governance/autonomous-loop.sh`、`governance/daily-governance.sh`)的鎖與一支測試檔。因為那兩支**可能正在跑、不能分兩次存檔**,它照家規「共用檔要原子寫入」寫了一支 python 補丁腳本、用 Bash 跑、原子換檔。結果:**逐字稿裡一次 Edit/Write 都沒有,閘門看到的只有 `python3 <補丁腳本>`——改了三支檔,收工閘一句話都沒講。**

★這條的意義★:不是刻意繞閘,是**「原子寫入」那條家規本身會把人推去用 Bash**,而 Bash 正好是這道閘的盲區。**兩條紀律互相把對方推進洞裡。** 對造自陳會照紀律自己寫回圖譜、不等閘催——也就是說今天這道閘對這次改動的貢獻是零,寫回全靠自律。

順帶記一個對造外家席報的 bash 陷阱(與本案無關但同日同源):函式被寫在 `||` 左手邊時,**bash 會把整個函式體的 `set -e` 關掉**,「寫 pid 失敗會自動中止」是假的;之後若為任何 hook 包 shell wrapper,先記著。

## 不涵蓋
- 不裁修法;修法在 v4 計劃裡跟入口一起設計,v4 若停案本 Issue 獨立處理。
- 沒量「該擋卻沒擋」的實際比例。

REVISIT:2026-10-07 若 v4 停案,本 Issue 獨立處理(修法方向見摘要)
