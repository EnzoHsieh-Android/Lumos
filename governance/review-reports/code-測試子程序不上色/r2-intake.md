# code-測試子程序不上色 r2 收貨

一席架構對齊(新席),從逐字稿抽原始最後回覆存檔。quote-check 全錨。

彙整 id:a1。載體:架構對齊席。最高 minor。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| a1 | 席位實測 `NO_COLOR=1 FORCE_COLOR=3 python3.14 -c "raise RuntimeError('x')"` | 不含 `\x1b[`;前置斷言的現場帶著殼裡的 NO_COLOR 時沒成立,會誤紅 | HIT |

## 處置

- a1 折:前置斷言造現場時連 NO_COLOR 一起排除,只吃自己造的環境。四種殼(無、FORCE_COLOR=3、NO_COLOR=1、兩者都設)都 4 條全過。

## 修補因果(regression-set)

a1 由 r1 修補(新增前置斷言)引入。regression-set = a1。
