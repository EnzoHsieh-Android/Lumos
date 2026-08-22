---
type: system
status: doing
created: 2026-08-22
updated: 2026-08-22
aliases:
  - 架構對齊席
  - 架構鏡頭
  - 寫法一致性審查
tags:
  - type/system
  - status/doing
summary: |-
  FLOW:pitfalls --diff 列對照檔→loop next 吐「架構對齊」席→派工用 templates §7.6 三問→finding 進處置閘
  KEY:只判「跟專案既有的一不一樣」,不評風格好壞;major 只給「引入第二種做法」或「跨層直呼」
  KEY:對照組=同資料夾同副檔名、檔名最相似的 3 個既有檔(排除測試檔);慣例 skill 依副檔名(kotlin/csharp/vue-idioms)
  DEP:[[Systems/pitfalls-code-loop]]
  DEP:[[Systems/design-loop]]
  TEST:t_pitfalls_diff_arch_alignment_hints(對照組選法/排除測試檔/慣例 skill/人讀三問);roster 測試含此席
---
# arch-alignment-lens

# arch-alignment-lens

> 白話:Enzo 2026-08-22 提的需求——自動開發的流程不能產出「跟原本不一樣」或「不入流」的寫法,破壞共同開發的體驗。以前審查席看的是正確性、併發、邊界、合約,沒有一席管「這樣寫跟專案既有的一不一樣」。

## 三個零件
1. **席位**:四個席位表各加一席「架構對齊」(required,不佔人數)。`lumos loop next` 會吐它。
2. **派工**:`skills/lumos-design-loop/templates.md` §7.6——三問(分層與依賴方向 / 命名與錯誤處理 / 有沒有引入第二種做法),每問附對照 file:line;嚴重度錨只給兩種情況 major。判不準(鄰居本身就不一致)標 ⚠ 交編排者,不硬判。
3. **對照組自動化**:`lumos pitfalls --diff` 對每支改動 code 檔列同層最像的 3 個既有檔 + 慣例 skill,人讀與 --json 都有(`arch_alignment`)。審查員拿這三個檔當「專案現在的寫法」。

## 刻意不做的
- 不做機械判「像不像」(AST 相似度之類)——「不入流」是語意判斷,交給席位;機械層只負責把對照組端到審查員面前。
- 不把風格偏好算 finding。
