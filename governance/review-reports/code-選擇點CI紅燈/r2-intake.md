# code-選擇點CI紅燈 r2 收貨紀錄

第一輪 c1 折入(c478bdcb3:run_id 另收 null、測試補 no-run 事件)後派全新兩席看 r2-snapshot.patch(261 行;修補差異 r2-repair.patch 145 行)。兩份引句全數錨定。正確性席 clean:逐一核對 `_ci_record` 四個呼叫端的寫出值都在型別表內,兩種改壞(拿掉 None、拿掉 int)各自翻紅。

## 重現表

| id | 核對 | 結果 |
|---|---|---|
| a1 | Systems/reversibility-governance-ledger.md 新 PITFALL 的 `[修法:]` 括號裡寫了審查輪次;同篇鄰居把審查出處寫在 `[出處:]` | HIT |

## 分組與處置

| 組 | 條目 | 處置 |
|---|---|---|
| — | a1 | 放行(minor,附來源):結構正確、必有鍵齊全,只是出處字樣放的欄位不同;同一行 `[出處:]` 已寫事故來源 |

## 回歸因果
- 修補只動型別表一項、註解與測試;正確性席兩版核對 no-run 寫端在修前修後都寫 null,c1 已修掉。regression-set none。
