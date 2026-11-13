---
type: issue
status: open
created: 2026-11-13
updated: 2026-11-13
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/issue
  - status/open
  - scope/stack-knowledge
related:
  - "[[Projects/人裁殺傷力在真實Android專案跑得起來_計劃]]"
summary: |-
  PITFALL:人裁跑殺傷力前的 run_cmd 檢查在幾種寫法下漏擋,壞設定要等殺傷力基準跑完才以 abort 或 killed_unattributed 被拒 [出處:2026-11-13 代碼審 code-人裁殺傷力android r3 七席] [根因:任務清單靠 detekt 共用切段,shlex 遇註解內不成對引號整行丟掉、sh -c 只認 -c、cd 換目錄沒當專案目錄] [repro:_gradle_task_list("./gradlew test # don't") 回空清單] [影響:只會晚擋,不寫錯計劃]
---
# 人裁run_cmd事前檢查漏擋與測試綁定的邊角

## 症狀

代碼審第三輪(上限輪)七席都只報 minor,收尾時放行、記在這裡:

1. run_cmd 行尾註解有不成對的引號(`./gradlew :app:test # don't run all`):整行被 `_detekt_walk_segments` 跳過,`_gradle_task_list` 回空清單,Android 的 test 任務不擋(正確性 c1、通才 t1、合約 g1、架構對齊 a2 四席一致)。
2. `bash -lc '…'`、`sh -ec '…'`:`sh -c` 展開只認 `body[1] == "-c"`;引號包住的 `'#x'` 被當註解截掉後面的詞(資安 x1)。
3. `cd android && ./gradlew :mobile:test`:只認 `-p`/`--project-dir` 換專案目錄,`cd` 沒認(邊界 b2)。
4. `--import` 插入點那一行在整支檔別處(例:KDoc 範例)也出現:事前檢查只看檔頭區,`_kill_also_apply` 要求全檔恰好一行,殺傷力起跑後才報錯(邊界 b1)。
5. 設定鍵名公式在 `_situation_rule_platform` 與 `_situation_rule_android_cmd_problem` 各寫一份(架構對齊 a1)。
6. 檔頭掃描靠在換行後插 `\x00` 標記判「行尾是否落在註解或字串裡」,依賴 `_strip_c_comments` 的實作細節(架構對齊 a3)。
7. 代碼審第二輪新加的 `t_situation_rule_android_run_cmd_segments`、`t_situation_rule_header_scan_strip`、`t_situation_rule_diff_no_git` 沒綁到計劃條款,S6 條款字面沒涵蓋每段、`:test`、`-p`(合約 g2)。

## 根因

任務清單沿用 detekt 的共用切段(先 shlex 整行切詞,再找 `#`),shlex 對註解內的引號不容忍;專案目錄只從 Gradle 選項推,不追 shell 的 `cd`;插入點的事前檢查與殺傷力端的套用檢查範圍不同(檔頭區對整檔)。

## 現在怎麼繞

都是安全方向:漏擋時殺傷力照跑,基準非綠判 abort 或 killed_unattributed、人裁拒絕、計劃不寫。照擋下訊息或失敗摘錄改 run_cmd(拿掉註解裡的引號、改用 `-p`、`-c` 分開寫)或換一個插入點不重複的寫法再跑。

## 什麼條件算修好

- 第 1、2 點:先找引號外的 `#` 截行再 shlex,或 shlex 失敗時退回截在第一個空白開頭的 `#` 重試;`-lc`/`-ec` 這類合併旗標也當 `-c`;run_cmd 有 gradle 字樣卻得到空任務清單時印一行「檢查沒看懂這條命令」。各加一格會紅的案例。
- 第 3 點:`cd <目錄> &&` 後面那段的專案目錄以那個目錄為準。
- 第 4 點:`_situation_rule_imports_problem` 對全檔數插入點那一行,不是一次就當場拒絕並講明。
- 第 5、6 點:抽共用小函式;檔頭掃描改用 `keep_newlines` 逐行對齊、不靠注入字元。
- 第 7 點:三支測試綁進對應條款,S6 字面跟上。

REVISIT:2026-12-15 讀這篇,決定要不要開一份小計劃一次修掉;若雙向追溯計劃先動工、也會改到 run_cmd 檢查,就併進那份
