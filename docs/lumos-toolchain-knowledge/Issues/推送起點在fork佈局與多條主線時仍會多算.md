---
type: issue
status: open
created: 2026-09-30
updated: 2026-09-30
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - scope/guards-gates
summary: |-
  PITFALL:[2026-09-30 推送閘接漂移檢查代碼審驗收輪 正確性席 F1–F3、外家否決席 F1]漂移檢查的推送起點(`_push_range_start`)在四種少見佈局下仍會算錯:①本地 main 的 upstream 設成本機另一條分支、推那條分支時判成「沒有新東西」而漏查(相對第 2 輪修正前是退步);②分支同時合了兩條互不包含的主線,只取一個分岔點,另一條主線上別人的轉正被算成這次的;③GitHub 教的 fork 佈局(本地 main 追自己 fork 的 origin/main),正本的 main 不在候選裡,新分支首推與同步 fork main 都會多算;④數分岔點深度的 git 呼叫逾時時仍任選一個起點 [test:t_prepush_drift_start_mainline_shapes]
  WHY:[2026-09-30 編排者裁,Enzo 睡前授權]驗收輪(上限後破例的一輪)只剩 minor,不再改碼:漂移檢查預設只提醒(block 要專案自己設),CI 會對同一次推送再查一次;四種都要非單一主線的佈局,工具鏈與 rtb 目前都只有 main。改動要重新過代碼審,所以留到有人真的碰到或 REVISIT 那天
related:
  - "[[Issues/推送前其他閘的範圍在合過主線時會多算]]"
  - "[[Systems/存量漂移守衛]]"
  - "[[Systems/bound-tests-gate]]"
---
# 推送起點在fork佈局與多條主線時仍會多算

## 現象

推送閘接漂移檢查的代碼審在第 3 輪到頂後開了一小輪驗收(只看第 3 輪修正差異),三席抓到四條 minor,卷證在 `governance/review-reports/code-推送閘接漂移檢查/r4-*`:

1. 本地 main 的 upstream 設成本機另一條分支(例如 develop),推 develop 時這個候選就是被推的頂端;新寫法只比「遠端/分支」全名,本機分支的 upstream 不是遠端 ref,不會被跳過,整道判成「沒有新東西」回 0。第 2 輪修正前同一輸入會擋(正確性席實測)。
2. 分支同時合了 develop 與帶 hotfix 的 main(兩條互不包含)時,`merge-base --all` 回兩個分岔點,只挑歷史最長的一個當起點,另一邊主線上別人的轉正被算進來,block 模式誤擋。第 2 輪修正前也一樣。
3. GitHub 文件教的 fork 佈局:本地 main 追自己 fork 的 origin/main、正本叫 upstream。正本的 main 不在候選清單(候選只有被推遠端的 HEAD/main/master 與 main/master 的 upstream),新分支首推到 fork、同步 fork 的 main 兩種推送都會多算。第 3 輪新加的兩條 fork 測試都先把本地 main 設成追正本,沒測到這個佈局。
4. 數分岔點深度(`rev-list --count`)的 git 呼叫逾時時,仍任選一個起點,可能漏查(外家否決席,未能在真環境重現)。

## 要做的

- 讓漂移檢查的核心能吃「頂端排除多個分岔點」(`git rev-list 頂端 --not 基底一 基底二…` 的形狀),不再只收 `A..B`:②、③(把所有遠端的 main/master 都當候選)一起解。
- 本機分支當 upstream 時,用 `rev-parse --symbolic-full-name` 解出來是 `refs/heads/…` 就跳過(①)。
- 深度計數逾時照「判不了」處理(④)。
- 以上要重新過代碼審;測試要照 checkout 或 fork 的真步驟建 repo,不准測試自己先補設定。

REVISIT:2026-10-31 看工具鏈與 rtb 的治理帳有沒有漂移檢查在非單一主線佈局下誤擋或漏查的紀錄,有就照上面做;沒有就順延兩個月
