---
type: project
status: done
created: 2026-07-19
updated: 2026-07-20
tags:
  - type/project
  - status/done
related:
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/pitfalls-code-loop]]"
summary: |-
  KEY:把[[Systems/效能檢核目錄]]的棧別效能提問接進三個時機點——①pitfalls --diff 按棧附追問(diff 副檔名認棧既有機制,命中 kt/cs/vue/sql 附該棧效能三問進 manifest→自動流進 pre-push 提示+code-loop 鏡頭)②impact hook 動手前注入(同一問題表)③pass 留痕含檢核答案(散文紀律);內容源單一=效能檢核目錄節點,問題表勿雙寫
  KEY:Vercel 實證錨——靠模型自己想起查規範 56% 跳過→機制推送不靠自覺;提問式>陳述式(pitfalls 逼答哲學)
  KEY:範圍刀——①動 scripts/lumos(pitfalls 問題表按棧分組+manifest 附問)=真代碼,TDD+standard 終審;②impact hook 注入=動 hook 檔(anchor 保護,approve 走正門);③純紀律。不新增宣告檔(問題表內建 lumos 自帶,同 PITFALL_QUESTIONS 慣例);不做效能自動評分(oracle 教訓)
  DEP:[[Systems/效能檢核目錄]]｜[[Systems/pitfalls-code-loop]]
  DECISION:[2026-07-19]問題表自帶於 scripts/lumos(同 _PITFALL_QUESTIONS 慣例)而非宣告檔——檢核問題是方法論資產跨專案同一份,非專案配置;內容與效能檢核目錄節點同步義務記入(防雙寫漂移,散落漂移家規)(valid)
verified_by:
  - "[[Verification/2026-07-20_棧別效能追問]]"
---
# pitfalls棧別效能追問_計劃

> 把 [[Systems/效能檢核目錄]] 的棧別效能提問接進工作流三時機(動手前/終審/蓋章前),讓最佳實踐「被推到眼前」而非靠 Claude 自己想起(Vercel 實證:自覺路徑 56% 跳過)。

PRIOR-ART: ① 最小解——pitfalls 已按副檔名認棧、已有 _PITFALL_QUESTIONS 提問表,本計劃=該表按棧分組+三問內容;impact hook 已存在,加注入段。零新機制。② 世界解過——Claude Code hooks 保證注入模式(2026 社群共識)+lumos 自家 impact hook 先例。③ 裁定=borrow-design。

## 交付

1. **[T1] ✅(2026-07-19)pitfalls --diff 按棧附追問**(scripts/lumos,TDD;t_pitfalls_stack_questions 6 斷言):
   - 問題表 `_STACK_PERF_QUESTIONS = {"kt": [...3問], "cs": [...], "vue": [...], "sql": [...]}`(內容抄自效能檢核目錄「人判提問」欄,每棧取最載重 3 問)。
   - `--diff` 命中某棧檔案時,manifest 尾附該棧追問(同既有 class 追問格式);`--json` 帶 `stack_questions` 欄。
   - 自動生效面:pre-push 印 tier 時帶出+code-loop reviewer 拿 manifest 即拿到問題。
   - 測試:t_pitfalls_stack_questions(命中 kt 附 Compose 問/未命中不附/json 欄位)。
2. **[T2] ✅(2026-07-19)impact hook 注入段**(實作走單源路線:lumos impact --ranked --json 輸出帶 stack_questions[冷卻 incidents-only 快速路不帶,尊重降噪],hook 只格式化不持有表——比原構想更防雙寫;hook 檔不在 anchor baseline 免 approve;t_impact_hook_stack_questions 3 斷言):
   - PreToolUse 注入時,若目標檔副檔名命中問題表 → 尾附該棧效能三問(一行一問,同現有注入格式)。
3. **[T3] ✅(2026-07-19)蓋章紀律**(code-loop SKILL 收斂節一句):pitfalls manifest 含 stack_questions 時,pass --note 須含對應檢核答案(同接受理由紀律)。
4. **同步義務**:效能檢核目錄節點改 → `_STACK_PERF_QUESTIONS` 同步(反向亦然);漂移守衛=測試斷言表中每棧問題數與目錄「人判提問」欄一致性(輕量:數量級檢查)。

## 終審折入(2026-07-19,單 reviewer standard 審)
- [major,實測重現] 三時機②③在最常見情境形同虛設——.kt 命中棧表但無 regex 命中→tier=standard→pre-push 不印、code-loop 不觸發,只剩①hook 活著 → 修:pre-push 加 standard+棧命中 advisory 分支(恆不影響 rc;anchor approve 走正門);T3 紀律擴及 standard 路(義務落終審紀錄/commit message)。
- [minor] hook 僅提問無節點時仍接「判上列節點」收尾指令=答非所問 → 修:有節點才接指令(+2 測試斷言,全套 1247)。
- 假陽記錄:本 diff 自身 tier=high 由單一命中觸發=cs 棧問題字串裡的「SELECT *」被掃描器認成 SQL(考卷把考題當作弊,data string 非執行碼)→ code-loop skip 留痕。

## 實務隱患
- 效能:注入量=每棧 3 問(行數小),hook 延遲可忽略;問題表純資料無網路。
- 提醒疲勞:只在 diff 真命中該棧才附;三問取最載重,不塞全表。
- 併發/冪等:無(純讀+格式化輸出)。

## 誠實天花板
- 提問保證被看見,不保證答對——答案品質靠審查員+辯方;無效能自動評分(oracle 教訓)。
- 三問是取捨:載重優先,覆蓋不全;全表在效能檢核目錄,審查員可自取。

## 進實作前(紀律)
T1 動 scripts/lumos=TDD+終審按 pitfalls --diff 分流;T2 動 anchor 檔走 approve;T3 純文字。整體貼 standard,可跳 design-loop 並註明(問題表+格式化 glue,實作真測>設計散文;同 test-layers 前例)。落地 Verification 以 plan_refs 回指。
