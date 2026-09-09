---
type: system
status: doing
created: 2026-08-22
updated: 2026-08-22
self_audit: sonnet/2026-08-30
aliases:
  - 架構對齊席
  - 架構鏡頭
  - 寫法一致性審查
tags:
  - type/system
  - status/doing
  - scope/agent-dag
summary: |-
  FLOW:pitfalls --diff 列對照檔→loop next 吐「架構對齊」席→派工用 templates §7.6 三問→finding 進處置閘
  KEY:只判「跟專案既有的一不一樣」,不評風格好壞;major 只給「引入第二種做法」或「跨層直呼」
  KEY:對照組=同資料夾同副檔名、檔名最相似的 3 個既有檔(排除測試檔);慣例 skill 依副檔名(kotlin/csharp/vue-idioms)
  DEP:[[Systems/pitfalls-code-loop]]
  DEP:[[Systems/design-loop]]
  TEST:t_pitfalls_diff_arch_alignment_hints(對照組選法/排除測試檔/慣例 skill/人讀三問);roster 測試含此席
related:
  - "[[Issues/架構對齊席與棧別檢核題可能相反]]"
  - "[[Projects/兩席相反時端出張力_計劃]]"
  - "[[Systems/棧別提問表態閘]]"
verified_by:
  - "[[Verification/2026-09-09_兩席相反時端出張力實作測試]]"
---
# arch-alignment-lens

# arch-alignment-lens

> 白話:Enzo 2026-08-22 提的需求——自動開發的流程不能產出「跟原本不一樣」或「不入流」的寫法,破壞共同開發的體驗。以前審查席看的是正確性、併發、邊界、合約,沒有一席管「這樣寫跟專案既有的一不一樣」。

## 三個零件
1. **席位**:四個席位表各加一席「架構對齊」(required,不佔人數)。`lumos loop next` 會吐它。
2. **派工**:`skills/lumos-design-loop/templates.md` §7.6——三問(分層與依賴方向 / 命名與錯誤處理 / 有沒有引入第二種做法),每問附對照 file:line;嚴重度錨只給兩種情況 major。判不準(鄰居本身就不一致)標 ⚠ 交編排者,不硬判。
3. **對照組自動化**:`lumos pitfalls --diff` 對每支改動 code 檔列同層最像的 3 個既有檔 + 慣例 skill,人讀與 --json 都有(`arch_alignment`)。審查員拿這三個檔當「專案現在的寫法」。

## 跟棧別檢核題撞到時(2026-09-09 起)

這一席要「跟既有一樣」,棧別檢核題要「用比較好的做法」,兩者可能對同一段程式給相反意見([[Issues/架構對齊席與棧別檢核題可能相反]])。
Enzo 裁:不挑邊、把兩邊端上來。落成三塊(設計與審查在 [[Projects/兩席相反時端出張力_計劃]]):

1. **表態多一種值 `tension`**:作者答檢核題時可以說「我看見兩邊了,這次選沿用既有/改用建議」,附既有寫法在哪(path:line)、隱患、建議。合法的不擋,`code-loop check` 印成 ⚠ 交人裁。
2. **`pitfalls --diff` 端出「可能撞」候選**:改動檔的增行命中某題觸發字、對照的三個既有檔一個都沒有 → 印一行、表態樣板那題帶 `hint`。只端候選、不判——跟上面「不做機械判像不像」一致,看的是觸發字有沒有出現。
3. **派工詞口徑**(templates.md §7.6):遇到 tension 的題,本席查四欄真假(既有真的那樣寫嗎、隱患真的成立嗎、建議可行嗎、chosen 跟 diff 一致嗎),不重裁誰贏;自己發現「跟既有不一樣」而該題答了 satisfied,就把發現寫成張力形狀。

天花板:tension 跟 na 一樣可以敷衍(工具只驗存在與長度);候選只抓「新檔引入鄰居沒有的做法」,反方向「照舊寫法沒採建議」抓不到。

## 刻意不做的
- 不做機械判「像不像」(AST 相似度之類)——「不入流」是語意判斷,交給席位;機械層只負責把對照組端到審查員面前。
- 不把風格偏好算 finding。
