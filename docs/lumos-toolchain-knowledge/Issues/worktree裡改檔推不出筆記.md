---
type: issue
status: resolved
created: 2026-10-02
updated: 2026-10-02
aliases: []
about_code: []
tags:
  - type/issue
  - status/resolved
  - scope/retrieval
summary: |-
  FLAG:TECHNICAL
  PITFALL:[2026-10-02]Claude Code 在主 repo 啟動、之後切進 git worktree(或直接改另一個 worktree 裡的檔),改檔前推播一篇都不出現、也沒有任何提示。根因:推播 hook 用啟動目錄當 repo,拿主 repo 去查 worktree 裡的檔,查詢回 0 筆、hook 靜默放行。[test:t_impact_hook_repo_follows_worktree]
  WHY:[2026-10-02]修法只認「同一個 repo 的另一個 worktree」,不跟去不相干的 repo——跟去會把陌生 repo 的筆記推進對話;細節在 Systems/改檔前推播 的 WHY
  FACT:[來源:生產][Claude Code 2.1.287,2026-10-02]切進 worktree 後,hook 事件帳記下的 repo 仍是啟動目錄,對話紀錄記的目錄才跟著換
related:
  - "[[Systems/改檔前推播]]"
  - "[[Projects/推播miss量測_計劃]]"
---
# worktree裡改檔推不出筆記

> **已結案(2026-10-02)**:改檔前推播已修好,worktree 裡改檔會用那個 worktree 的圖譜查。同一種找 repo 寫法的另外三處另列在最後一節,附回頭檢查日。以下「症狀」與「根因」是當時的排查紀錄,不是現況。

## 症狀

- 照全域規則開 git worktree 做事的 session,改檔前一篇筆記都推不出來,而且沒有任何錯誤或提示。
- 2026-10-02 試做 Claude Code mod 時,為了測推播去重切進 worktree,才發現推播整個消失。
- 實測對照(同一支檔、同樣的改動):啟動目錄指主 repo → 推 0 字;指 worktree → 推 1152 字。

## 根因

- 推播 hook 用「Claude Code 的啟動目錄」當 repo,沒有才用 hook 收到的目錄。這個順序是當初為了「hook 行程的目錄不一定在 repo 根」定的,見 [[Projects/主動影響幅度偵測_計劃]];當時沒有考慮 worktree。
- 用 Claude Code 內建方式切進 worktree 後,啟動目錄變數不變,hook 行程也還是在主 repo 跑(hook 事件帳在那段時間記的 repo 是主 repo)。
- 於是拿主 repo 的圖譜去查一支 worktree 裡的檔:查詢回 0 筆 → hook 判定沒東西可推 → 撤掉冷卻標記、靜默放行。

## 現在怎麼繞

- 不用繞了:推播 hook 改成「被改的檔若在同一個 repo 的另一個 worktree,就用那個 worktree 當 repo」,見 [[Systems/改檔前推播]]。
- 已安裝在使用者家目錄的那份 hook 要重新安裝才會換成新版。

## 什麼條件算修好

- 防回歸測試涵蓋五種情況並全綠:worktree 裡的檔換 repo;不相干 repo、主 repo 自己的檔、相對路徑都照舊;git 查詢失敗時退回原本做法。
- 端對端:用修好的 hook,啟動目錄指主 repo、改 worktree 裡的檔,推出來的內容要列出那支檔的家。2026-10-02 實測從 0 字變成 1086 字,家正確列出。

## 同一種寫法、還沒修的地方

這幾支也是先用啟動目錄找 repo,切進 worktree 時一樣會看錯地方。後果比推播輕,所以這次沒一起修:

- 收工前檢查圖譜同步的 hook:會去看主 repo 的改動,漏看 worktree 裡的。worktree 自己的提交前檢查照樣會擋,所以只少了提醒。
- 派工鏡頭 hook:拿主 repo 的圖譜算子代理的影響範圍。git 歷史是共用的,但圖譜用的是主 repo 當下那份,可能跟 worktree 分支不一樣。
- hook 事件記錄器:把 worktree 裡發生的事件記進主 repo 的帳。

REVISIT:2026-10-16 逐支確認這三處在 worktree 裡的實際後果;值得修的照推播 hook 的做法改,並各補一條先紅的測試。

## 線索(未驗證)

[[Projects/推播miss量測_計劃]] 量到「上週有編輯的主 session 逐字稿只有 1 份」,當時推測是量測腳本把 worktree 的逐字稿篩掉了。這個 bug 會讓 worktree session 根本沒有推播可量,可能是同一件事的另一面,但我沒有驗。
