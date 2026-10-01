---
type: issue
status: open
created: 2026-10-01
updated: 2026-10-01
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - scope/guards-gates
summary: |-
  PITFALL:[2026-10-01 殺傷力配方修補體驗設計審第 1 輪邊界、正確性、接手席實跑]`lumos guard kill` 遇到格式壞的配方(元素不是物件、`file`/`old`/`new` 是數字)整支崩潰、一行結果都不印;`invariant` 是數字時原本留痕寫完、印結果行才崩潰(殺傷力配方修補體驗那次順手改成先轉字串,已不崩潰);缺 `new`(原文恰好一次時)、`platform` 寫成陣列、invariant 不是字串又帶合約過濾也崩潰(第 2 輪正確性席實測)。崩潰時回傳 1,跟「有配方 survived」同一個回傳碼。另一個既有洞:筆記裡手寫 `"_logged": true` 會讓那條結果不進 kill-log。落單替身字元(手改筆記寫成 `\ud800` 這種 JSON 跳脫)同族:算身分已改 surrogatepass 不崩潰,但同一篇另一條帶這種字元時 kill-rm 移任何一條都回 2(原始編碼錯誤)、guard kill 在合約片段/test/說明/壞法帶這種字元時崩潰回 1,原文帶這種字元時人讀模式不崩、`--json` 模式崩(代碼審第 1 輪通才席實測)。kill-add 寫不出這種配方,只有手改筆記會出現;doctor P2 會把它們列成「配方欄位格式不對」並附 kill-rm 修法。重現:手寫一條 `{"file": 5, "old": "x", "new": "y", "test": "TestX", "invariant": "…"}` 進 kill_recipes,跑 `lumos guard kill <節點>`
  REVISIT:2026-11-01 guard kill 讀配方後先逐條判格式,壞的那條判 error「配方欄位格式不對」、其他照跑(判法照 doctor P2 的 malformed),補一條重現測試
---
# guard kill遇到格式壞的配方整支崩潰

白話:殺傷力配方是人寫的(或手改的)JSON,欄位型別寫錯時,真跑殺傷力驗證的指令會直接當掉,同一篇其他好的配方也跟著跑不到。健康檢查那段已經會把這種配方列成「格式不對」並給移除指令,所以實務上有出路;但 guard kill 自己該把壞的那條判成錯誤、其他照跑。來源 [[Projects/殺傷力配方修補體驗_計劃]](這次不修,範圍外)、程式說明在 [[Systems/guard-kill]]。
