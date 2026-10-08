# code-過期鎖安全接手 r2 收貨與處置

新鮮的兩個唯讀 `codex exec` 進程分別讀同一份 397 行 delta，凍結檔 `r2-snapshot.patch` SHA-256 `9fe58e931d940d0b526eaa4c512ae64dd226641b513f06a80488fc67b71296f1`；完整前輪卷證沒有派給它們，收齊前未改審材。`quote-check`、`refcheck`、`report-normalize` 全過。

| id | 重現 | 處置 |
|---|---|---|
| R2-01 | HIT：第一次取得鎖後背景啟動失敗，helper 釋放原鎖；另一呼叫者取得新鎖，舊等待端命中快取時按 `already=False` 刪除新鎖。審查席現場得到 rc 0 且 replacement lock 消失；永久測試先紅 `acquired=True lock=False`，改成等待端只讀快取後綠 `acquired=True lock=True`。正常背景程序自行核對啟動者再清鎖，整合測試 8 項綠。 | folded |
| A1 | HIT：抽出的 `_lens_lock_timeout` 名稱看不出會輸出 JSON／人話，與同層輸出 helper 慣例不一致。改名 `_lens_report_lock_timeout`，呼叫點同步。 | folded |

這一輪證明「只讓非持有者不刪」仍不夠：起初持有過不等於現在仍持有。第三輪須用全新的 delta 掃描這次移除等待端刪鎖與改名，尤其檢查背景正常清鎖與失敗路徑；原先的同版單持有聲明在第三輪與機械閘過關前仍不升格。
