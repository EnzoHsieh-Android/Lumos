---
type: system
status: doing
created: 2026-10-21
updated: 2026-10-23
responsibility: 負責 lumos macrobench:讀 Android 專案自己跑出的 Macrobenchmark 結果檔、跟基準比、只報變慢,並照專案的人裁門檻檔判驗收門檻;不負責建置或執行基準測試、不接裝置、不擋推送、不從量測產生門檻
aliases: []
about_code:
  - scripts/lumos
  - scripts/templates/android-receipt-rerun.sh
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
  WHY:另讀 .lumos/macrobench-thresholds.json 判人裁的驗收門檻,跟基準比對分開、沒基準也照判,沒達也回 0 [出處:[[Projects/Macrobenchmark驗收門檻_計劃]] 2026-10-23 Enzo 裁只提醒不擋] [因:驗收門檻是絕對值,第一次接上就要能判;每條記 contract 指回功能節點的合約行,流程驗收與效能門檻才連得起來] [不選:節點摘要行新增前綴(要改 lint 與形狀檢查)] [test:t_macrobench_threshold_fail]
  PITFALL:門檻的 stat 寫錯類(滑動類指標寫 median)只看門檻檔判不出來,要對照這次結果才知道指標是哪一類 [出處:2026-10-23 實作] [根因:門檻檔不記指標類型,類型由結果檔決定] [test:t_macrobench_threshold_bad_file]
  WHY:--update-baseline 把每個情境的來源結果檔(相對路徑與 sha256)一起寫進基準,比對不看這欄 [出處:[[Projects/Macrobenchmark驗收門檻_計劃]] S9,2026-10-23 測試專案端到端演練] [因:逐層診斷 L1 要拿基準那次的 Trace 做 A/B,基準檔原本只有統計值,找不到是哪一次] [不選:另存一份來源索引檔(兩份要同步)] [test:t_macrobench_baseline_records_source]
  PITFALL:門檻、容差、基準或結果檔的數字寫成 NaN 或 ±Infinity 時,Python 的 json.loads 照收、型別檢查也當成數字;NaN 門檻讓「現值 > 門檻」恆假而永遠判達標,無限大容差讓什麼都不算退步 [出處:2026-10-23 代碼審 code-android-evidence 單審席] [根因:只檢查型別、沒檢查有限數] [修法:macrobench 讀數字一律走只收有限數的那一支] [test:t_macrobench_rejects_nonfinite]
  PITFALL:往 scripts/templates/ 或 scripts/hooks/ 新增要複製進消費專案的檔,只放檔案不夠:沒登記 _VENDORED_TREE_FILES 就不會被複製進消費專案(安裝只照這份精確清單複製),而且清單跟受版控的檔對不上會讓守衛測試紅;沒帶 SPDX 檔頭,授權聲明不跟著走 [出處:2026-10-23 代碼審 code-android-evidence r3 與修正關卡] [根因:安裝照 _VENDORED_TREE_FILES 精確清單複製、授權檢查另外看檔頭,放檔、登記、檔頭是三件事] [test:t_vendored_file_list_matches_what_install_ships]
verified_by:
  - "[[Verification/2026-10-21_Macrobenchmark退步提醒]]"
  - "[[Verification/2026-10-23_macrobench實機端到端]]"
  - "[[Verification/2026-10-23_Android驗證收據第零階段試跑]]"
---
# macrobenchmark-adapter

白話:Android 專案在測試機上跑完 Macrobenchmark(量啟動時間、滑動時每幀耗時的官方工具)後,`lumos macrobench` 讀它留下的結果檔,跟存好的基準比,列出哪個情境變慢了。只讀檔、只提醒;建置、裝置、跑測試都是消費專案自己的事。

- 設定 `.lumos/macrobench.json`:`results_dirs`(必填,結果目錄清單)、`tolerance_pct`(預設 10)、`abs_tolerance`(容差下限,預設 1;容差取 |基準|×`tolerance_pct` 與它兩者較大的)、`higher_is_better`、`ignore_metrics`(預設忽略 `frameCount`)。
- 基準 `.lumos/macrobench-baseline.json`,用 `lumos macrobench --update-baseline` 建立或放行刻意的變慢。
- 換了裝置(型號或系統指紋不同)整項不比,只列出來。
- 基準檔任何一項形狀不對,整份當讀不了:不比、`--update-baseline` 也不蓋掉它,要人看過再刪(計劃條款 S11)。「形狀對」的標準跟讀結果檔產出的一樣:啟動類 median/minimum/maximum 都是數字;滑動類只能有 P50、P90、P95、P99 這幾個鍵、全是數字,P50 與 P90 必有;device 是物件。只驗比對會用到的那幾個值會漏,實際踩過 P99 是 null 時噴例外。
- 同一個情境出現在兩個結果檔,兩份都不收,訊息明講重複出現(更新基準與一般比對兩條路都是),不說成讀不了;常見原因是 `results_dirs` 同時指到同一份結果的兩個副本(計劃條款 S12)。
- 第一個消費端的跑法(假 POS 伺服器、模擬器設定)記在 Citrus_KDS 圖譜的 `Systems/效能基準`。

REVISIT:2026-12-21 接上實機結果後,看結果檔或基準裡有沒有出現 NaN 或 Infinity;有就把數值判斷改成只收有限數,現在 NaN 會讓那一項永遠比不出變慢 [closed:2026-10-23 門檻檔的 NaN 讓門檻恆判達標(代碼審 code-android-evidence 抓到),同一族一次改完:macrobench 讀數字一律只收有限數]

`scripts/templates/android-receipt-rerun.sh` 是 lumos-android-evidence 收據的重跑腳本範本:照 queries.sql 的標頭重跑查詢並比對 expect,0 全部相符、1 比對不符、2 收據本身寫錯(標頭沒被解析到、一條 expect 都沒有、manifest 列的查詢不在檔裡、查詢指到不存在的 artifact 或 requires),回 2 時 stderr 印「擋下:」。登記在工具組複製清單(`_VENDORED_TREE_FILES`),消費專案才會在 lumos init/update 時拿到它。寫收據時複製進消費專案的收據目錄;它跟 macrobench 同屬 Android 效能證據這一塊,所以掛在這篇。
