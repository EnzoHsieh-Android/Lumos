---
type: issue
status: open
created: 2026-10-06
updated: 2026-10-06
aliases: []
about_code:
  - scripts/hooks/claude/_hookevent.py
tags:
  - type/issue
  - status/open
  - scope/platform
summary: |-
  FLAG:TECHNICAL
  PITFALL:[2026-10-06 事件帳外掛代碼審後重跑真會談時看到]repo 裡的 governance 是指到 repo 外的符號連結時,既有 hook 照樣把 hook-events.jsonl 寫進連結目標;事件帳外掛與讀取端都已經不跟連結,這支還會跟 [重現指令:暫存 repo 裡把 governance 做成指到 repo 外資料夾的連結,跑一場 claude -p,看連結目標底下有沒有 runtime/hook-events.jsonl]
---
# hook事件帳順著連結寫到repo外

## 症狀

repo 裡的 `governance` 被做成指到 repo 外資料夾的符號連結時,既有的 lumos hook 照樣把 `runtime/hook-events.jsonl` 寫進連結目標。2026-10-06 在事件帳外掛代碼審後重跑真會談時看到(那場的外掛已經不寫了,寫進去的是這支 hook)。

## 根因

hook 事件帳的寫入(`_hookevent.py` 的 `record`)直接建資料夾再追加寫入,不檢查路徑上有沒有連結;事件帳外掛與讀取端(`_events_path_safe`)後來都加了「上層任一層是連結就不碰」,這支是同一族但沒跟上。影響:陌生 repo 可以讓 hook 每次執行都往 repo 外的某個資料夾追加一行(內容只有 hook 名稱、結果與時間,不含指令文字)。

## 現在怎麼繞

沒有繞法;只在 repo 被人刻意放了連結時發生。

## 什麼條件算修好

hook 事件帳寫入前逐層檢查 `governance`、`runtime` 不是連結,是就不寫;補一支「連結 repo 裡跑 hook 不寫到連結目標」的測試。
REVISIT:2026-11-06 決定要不要修:看這段期間有沒有在消費專案遇過被做成連結的 governance
