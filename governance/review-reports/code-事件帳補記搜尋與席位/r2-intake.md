# code-事件帳補記搜尋與席位 r2 收貨紀錄

- 驗收輪:只審 r1 修正的差異(`r2-snapshot.patch`,381 行)。正確性與架構對齊兩席全新;外家不派。
- 引句兩席全錨。reflog 只有編排者自己的提交。
- 這輪沒有 major。編號:c 正確性、a 架構對齊。

| id | 等級 | 處置 |
|---|---|---|
| a1 | minor | 折:Systems/lumos-guard 裡「不像事件帳那樣」那句改寫,分清範本檢查與事件帳 seat 欄是兩回事 |
| a2 | minor | 折:`t_ledger_seat_re_matches_guard` 的說明補上案例檔比對與放兩份的理由 |
| c1 | minor | 放行:截斷 200 字可能切在代理對中間,跟既有 `cmd` 前 500 字、`pattern` 前 200 字同一種截法;讀取端文字輸出不印這一欄,JSON 輸出會把孤立代理跳脫 |
