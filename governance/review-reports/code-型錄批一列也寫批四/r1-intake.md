# r1 收貨紀錄(code-型錄批一列也寫批四)

- 分級 standard:一位審查員加一席架構對齊,兩席交回後一次存檔;兩份全錨;架構對齊席 clean。
- 臨時目錄收貨後刪(兩席都沒留東西)。

| id | 席 | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|---|
| f1 | 審查 | major | 註記「間接」「相關」「需標註」的列被補成批四,但那條檢查擋不到這列的壞寫法(TEST-23、UI-1、PERF-2) | HIT:席用 _batch4_problems 重現;另讀 ConstantContentStateKeyInItemsCall 官方檢查頁,管的是 items 裡內容狀態 key 不重複,不管 items 有沒有 key = | 折:三個字加進 _B4_SKIP(「只管…」「只部分涵蓋」照算,擋得到其中一部分);UI-1 那段 androidx 補「相關」註記;三列退回批一;筆記 WHY 那句「沒有一列是判過不接」改寫 |
| f2 | 審查 | minor | 改壞例子只涵蓋 Lint 標籤,compose-rules 標籤的批一列沒守 | HIT:改壞「只比 Lint 標籤」→ 補例子前照綠 | 折:補「批一的列拿掉 compose-rules 那種批四」 |

架構對齊席標一項 ⚠(_batch4_problems 與 _dt_row_lint 後綴不一致,鄰居本身不一致),不算發現,不改。

## 修補後驗證

- 改壞兩種各自翻紅:拿掉三個新排除字樣 → 三條斷言與 S4(UI-1)紅;只比 Lint 標籤 → S4(UI-3)紅。-k kt_catalog 163 passed;型錄自檢 0 問題。
- 主線已標批四的列沒有受新排除字樣影響(試算:只有這批補的 ARCH-44、TEST-23、PERF-2 標籤會變,ARCH-44 是「只部分涵蓋」照算)。

## 先查世界

- PRIOR-ART:f1——Android Lint 官方檢查頁 ConstantContentStateKeyInItemsCall(https://googlesamples.github.io/android-custom-lint-rules/checks/ConstantContentStateKeyInItemsCall.md.html)。判準:註記寫明那條檢查擋不到這列壞寫法的不算接電,擋得到一部分的照算;用字樣判,同一條口徑,不逐列寫例外。
