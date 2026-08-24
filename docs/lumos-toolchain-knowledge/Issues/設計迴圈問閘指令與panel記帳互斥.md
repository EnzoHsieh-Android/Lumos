---
type: issue
status: resolved
created: 2026-08-24
updated: 2026-08-24
aliases: []
about_code: []
tags:
  - type/issue
  - status/resolved
summary: |-
  FLAG:TECHNICAL
  KEY:design-loop SKILL 步驟 8 寫問閘用 `lumos loop status --disposal`,但 scripts/lumos:4527-4534 明擋 --disposal 與 --panel/--min-seats 併用;多席 panel 型記帳(每席一筆 canary record 帶處置集合)丟給 --disposal 會被「一輪只能有一筆處置」擋下——實務上多席迴圈只能問 --gate --panel(K=2),skill 文字沒講這個分岔
  KEY:實測:node-restore-sop r1(2026-08-24)照 skill 敲 --disposal 被擋,改 --gate --panel --min-seats 3 才通;selfaudit-loop-v5 同型態;=文件與 code 打架,兩套閘語意(disposal 單輪處置合取 vs panel K=2 連續兩輪)並存無路由指引
  DECISION:已裁並落地(d1,2026-08-24):①+②-lite——擋下訊息指路(指令獨立成行)+兩份 SKILL 問閘分岔+05/06 子檔鏡像同步+漂移守衛測試 t_loop_status_disposal_panel_routing(紅釘實跑);全自動路由被排除(閘的選擇顯式留痕)
decisions:
  - content: 裁①+②-lite(Enzo 2026-08-24「接著解」):--disposal 撞多席記帳的擋下訊息加路由指引(指路不代選,判準語意零變動);design-loop/code-loop 兩 skill 問閘句補分岔;釘漂移守衛測試
    id: d1
    context: 選項②全自動路由被排除:閘的選擇該顯式留痕,靜默替人選會掩蓋記帳型態錯誤(閘只留可重算的);純①改字不擋下次再撞
    why_chosen: 訊息層修=零判準風險;測試釘住訊息錨字串防迴歸;自主迴圈讀得懂指路即可續跑
    decided: 2026-08-24
    valid: true
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

## 結案(2026-08-24)

✅ d1 落地:CLI 指路+兩 SKILL 分岔+05/06 鏡像+測試(code-gate-routing 迴圈單席+架構席審過,最嚴重 minor 全折)。

## 附帶觀察(2026-08-24,同族第二道縫)
本 Issue 的修復走 code-gate-routing 迴圈收斂時,處置閘的 quote 關卡再曝一個同族假設縫:發現若屬「diff 之外的鏡像檔沒跟上」型(本輪 7 條裡 4 條),引句天然錨在凍結 patch 之外,quote-check 對 patch 錨定必失敗——閘的材料假設(報告只引被審 diff)與跨檔鏡像審查不合。本輪以 code-loop pass 留痕收斂(tier standard、全 minor 全折、測試綠);此縫留觀察,若再撞第二次立案處理(如 quote-check 加 --repo 後備錨定)。

## 原待裁(史料)
出處:node-restore-sop-v2 r2/r3 審計(governance/review-reports/node-restore-sop-v2/);相關:[[Systems/convergence-evidence-gate]]、[[Projects/節點還原SOP_計劃]]
