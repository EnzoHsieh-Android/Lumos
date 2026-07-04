---
type: verification
status: pass
created: 2026-07-04
updated: 2026-07-04
tags:
  - type/verification
  - status/pass
related:
  - "[[Systems/risk-tiered-review]]"
valid_under: difficulty.py RISK_CLASSES 四類詞表+params(high=3/8,standard=2/6)+assess_spec 黑名單剝除與防呆雙條件(節數<2 或字元<200);wrapper 接線形(分級注入/SPEC 前置守衛/收檔 gate 重驗/high 級 cross_verdict 核對);orchestrator-prompt __NEED__/__TIER__ 佔位符與 ratchet/high 條文
revalidate_when: 改 RISK_CLASSES 詞表或黑名單;改 params 對映;改收檔守衛接線;改 §2.5c high 條文;RISK_CLASSES regex 定案後以真資料重測 29%/88% 量級並釘進測試(spec 天花板 1 待辦)
summary: |-
  TEST:TestDifficulty 11(四類命中/standard/決定性/self-gov/params/黑名單剝除/標題變異/實質 high/近空回退/短 corpus 回退/inline-code+檔名剝除)+ TestPromptPlaceholders(佔位符存在+防硬編回歸)+ TestConfidenceReportTier(tier 渲染/紅標/向後相容)+ t_loop_gate_need3(K=3 off-by-one 釘);44+353 全綠
  VERIFY:bash -n 過;review 三輪(Task1 防呆雙條件被削經 controller 攔下還原、Task2 SPEC 前置守衛 Important 修、Task4 測試 class 依 spec 分離)
---
# 2026-07-04 risk-tiered-review 驗證

`python3 scripts/test_autonomous_loop.py`:44 tests OK(TestDifficulty 11 + TestPromptPlaceholders + TestConfidenceReportTier 等)。
`python3 scripts/test_lumos.py`:353 passed 0 failed(含 t_loop_gate_need3)。
`bash -n governance/autonomous-loop.sh`:語法過;收檔守衛三分支(SPEC 無效/gate 重驗不過/high 級 cross 非 endorsed)皆 errexit-safe 走 requeue+LINE+exit 0。
審查過程攔下三個真缺陷:implementer 擅削 spec 防呆字元條件(還原+fixture 加長)、TIER_FINAL 計算缺 SPEC 前置守衛(補)、測試 class 未依 spec 獨立(分離)。
