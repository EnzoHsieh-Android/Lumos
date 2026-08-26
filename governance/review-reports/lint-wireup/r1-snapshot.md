---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:第 2 批接活⑦——SARIF lint 鏈(lint.json→pitfalls claim)真機驗證過但三處斷線:lint-check 未接 doctor --ci(自家待辦沒打勾)、pre-push 恆 --no-lint(刻意,明文化)、smoke 無排程(裁維持手動+回頭條件)
  KEY:[S1] doctor --ci 加 [LINT] 檢(有 .lumos/lint.json 才驗 schema/新鮮度,無宣告=跳過不擋)[S2] pre-push --no-lint 明文入 pitfalls-code-loop 筆記+revalidate_when [S3] smoke 裁維持手動+KDS 下次真機必跑條件
  DEP:[[Projects/建了沒人跑批次裁定_計劃]]｜[[Systems/pitfalls-code-loop]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
---

# lint接線收口_計劃

> 白話:社群 linter 橋(SQL/樣式/Compose 的告警轉成審查風險票)在 KDS 真機驗證過,但最後一哩沒接:doctor 不驗宣告檔、pre-push 刻意跳過沒寫成文、煙測沒人跑。這案把三處收口——能機械的機械,不能的明文裁定+回頭條件。

## 條款

- **[S1] doctor --ci 加 [LINT] 檢**:repo 有 `.lumos/lint.json` 宣告檔時,靜態驗(JSON 合法、schema 必填鍵、宣告的 linter 指令存在於 PATH 的提示級檢查);無宣告檔=一行「未宣告,跳過」不擋。本 repo 無宣告=恆跳過(此檢為消費 repo 服務);紅=CI 擋。
- **[S2] pre-push --no-lint 明文化**:速度理由的刻意裁定寫進 [[Systems/pitfalls-code-loop]](現況只在 hook 註解);附 revalidate_when=消費 repo 出現「lint 本可擋的缺陷漏進 push」事故時重看。
- **[S3] smoke 裁維持手動**:smoke 需真機 gradle 環境,排程假綠風險大於價值;回頭條件=KDS 下次真機驗證必跑一次 smoke 並留痕。
- 邊界:lint-check 指令本體、SARIF 轉換器、pitfalls 的 lint claim 消費路徑全不動。

## 行為斷言

fixture:壞 JSON 的 lint.json → doctor --ci 紅且訊息白話;缺必填鍵 → 紅;合法宣告 → 綠;無 lint.json → 綠且輸出含「未宣告」;本 repo 真跑 doctor --ci 行為不變(無宣告路徑)。pre-push 行為零變(diff 可證)。

## 實務隱患

- **守衛面**:doctor --ci 是 CI 擋推的守衛,新檢紅=擋——走完整設計審;fail 方向=只驗「有宣告的 repo」,無宣告恆過,對現有所有 repo 零風險面。
- **相容性**:[LINT] 檢排在既有檢之後,不動既有檢的輸出切片(案 A 教訓:E4 位置影響測試切窗)。已排除:金流/對外/不可逆。
