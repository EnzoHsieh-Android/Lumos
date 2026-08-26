---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:地基盤點第 3 批案 C——08-25 收斂制大改(處置閘/d5 記帳)至今 n=1 天無回測基建:[S1] gate 回放 runner(lumos loop replay <id>:對凍結帳+報告重算 --disposal 判定,與 golden 檔比對,決定論可重算)[S2] 為 08-25 後全部 d5 迴圈建 golden 判定檔(本日 10+ 迴圈=首批素材)[S3] 新舊制同料對照一次性分析(舊 panel 迴圈的帳套 d5 語意重算:會不會收斂/差幾輪,產報告存檔)[S4] runner 接週期(autonomous-loop 週跑一次全量回放,漂移=喊人)
  DEP:[[Systems/design-loop]]｜[[Systems/loop-convergence-recording]]｜[[Projects/地基盤點2026-08-26_調研]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
---

# 改制回測_計劃

> 白話:昨天把收斂判準整組換掉(處置閘),證據只有「上線當天十個迴圈跑得過」。這案把「重算一遍還是同樣判定嗎」變成可以每週自動問的問題:凍結帳+凍結報告都在硬碟上,判定是純讀側決定論——回放器跑一輪,跟存好的標準答案比,不一樣就喊人。

PRIOR-ART: borrow——golden master testing(凍結輸出當標準答案,重算比對)是回歸測試教科書做法;決定論讀側重放=事件溯源(event sourcing)的 replay 慣例;governance/golden/ 已有 30 包快照素材與單次重放先例(2026-07-16),缺的只是 runner 與排程。

## 現況事實

- 處置閘判定=純讀側(canary 帳列+報告檔 sha+快照),`loop status --disposal` 決定論可重算;今日已收斂迴圈 10+ 個,素材齊(governance/review-reports/<loop>/ 各輪快照與報告全凍結入版控)。
- golden/ 30 包只有 {spec,findings} 散文快照,無判定檔、無 runner、無排程;歷史僅 2026-07-16 人工重放一次。
- 舊制 panel 迴圈的帳仍在(replay-only 通道活著),但從未被拿來與新制同料對照。

## 條款

- **[S1] 回放 runner**:`lumos loop replay <id> [--golden <檔>]`——對該 loop 的凍結帳重算 --disposal 逐輪判定(G3/處置/留痕/引句四合取結果+最終 PASS/FAIL),輸出判定摘要 JSON;帶 --golden 時與標準答案比對,異=rc1 白話列差異。舊制迴圈(panel 定錨)自動走 --gate --panel 回放語意重算。判定重算★不寫任何帳★(唯讀)。
- **[S2] golden 判定檔首批**:`lumos loop replay <id> --freeze` 產 `governance/golden/<id>/verdict.json`(逐輪四合取+最終判定+輸入指紋:帳列 sha 集+報告 sha 集);為 08-25 後全部 d5 迴圈(含本日十餘個)凍結首批。
- **[S3] 新舊制同料對照(一次性分析,產物入 golden/)**:取 2026-08-06~08-25 間 panel 定錨迴圈,各自以 (a) panel 回放語意 (b) d5 處置語意重算——輸出對照表(各 loop:兩制判定/收斂輪次差/d5 下會卡哪一關),存 `governance/golden/regime-comparison-2026-08.md`(新檔,本案產);結論寫回 [[Systems/design-loop]](給 08-25 改制補上遲到的對照證據)。
- **[S4] 週期接線**:autonomous-loop 週跑(比照考卷 run_exam 形狀):全量 golden 回放,任何 loop 判定漂移→LINE 喊人(判定會漂=讀側邏輯被改壞或帳被動,兩者都該人看);fail-open 不阻斷主流程。
- 邊界:不改判定邏輯本身;golden 檔=判定快照非帳(帳不可撤原則不變);舊制對照是分析非裁決(不回頭改任何歷史判定)。

## 行為斷言

replay 對今日任一已收斂 loop=判定與當日 gate 輸出一致;--freeze 產檔含輸入指紋;竄改一筆帳列(fixture)→ replay vs golden rc1 且白話指出差異;舊制 loop 走 panel 語意不誤用 d5;週跑 wrapper 在 golden 空時跳過不炸。

## 實務隱患

- 守衛面:runner 唯讀不進閘(advisory);週跑漂移=喊人不擋。對外送出:僅 LINE 喊人,復用既有 line_notify.send 素警示通道(build_alert,不套模板),測試打樁。已排除:金流/不可逆。
- 誠實邊界:回放只證「判定邏輯+帳未變」,不證判定正確(正確性歸當時審查);[S3] 對照受「舊帳欄位語意與 d5 不全同構」限制,對不上的欄位明列「不可比」不硬折。
