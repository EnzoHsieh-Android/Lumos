---
type: issue
status: open
created: 2026-09-10
updated: 2026-09-10
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/issue
  - status/open
  - scope/guards-gates
summary: |-
  FLAG:TECHNICAL
  DECISION:這批(工具自裝檔)不修:那批已審四輪,修這個又是一段沒審過的改動;而且「解不了的位元組怎麼辦」會影響風險掃描看到的內容,值得單獨想
  KEY:推送前檢查與 CI 都會跑的 pitfalls --diff 用文字模式讀整份 git diff;提交裡有一支內容不是 UTF-8、git 又沒當成二進位的檔,解碼就丟錯、整支中斷
  KEY:2026-09-10 代碼審第四輪寫「工具檔內容不是 UTF-8 也要認得」的測試時撞到,跟那批改動無關,是既有問題
---
# 風險掃描遇到非UTF-8內容整支中斷


## 現象

`lumos pitfalls --diff <範圍>`(推送前的檢查與 CI 都會跑)在 `scripts/lumos` 的 `_pitfall_diff_collect` 裡用文字模式讀整份 `git diff` 的輸出。
提交裡只要有一支檔的內容不是 UTF-8、而 git 沒把它當成二進位(例如開頭是 `\xff\xfe` 的文字檔),
解碼就丟 `UnicodeDecodeError`,整支中斷——推送前的檢查跟著停。

## 怎麼發現的

2026-09-10 代碼審第四輪(`code-工具自裝檔不算消費專案`)寫「工具檔內容不是 UTF-8 也要認得是原封不動」的測試時,
測試還沒走到要驗的地方,就先在風險掃描讀差異那段中斷。

## 下一步

修法候選:讀差異時指定 UTF-8、解不了的位元組換成替代字元(只影響那幾個字元的比對,其他行照掃)。
先寫一條「提交裡有非 UTF-8 內容 → 風險掃描照樣跑完」的測試,確認會翻紅再改。
REVISIT:2026-10-10 還沒修的話排進下一批;期間若有消費專案的推送被這個擋下,當天修
