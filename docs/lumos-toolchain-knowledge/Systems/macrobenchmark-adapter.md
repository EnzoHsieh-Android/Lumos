---
type: system
status: doing
created: 2026-10-21
updated: 2026-10-28
responsibility: 負責 lumos macrobench:讀 Android 專案自己跑出的 Macrobenchmark 結果檔、跟基準比、只報變慢,照專案的人裁門檻檔判驗收門檻,並讀收集腳本寫的 stability.json 判記憶體與穩定性(--stability)、列原生配置排行(native_retained,只列不判);不負責建置或執行基準測試、不接裝置(接裝置的是收集腳本,家在 Systems/android-stability-collector)、不擋推送、不從量測產生門檻
aliases: []
about_code:
  - scripts/lumos
  - scripts/templates/android-receipt-rerun.sh
  - scripts/templates/android-ui-attribution.sql
tags:
  - type/system
  - status/doing
  - scope/stack-knowledge
summary: |-
  WHY:判退步要同時過兩道:中位數慢超過容差、而且比基準最大值還慢;例外是基準與現況都記著至少 20 輪時,啟動類只看差幅(見下一行) [出處:[[Projects/Macrobenchmark退步提醒_計劃]]] [因:官方說基準結果本來就浮動;只比百分比,基準那次剛好偏快就會誤報] [不選:官方的 step fitting(要存多次建置的歷史,第一版不做)] [test:t_macrobench_regression_needs_both]
  WHY:基準與現況都記著至少 20 輪時,啟動類只看中位數差幅、不再要求超出基準最大值;任一邊少於 20 輪或舊基準沒記輪數,照舊兩道 [出處:[[Projects/Android效能判定統計化_計劃]] 第 1、2 條,[[Verification/2026-10-24_效能判定規則實機評測]]] [因:實測 20 輪時拿掉那道,啟動 +20ms 那級從 1/24 抓到 10/24,同場與跨時段誤報仍是 0;10 輪時跨時段多 1 組誤報,所以綁在 20 輪] [不選:一律拿掉那道(5、10 輪時沒好處、10 輪還多誤報);另開設定讓專案自己選(多一個要記得的開關)] [test:t_macrobench_mag_only_at_20]
  WHY:讀結果檔時記下每個情境的輪數(iterations)與啟動類各指標的變異係數(cv,母體標準差除以平均),--update-baseline 一起寫進基準;現況少於 20 輪時 --json 的 low_iterations 列出、文字輸出印一行提醒,判定不變 [出處:[[Projects/Android效能判定統計化_計劃]] S3、S4] [因:20 輪規則要知道兩邊各跑幾輪,舊基準只有統計值;L0 收據要記各輪的變異係數] [不選:讀不出輪數時猜一個值(猜錯會讓 5 輪的專案也放寬)] [test:t_macrobench_baseline_records_iterations]
  PITFALL:極端但有限的 runs(例:1e300 與 -1e300 混著 5e-324)算出的變異係數是無限大,寫進基準後讀基準的形狀檢查拒收非有限數,整份基準讀不回來、--update-baseline 也不肯蓋 [出處:2026-10-25 代碼審 code-macrobench-20-iters r1 單審] [根因:寫端沒照讀端的標準過濾] [修法:_macrobench_cv 算的途中溢位、平均為 0、結果不是有限數一律回 None 不記] [test:t_macrobench_baseline_records_iterations]
  WHY:--results-dir 讓這次只讀指定目錄底下的結果檔、不讀 results_dirs,基準與門檻照舊用專案的;設定沒有 results_dirs 也照跑,不能跟 --update-baseline 一起用 [出處:[[Projects/Android端到端驗收_計劃]] S15] [因:端到端驗收要判「這一次」跑出的結果,results_dirs 裡上次留下的舊檔會混進來;基準要從專案自己的結果目錄存,不從一次驗收的暫存目錄存] [test:t_macrobench_results_dir]
  WHY:macrobench.json 可以只有 e2e 段(不填 results_dirs);e2e 段的格式由這裡讀設定時一起驗,規則與其他行為歸 [[Systems/android-e2e-acceptance]] [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r2 架構對齊席] [因:同一個設定檔只該有一個驗證入口(lumos macrobench --check-config)] [test:t_android_e2e_config_strict]
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
  WHY:--stability 的文字輸出把明細與原因先過既有的 _events_clean(控制字元、U+2028 這類分行字元換空白、截長;r4 資安席指出 _esc_clean 留下 U+2028)再印 [出處:2026-10-24 代碼審 code-android-mem-stability r2 資安席] [因:明細裡有被量 App 的類別名、收集到的錯誤文字,含換行時會偽造出一行 [達標] 給讀輸出的 AI] [不選:另寫一支清理函式(專案已經有 _esc_clean)] [test:t_android_memstab_unreadable_never_passes]
  WHY:check 條目達標時,exits 與 frozen 也逐條印 [達標] 明細,其他種類只算條數 [出處:2026-10-24 代碼審 r2 架構對齊席指出跟舊條目印法不同] [因:計劃 S5 要回報其他原因的結束紀錄、frozen 要看到最長阻塞,達標時不印就看不到] [test:t_android_memstab_exits]
  WHY:stability 段的 warmup、cycles 與結果檔的 cycles 限 1 到 10000 [出處:2026-10-24 代碼審 r2 邊界席] [因:沒上限時寫錯成天文數字,驅動會一直跑;結果檔的超大輪數讓每類門檻大到永遠不會達到,java_growth 判成通過] [test:t_android_memstab_check_fields_strict,t_android_memstab_unreadable_never_passes]
  WHY:門檻條目兩種寫法與 stability 的 test_data 共用一支署名檢查,decided_by 寫成 <裁定的人> 這種佔位也擋 [出處:2026-10-24 代碼審 r3 文件資安席、整合席、架構對齊席] [因:skill 範例用佔位提醒要問人,只改日期就照抄時不能當成有人裁過;同一組檢查原本在兩支函式各寫一份] [test:t_android_memstab_check_fields_strict]
  WHY:--stability 給了結果檔、門檻檔卻沒有 check 條目時,--json 也帶 stability_unjudged 一欄,文字輸出印同一句 [出處:2026-10-24 代碼審 r3 整合席] [因:skill 的 L0 走 --json,三個清單全空會被當成通過、收據記 L0 通過;這一欄跟其他欄一樣一開始就放好(值是 null),讀取端不用判斷鍵在不在(r4 架構對齊席)] [test:t_android_memstab_unreadable_never_passes]
  WHY:讀結果檔時先限深(20 層)、字串過 _esc_clean;數字欄位負數一律當量不到 [出處:2026-10-24 代碼審 r3 邊界席] [因:孤立代理字元讓 --json 印到 UTF-8 時整支崩;這些欄位是次數、位元組、時間,-1 以外的負數只會是手改或壞掉的檔] [test:t_android_memstab_unreadable_never_passes]
  WHY:門檻檔的條目寫了 check(native_unreachable、java_growth、instances、peak_vitals、exits、strictmode、frozen)就對 --stability 給的 stability.json 判記憶體與穩定性,沒寫 check 的照舊對 Macrobenchmark 結果檔判、判定結果不變;驗證多了一項:decided_by 寫成 <裁定的人> 這種佔位會被擋(跟 check 條目共用署名檢查);有 stability 段時 results_dirs 可以不填,沒有 macrobench.json 也照判 check 條目 [出處:[[Projects/Android記憶體與穩定性驗收_計劃]]] [因:這幾種檢查不是單一上下限,硬塞進 max 會寫出假數字;只做穩定性的專案沒有 Macrobenchmark 結果目錄] [不選:另開門檻檔或指令(多一種做法)] [test:t_android_memstab_check_compat]
  WHY:stability.json 每個來源帶 status,不是 ok 的、值是 -1 或不是有限數的,用到它的檢查一律列成跳過不列通過;驅動沒跑完時只跳過需要完整 N 輪的五種,exits 與 strictmode 照判 [出處:[[Projects/Android記憶體與穩定性驗收_計劃]] 設計審 r1–r3] [因:這類守衛最常見的失效是讀不到所以全綠;App 在量測輪崩潰時驅動一定跟著失敗,這時正是 exits 該判不過] [test:t_android_memstab_source_not_ok_skipped]
  WHY:原生配置排行放進結果的固定鍵 native_retained({enabled, status, reason, sites}),一開始就放進初始字典,主路徑與只有 stability 的路徑都印;不進 threshold_failures、不改回傳碼;形狀不對整段不採用、印一行 [出處:[[Projects/原生記憶體增長提示_計劃]] 設計審 r2、r4] [因:排行一定會列出快取與池,拿來擋會每次都擋;skill 走 --json,沒有固定鍵就分不出「沒打開」「沒跑成」與「零筆」] [不選:線性增長超過門檻就擋推送(d2;分漲停的判法在 [[Projects/原生記憶體增長判法_計劃]] 還沒量準)] [test:t_android_native_lumos_no_verdict_change] [test:t_android_native_lumos_paths] [test:t_android_native_lumos_shape]
  WHY:stability.native_retained 的型別在 _macrobench_stab_optional_err 驗,名字要對到 stability_scenarios 或 "@default" 那條放 _macrobench_stab_top_err;不寫進 stability_scenarios、不改情境名規則 [出處:[[Projects/原生記憶體增長提示_計劃]] 設計審 r2] [因:舊版 lumos 不驗 stability 段的未知鍵,退回舊版時設定不會被擋;跨段檢查只有最外層拿得到 stability_scenarios] [test:t_android_native_config]
