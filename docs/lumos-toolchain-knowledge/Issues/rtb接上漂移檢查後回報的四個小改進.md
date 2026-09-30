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
  PITFALL:[2026-09-30 rtb 會談更新到 390e5359 後的回報]四個小改進,都不影響判定:①`lumos install --force` 會把 ~/.local/bin/lumos 改指到執行它的那份,在 git worktree 或暫存目錄裡跑會讓全域 lumos 指到會被刪的目錄,應至少警告;②漂移檢查起點那句把四種原因(沒有遠端預設分支、沒有 upstream、沒有遠端 main/master、就是這次推的那條)擠在一句,應印實際是哪一種;③起點被截到推送前掛鉤的上線點、範圍變空時什麼都不印,看的人分不出是沒跑還是跑了沒發現,應講一聲;④doctor [P] 段把筆記裡的指令「scripts/lumos impact --file」當成已不存在的檔案路徑(誤報) [test:待補]
related:
  - "[[Systems/存量漂移守衛]]"
  - "[[Projects/舊句檢查_計劃]]"
---
# rtb接上漂移檢查後回報的四個小改進

## 來由

2026-09-30 工具鏈推上舊句檢查(390e5359)後,請 rtb 會談更新工具。rtb 用 `lumos update --source <自己的 clone>` 更新(rc0),推上 8330d60,回報了下面四條。都只影響訊息或安裝便利,不影響漂移檢查的判定。

## 四條

1. **install 在 worktree 或暫存目錄執行**:`cmd_install` 會把全域 `~/.local/bin/lumos` 改指到 `Path(__file__)`。rtb 是在臨時 worktree 裡跑 update,刻意沒跑 install,否則全域 lumos 會指到之後會被刪的目錄。應在 `__file__` 位於 git worktree(非主工作樹)或系統暫存目錄時警告,或要求確認。
2. **起點那句太籠統**:`_push_range_start` 找不到主線時那句把四種原因列在一起;rtb 那次實際是「推的就是主線本身」。應只印實際成立的那一種。
3. **截到上線點時沉默**:推送範圍被截到掛鉤上線點、截完是空的時候,c1–c5 與舊句檢查都不印任何東西(rtb 接上掛鉤的那次推送就是這樣)。應印一行「這次範圍在掛鉤上線之前,沒有要查的」。
4. **doctor [P] 誤報**:rtb 的 `Issues/Phase14後筆記漂移清理` 裡寫的指令「scripts/lumos impact --file」,被 [P] 段當成已不存在的檔案路徑。

## 要做的

- 四條都小,下次動到對應那段時一起修;修的時候各補一支測試(把修法改回去會紅)。

REVISIT:2026-11-15 看這四條有沒有在別的改動裡順手修掉;沒有就排進一次小改動
