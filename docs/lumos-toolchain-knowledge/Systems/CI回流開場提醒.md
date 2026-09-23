---
type: system
status: doing
created: 2026-09-23
updated: 2026-09-23
responsibility: 開場時讀 CI 帳,當前提交的 CI 是紅的就提醒一次;只讀帳不打網路、不跑 CI、不寫帳(寫帳是 ci-wait 的事)。Claude 與 Codex 共用這一支(安裝時各複製一份)
aliases: []
about_code:
  - scripts/hooks/claude/ci-status-hook.py
tags:
  - type/system
  - status/doing
  - scope/guards-gates
related:
  - "[[Projects/CI回流閉環_計劃]]"
summary: |-
  WHY:[2026-09-23]這支 hook 在 CI 回流閉環上線時就有,但一直沒有家;這次修它的判法時補上。
  PITFALL:[2026-09-23 實踩]★同一個 CI 執行重跑過,只算最後一次嘗試★:判「上次 CI 是紅的」是對當前提交的全部筆取最壞,那是為了多支 workflow 各記一筆時綠的不要蓋掉紅的;但同一個執行重跑也是新的一筆,第 1 次紅、第 2 次綠時舊的紅永遠贏——重跑變綠了,開場還一直喊紅。現在先把同一個執行只留最後一次嘗試,再跨執行取最壞。同一個執行的編號一筆存數字、一筆存字串也算同一個;同一次嘗試有兩筆結論不同時留比較糟的那筆(紅 > 取消或跳過 > 成功),不看在帳裡的先後(代碼審 r1、r2)。重現:帳裡同一個 run_id 寫一筆 attempt 1 紅、一筆 attempt 2 綠,開一個新會談 [test:t_ci_rerun_latest_attempt_wins]
  RULE:[since:2026-09-23][confirmed:2026-09-23][retire:hook 改成能 import 主程式(不再是獨立複本)]★判法在主程式與這支 hook 各有一份逐字相同的複本★:hook 是獨立檔,複製到全域後 import 不到主程式。改了一邊沒改另一邊,主程式的 ci-status 與開場提醒對同一次 CI 會給相反結論;有測試比對所有複本的語法樹——★掃主程式加整個 hooks 目錄、函式從整棵樹找(包在 if、class、另一個函式裡的也算)、連 async 定義都算★;函式裡那組「算紅」的結論也要跟各檔自己的常數一致。守衛前兩版分別寫死兩個路徑、只看最外層,都被代碼審實際塞進錯的複本證明是假綠 [test:t_ci_latest_attempts_copies_identical]
  PITFALL:[2026-09-23 同一次實踩的另一半]★CI 重跑之後要再跑一次 `lumos ci-wait`★,不要只用 gh 看結果——不跑的話成功那次根本不會進帳,ci-status 與開場提醒讀到的永遠是重跑前那筆。重現:`gh run rerun <id> --failed` 後不跑 ci-wait,直接 `lumos ci-status`
---
# CI回流開場提醒

`scripts/hooks/claude/ci-status-hook.py` 在開場時讀 CI 帳,當前提交的 CI 是紅的就提醒一次。只讀帳,不打網路、不跑 CI、不寫帳——寫帳是 `lumos ci-wait` 的事,唯讀查詢是 `lumos ci-status`(兩者都在主程式裡,這篇只管這支 hook)。

Claude 與 Codex 共用這一支檔,安裝時各複製一份到全域的 hooks 目錄。
