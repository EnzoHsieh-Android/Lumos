---
type: project
status: doing
created: 2026-08-14
updated: 2026-08-14
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
related:
  - "[[Projects/收斂機制優化調研2026-08-14]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/design-loop]]"
  - "[[Systems/pitfalls-code-loop]]"
summary: |-
  FLAG:TECHNICAL
  KEY:目標=panel 收斂合取中 capture-recapture 殘餘估計降 advisory(S1)+PASS 帶殘餘觀測行(S2)+canary-stats 加席位重疊分布段(S3)+席名慣例入 skill(S4)
  KEY:動機=雙證據:文獻(前提違反時系統性低估殘餘,Wohlin 1995 起 10 年線)+自帳實測(歷史殘餘<1.0 的 21 輪中 14 輪=67% 下一輪仍出 major+,三專案一致;見[[Projects/收斂機制優化調研2026-08-14]])——低估殘餘=危險方向的假安心,不配當硬合取
  KEY:PRIOR-ART=borrow-design(降級方向借文獻+自帳;報表為既有 loop canary-stats 小修,不造新指令;席名慣例=純紀律零機檢)
  KEY:範圍刀=只動 panel 無-cluster 路徑的 capture 兩條(殘餘超門檻/無counts fail-closed);K=2、存活≤minor、輪有效、G3/min-seats、cluster 帳(已 advisory)、light/循序/settle(不吃 capture)、K 計數改法(候選②另案)、翻紅釘 v2(既有計劃)一律不動
---
# 收斂閘殘餘估計降級_計劃

## 問題

panel 模式收斂合取有一條「capture-recapture 殘餘估計 < 1.0」，帶 fail-closed（無重疊數據＝直接不收斂）。這個估計器的獨立性與等捕獲率前提在 LLM 席上不成立，文獻結論是**系統性低估殘餘**；自家五本帳實測：殘餘 < 1.0（帳面「快抓完」）的 21 輪裡 **14 輪（67%）下一輪仍挖出 major+**，最極端一筆估 0 → 下輪折入 23 條含 blocker。一條三分之二時間給假安心的合取，比沒有更毒——它讓收斂宣稱聽起來有統計背書。

## 改動（四條 S）

### S1 capture 兩條合取降 advisory（核心）

`_panel_round_conjuncts`（scripts/lumos:3520 與 3530 的兩個 `fails.append`,邏輯段 3516-3530）（`殘餘超門檻`／`無capture_counts`）移除，改為純觀測輸出。合取縮為：輪有效 ∧ 存活 max≤minor（＋既有 K=2／G3／min-seats 旗標啟用項）。**一刀切、不設 cutoff**：方向是放鬆（舊 FAIL 可能變 PASS、絕不把舊 PASS 變 FAIL，無誤紅風險），且 gate 是「當下擋不擋」非歷史重放審計工具，已終結 loop 無重問場景（與 A 案 K=2 cutoff 的差異：那次方向是收緊、會誤紅，故需 cutoff）。

### S2 觀測行語意升級

降級後仍印殘餘估計，兩種情況帶明話警語：
- 有 counts：`[panel] capture-recapture 殘餘(advisory,不進合取): 估計 X.XX` ＋ 估計 <1.0 時附「⚠ 低殘餘≠快抓完:自帳實測 67% 假安心率(2026-08-14)」。
- 無 counts：advisory 提示「無 capture_counts,殘餘觀測缺席」——不再 fail。

### S3 canary-stats 加「席位重疊分布」段

`loop canary-stats [<id>]` 尾段新增：per-loop 相異缺陷數、只被一席抓到的數與佔比（f1）、per-auditor 記錄數。資料源＝帳上 `capture_counts`（list 型）。**誠實界線印在輸出裡**：席名即 auditor 欄原文（各專案寫法不統一）、鏡頭層不在帳內不可得。無 counts 的 loop 該段缺席不炸。

### S4 席名慣例（skill 一句話）

design-loop SKILL.md panel 節加一句：派工時 `--auditor` 席名建議 `<鏡頭>-<模型>`（如 `correctness-sonnet`），供跨輪席位／鏡頭分析；純慣例，無機械檢查（明寫）。

## 測試策略（TDD：先紅後綠）

1. **既有期望反轉**（這就是行為變更的翻紅釘）：`t_loop_panel_gate` 的兩條——「殘餘超門檻 → rc1」改期望 rc0＋stdout 有 advisory 警語；「無 capture_counts → fail-closed rc1」改期望 rc0＋stdout 有缺席提示。改測試當下必紅（code 未動），實作後轉綠。
2. **新 t_capture_advisory**：①殘餘超門檻＋其餘全過 → rc0 且 stdout 含「advisory」與估計值 ②無 counts → rc0 含缺席提示 ③存活 major 照樣 rc1（證明只降 capture、沒鬆到別條）④低殘餘印假安心警語。
3. **新 t_canary_stats_overlap**：fixture 帶 capture_counts → 印 f1 佔比行；無 counts loop → 不印該段、不炸。
4. 全套迴歸（cluster 帳 advisory 行為不變、light/settle/循序不變）。

## 實務隱患

- **鬆閘方向的補償**：拿掉一條合取後，panel 收斂剩「輪有效∧存活≤minor∧K=2」。K=2（連續兩乾淨輪）本就是外部文獻推薦的停損主判準（premature-termination 防線），殘餘估計原是輔助——輔助失真該退，主判準不動。收斂措辭同步講小：PASS 訊息維持「此陣容未再發現」語意。
- **測試期望反轉的假綠風險**：反轉後的測試若只斷 rc0 不斷 stdout，會分不出「advisory 生效」與「整段被刪」——斷言必須含觀測行存在性（同 F5 教訓）。
- **S3 除以零／空 list**：f1 計算對空 counts、壞行防禦（沿 canary-stats 既有壞行跳過慣例）。
- **降級語意的散落同步**：skill 兩份（design-loop panel 節收斂行、code-loop panel 節收斂行）、templates.md 收斂行、Systems 三節點 KEY——折入時跑散落 grep（`殘餘<門檻`／`fail-closed`／`capture`）。

## 驗收

- 全套測試綠；doctor 0 issue。
- 手動：對歷史 loop（rel-mainnet）重問 `--gate --panel`，確認殘餘行變 advisory 且 PASS/FAIL 判定只由剩餘合取決定。
