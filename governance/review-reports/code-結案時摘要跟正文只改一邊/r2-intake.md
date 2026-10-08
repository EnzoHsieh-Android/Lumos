# code-結案時摘要跟正文只改一邊 r2 收貨

席報告 2 份(正確性r2 3 條 minor、架構對齊r2 3 條含 1 major)。

彙整 id:正確性r2 d1–d3、架構對齊r2 b1–b3。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| b1 | Grep:`_ns_close_summary_collect`/`_ns_close_summary_emit` 呼叫 `_drift_note_status`、`_drift_summary_is_current` | 兩處直呼 | HIT |
| d1 b2 | 補 ⑩⑪ 先紅後綠;翻紅「doctor 不接」「設定提醒不印」各自紅 | — | HIT |
| d2 | 補 ⑫(單行摘要結案)先紅後綠;翻紅「摘要切法只認前綴行」紅 | — | HIT |

## 處置

全折(6 條):入口吃兩版全文、note-shape 不碰存量漂移其他函式(b1);摘要切法改用 c7 那套(d2);開關寫錯值提交時講、doctor 開頭講(d1 b2);換行路徑挑掉算進沒看(d3);記帳欄位補 rules、lines(b3)。
