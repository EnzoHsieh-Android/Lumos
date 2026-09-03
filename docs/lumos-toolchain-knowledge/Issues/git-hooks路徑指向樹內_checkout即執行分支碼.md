---
type: issue
status: open
created: 2026-09-03
updated: 2026-09-03
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
summary: |-
  FLAG:
  DECISION:
  KEY:
related:
  - "[[Projects/派工鏡頭注入_計劃]]"
  - "[[Systems/anchor-integrity]]"
---
# git-hooks路徑指向樹內_checkout即執行分支碼

> 白話:本 repo 把 git hooks 裝在版本控制的樹裡(`core.hooksPath=scripts/hooks`),好處是 pre-commit/pre-push 跟著 repo 走、每台機器一致;壞處是★checkout 任何分支,就會執行那條分支裡的 hook 檔★。送審的分支若加一支 `scripts/hooks/post-checkout`(或改既有三支),審查者一 checkout 就跑攻擊者的碼——改本地 ref、改 `~/.claude`、什麼都能做。

## 怎麼發現的

2026-09-03 [[Projects/派工鏡頭注入_計劃]] r3 載荷安全席在暫存 repo 實測 `git checkout` 觸發樹內 hook 任意執行;編排者先寫「本 repo 未指向樹內」,查 `git config core.hooksPath` 才發現就是 `scripts/hooks`。

## 為什麼現有防線擋不住

- 錨點([[Systems/anchor-integrity]])只擋「改了錨點檔還想 push」,不擋「checkout 別人已經 push 上來的分支」;而且只錨三支既有 hook,新增一支 `post-checkout` 不在清單。
- CI 跑的是分支內容,同樣會執行。

## 影響範圍

任何會 checkout 他人分支的流程:本機代碼審、`lumos-code-loop` 的 worktree 驗證席、CI。信任模型實際上是「能 push 分支的人=能在審查者機器上執行碼的人」——這在單人 repo 是可接受的現況,多人協作前必須處理。

## 候選處置(未裁)

1. hooksPath 改指向樹外(`~/.lumos/hooks/`),由 install.sh 複製並由錨點比對來源;代價=每台機器多一步、hook 更新要重跑安裝。
2. 保留樹內,但 code-loop 驗證席與 CI 在 checkout 前先 `git config core.hooksPath /dev/null`;代價=只保護自動流程,不保護人手 checkout。
3. 接受現況,寫成單人 repo 的界線;REVISIT 綁事件:第二個協作者加入前必裁。

REVISIT:2026-12-01 若仍單人 repo,確認第 3 項仍成立;若已多人,必須在此之前裁 1 或 2。
