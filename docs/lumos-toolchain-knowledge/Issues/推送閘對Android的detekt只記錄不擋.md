---
type: issue
status: open
created: 2026-11-04
updated: 2026-11-04
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/issue
  - status/open
  - scope/stack-knowledge
summary: |-
  FLAG:TECHNICAL
  PITFALL:Android 專案照標準接法宣告的 detekt,在推送前的新增告警檢查裡只記錄不擋;改帶檔案佔位符也一樣,一次改兩支以上 kt 檔 detekt 就拒跑、檢查自動放行 [出處:2026-11-04 設計審 detekt協程規則真的在跑 r1 邊界席、接手席] [根因:新增告警檢查只跑含檔案佔位符的命令,標準接法沒有;佔位符展開成空白分隔的多個路徑,detekt 1.23.8 只收逗號分隔] [repro:detekt --input a.kt b.kt --report sarif:o.sarif 回 rc=1 Was passed main parameter] [影響:補開的協程規則在推送時從不擋人]
related:
  - "[[Systems/pitfalls-lint-adapter]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Projects/Android的detekt推送前真的擋_計劃]]"
---
# 推送閘對Android的detekt只記錄不擋

> 白話:Android 專案宣告了 detekt,看起來推送前會擋新增的問題,實際上從來沒擋過。

## 症狀

- 照 [[Systems/linter精選目錄]] 的標準接法(`--input <原始碼目錄>`)宣告的 detekt,推送前的新增告警檢查把它歸成「只記錄」,新寫的 GlobalScope、Dispatcher 寫死等告警不會擋推送。
- 改成 `--input {LINT_FILES}` 也擋不住:這次改動只有一支 kt 檔時能跑;兩支以上時 detekt 回 rc=1、不產 SARIF,檢查把它記成環境類沒跑完、自動放行。
- 冒煙(lint-check 的真跑驗證)遇到這種宣告、專案又有兩支以上 kt 檔時,會誤報「跑不出可解析 SARIF」。

## 根因

- 新增告警檢查要在合併基準與這次改動上各跑一次、比出新增的告警,所以只跑含檔案佔位符的命令;沒有佔位符的命令逐條降級成只記錄。這是 [[Systems/pitfalls-lint-adapter]] 那一帶刻意的設計,本身沒錯。
- 佔位符由唯一一支替換函式展開成「每個路徑各自加引號、空白相接」,對 eslint、ruff 這類工具是對的;detekt 1.23.8 的 `--input` 只收一個值,多個路徑要用逗號分隔,空白後面的路徑會被當成不認得的參數而整個拒跑。
- 兩件事疊起來:不帶佔位符 → 不擋;帶佔位符 → 多檔就拒跑 → 放行。沒有一種寫法擋得住。

## 現在怎麼繞

- 沒有能擋的繞法。detekt 的告警目前只能靠代碼審查員讀它的報告、或人手動跑 detekt 看結果。
- [[Projects/Android的detekt規則說實話_計劃]] 先把這件事寫進提醒與文件,不讓人以為有在擋。

## 什麼條件算修好

- 照標準接法宣告的 detekt,在一次改兩支以上 kt 檔的推送裡,新增一條 GlobalScope 裸用會被擋下;合併基準就有的同一條不擋。
- 修法在 [[Projects/Android的detekt推送前真的擋_計劃]] 設計。
