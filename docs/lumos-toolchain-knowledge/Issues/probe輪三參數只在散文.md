---
type: issue
status: open
created: 2026-08-21
updated: 2026-08-21
aliases: []
tags:
  - type/issue
  - status/open
  - priority/P2
  - scope/loop-engineering
summary: |-
  FLAG:TECHNICAL
  KEY:panel 收斂後「應抽」要加開 probe-* 輪,skill 寫「席可縮 3/不計 cap/上限 1 次」三參數——scripts/lumos 零實作:cap 計數含全部 distinct round、無次數上限、無席數檢查
  KEY:standard cap=3 下 probe 吃掉 1/3 額度,是實質行為差異非措辭;「限 1 次」無守衛則可重開 probe 洗輪
  DECISION:[2026-08-21]立案(依「寫下風險當成處理」B 型判準:可機械但未做→開 Issue);動的是收斂閘周邊,修法須過 design-loop
related:
  - "[[Issues/寫下風險當成處理風險]]"
  - "[[Systems/convergence-evidence-gate]]"
---
# probe輪三參數只在散文

> 白話:審查收斂後有個「抽查」機制——抽中就得多開一輪叫 probe。說明書寫這一輪「席位可以少一點、不算進輪數上限、只能開一次」。**程式碼三樣都沒做。**

## 可數事實(2026-08-21 L4 交叉審計 r2 s3 席實證)

- `cmd_loop_next` 的 cap 計數 = `len({r["round"] for r in rounds})`,★含 probe-* 在內★,無排除邏輯。
- 全檔無任何「同 loop 只能一次 probe-*」檢查。
- 無席數=3 的檢查;probe 輪只是一般 round-id 字串。
- 唯一機械化的:應抽/免抽判定(sha 可重算)、probe 冒 major 時 K=2 窗滑入髒輪自然 FAIL。

## 為什麼不是措辭問題

standard 檔 cap=3。照程式碼,probe 佔掉一輪 → 實際只剩兩輪可用於真審計;skill 卻告訴編排者「不計 cap」。**編排者照 skill 排程,會在第三輪撞 cap 時才發現**。「限 1 次」無守衛則理論上可重開 probe 洗掉髒輪。

## 來源與判準

立案依據=[[Issues/寫下風險當成處理風險]] 的 B 型判準(存在便宜檢查點:round-id 前綴過濾、計次)。沒選「降級散文」是因為降級後 probe 機制本身就失去意義(cap 不豁免=抽中即懲罰)。

## 待裁

- [ ] 修 code(三處小改,但動 `cmd_loop_next` cap 邏輯=收斂閘周邊 → 須走 design-loop)
- [ ] 或裁定 probe 輪整個退場(抽查判定保留、不再加開輪)——那就是降級而非實作
- ✅ 已查(2026-08-21):`docs/.canary-log.jsonl` 內 `probe-*` 輪 **0 筆**——機制自 2026-08-05 落地至今從未被執行過。★退場成本=0;這使第二條(退場)成為預設選項,除非有人講出一個要留它的理由★。同時這是 [[Issues/只退場不痛的機制]] 講的「零觸發」又一例,且有完整出處
