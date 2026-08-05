---
type: project
status: doing
created: 2026-08-05
updated: 2026-08-05
aliases:
  - K=1 改革
  - 收斂判準 A 案
related:
  - "[[Systems/convergence-evidence-gate]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Projects/design-loop重設計]]"
tags:
  - type/project
  - status/doing
summary: |-
  FLAG:DECISION
  KEY:★立案動機★——panel 是風險最高路徑(tier=high 專用)卻配最鬆判準(一個乾淨輪即收斂 K=1);convergence-evidence-gate 節點自認「未經檢驗的取捨」。本案=用證據定新判準,walk design-loop 新制審後 TDD 落地
  KEY:★證據一(外部主證)★——AEGIS 迭代審計(arXiv 2605.12280,9 輪審 7152 行 spec):缺陷序列 15→8→12→2→8→1→4→1→0,★非單調收斂★——單乾淨輪後反彈兩次(2→8、1→4);「一輪乾淨=枯竭」在該實測誤停兩次
  KEY:★證據二(內部回放,2026-08-05,governance/eval/k1_stop_replay.py 可重算)★——分層回放兩庫 509 筆帳:①panel 直接層 n=4 觀測、反彈 1(code-relmainnet r2 乾淨→r3 major);右截尾 14≫4(K=1 收斂即停看不到後續)→★內部資料不足以獨立定案,方向與外部一致,且截尾方向=低估誤停率★ ②legacy 類比層反彈普遍:toolchain code-loop 8/10、design 2/6;landmark design 3/9、code 1/12(輪內觀測相關=同 loop 多乾淨輪算多次,誠實揭露)
  KEY:★證據三(改變設計方向的發現)★——code-slim-handoff:minor→minor→clean→clean→★major(missed)→blocker★——★連續兩個乾淨輪之後仍冒 blocker★=K=2 也不是銀彈;AEGIS 尾段(1→4)同構。結論:單靠調大 K 治不了,設計空間要往「K∧枯竭訊號合取」或「收斂後抽查」走
  KEY:★候選設計(待 design-loop 審裁)★——(a) K=2 連續有效乾淨輪(治單輪反彈,不治 handoff 型) (b) K=2+確認輪縮編(W=審計員席數,確認輪減半如 5→3,★材料全量★——反彈發生在同材料上,delta 確認確不了枯竭) (c) K=1+殘餘估計上界:傾向否決(capture-recapture 已知弱點=findings 個位數時 CI 寬到無用,Wohlin 十年回顧) (d) 發現衰減率規則(Dalal-Mallows 思想免成本模型 lite 版:連續兩輪「存活折入數」帳面欄嚴格遞減且末輪≤1 才准收斂——只消費既有 findings 欄,可重算) (e) ★收斂後隨機抽查輪★(對「閘自己」的 canary:K=1 收斂後以機率 p 加開一輪覆核,兼治右截尾=未來回放有資料;借 d4 隨機化嚇阻邏輯)
  KEY:★排除項(作者自證)★——SPRT 序貫檢定:Wald-SPRT 辯論停止器(arXiv 2605.19193)作者自陳判別型任務上失效(MMLU 上 KL 崩潰),找缺陷=判別型,不試
  PRIOR-ART:①最小解在既有機制層——(a)/(b)只動 need 參數與席數表;(e)=把 d4 隨機化用到閘自身 ②世界解(2026-08-05 真搜):AEGIS 非單調序列(主證)/capture-recapture 十年回顧 Mh-jackknife 最穩健但小樣本 CI 寬(wohlin.eu/jss04-1)/Dalal-Mallows 1988 成本權衡停止(借思想不借機器:每 loop 2-3 輪餵不飽率模型)/LLM 判官自我不一致 3-5 runs 平台期(arXiv 2510.27106 等)/SPRT 排除見上 ③裁定=borrow-design(零依賴)
  KEY:★誠實天花板★——內部回放繼承帳本天花板(severity=當時辯方後自報,報告蒸發不可重審;C 慣例 2026-08-05 起新資料有留痕);時代異質已分層但層內仍有判準漂移殘餘;panel 直接層 n=4 太薄,主證在外部與近案(T8/RSNO 三輪皆逐輪出 major)
  DEP:scripts/lumos(_loop_status_panel / _round_valid_m2 兩函式)｜governance/eval/k1_stop_replay.py｜skills/lumos-code-loop/SKILL.md
---
# panel 收斂判準改革（A 案）

> 白話：現在的規則是「五個審查員一輪全醒著且沒挖到大洞，就蓋章收工」。外部實測和我們自己的帳都顯示：缺陷的出現是會反彈的——這輪乾淨不代表挖完了。本案要用證據換一把更誠實的尺。

## 為什麼現在立案

2026-08-04 T8 終審（r1-r3 每輪都出 major、達 cap 攤人）與 RSNO 三輪同構——若任一輪碰巧乾淨，K=1 會在發現明顯未枯竭時放行。翻案條件、證據、候選設計見 summary。

## 實務隱患

- **併發**：本案只動收斂判準（讀側純函數），無新寫入路徑；(e) 抽查輪若落地，抽查記錄走既有 `canary record` 原語（append＋讀回自驗），無新併發面。
- **效能**：gate 是人工節奏呼叫（每輪一次），判準計算 O(帳面輪數)，無熱路徑。
- **資源**：無新連線/檔案生命週期；回放腳本唯讀。
- **self-governance 特有**：①改「閘自己」＝裁判改自己的哨子——本 spec 必須過 design-loop 審（本節點正在做的事），且落地測試需含「舊帳在新判準下的回放對照」防靜默放寬；②(e) 的抽查機率 p 由編排者擲，與 d4 同款「隨機性本身不可稽核」誠實限制，記帳只能記 `probed: true/false`；③右截尾治理依賴 (e) 真的被執行——若抽查輪常態被跳過，盲區回歸，需 canary-stats 曝光抽查率。

## 下一步

1. 本 spec 走 design-loop 新制審（處置閘），重點攻擊面：候選設計的組合語意、(e) 抽查輪的成本與嚇阻模型、回放腳本的分層正確性。抽查輪與 cap 的互動規則（抽中的覆核輪不計入 cap、其 findings 照常走處置帳）已定於〈回放輸出〉節末，審時逐句核對。
2. 收斂後 TDD 落地（動 `_loop_status_panel` 判準＝守衛面，測試先紅後綠＋翻紅釘）。

## 回放輸出（凍結）

見 `governance/eval/k1-stop-replay-2026-08-05.txt`（腳本同目錄可重算）。
