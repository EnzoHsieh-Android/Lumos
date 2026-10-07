# code-撤除候選也看manual條款 r2 收貨

席報告 2 份(正確性 1 條 minor、架構對齊 1 條 minor),都是沒看過 r1 的新席。quote-check:正確性全錨;架構對齊 6 句有 1 句(跨兩行的 lands_in 引句)因差異檔每行開頭的 + 號錨不到,下表機械重現。

彙整 id:正確性 c1、架構對齊 a1。載體:正確性席(全錨)。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c1 | 測試格⑨:同一個 [S1] 定義兩次,第一條掛 `[manual:開頁面目測一次]`、下一層寫撤除;對照改掛 `[test:test_alive]` | 修前 [manual:] 那格 `[]`(漏),[test:] 那格列一行 | HIT |
| a1 | `grep -n lands_in r2-snapshot.patch` | 第 16–17 行 `+lands_in:`、`+  - Systems/筆記內容閘`;說明實際寫在 Systems/lumos-cli-read | HIT |

## 歸因

c1:有證據的修復回歸——席位在臨時 clone 對修前 069d6c64 與修後 280085c9 跑同一案例,修前列、修後不列;成因是 r1 改成只認條款解析的 state=manual,重複定義列的 state 是 duplicate。a1:原有漏查(lands_in 自計劃建立起就只列一篇)。

## 處置

全折(2 條):重複定義(duplicate/shadowed)時只拿那一行再交給 clause_bindings 判一次,口徑仍是同一支解析(c1,補測試格⑨,修前紅修後綠);lands_in 用 `lumos append` 補 Systems/lumos-cli-read(a1)。原列的 Systems/筆記內容閘 沒有移除指令、開頭欄位不准手改,先保留。
