---
type: issue
status: open
created: 2026-07-05
updated: 2026-07-05
tags:
  - type/issue
  - status/open
  - priority/P2
related:
  - "[[主動影響幅度偵測_計劃]]"
summary: |-
  FLAG:DECISION
  KEY:lumos-design-loop 機制缺陷——每輪把 finding 折進 spec body 後,summary/schema 範例/審計紀錄/天花板無機械綁定要同步 → 下輪審計員花 finding 抓「植入者沒同步的漂移」而非新設計問題;污染 G2 枯竭判準、拉長輪次、讓真收斂被自傷 finding 遮住
  KEY:實證來源=「主動影響幅度偵測」9 輪 loop:findings 10→7→7→8→6→5→5→8→7 不枯竭,經測約 ~2 finding/輪是折入漂移(summary 殘留舊記號/審計紀錄未標翻案/schema 範例與 body 不同步),非真設計缺口
  KEY:修法方向(機械守衛非靠紀律)=給 lumos lint/refcheck 加文件內一致性檢查:① §-ref 解析(「見 §N」的 §N 必須存在,順帶機械擋 (a) 型 canary + 真 §漂移)② summary FLOW/KEY 提到的旗標/欄位/schema key 必須在 body 出現 ③ 審計紀錄被後輪翻案的條目需標 superseded
  DECISION:先記為 lumos 工具鏈改進 Issue(非某 spec 問題);真要做需自己走 brainstorm→design-loop(注意別遞歸)。與知識同步散落漂移同病根(需機械守衛逼)
  DEP:[[lumos-refcheck]]
  DEP:[[design-loop]]
---
# design-loop 折入漂移 → 需機械守衛

## 問題(實證發現)

`lumos-design-loop` 每一輪:審計員找 finding → 植入者(Claude)把 finding **折進真檔 spec 的 body**。但 spec 的其他表述(frontmatter `summary` block、`--json` schema 範例、`## 審計修正紀錄`、`## 誠實天花板`)**沒有機械綁定要跟著同步**,靠植入者記得手動同步。

→ 下一輪乾淨審計員讀到「body 改了、summary/schema/紀錄沒跟上」的**內部漂移**,把它當 finding 報。**這些 finding 是 loop 機制的自傷,不是設計本身的缺口**,卻:
- 污染 **G2 發現枯竭** 判準(findings 數被自傷灌水、永遠不枯竭)
- 拉長輪次(每輪 ~2 finding 花在補漂移)
- 讓「真收斂」被自傷 finding 遮住,難判斷何時該停

## 實證

「[[主動影響幅度偵測_計劃]]」9 輪 loop findings 軌跡 **10→7→7→8→6→5→5→8→7**,不枯竭。逐輪拆解約 **~2 finding/輪是折入漂移**:
- r6-F1 / r9-F3:summary KEY 殘留舊「2..depth」記號(body 已改)
- r4-F3 / r9-F4:審計紀錄某條被後輪翻案卻沒標 superseded
- r8-F5(部分)/一致性掃描抓的:schema 範例與 body 演算法不同步

即使中途做了兩次「整體固化 pass」手動補漂移,下輪仍冒新漂移——**手動同步壓不住,需機械守衛**。

## 修法方向(機械守衛,非靠紀律記得)

給 `lumos lint` / `refcheck` 加**文件內一致性檢查**(spec 內部,不只 spec→repo):
1. **§-ref 解析**:body/summary 裡 `見 §N`、`§N〈...〉` 的 `§N` 必須對到實際存在的 `## §N` 標題。**副效益**:機械擋掉 design-loop 的 (a) 型 canary(壞 §交叉引用)+ 真實 §漂移。
2. **summary↔body 欄位一致**:`summary` FLOW/KEY 提到的旗標(`--xxx`)/config 欄位/schema key,必須在 body 出現(反向亦可警示 body 有、summary 漏)。
3. **審計紀錄翻案標記**:`## 審計修正紀錄` 內某條若被後輪條目否定,需標 `superseded`/`已被 rN 翻案`(這條較難全自動,可先做半自動提醒)。

①②機械可行且高價值(①順帶強化 canary 防線);③偏語意,先做提醒級。

## 現況 / 下一步
- 先記為 lumos 工具鏈改進 Issue。真要實作需自己走 brainstorm→design-loop(⚠ 注意別遞歸:改 design-loop 的工具本身也會過 design-loop)。
- 與「知識同步散落、機制同步只改最相關段漏散落列舉」同病根——都要機械守衛逼,人手動(含 Claude 折入)都會漏。
