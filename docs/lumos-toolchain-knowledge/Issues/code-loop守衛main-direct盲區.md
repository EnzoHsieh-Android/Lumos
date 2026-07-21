---
type: issue
status: open
created: 2026-07-21
updated: 2026-07-21
tags:
  - type/issue
  - status/open
related:
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Projects/loop機械脊椎M1包_計劃]]"
pitfall_when:
  - "glob:scripts/hooks/pre-push"
  - "content:code-loop check"
summary: |-
  FLAG:TECHNICAL
  KEY:pre-push 的 tier=high→code-loop 硬擋守衛以 merge-base..HEAD 算 diff——**直接 commit 在 main 上時 merge-base==HEAD、diff 恆空→tier 恆判 standard→守衛空轉放行**(2026-07-21 M1包 落地實測:pitfalls --diff 對實際變更判 high,code-loop check 卻 OK「無 branch diff」)。hook 為 feature-branch 終審設計,main-direct 工作流=結構性繞過
  KEY:影響面=凡 main-direct 的 gate/守衛類 code 變更都不會被 code-loop 硬擋——把關точка失效,只剩散文紀律(編排者自覺調用 lumos-code-loop)
  KEY:候選修法(未裁)——①pre-push 對 main-direct push 改用「本次 push 的 range(remote..HEAD)」算 tier ②家規化:gate 類 code 一律 feature branch(紀律面,無機械強制) ③兩者並行。動 hook=改守衛,修法本身須過 design-loop
  KEY:發現脈絡=M1包 實作 push 後自查(spec 明言「實作後 pitfalls 必判 high→full code-loop」但 push 未被擋);該批 code 的補救=事後 code-loop 終審(使用者裁定中)
---
# code-loop守衛main-direct盲區

pre-push 守衛（scripts/hooks/pre-push:64-88）：`pitfalls --diff` 判 tier=high 時跑 `lumos code-loop check`，blocked 才硬擋。但 `code-loop check` 以 **merge-base..HEAD** 為 diff 範圍——在 main 上直接 commit 時 merge-base==HEAD，「無 branch diff」→ tier=standard → OK 放行。

**實測（2026-07-21）**：M1 包 gate code 落地 push，`pitfalls --diff a08c971..HEAD` 對實際變更判 `tier: high`，但 push 時 `code-loop check` 回 OK。整天的 main-direct commit 全數繞過此閘。

修法候選見 summary；動 hook 屬改守衛，須過 design-loop。
