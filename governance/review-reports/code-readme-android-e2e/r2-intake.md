preflight-4: ran

# code-readme-android-e2e r2 收貨

審材:主線 17a0d393 到 d6eeccd0 的完整改動 r2-snapshot.patch(316 行),加修補差異 r2-repair.patch(29deb0ef → d6eeccd0,176 行)。
兩席全新:單審(sonnet)、架構對齊(sonnet),都交回後才一起存檔;席報告從對話紀錄取最後一則回答原文。單審引句全錨;架構對齊乾淨、0 條。
修補因果:F1 是上一輪沒人看的角落(第六件事那句 r1 就在,r1 單審把七件事判成跟腳本一致,沒對 StrictMode 規則範圍),不是上一輪修補造成的。

## 機械重現

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| F1 | major | 讀計劃:Android記憶體與穩定性驗收_計劃 第 37 行 WHY 寫 StrictMode 的 VM 規則(可關閉物件沒 close、註冊沒取消、Activity 被留住),要消費專案自己打開、沒宣告就跳過;README 寫「在主執行緒做不該做的事」 | HIT | 折:中英兩版改成「系統內建的檢查(StrictMode)有沒有抓到資源沒關、註冊沒取消、畫面被留住這類違規(要專案在測試版自己打開,沒打開就列成跳過)」 |

全折 1、放行 0、駁回 0。--regression-set none。
