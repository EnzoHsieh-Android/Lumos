# code-凍結並行重凍防線 r1 收貨

席報告 2 份(正確性 1 條、架構對齊 1 條,全部 minor)。quote-check 全錨。收貨看 git status 沒動 repo。正確性席另外實測:拿掉寫入端那道判定,新測試三個檢查全紅。

彙整 id:正確性 c1、架構對齊 a1。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c1 | 讀碼:`_replay_write_verdict` 的 `if target.exists():` 與 `os.replace(tmp, target)` 之間沒有鎖;主線版(修前)同一段同樣如此 | 空檔存在、原本就有 | HIT |
| a1 | 讀碼:`_replay_refreeze_blocked` 只印訊息、呼叫端 return 2;`_anchor_blocked` 同形、`_escape_log_guard` 回 rc | 兩種寫法專案都有 | HIT |

## 處置

附理由放行 2 條(沒有 major,這輪不改碼,不需要再派席看修正差異):
- c1:主線原本就有的檢查與寫入之間的空檔,這次修的是「沒帶 --note 的重凍不得歸檔別人的檔、不得崩潰」,已達成;剩下的空檔要兩個第一次凍結在同一瞬間撞上,而且要改成不覆蓋的建立方式才能根除。家筆記補一條 REVISIT:2026-12-08,查到一筆就改用 os.link。
- a1:專案內兩種寫法都有(`_anchor_blocked` 同本案、`_escape_log_guard` 回 rc),架構對齊席自己也傾向不算缺陷。
