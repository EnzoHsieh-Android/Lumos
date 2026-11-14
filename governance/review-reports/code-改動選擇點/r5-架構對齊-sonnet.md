severity: minor

## a1 不唯一行的放行提示在引號之後才跳脫,寫法跟同一組的鄰居不同
severity: minor
blocking: 否 結構對、只有處理順序與鄰居不同,不會讓放行指令變成執行別的東西。

引句:「f"lumos lint-waive {_kill_esc(_sh_quote(_CHOICE_WAIVE_PREFIX + str(x['file']) + ':' + str(x['line'])))} --note \"不適用:<理由>\"")」

- 輸入:檔名含雙向覆寫字元(例 `a b\u202e.kt`)、某行不唯一。
- 走到:`_choice_kill_report`(`scripts/lumos:78210`)。它先 `_sh_quote` 再 `_kill_esc`。
- 壞在哪:引號內的控制字元被換成字面 `\u202E`。貼回 shell 時,放行鍵跟 lint-waive 認得的 `choice:<原檔名>:<行>` 對不上,所以那一行放不掉。
- 同組鄰居 `scripts/lumos:78791` 寫成 `lumos lint-waive {_sh_quote(_CHOICE_WAIVE_PREFIX + point)} ...`,不再外包 `_kill_esc`。同一組「放行出口」有了兩種寫法。
- 平常的 ASCII 檔名、空白、`$(...)` 不受影響,引號照舊擋得住。
- 我沒有跑完整重現。只做了一次字串實驗,最後一步 `shlex.split` 回 IndexError,所以「貼不回」只有推論,沒有證據。
- 歸因:未判定。修前版本沒有 `_sh_quote`(差異是從不加引號改成加引號),我也沒跑修前版本的指令。
- 佐證:`scripts/lumos:468`(`_sh_quote`)、`scripts/lumos:78791`。

## 三問

1. **分層與依賴方向**:一致。修補只呼叫既有的 `_sh_quote`、`_kill_esc` 與 `_CHOICE_WAIVE_PREFIX`,沒有自己拼引號或繞過共用函式。對照 `scripts/lumos:468`、`scripts/lumos:78791`。
2. **命名與錯誤處理**:大致一致。放行指令的組字、`--note` 樣式都跟鄰居相同。差別只在 a1 說的跳脫順序。rc 與訊息沒動。
3. **第二種做法**:沒有。K3 的名稱剖析、K2 的快取傳遞和整批掃描關忽略規則,都不在本輪的 `r5-repair-code.patch` 裡。它只動 `scripts/lumos` 一處,其餘是帳本、筆記和錨點基線。我沒有去核對那些改動在別處的實作,所以那一塊未驗。

## 已驗與未驗

- 已驗:修後 `scripts/lumos` 只有 78210 一處用了「引號外再跳脫」,其他放行提示沒有。證據是 `grep "lumos lint-waive"` 的結果,只看了修後版本。
- 未驗:
  - 修前與修後兩版的行為對照。
  - K1 到 K3 的測試是否真的紅綠。
  - K2、K3 的程式碼本體。

不對齊共 1 條,其中 major 0 條
最嚴重:minor;blocking 共 0 條

圖譜鏡頭:這次沒附固定席節點,不逐條判。