verified_by:
  - "[[Verification/2026-10-21_Macrobenchmark退步提醒]]"
  - "[[Verification/2026-10-23_macrobench實機端到端]]"
  - "[[Verification/2026-10-23_Android驗證收據第零階段試跑]]"
  - "[[Verification/2026-10-23_Android介面寫法分流實驗室驗收]]"
  - "[[Verification/2026-10-24_Android記憶體與穩定性實驗室驗收]]"
  - "[[Verification/2026-10-24_效能判定規則實機評測]]"
---
# macrobenchmark-adapter

白話:Android 專案在測試機上跑完 Macrobenchmark(量啟動時間、滑動時每幀耗時的官方工具)後,`lumos macrobench` 讀它留下的結果檔,跟存好的基準比,列出哪個情境變慢了。只讀檔、只提醒;建置、裝置、跑測試都是消費專案自己的事。

- 設定 `.lumos/macrobench.json`:`results_dirs`(結果目錄清單;有 `stability` 段或 `e2e` 段的專案可以不填或給空清單)、`tolerance_pct`(預設 10)、`abs_tolerance`(容差下限,預設 1;容差取 |基準|×`tolerance_pct` 與它兩者較大的)、`higher_is_better`、`ignore_metrics`(預設忽略 `frameCount`)。
- 基準 `.lumos/macrobench-baseline.json`,用 `lumos macrobench --update-baseline` 建立或放行刻意的變慢。
- 換了裝置(型號或系統指紋不同)整項不比,只列出來。
- 基準檔任何一項形狀不對,整份當讀不了:不比、`--update-baseline` 也不蓋掉它,要人看過再刪(計劃條款 S11)。「形狀對」的標準跟讀結果檔產出的一樣:啟動類 median/minimum/maximum 都是數字;有 iterations 時要是正整數、有 cv 時每個值都是有限數;滑動類只能有 P50、P90、P95、P99 這幾個鍵、全是數字,P50 與 P90 必有;device 是物件。只驗比對會用到的那幾個值會漏,實際踩過 P99 是 null 時噴例外。
- 同一個情境出現在兩個結果檔,兩份都不收,訊息明講重複出現(更新基準與一般比對兩條路都是),不說成讀不了;常見原因是 `results_dirs` 同時指到同一份結果的兩個副本(計劃條款 S12)。
- 第一個消費端的跑法(假 POS 伺服器、模擬器設定)記在 Citrus_KDS 圖譜的 `Systems/效能基準`。

