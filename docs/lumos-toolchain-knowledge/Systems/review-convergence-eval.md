---
type: system
status: done
created: 2026-10-07
updated: 2026-10-07
responsibility: 負責審查帳衍生資料集、案例來源及試行證據比較與專屬測試，不負責產品審查閘、人裁或執行模型及產品指令
aliases: []
about_code:
  - governance/eval/review_convergence.py
  - governance/eval/test_review_convergence.py
  - governance/eval/review_convergence.md
tags:
  - type/system
  - status/done
  - scope/evals
summary: |-
  WHY:[因:缺件不能當成效證據]衍生比較與產品審查閘分開，避免缺件或格式合格被當修补有效 [出處:Projects/審查回顧轉可比較eval_計劃]
  PITFALL:[根因:把較少輪誤當品質改善]較少輪但破壞既有行為不能算改善 [出處:Verification/2026-10-07_審查回顧eval補強] [test:t_review_eval_comparison]
verified_by:
  - "[[Verification/2026-10-07_審查回顧eval補強]]"
  - "[[Verification/2026-10-07_實作測試獨立判準盤點]]"
related:
  - Systems/測試假綠形態
---
# review-convergence-eval

PITFALL:識別欄位的長度上限不可共用到檔案路徑，否則合法長路徑會從有效試行變成無效資料；以同一真實129字檔名核對兩端。 [出處:Verification/2026-10-07_審查回顧eval補強] [test:t_review_eval_trials]

PITFALL:Python把布林與數字視為相等，直接比較JSON原件會漏掉衝突；以逐項比較區分布林與數字、允許相等JSON數值的不同寫法，不以輸入順序決定成本。 [出處:Verification/2026-10-07_審查回顧eval補強] [test:t_review_eval_cohort]
