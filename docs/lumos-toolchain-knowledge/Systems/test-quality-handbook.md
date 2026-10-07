---
type: system
status: doing
created: 2026-10-07
updated: 2026-10-07
responsibility: 固定手冊兩臂試行與證據歸因；只測隔離的小型題目，不推論所有語言或模型
self_audit: GPT-6-Codex-clean-agent/2026-10-07
aliases: []
about_code:
  - governance/eval/test_quality_handbook.py
  - governance/eval/test_test_quality_handbook.py
tags:
  - type/system
  - status/doing
  - scope/evals
summary: |-
  WHY: 凍結兩臂與題目後才量測手冊效果 [出處:2026-10-07 使用者要求先實驗再決定推送] [因:掃描器考卷通過不能證明模型會讀取或遵循規範]
related:
  - "[[Systems/test-quality-scan]]"
verified_by:
  - "[[Verification/2026-10-07_測試手冊措辭兩臂試行]]"
---
# test-quality-handbook

## 判準與限制

WHY: 入口與行為分兩道量測 [出處:[[Projects/測試品質掃描試行_計劃]]] [因:強制載入後的好表現不代表會自動載入]。入口先用技能目錄與 Read 模擬描述選擇，行為則在兩臂提供相應規範。原生 Skill 及真實專案的推論需相應證據。

WHY: 只執行受限的 unittest 題目 [出處:2026-10-07 手冊效果固定試行] [因:生成測試不是可信程式，試行只需固定斷言與函式呼叫]。這是考卷語法限制，不是通用 Python 沙盒；不在允許語法內的測試列無效，不當成品質不良。零測試、錯誤基準與匯入錯誤不算故障被抓到。

WHY: 新措辭組合只比較整體效果 [出處:2026-10-07 使用者三點提醒] [因:正面目標與逐項完成條件同时改動，沒有拆臂就不能歸因單項]。兩次重複僅支援小型試行觀察；舊新版皆滿分的題目記無鑑別力。

## 本篇的檔案邊界

- `governance/eval/test_quality_handbook.py` 的固定題目、版本凍結與有效場次取捨歸本篇；手冊與掃描器來源脈絡另見 [[Systems/test-quality-scan]]。
- `governance/eval/test_test_quality_handbook.py` 的獨立控制案例歸本篇，重點是抓錯歸因與無效结果不混為成功。

PITFALL: 初批事件彙整中止導致行為對照資料不齊 [出處:2026-10-07 固定手冊試行 v1 instrument-disposal] [根因:事件的 message 可為文字，彙整器假設全部是物件] [repro:python3 -m unittest discover -s governance/eval -p test_test_quality_handbook.py -v]。儀器修訂保留首批，解析前先保存原始事件；最終納入範圍以驗證紀錄的場次清單裁定，不以模型會談 valid 直接宣稱實驗有效。

WHY: 候選措辭暫留實驗材料 [出處:[[Verification/2026-10-07_測試手冊措辭兩臂試行]]] [因:固定指標無提升且事後探查有覆蓋缺口，措辭清楚不能代替測試抓錯證據]。原規範持續使用；採用候選需另批獨立留出與原生路由證據，重驗條件見驗證紀錄。
