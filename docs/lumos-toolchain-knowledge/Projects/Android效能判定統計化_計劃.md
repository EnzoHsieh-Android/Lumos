---
type: project
status: todo
created: 2026-10-24
updated: 2026-10-24
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
related:
  - "[[Projects/Macrobenchmark退步提醒_計劃]]"
  - "[[Projects/Macrobenchmark驗收門檻_計劃]]"
  - "[[Projects/Android記憶體與穩定性驗收_計劃]]"
lands_in:
  - Systems/macrobenchmark-adapter
---
# Android效能判定統計化_計劃

白話:`lumos macrobench` 判「有沒有變慢」現在只比一次基準的彙總值(中位數、百分位),5 輪滑動,雜訊靠容差下限吸收;診斷鏈(Macrobenchmark、Perfetto、simpleperf)已是官方推薦路徑,落後的是判定的統計面。這份計劃收 2026-10-24 調研排出的五條優化,加上記憶體計劃移過來的第 6 條,排在 [[Projects/Android記憶體與穩定性驗收_計劃]] 之後做;子案二(Maestro 整合成 E2E 驗收)改成擋合併之前要先做前三條,因為擋了以後誤報就是硬成本。Enzo 2026-10-24 問「我們的效能做法貼近世界解嗎?還是有可以優化的地方?」,看完調研回「好」。下面是待辦清單,動手前照設計流程走(何時開始見 REVISIT)。

PRIOR-ART: Google 官方建議 CI 用 step fitting 比對滾動視窗(developer.android.com/training/testing/continuous-integration/automation);Mozilla Perfherder 用 t-test 加變化幅度兩道門檻、太吵的測試由 Performance Sheriff 降級(wiki.mozilla.org/TestEngineering/Performance/Sheriffing/Alerts);Chromium Pinpoint 取 Kolmogorov-Smirnov 與 Mann-Whitney 兩個 p 值的較小者(catapult 的 pinpoint compare.py);Android vitals 的慢幀 16ms、凍結幀 700ms、過多慢幀 50%、過多凍結幀 0.1%;Perfetto stdlib 的 android.frames 模組。以上 2026-10-24 調研讀到;Google 的 step fitting 原文(androidx 部落格)回 403 沒讀到;Uber、Airbnb、Spotify 等公司的一手文章沒找到。
RETIRE-IF: 六條都做完後連續兩個真實專案三個月內,統計檢定那道門從沒改變過判定結果(誤報與漏報都沒減少),就拿掉檢定、回到雙道規則。
REVISIT:2026-11-30 記憶體與穩定性子案收尾後,照下面六條開設計;動手前先 lumos search 檢定 統計 與 lumos decisions Macrobenchmark退步提醒_計劃,確認沒有否決過同類做法

## 待辦(依效益除以成本排)

1. 同一次建置內用每輪原始數值做 Mann-Whitney 檢定,當原本兩道規則之後的第三道門,只用來壓誤報;基準檔要多存每輪原始值。不撞 [[Projects/Macrobenchmark退步提醒_計劃]] 否決 step fitting 的理由(那條否決的是跨建置的歷史視窗)。順便評估 K-S 檢定抓 120Hz 兩群跳動那種雙峰。
2. 實驗室滑動從 5 輪加到至少 10 輪,L0 收據記每項指標的變異係數;併做 [[Projects/Macrobenchmark退步提醒_計劃]] 與 [[Verification/2026-10-23_macrobench實機端到端]] 裡那條容差實測的 REVISIT。
3. 設定加「太吵的指標只列出不判定」的出口(借 Mozilla 把太吵的測試降級的做法),一次解掉 120Hz 雙峰與混合畫面 37% 超時兩件同類事。
4. 報告多印一行 Android vitals 對照(超過 16ms 的幀佔比、超過 700ms 的幀數),只當參考線不當門檻,寫清楚跟線上統計的口徑差。
5. 評估用 Perfetto stdlib 的幀表取代歸因範本自己切幀;代價是 CI 不能再用 Python 內建 sqlite3 跑範本測試,所以先寫比對腳本看兩邊切出的幀一不一致再決定。
6. 記憶體峰值跟 App 自己的基準比(從 [[Projects/Android記憶體與穩定性驗收_計劃]] 移過來,那份只做官方底線):基準要存每次收集的峰值,容差用記憶體單位(KB)另設,不沿用毫秒類指標的絕對容差。
- 另待驗:官方建議看 P95/P99,我們以「P99 太吵」降成只列出,理由只有少量實測,做第 2 條時用 10 輪資料重驗。

## 實務隱患

- 已排除:金流:只讀效能量測結果檔,不碰交易。
- 已排除:對外送出:判定在本機跑,不送出資料。
- 已排除:不可逆:判定唯讀,基準檔多存欄位可回退。
- 已排除:守衛面:判定照舊只提醒不擋;擋合併在子案二另案。

## 條款

- [S1] 當這份計劃開始設計時,應先依待辦六條寫出各自的條款與測試,再跑規格閘 [manual:設計開始時改寫本節,這行刪掉]
