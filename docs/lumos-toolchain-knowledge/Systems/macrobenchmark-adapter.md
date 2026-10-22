---
type: system
status: doing
created: 2026-10-21
updated: 2026-10-23
responsibility: 負責 lumos macrobench:讀 Android 專案自己跑出的 Macrobenchmark 結果檔、跟基準比、只報變慢;不負責建置或執行基準測試、不接裝置、不擋推送
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/system
  - status/doing
  - scope/stack-knowledge
summary: |-
  WHY:判退步要同時過兩道:中位數慢超過容差、而且比基準最大值還慢 [出處:[[Projects/Macrobenchmark退步提醒_計劃]]] [因:官方說基準結果本來就浮動;只比百分比,基準那次剛好偏快就會誤報] [不選:官方的 step fitting(要存多次建置的歷史,第一版不做)] [test:t_macrobench_regression_needs_both]
  WHY:滑動類只有百分位,P50 與 P90 過容差算退步,P99 只列出 [出處:[[Projects/Macrobenchmark退步提醒_計劃]] S8] [因:P99 浮動大,拿來判會一直誤報] [test:t_macrobench_sampled_percentiles]
  WHY:有退步也回 0,只提醒不擋推送 [出處:[[Projects/併發與效能表態要合約背書_計劃]] 2026-10-01 推送前證據不收毫秒] [因:毫秒隨機器與溫度浮動,拿來擋會隨機誤擋] [test:t_macrobench_exit_codes]
  PITFALL:結果檔名的寫法隨函式庫版本變,照官方文件範例拼檔名會找不到檔:1.2.4 把套件名的點換成底線,1.4.1 保留點 [出處:2026-10-21 Citrus_KDS 模擬器實跑(1.2.4)、2026-10-23 實機小專案(1.4.1)] [根因:函式庫自己決定檔名正規化,各版不同] [test:t_macrobench_reads_real_kds_file]
  SEE:[[Systems/compose-metrics-adapter]] [[Projects/Macrobenchmark退步提醒_計劃]]
  WHY:--update-baseline 把這次讀到的項目蓋進舊基準,不整份重寫 [出處:[[Projects/Macrobenchmark退步提醒_計劃]] S6] [因:某個結果檔這次壞掉時,它原本的項目不能跟著消失] [代價:已刪掉的情境會留在基準裡,每次列成「沒跑到」] [test:t_macrobench_update_baseline_skips_failed]
  REVISIT:2026-12-21 看接上的消費專案基準裡有沒有累積「沒跑到」的舊情境;有就加一個刪除舊情境的選項
  WHY:容差取「基準絕對值×容差百分比」與絕對容差兩者較大的那個,不只按比例 [出處:2026-10-23 實機小專案正常版重跑] [因:每幀超時這種接近 0 的指標,10% 的容差只剩零點幾毫秒,正常抖動就被報成變慢;滑動類又沒有超出基準浮動範圍那第二道] [不選:只對每幀超時一個指標特別處理(其他接近 0 的指標會再踩一次)] [test:t_macrobench_real_tablet_lab]
verified_by:
  - "[[Verification/2026-10-21_Macrobenchmark退步提醒]]"
  - "[[Verification/2026-10-23_macrobench實機端到端]]"
---
# macrobenchmark-adapter

白話:Android 專案在測試機上跑完 Macrobenchmark(量啟動時間、滑動時每幀耗時的官方工具)後,`lumos macrobench` 讀它留下的結果檔,跟存好的基準比,列出哪個情境變慢了。只讀檔、只提醒;建置、裝置、跑測試都是消費專案自己的事。

- 設定 `.lumos/macrobench.json`:`results_dirs`(必填,結果目錄清單)、`tolerance_pct`(預設 10)、`abs_tolerance`(容差下限,預設 1;容差取 |基準|×`tolerance_pct` 與它兩者較大的)、`higher_is_better`、`ignore_metrics`(預設忽略 `frameCount`)。
- 基準 `.lumos/macrobench-baseline.json`,用 `lumos macrobench --update-baseline` 建立或放行刻意的變慢。
- 換了裝置(型號或系統指紋不同)整項不比,只列出來。
- 基準檔任何一項形狀不對,整份當讀不了:不比、`--update-baseline` 也不蓋掉它,要人看過再刪(計劃條款 S11)。「形狀對」的標準跟讀結果檔產出的一樣:啟動類 median/minimum/maximum 都是數字;滑動類只能有 P50、P90、P95、P99 這幾個鍵、全是數字,P50 與 P90 必有;device 是物件。只驗比對會用到的那幾個值會漏,實際踩過 P99 是 null 時噴例外。
- 同一個情境出現在兩個結果檔,兩份都不收,訊息明講重複出現(更新基準與一般比對兩條路都是),不說成讀不了;常見原因是 `results_dirs` 同時指到同一份結果的兩個副本(計劃條款 S12)。
- 第一個消費端的跑法(假 POS 伺服器、模擬器設定)記在 Citrus_KDS 圖譜的 `Systems/效能基準`。

REVISIT:2026-12-21 接上實機結果後,看結果檔或基準裡有沒有出現 NaN 或 Infinity;有就把數值判斷改成只收有限數,現在 NaN 會讓那一項永遠比不出變慢
