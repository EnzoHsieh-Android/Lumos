# code-結案時摘要跟正文只改一邊 r1 收貨

席報告 2 份(正確性 4 條、架構對齊 5 條)。quote-check 全錨;refcheck ok。

彙整 id:正確性 c1–c4、架構對齊 a1–a5。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c1 | 正確性席臨時 repo 暫存 400 篇只改 status:舊版 3.9 秒、新版 78 秒;編排者修後量 400 篇只改 updated 2.7 秒、400 篇同時結案 2.4 秒 | 修後放行 | HIT |
| c4 | 編排者對本 repo 跑 `_drift_state_findings` 列 c7:4 筆,2 筆是 WHY/帶日期 KEY 的歷史句 | 修後 WHY、PITFALL 不列 | HIT |
| c2 c3 a3 a4 | 補測試格 ⑥–⑨(S1)、⑥⑦(S2)先紅後綠;翻紅 5 處紅 | — | HIT |

## 處置

全折(9 條):讀版本改批次讀、只看狀態行有動、上限 50 篇(c1 a2);判定收成存量漂移那層一支入口(a1);改名同時結案照算、引號照既有解析(c2);drift fix --kind c7 指路(c3);c7 不看 WHY、PITFALL(c4);記 hinted 帳(a3);收集與印出拆開、加 note_shape.close_summary 開關(a4);摘要比對改邏輯行(a5)。
