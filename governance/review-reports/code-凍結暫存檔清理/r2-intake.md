# code-凍結暫存檔清理 r2 收貨

席報告 2 份(正確性 1 條、架構對齊 2 條,全部 minor)。quote-check 全錨。兩席都沒讀上一輪報告,收貨看 git status 沒動 repo。

彙整 id:正確性 c4、架構對齊 a4–a5。

## 歸因

- c4:原有漏查——擋下前先跑處置閘印 PASS、擋下訊息走 stderr,修前修後結構一樣(正確性席兩版讀碼並在 fixture 實跑 `| tail -1`)。上一輪照工具鏈會談建議只改了訊息文字,沒解決順序。
- a4(`unlink(missing_ok=True)` 全檔唯一)、a5(函式內重複匯入 uuid):上一輪修補引入的寫法差異。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c4 | t_loop_replay_freeze_leaves_no_tmp ② 新斷言:被擋時 stdout 不得有 `[disposal]`、`GATE PASS` | 修前 stdout 有整串 [disposal] 與 PASS | HIT |
| a4 | grep `missing_ok=True` 整支 scripts/lumos | 只有這一處 | HIT |
| a5 | grep `^import uuid` | 頂層第 59 行已有 | HIT |

## 處置

全折(3 條):
- c4:重凍缺 --note 的檢查提前到跑處置閘、寫暫存檔之前(判定檔路徑那時就算得出來),被擋時不印任何 [disposal] 與 PASS;訊息講現行是第幾輪(那時還不知道這次要凍的是第幾輪,拿掉那半句)。故意把檢查挪回處置閘之後,新斷言翻紅。
- a4:清理改成 `os.unlink` 加 `except OSError`,照 `_write_lf`。
- a5:改用頂層 `uuid`。
