---
type: system
status: done
created: 2026-07-04
updated: 2026-07-04
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-07-04_risk-tiered-review]]"
summary: |-
  FLOW:選 gap→difficulty.assess(weakness+suggestion)→注入 __NEED__/__TIER__/MAXR_EFF(high=max(MAXR,8))→orchestrator §1 ratchet 逐輪重跑 assess_spec 只升不降→收檔:wrapper 自算 assess_spec($SPEC) 取 NEED_FINAL(與注入取大)重跑 loop status --gate→rc≠0 或 high 級 cross_verdict≠endorsed→requeue+LINE 歸因,不放行
  KEY:審查強度跟風險面走——RISK_CLASSES 四類(payment/external-send/prod-irreversible/self-governance)零參數二值分級;high=K3/cap≥8/關 fail-open(degraded 不放行、endorsed-after-refute 不算綠燈,只剩乾淨 endorsed 一條自動路);standard 行為分毫不變
  KEY:機械脊椎=收檔不信 orchestrator 自報 converged——wrapper 自算 tier 重驗 gate,謊報低 tier 拉不低門檻;SPEC 空/不存在有前置守衛(errexit-safe 走 requeue 非 rc1 暴死)
  KEY:assess_spec=## 切分→黑名單剝除(方案評比/canary 相容性/誠實天花板/審計修正紀錄;前提節保留)→防呆(節數<2 或字元<200 回退全文偏嚴)→剝 inline-code+檔名→assess
  KEY:誠實天花板——分級量表面類別非難度(純內部難 gap 漏到 standard,靠 canary/cross/人兜底);ratchet/high 條文是 prompt 層散文自律(機械兜底=收檔重驗);escalate 輪 cap 不可投遞(誠實收窄);偽造 canary log 可穿(同 evidence-gate 天花板);\b 詞界對中文緊鄰 false negative(prod環境不命中,保守方向)
  KEY:對 RHB 病灶(難題上審計員放水)只買到更多次揮棒,不降單輪放水率——縱深非解藥
  DEP:[[convergence-evidence-gate]](收檔重驗消費 --gate)｜[[lumos-refcheck]]｜gap_select.requeue_unconverged
  TEST:TestDifficulty 11 + TestPromptPlaceholders 1 + TestConfidenceReportTier 1(unittest)+ t_loop_gate_need3(CLI);44+353 全綠
  VERIFY:[[2026-07-04_risk-tiered-review]]
decisions:
  - content: 方案 A 關鍵詞分級+機械重驗;否決 RHB 環境硬化(本機無 agent 摸不到的執行面,硬寫=自欺)與純 diff 標記送審(marker 零成本自貼)
    id: d1
    context: gap 建議借 RHB 讓錨點跑在 agent 改不到的地方;單機工作流做不到,留 future 真 CI
    why_chosen: 分級器零參數確定性;「強制人工複核」的實義=關掉高風險級自動放行寬容路徑(loop 產出本就 100% 人放行)
    decided: 2026-07-04
    valid: true
  - content: 黑名單剝除不選白名單;「前提與既驗事實」節保留
    id: d2
    context: 黑名單詞對真 spec 標題全數子字串命中,錯配方向=多保留=偏嚴;白名單錯配=剝主內容=靜默降級;r7 辯方 14 份真 spec 實測前提節保留下 8 standard/6 high 全真陽性
    why_chosen: 與天花板「假陽性偏嚴」姿態一致;唯一 full→kept 降級案是修正樣板 canary 假陽性
    decided: 2026-07-04
    valid: true
  - content: escalate 輪 cap 不可投遞(維持已注入值),只投遞 K 與 §2.5c 條文
    id: d3
    context: __MAXR__ 由 wrapper 起點一次性 sed 注入,loop 中途無重注入管道(spec r4-F4 誠實收窄)
    why_chosen: 寫做得到的;損失=escalate 輪少 2 輪預算,fail-closed 方向不受影響(收檔守衛以自算 tier 重驗)
    decided: 2026-07-04
    valid: true
---
# risk-tiered-review

**風險分級審查強度**——難 gap 自動加輪數、關 fail-open;簡單 gap 走快路。審查的力氣跟著風險走,不齊頭平分。

## 動機
RHB 實測:題目越難、老實解法越不可行,連低作弊率的好模型也開始抄捷徑——自主 loop 碰難 gap 時恰是審計最易失靈時。現制一視同仁=在最容易出事的場合給最少的盯。

## 組件
- `governance/autonomous_loop/difficulty.py`:RISK_CLASSES/assess/assess_spec/params(純函數零依賴)。
- `governance/autonomous-loop.sh`:選 gap 後分級注入;收檔守衛(SPEC 前置驗證→自算 tier 重驗 gate→high 級 cross_verdict 核對),全部 errexit-safe、擋下走 requeue+LINE 歸因。
- `governance/autonomous_loop/orchestrator-prompt.md`:§2 開頭 tier 行、步驟 8 `--need __NEED__`、§1 尾 ratchet(逐輪重跑、只升不降)、§2.5c high 條文、§3 輸出 tier/tier_escalated/need/maxr 四純量鍵。
- `confidence_report.build_report`:增 tier/hits/reported_tier(向後相容);自報≠自算紅標,人 review 一眼可辨。

## 相關
- 設計稿:`docs/design/2026-07-03-risk-tiered-review.md`(11 輪收斂:6 自動撞 cap+5 人工續審;證據閘首個完整實戰案;r9 missed 依規作廢重審)。
- 實作計畫:`docs/superpowers/plans/2026-07-04-risk-tiered-review.md`。
