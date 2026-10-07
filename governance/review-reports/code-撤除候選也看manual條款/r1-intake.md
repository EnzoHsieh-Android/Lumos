# code-撤除候選也看manual條款 r1 收貨

席報告 2 份(正確性 2 條 minor、架構對齊 1 條 major + 1 條 minor)。quote-check 兩份全錨。

彙整 id:正確性 c1–c2、架構對齊 a1–a2。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c1 | 測試格⑧:同一行 `[test:test_alive] [manual:開頁面目測一次]`、下一層寫撤除 | 修前列兩行(一行講 [test:]、一行講 [manual:]) | HIT |
| c2 a1 | 測試格⑦:`[manual:x]`(1 字,條款解析 `_MANUAL_MIN_CHARS`=4 判未標)、下一層寫撤除 | 修前列出;自寫 MANUAL_REF_RE 再解析一次,跟 clause_bindings 的 state 口徑不同 | HIT |
| a2 | lint 看守檔筆記新 WHY 行 | 行內沒有 [因:] | HIT |

## 處置

全折(4 條;輪內有 major,依規不放行):`_ns_tr_manual_clauses` 改成直接取 `clause_bindings` 判 state=manual 的條款,不再自己解析 `[manual:]`(c1 c2 a1 一起解);守檔筆記 WHY 行補 [因:](a2)。測試原範例 `[manual:看畫面]` 只有 3 字,照條款解析是未標,改成夠長的說明。翻紅:改回只看有沒有 manual 值 → ⑧紅;⑦在新寫法下由條款解析本身擋。