REVISIT:2026-12-21 接上實機結果後,看結果檔或基準裡有沒有出現 NaN 或 Infinity;有就把數值判斷改成只收有限數,現在 NaN 會讓那一項永遠比不出變慢 [closed:2026-10-23 門檻檔的 NaN 讓門檻恆判達標(代碼審 code-android-evidence 抓到),同一族一次改完:macrobench 讀數字一律只收有限數]

`scripts/templates/android-receipt-rerun.sh` 是 lumos-android-evidence 收據的重跑腳本範本:照 queries.sql 的標頭重跑查詢並比對 expect,0 全部相符、1 比對不符、2 收據本身寫錯(標頭沒被解析到、一條 expect 都沒有、manifest 列的查詢不在檔裡、查詢指到不存在的 artifact 或 requires)或分析工具執行不了(環境沒準備好,不是收據寫錯),回 2 時 stderr 印「擋下:」並說是哪一種。收據寫歪到解析那一步才出錯的幾種情形目前是 Traceback 回 1,見 [[Issues/Android收據重跑第四輪放行的小缺口]]。登記在工具組複製清單(`_VENDORED_TREE_FILES`),消費專案才會在 lumos init/update 時拿到它。寫收據時複製進消費專案的收據目錄;它跟 macrobench 同屬 Android 效能證據這一塊,所以掛在這篇。

`scripts/templates/android-ui-attribution.sql` 是 lumos-android-evidence L1 的分類查詢範本:把 App 主執行緒每一幀的自身時間拆成 Compose、只有 XML 才有的元件、兩種寫法共用的畫面管線、其他四類,嵌在 XML 裡的 Compose 算給 Compose;跟基準比哪一類長最多,決定往 Compose 分支還是原本的 L2 走。規則與為什麼這樣分見 [[Projects/Android介面寫法分流_計劃]]。只用標準 SQLite 語法與 slice/thread_track/thread/process 四張表,測試(`t_android_ui_attribution_*`)用 Python 內建的 sqlite3 跑同一支檔;實際分析時交給 trace_processor。第一欄 `frame` 是「f 接幀起點」的字串,收據的重跑腳本拿第一欄當鍵。一樣登記在工具組複製清單。範本整份(含檔頭註解)貼進收據的 queries.sql 照樣能重跑:範本註解不以分號結尾;重跑腳本用 Python 的 UTF-8 模式跑(`exec env PYTHONUTF8=1 python3 -`),收據檔頭帶 BOM 也讀得到,分析工具執行不了時回 2 並刪掉暫存查詢檔(`t_android_ui_attribution_receipt_rerun` 在預設與 LC_ALL=C 兩種環境跑,macOS 與 Linux 容器都驗過)。
