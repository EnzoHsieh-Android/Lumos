# r1 收貨(code-結案連帶掃描)

standard 分級:一位通才(正確性-sonnet)加架構對齊席(sonnet),收齊才動工作目錄。quote-check 全數錨定、report-normalize 不用改、refcheck 對得上。

## 發現

| id | 來源席 | 一句話 |
|---|---|---|
| E1 | 正確性 F1(major) | 子句切點正則的兩個分號都是半形,全形「；」不切:誤報 c6、修法把括號補到不相干的子句後面 |
| E2 | 正確性 F2 | doctor 的漂移段迴圈只列 c1 到 c5,c6 不出現 |
| E3 | 正確性 F3 | 已裁定括號按整行判,同一行補了一個待定子句,另一個也跟著消失 |
| E4 | 正確性 F4 | summary 寫成單行值時,值所在那一行被略過 |
| E5 | 正確性 F5 | --decision 的新句沒重驗待定詞,寫「還沒做」也能結案 |
| E6 | 架構對齊 F1 | 列出函式的出錯防護只包在 decision 兩處,set 與 drift fix 沒包 |
| E7 | 架構對齊 F2 | 改名後的 _closing_revisits 一支管三種列出,鄰居一事一函式 |
| E8 | 架構對齊 F3 | 另開第三份「已收尾」狀態常數 |
| E9 | 架構對齊 F4 | _drift_close_gates 回三樣東西,鄰居回 (結果, 錯誤);呼叫端又重算一次 |

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| E1 | 逐字元查正則(0x3b 兩次);S1 加「子 … 已上線；這邊還沒做」、S2 加全形分號的補括號位置 | HIT:兩格舊程式都紅 |
| E2 | S1 加 doctor --verbose 要有 [c6] | HIT |
| E3 | S2 加同一行兩個待定子句,補一個後另一個要照列 | HIT |
| E4 | S1 加單行 summary 的計劃 | HIT |
| E5 | S5 加 --decision "還沒做,另開計劃" 要回 2 | HIT |
| E6 | 讀 main 的 set 路徑與 cmd_drift_fix | 成立(設計一致性) |
| E7 | 讀 _closing_revisits | 成立 |
| E8 | 對照 _DRIFT_CLOSED、_ISSUE_CLOSED_STATUSES | 成立 |
| E9 | 讀 _drift_close_gates 與 _drift_fix_c2 | 成立 |

## 處置

本輪有 major,不放行任何發現,九條全折:

- E1:切點補全形分號(U+FF1B)。
- E2:doctor 漂移段迴圈加 c6。
- E3:新函式 _drift_pending_clause 逐子句判(有待定詞且子句裡沒有已裁定括號);修法的「處理到」改成看這個目標還在不在那一行的待定連結裡。
- E4:summary 單行值那一行也收。
- E5:--decision 新句含待定詞回 2。
- E6:出錯防護收進 _drift_print_backrefs 本體,四個呼叫處一致,拿掉 _decision_backrefs。
- E7:待定決策行的列出拆成 _closing_pending_decisions。
- E8:_DRIFT_SETTLED 改成由 _DRIFT_CLOSED 與 _ISSUE_CLOSED_STATUSES 合成。
- E9:_drift_close_gates 只回 (內容, 錯誤);留下的行號在 _drift_fix_c2 用加了橫幅之後的內容算一次。
