---
type: issue
status: open
created: 2026-08-24
updated: 2026-08-24
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
summary: |-
  FLAG:TECHNICAL
  KEY:design-loop SKILL 步驟 8 寫問閘用 `lumos loop status --disposal`,但 scripts/lumos:4527-4534 明擋 --disposal 與 --panel/--min-seats 併用;多席 panel 型記帳(每席一筆 canary record 帶處置集合)丟給 --disposal 會被「一輪只能有一筆處置」擋下——實務上多席迴圈只能問 --gate --panel(K=2),skill 文字沒講這個分岔
  KEY:實測:node-restore-sop r1(2026-08-24)照 skill 敲 --disposal 被擋,改 --gate --panel --min-seats 3 才通;selfaudit-loop-v5 同型態;=文件與 code 打架,兩套閘語意(disposal 單輪處置合取 vs panel K=2 連續兩輪)並存無路由指引
  DECISION:待裁:①skill 補一句「多席 panel 記帳→問 --gate --panel;單席循序→--disposal」②或 loop status 偵測記帳型態自動路由;裁前照現況(記帳型態決定問哪個閘,不偷改語意)
---
# 設計迴圈問閘指令與panel記帳互斥

> 白話:設計審查的操作手冊叫你用 A 指令問「審完了沒」,但只要這個迴圈是多人同審的型態,A 指令會直接把你擋下來,你得自己發現要改用 B 指令——而 A 和 B 判「過關」的標準還不一樣(B 要連續兩輪乾淨)。這個縫是 2026-08-24 節點還原 SOP 的設計迴圈撞到、三個審查員(外家讀碼+終盤席+架構席)合圍確認的。

## 現場(會重現的)

```
python3 scripts/lumos loop status node-restore-sop --disposal --spec docs/lumos-toolchain-knowledge/Projects/節點還原SOP_計劃.md --repo .
```
→「擋下:第 r1 輪有 5 筆記錄都帶了處置結果,一輪只能有一筆」(多席 panel 記帳型態)。改問 `--gate --panel --min-seats 3` 才通,且該閘 2026-08-06 後迴圈是 K=2 連續兩輪。

## 影響
- 照 skill 字面走的人第一次必撞;撞了之後自己選閘=收斂判準沒有單一權威。
- 兩閘語意不同(disposal=單輪處置合取;panel=K=2),選錯邊會做出不同的放行行為。

## 待裁(見摘要 DECISION)
出處:node-restore-sop-v2 r2/r3 審計(governance/review-reports/node-restore-sop-v2/);相關:[[Systems/convergence-evidence-gate]]、[[Projects/節點還原SOP_計劃]]
