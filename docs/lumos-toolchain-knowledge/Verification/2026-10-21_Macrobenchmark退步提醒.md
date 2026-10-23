---
type: verification
status: pass
date: 2026-10-21
valid_under:
  - 結果檔格式以 androidx.benchmark:benchmark-macro 1.2.4 在 Android 14 模擬器上寫出的為準
  - 容差與基準的數字未經實機量測,只驗判斷邏輯
revalidate_when:
  - 消費專案升級 Macrobenchmark 版本(結果檔欄位或檔名規則可能變)
  - 第一次在實機上跑出結果檔時,用它重跑讀真檔那支測試
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/Macrobenchmark退步提醒_計劃]]"
---
# 2026-10-21_Macrobenchmark退步提醒

白話:確認 `lumos macrobench` 照真結果檔的格式讀得到資料,判退步的規則照計劃的十條條款運作。

- **測試**:`python3.14 scripts/test_lumos.py -k macrobench`,10 支測試、48 條斷言全綠。
- **測試真的抓得到錯**:規格閘把實作換成什麼都不做的空殼時,10 條條款的測試全紅、沒有弱證據;換回實作全綠。另外手動做了五種改壞(拿掉「超出基準浮動範圍」那一道、拿掉換裝置不比、拿掉跨零規則、更新基準不保留舊項目、越大越好不反向),每一種都讓對應的測試變紅,改回來全綠。
- **真資料**:讀的是 Citrus_KDS 在 Android 14 模擬器上實跑的結果檔(`governance/research/macrobench/` 底下),啟動中位數、每幀超時 P90、裝置型號都跟當天直接讀檔的數字一致。
- **沒驗的**:沒有在實體裝置上跑;容差 10% 沒有實測依據。回頭條件寫在 [[Projects/Macrobenchmark退步提醒_計劃]] 的兩行 REVISIT。
