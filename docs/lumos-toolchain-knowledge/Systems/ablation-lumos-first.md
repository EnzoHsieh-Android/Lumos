---
type: system
status: doing
created: 2026-10-04
updated: 2026-10-04
responsibility: 負責探針消融結果檔的有效性篩選、缺場補跑與統計合併；不負責探針沙盒本身的隔離與健康檢查執行
aliases: []
about_code:
  - governance/eval/ablation_lumos_first.py
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY: 2026-10-04 第三輪代碼審證明探針整批 fatal 時仍可能保留逐場成功列；消融讀取端須再查整批有效性。出處 [[Verification/2026-10-04_探針隔離與清理收斂]] 與 r3-reproduction.json。
  PITFALL: 只按逐場 reason 判有效會把健康不可判的批次計入統計且抵掉缺場。出處 [[Issues/探針健康檢查不可判資料仍被重用]]。[test:t_probe_boundary_review4_fatal_batch_not_reused]
---
# ablation-lumos-first

此篇管消融結果的「能不能拿來算」這道邊界。[[Systems/codex-harness]] 管探針如何產生與隔離樣本；兩邊都要守住整批失效的訊號，否則即使探針退出碼正確，重開消融或只做合併時仍可能吃到事故資料。

第四輪修補採整檔排除：fatal 檔案保留原始逐場紀錄供事故分析，但不能抵掉缺場或進入統計；掃描失效檔時同時辨認全域連結損壞與未能完成健康／清理檢查的 fatal。沿用既有彙總欄位以免舊讀取器漏看，呈現文字改為「探針失效」，不把所有 fatal 都叫作 skills 連結損壞。若未來新增消費端，先以 [[Verification/2026-10-04_探針隔離與清理收斂]] 的致命批次反例驗證整批欄位有被讀到。
