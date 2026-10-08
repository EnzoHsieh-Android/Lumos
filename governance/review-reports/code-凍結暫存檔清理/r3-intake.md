# code-凍結暫存檔清理 r3 收貨

席報告 2 份(正確性 1 條、架構對齊 1 條,全部 minor)。quote-check 全錨。兩席都沒讀前兩輪報告,收貨看 git status 沒動 repo。

彙整 id:正確性 c5、架構對齊 a6。

## 歸因

- c5:修復回歸——上一輪把 --note 檢查提前到處置閘之前,寫入端沒留第二道;兩個第一次凍結並行、都沒帶 --note 時,後到的那邊歸檔前一份、在 `note.strip()` 崩潰,判定檔已換卻沒有治理帳留痕(正確性席 in-process 探針實跑)。
- a6:上一輪修補引入的寫法差異(判定檔路徑組兩次)。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c5 | 讀碼核對:提前檢查在 `cmd_loop_replay` 的 freeze 開頭;`_replay_write_verdict` 的 `if target.exists():` 歸檔前不看 note;呼叫端 `_loop_gov_mark(..., note.strip())` | note=None 時 AttributeError,路徑走得通 | HIT |
| a6 | 讀碼:`_cur_v` 與後面的 `target` 各組一次同一路徑 | 兩次 | HIT |

## 處置

這是 standard 的第 3 輪(上限)。兩條都 minor;修的話要再派一輪看修正,會超過上限、要人裁。附理由放行 2 條:
- c5:要兩個 `--freeze` 同時對同一個編號做「第一次」凍結、而且都沒帶 --note 才會發生;主線上的凍結都是人一次一個跑。家筆記寫了一條 REVISIT:2026-10-21,合併後另開小修正、照流程單獨審,在寫入端再判一次。
- a6:行為相同,只是路徑組兩次;跟 c5 的小修正一起收。
