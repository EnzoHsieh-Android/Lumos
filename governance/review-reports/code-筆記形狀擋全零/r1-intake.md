# r1 收貨紀錄(code-筆記形狀擋全零)

凍結材料:r1-snapshot.patch(第一版修正:只讓筆記形狀擋把 40 個 0 當空樹,99 行)。分級 standard(pitfalls:無適用檢核題)。兩席:通才 opus、架構對齊 sonnet;收齊前沒動工作目錄。

| 發現 | 重現 | 結果 |
|---|---|---|
| r1a-F1 新分支開在主線頂端時把主線舊帳當新增 | 通才席的重現腳本;回歸 `t_push_base_zero_or_missing` ①(修前紅) | HIT |
| r1a-F2 force-push 後起點找不到照樣放行 | 回歸 ③(修前紅) | HIT |
| r1a-F5 / r1f-F1 home check 同一個洞、沒放進共用解析 | 回歸 ⑤(修前紅);代碼審那道 ⑦(拔掉修法會紅,已實測) | HIT |
| r1a-F3 / r1a-F6 / r1f-F2 doctor 步驟的 shell 串接、少兜底、命令與說明黏在一起 | 讀碼;回歸 ⑥ | HIT(整段 shell 邏輯拿掉) |
| r1a-F4 測試只比字串、沒涵蓋有遠端 | 新測試改用本機裸遠端與 upstream | HIT |
| r1f-F3 行內未編譯正則 | 讀碼 | HIT(改成模組層常數 `_ZERO_SHA_RE`) |

9 條全折(輪內有 major,不得放行);refuted 無。修的過程另發現一支舊測試的替身會自己遞迴(新路徑多呼叫一次 git 才踩到),一併修。
