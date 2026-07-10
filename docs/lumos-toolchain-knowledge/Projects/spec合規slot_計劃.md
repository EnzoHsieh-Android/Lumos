---
type: project
status: done
created: 2026-07-10
updated: 2026-07-10
tags:
  - type/project
  - status/done
related:
  - "[[Projects/社群演算法補強_調研]]"
---
# spec合規slot_計劃

## 目標

解調研裁定③：code-loop 的 reviewer 都在找 bug，沒人拿收斂 spec 對照 diff 問「說好的做了嗎、有沒有偷偷少做/多做」（SDD 流程的 task reviewer 有問，不走 SDD 就沒人問）。

PRIOR-ART: ① 最小解=skill 文本加一個 panel slot 定義+派工模板，零碼。② 世界解過：DO-178C requirements-based coverage（需求→測試 trace+人審）、SDD task reviewer（本 repo templates.md §6 已有「spec 合規」判定——把它從 SDD 專屬泛化到 code-loop panel）。③ 裁定=borrow-design（自家 §6 泛化）。

## 變更規格

- lumos-code-loop SKILL.md panel 節：tier=high 且該分支**有收斂 spec**（計劃節點）時，panel 追加一個 **spec-conformance slot**（不帶 canary、不佔 W 配額，同 qwen 否決位地位）：輸入=收斂 spec + diff，鏡頭=逐條款對照，輸出=「已實作/縮水/多做/未實作」四類清單；縮水與未實作視同 finding 進辯方流程。無 spec 的分支跳過（記一句）。
- templates.md 新 §7.5 派工模板（從 §6 task reviewer 改寫成 diff 級）。

## 驗收

- 兩檔文本落地、與既有 panel 節無矛盾（終審 reviewer 把關）；下一個 tier=high 分支實際派一次。

## 相關模組

- [[Projects/社群演算法補強_調研]]
- [[Systems/pitfalls-code-loop]]
