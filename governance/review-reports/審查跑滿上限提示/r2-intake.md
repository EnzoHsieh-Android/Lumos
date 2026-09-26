# r2 收貨(2026-09-26)

七席全收;report-normalize 全過;quote-check 全錨。

## 編排者重現表

| id | 宣稱 | 重現指令 | 結果 | 處置 |
|---|---|---|---|---|
| r2g-F1 | 處置閘在第一個完整輪就收斂,走勢分支不可達 | `lumos loop status 逃逸帳對得起來 --disposal --spec …` r1 即 PASS;今天 code-記憶索引大小守衛、code-驗收前提欄位可改 也都是每輪全折即 PASS,多跑的輪是編排者自己決定再審修正差異 | HIT | 折入:Enzo 裁「換形狀再審最後一輪」——不修出口,改在要開超過上限的那一輪時印 |
| r2a-F2 | 折入數沿用的處置閘尾算式對 code 迴圈被跳過 | 讀 scripts/lumos 處置閘尾:`if not readonly and not str(loop_id).startswith("code")` 包住的是印出漏斗那段;`_review_yield_round` 函式本身不分迴圈種類 | 部分 HIT | 觀察對、判準錯:印的段落對 code 迴圈跳過,但函式可直接呼叫。折入成「直接呼叫函式,不靠處置閘印的那段」 |
