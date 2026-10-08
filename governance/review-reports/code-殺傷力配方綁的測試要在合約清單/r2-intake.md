# code-殺傷力配方綁的測試要在合約清單 r2 收貨

席報告 2 份(正確性r2 1 條、架構對齊r2 2 條,全 minor)。quote-check 兩份全錨;refcheck ok。

彙整 id:正確性r2 d1、架構對齊r2 b1–b2。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| d1 | t_kill_add_warns_test_not_bound 補 ⑮ 合約片段 `-x`、平台名 `-p` 兩格,修前跑 | 印出 `lumos guard bind Systems/L -x Foo`、`--platform -p` | HIT |
| b2 | 讀碼:cmd_guard_bind 定位用 TEST_REF_RE 去標記,共用函式用 INV_TAG_RE | 判法不同 | HIT |

## 處置

全折:d1(減號開頭不印可貼指令)、b1(_kill_cmd_arg 說明寫清楚跟 _kill_node_arg 佔位字的分工)、b2(_kill_find_contract 說明交代 guard bind 為什麼例外)。
