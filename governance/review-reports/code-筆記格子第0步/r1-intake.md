# r1 收貨與處置(code-筆記格子第0步,standard:正確性一席+架構對齊)

兩席收齊才動碼;報告從逐字稿原樣抽出。正確性席最後一行總結句格式不合,退回該席重寫(不由編排者改)。兩席引句全錨定,refcheck 全 ok。

## 重現

| id | 做法 | 結果 |
|---|---|---|
| C1 | `_ns_repo` 暫存 `RULE:大額退費要人工核可 [依據:人]` 跑 note-shape --staged | HIT:修前無任何提醒;修後補測試 t_rule_lifecycle_warns_at_commit ③,拿掉 slot_check 那段翻紅 |
| C2 | `note-shape --staged --slots` | HIT:參數不存在;範本改寫那一句 |
| C3 | `slot_check("SEE","[[A]]、[[B|別名]]")` | HIT,但別名不收是既有刻意決定(t_note_shape 系「別名夾帶現況」);改訊息與 reference.md 講明原因,不放寬 |
| C4 | 逐項拿掉值判斷跑 slots 子集 | HIT:補 10 條案例,逐項翻紅驗過 |
| C5 | `context_marker_warnings("WHY:\nRULE:\nFACT:")` | HIT:lint 改成空前綴不唸,測試 ⑤ |
| C6 | `SEE:Redis 連線上限是 200` 暫存 | HIT:note-shape 改成 SEE 夾句子擋,測試翻紅驗過 |
| A1 | 讀 `_rule_date`、`DATE_RE` | HIT:刪 `_slot_date`,改用 DATE_RE 加 `_rule_date` |
| A2 | 讀 S7/S8 的 gov_events 與 rule_lifecycle_warnings 的過期判斷 | HIT:抽 `_rule_stale_keys` 兩邊共用;S16 記 check-s16(已登記已知閘) |
| A3 | 對照否定現況句 prepare/collected/emit | HIT:補 `_ns_tag_hints_collected`,分解方式對齊 |

## 處置

全部折入(C1–C6、A1–A3),無放行、無駁回。C1 為唯一 blocking。
