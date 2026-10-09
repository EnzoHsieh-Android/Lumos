---
type: verification
status: pass
date: 2026-10-08
valid_under: Node24.16.0 node:test；Laravel12.69.3 PHPUnit11.5.57 PHP8.5.10；可信本機合成需求與SQLite :memory:；SemgrepCE1.179.0
revalidate_when: CLI捕獲／JUnit解析／部署白名單或runner/report版本改動時，重跑兩消費專案與無效證據控制
tags:
  - type/verification
  - status/pass
  - scope/evals
plan_refs:
  - "[[Projects/測試品質工具接線_計劃]]"
system_refs:
  - "[[Systems/test-quality-cli]]"
  - "[[Systems/test-quality-scan]]"
  - "[[Systems/test-quality-multilang]]"
---
# 測試品質工具接線_Node與Laravel原生消費驗證

## 驗證範圍與卷證

獨立消費專案在 /Users/enzo/lumos-test-quality-lab-20261008，README 與 run_experiment.py 可重跑。不可覆寫卷證存 governance/eval/results/test-quality-native-consumers-20261008，manifest 指紋及原始 XML／receipt／snapshot 對應 Node run-yk2hztlm、Laravel run-5eb89al1。附件源碼是 .txt 實驗資料；搬移卷證不是新的執行。原始來源分支為 audit/implementation-test-quality-oct07 的未提交實驗內容；正式推送前另過代碼審閘。

- [S1] Node update與Laravel init從本機來源部署新入口和三sidecar，各自vendor直接執行scan/capture/check/capabilities。
- [S2] 選配Semgrep實跑兩專案自比反例，各列一個候選；重抄演算法反例不由這份有限規則檢出，不能用零候選放行。
- [S3] 16個獨立卷證控制通過，覆蓋故障存活、非assertion／skip、改測試、還原不同、錯身份、改XML、零案例、suite error、重身份、DTD、缺命令、逾時、包裝案例假綠及舊CLI缺sidecar仍可help。三階段check檢出，verdict仍not_assessed。
- [S4] oracle-note只到declared；refactor標green-reported-equivalence-unreviewed，不把來源自述與全綠当獨立性／等價證明。
- [S5] Node基準3案例，故障2目標assertion紅，還原3綠、重構3綠；Laravel基準3Unit+2Feature，故障2Unit及1HTTP目標紅，還原及重構5綠。Laravel前置斷言確認testing/sqlite/:memory:，HTTP驗201精確JSON、DB寫入及422零副作用。故障為價格直接回0。原重構試跑只驗固定0/100/200的結果；數學9n/10不能替代語言中間運算的溢位／精度核對，不以該綠燈宣稱所有非負100倍數都等價。後續修正見[[Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證]]。
- 無匹配Node runner可退出0且包裝檔被計為1個passed；capture --target要求真正named test存在，該原生負例回invalid。PHPUnit零選中同樣invalid。
- 恢復來源後全部測試含反例：Node5綠，Laravel7綠／19assertions。綠反例不是合格判準。composer check-platform-reqs通過。

## 結論與外推限制

已接通可信本機收證與一致性核對，兩棧可重放，尚不授予整棧synthetic-verified：完整考卷中的bootstrap/fake/tenant/各框架理由與真專案仍須逐項原生驗證。沒有模型呼叫或代碼審收斂輪數量測。Node native capture不冒充node-jest bound-tests/guard路線；Pest執行、Jest/Vitest、其他語言原生runner、Laravel13、Dusk、真queue及正式DB未由本次驗證推論。
REVISIT:[when-file:scripts/test_quality.py][by:2026-11-08] 收證或歸因變更時重跑原生零選中及故障／還原，另按完整資格考卷補驗。

補充重跑：兩專案不提供Semgrep亦完成原生四阶段與零選中控制；scan回不完整／rc2，保留without-semgrep-scan.json，沒有把缺backend當零候選通過。runner附件反映此可選backend處理，原始快照／XML不變。

收工：相關核心子集2passed/0failed（包含16收證控制及既有掃描反例），變更節點lint通過；doctor全圖譜0issues／785篇，30段386條既有提醒屬全圖譜健檢，不等於本新增節點缺陷。乾淨agent圖譜×程式×原生卷證交叉審計無finding；推送仍待使用者決定。
