---
type: project
status: doing
created: 2026-07-16
updated: 2026-07-16
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/design-loop提效_計劃]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/canary-audit]]"
  - "[[Systems/autonomous-iteration-loop]]"
summary: |-
  FLAG:DECISION
  KEY:問題=loop 真實跑一次產生的資訊(輪數曲線/canary 型別命中/席位 missed 軸/辯方開庭/逃逸)散落且部分蒸發——判「最佳收斂方式」需要這本帳。實測盤點(2026-07-16):六 repo 共 ~61 loops/17 golden——toolchain 24+11/LandmarkMember 24+5/mOrangePos 11+0/Citrus_KDS 1+1/CompassKiosk 1+0;唯一活流失=自主日報 loop 的 /tmp 工作區事件流(corrosion-gauge 7 輪 K=3 只剩 golden 散文)
  KEY:★混淆★語料橫跨四五代協議(循序→panel 07-09→canary 硬化 07-10→M1 提效 07-16→M2 cluster 帳 07-16)——跨代混池=體溫計加溫度計;但版本更迭同時是 treatment variable(天然準實驗):跨代比較(panel 省輪?M1 辯方歸零?)可做,代內調參(每層 n=10-15)樣本不足
  KEY:replay 校準不受版本污染——golden 凍 spec+已知 findings(近似 ground truth 標籤),重跑審計算接住率與產出協議代無關;17 份遠超 10+ 門檻,隨時可跑 baseline
  KEY:逃逸帳=唯一能校準停止決策的標尺——「收斂好不好」ground truth 是下游抓到多少設計期漏的(實例:fromscratch 收斂後 code review 抓 token 消毒 blocker;M2 收斂後 code-loop 抓 Codex 3 洞);現只在散文,無機械歸因
  DECISION:v1 不做統計模型/dashboard/自動調參(代內 n 不足,先累後校準順序不可倒);只做「訊號機械化+歸因」四件:自主 loop 歸檔/逃逸帳/epoch 蓋章/分層 stats
  DEP:[[Systems/loop-convergence-recording]]｜[[Systems/autonomous-iteration-loop]]
verified_by:
  - "[[Verification/2026-07-16_replay校準baseline_v0]]"
---
# loop數據收集_計劃

> **狀態**：ideation 收成（2026-07-16，與人共同盤點），尚未 design-loop、尚未實作。緣起：使用者問「每次真實跑 loop 能不能累積數據供後續判斷最佳收斂方式」。

## 盤點（2026-07-16 實查六 repo）

| repo | loops | golden | 備註 |
|---|---|---|---|
| lumos-toolchain | 24 | 11 | 手動線全留存;**自主日報 loop 在 /tmp 工作區,事件流蒸發**（corrosion-gauge 7 輪 K=3 僅剩 golden 散文摘要）|
| LandmarkMember | 24 | 5 | 真業務語料（金流/票券/點數）,留存完整——與 toolchain 自指型 spec 是兩種難度剖面,正是「哪類 spec 用哪種收斂」的對照組 |
| mOrangePos | 11 | 0 | 06-22~06-25 era,早於 golden 慣例——事件流在、golden 缺 |
| Citrus_KDS | 1 | 1 | |
| CompassKiosk | 1 | 0 | |
| **計** | **~61** | **17** | |

## 兩個釘死的方法論前提

1. **協議代次是一等變數**（使用者點出的混淆）：語料橫跨 循序(≤07-09)→panel(07-09)→canary 生成硬化(07-10)→M1 提效(07-16)→M2 cluster 帳(07-16) 四五代。分析**一律分層嚴禁混池**;跨代比較是價值（treatment variable、天然準實驗）,代內調參是陷阱（n=10-15/層）。epoch 表可從 skill 的 git commit 史機械回溯,拿 loop ts 蓋章,不碰散文。
2. **逃逸帳是 ground truth**：收斂決策對不對,由下游（code-loop/實作/prod）抓到的可歸因缺陷裁決,不由 loop 自己的殘餘估計裁決。

## 里程碑

- **M1（堵流失+建標尺）**：①自主 loop 事件流歸檔——收斂/達 cap 時把 /tmp 工作區 canary-log 整檔搬回 repo（零判斷純搬運,同 golden 慣例）②`lumos loop escape` 原語——下游發現可歸因缺陷時記一筆（loop-id/發現階段/嚴重度/描述）,append-only ③epoch 表回溯蓋章（機械,一次性）。
- **M2（讀取器+新欄）**：①跨 repo 分層 `loop stats`（多 vault 來源,按 epoch 分組輸出:輪數曲線/caught-rate by canary 型別/席位 missed 軸/辯方開庭數/逃逸率）②新記錄結構化欄:`--protocol`/`--canary-type`/`--probe`(現埋於 note 散文,regex 撈不可靠)。
- **獨立實驗**：replay 校準。✅ **baseline v0 已跑（2026-07-16,[[Verification/2026-07-16_replay校準baseline_v0]]）**——2 spec×2 模型×釘住/未釘 8 席;三結論(haiku 只配機械清單/單席 sonnet 首輪廣度驚人=多輪價值在折入迴歸/洩漏效應分層)+**三鐵則:受試用 git 史前折 v1、repo 釘同期 worktree、prompt 明示提案語意**——三條缺一分數即污染。擴大跑(更多 golden/加 opus)按需。

## 已知會被機械報表接住的人肉觀察（動機實例）

深鏡頭席三連漏 canary（席位×軸）/資源例外型 canary 天生 haiku 可見（型別難度）/fromscratch 9→6→3 遞減 vs M2 6→9→7 不遞減（spec 類型剖面）/M1 後辯方零開庭（提效量測）——這些全靠人肉看 note 撈出來,本該一行 stats。

## 天花板（誠實）

- 逃逸歸因是人工判斷（「這個 bug 算不算某 loop 該抓的」）,GIGO 同 cluster 歸併。
- 61 loops 分五代後每層樣本小——v1 產出是**可比較的帳**,不是統計結論;結論等帳厚。
- 收集本身不改善任何 loop——它買的是「下次改 loop 機制時有據可依」,對齊 loop engineering 大方向（機制價值看對自動 loop 有沒有用:自主 loop 要自選收斂策略,前提是有帳可查）。

## 進實作前（紀律）

M1 三件皆機械搬運/append 級,貼近 trivial——實作時單 reviewer 即可,註明;M2 stats 讀取器動分析語意,建議過一輪輕 design-loop。落地 Verification 以 `plan_refs` 回指本節點。
