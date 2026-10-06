---
type: issue
status: open
created: 2026-10-05
updated: 2026-10-05
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - scope/platform
summary: |-
  FLAG:ORIGIN
  WHY:[2026-10-05 Projects/Lumos事件帳_計劃 設計審 r2 架構席與接手席]要把 enforcement 新的一列寫進「管 enforcement 的那篇」時,查不到這篇:enforcement_status 與 enforcement_summary 沒有任何 Systems 筆記在正文或負責範圍裡講它,hook 事件帳「活著沒」的判法也只寫在 Projects/enforcement可觀測性_計劃。各列的語意因此散在各自功能的筆記裡(這次的 claude-event-ledger 列寫在 Systems/lumos事件帳)
related:
  - "[[Systems/lumos事件帳]]"
---
# enforcement_status沒有家

## 症狀

改 `lumos enforcement` 的人找不到一篇講「各列狀態值的規矩、分母怎麼算、開場提醒點名哪幾種」的 Systems 筆記。2026-10-05 設計審第一輪把新列的落點寫成一篇主題不相干的節點,第二輪才被兩席查出那篇根本沒講 enforcement。

## 根因

enforcement 是 [[Projects/enforcement儀表板_計劃]] 與 [[Projects/enforcement可觀測性_計劃]] 兩份計劃做出來的,現況沒有落到一篇 Systems 筆記;它所在的主程式由很多篇各管一段,沒有一篇的負責範圍寫到它。

## 現在怎麼繞

- 各列語意寫在那一列所屬功能的筆記:事件帳那一列在 [[Systems/lumos事件帳]]。
- 狀態值的硬規矩(開場提醒只點名 inactive、degraded;分母排除 unknown、stale、registered-trust-unknown)目前只能讀程式碼與上面兩份計劃。

## 什麼條件算修好

開一篇 Systems 筆記(或擴充既有一篇的負責範圍)講 enforcement 的列結構、狀態值與分母規則,各功能筆記改成連過去;本 Issue 結案。

