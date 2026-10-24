---
type: system
status: doing
created: 2026-10-24
updated: 2026-10-24
responsibility: 負責在主機端排順序、用 adb 與 trace_processor 收記憶體與穩定性資料寫成 stability.json(收集腳本、兩支查詢範本、錄製設定);不負責判過不過(判定在 lumos macrobench --stability),也不負責驅動 App(驅動指令由消費專案提供)
aliases: []
about_code:
  - scripts/templates/android-stability-collect.sh
  - scripts/templates/android-stability-cycle.sql
  - scripts/templates/android-heap-classes.sql
  - scripts/templates/android-stability-record.pbtxt
tags:
  - type/system
  - status/doing
  - scope/stack-knowledge
summary: |-
  WHY:收集腳本在主機端排全部順序(讀結束紀錄、跑暖機、掃原生、錄快照、邊錄追蹤檔邊跑量測、再掃再錄、再讀結束紀錄),驅動只負責開關畫面 [出處:[[Projects/Android記憶體與穩定性驗收_計劃]] 設計審 r1] [因:Macrobenchmark 在裝置上跑,插不進主機端錄快照與原生掃描的時間點;子案二換成 Maestro 時只換驅動指令] [test:t_android_memstab_collect_driver_status]
  WHY:結束紀錄用前後兩次比對(pid 加 timestamp),不用時間過濾 [出處:2026-10-24 實驗室實測] [因:dumpsys activity exit-info 的時間是裝置本地時間不帶時區,前後比對不用換時區、不受主機與裝置時鐘偏差影響] [test:t_android_memstab_exit_info_diff]
  WHY:先掃原生、再錄快照 [出處:[[Projects/Android記憶體與穩定性驗收_計劃]] 設計審 r3] [因:錄快照時在行程裡的配置不能算進掃描]
  PITFALL:日誌串流在驅動一結束就關掉,最後幾行還沒寫出來就被丟掉,StrictMode 違規會漏 [出處:2026-10-24 實作時測試抓到(假驅動瞬間結束)] [根因:串流是另一個子程序,輸出有延遲] [修法:驅動結束後先等 SETTLE 秒(預設 2)再關串流,關之前確認串流還活著,一開就斷記 failed] [test:t_android_memstab_collect_never_fakes_ok]
  PITFALL:`am dumpheap` 在 SM-X710 Android 16 上對 profileable 的基準建置回 SecurityException: Process not debuggable,官方文件說 profileable 就可以 [出處:2026-10-24 實驗室實測] [根因:裝置實際要求除錯版] [修法:Java 快照改用 skill 的 java_heap_dump(Perfetto java_hprof),同一個建置錄得到] [repro:adb shell am dumpheap -g com.example.mblab /data/local/tmp/x.hprof]
  PITFALL:錄製設定推到 /data/local/tmp 時 perfetto 讀不到(errno 13 Permission denied) [出處:2026-10-24 實驗室實機] [根因:裝置的 SELinux 規則不准 perfetto 讀 /data/local/tmp] [修法:推到 /data/misc/perfetto-configs/] [test:t_android_memstab_collect_test_data_gate]
  PITFALL:shell 對 perfetto 送 kill -0 回 Permission denied,錄製明明在跑卻被判成提早結束 [出處:2026-10-24 實驗室實機] [根因:裝置不准 shell 對 perfetto 送 0 號訊號,kill -TERM 照樣有效] [修法:用 ps 看在不在] [test:t_android_memstab_collect_record_alive]
  PITFALL:收集腳本沒先停 App 時,上一次留下的物件算進這一次 [出處:2026-10-24 實驗室連跑 Java 漏法與原生漏法] [根因:monkey 啟動時沿用還活著的行程] [修法:開跑先 am force-stop,而且在讀前一次結束紀錄之前] [test:t_android_memstab_collect_driver_status]
  PITFALL:宣告的類別在正常版兩份快照都沒有實例,被當成名字拼錯而跳過 [出處:2026-10-24 實驗室正常版] [根因:實例都正確釋放時快照裡本來就沒有它] [修法:收集腳本連它的類別物件 java.lang.Class<類別名> 一起存,判定看到類別物件就算 0 個] [test:t_android_memstab_instance_limit]
  WHY:清舊快照只刪產物目錄底下真的檔案,遇到捷徑(symlink)的目錄或檔就跳過 [出處:2026-10-24 代碼審前表態 infra-path] [因:產物目錄裡的捷徑指到別處時,照樣按檔名樣式刪會刪到專案外] [test:t_android_memstab_collect_test_data_gate]
  WHY:日誌串流只在宣告了 strictmode 時才開,只收這個 pid、量測開始之後的行,原始串流算完就刪、落地的 logcat.txt 只留違規那幾行 [出處:2026-10-24 代碼審 code-android-mem-stability r1 資安席] [因:整台裝置的日誌常含帳號、權杖、網址,而 run 目錄會留在本機好幾天] [不選:整份日誌留著當現場(違規那幾行已經夠定位,其他只增加外洩面)] [test:t_android_memstab_collect_logcat_scope]
  WHY:收到 SIGTERM 時先刪本機的原始日誌、收掉驅動整組子程序與日誌串流,最後才停裝置上的錄製並刪暫存設定與追蹤檔;驅動用獨立的程序群組跑,收尾時整組殺 [出處:2026-10-24 代碼審 r1 資源席] [因:人按 Ctrl-C 或 CI 逾時砍掉時,裝置上的 perfetto 會一直錄下去、驅動的孫程序變孤兒] [test:t_android_memstab_collect_cleanup]
  WHY:專案是 git repo 時,開跑前對 .lumos/artifacts/android/<run-id>/ 底下每一種會寫出的檔名各問一次 git check-ignore,任一個沒被忽略就回 2、不碰裝置 [出處:2026-10-24 代碼審 r1 資安席;r2 資安席(原本只問結果檔,.gitignore 只寫 *.json 時快照與日誌照樣會進版控)] [因:快照與日誌可能含個資,一個 git add -A 就進版控] [test:t_android_memstab_collect_edges]
  WHY:腳本用 python3 -P 跑、先拿掉 PYTHONPATH,不用 -I;開跑前先確認 python3 是 3.11 以上 [出處:2026-10-24 代碼審 r1 資安席與邊界席;r2 資安席(殘留的 PYTHONPATH 照樣載入同名模組)、r2 架構對齊席(3.9 只會噴看不懂的用法錯誤)] [因:-P 讓專案目錄裡同名的 .py 檔不會被當成標準函式庫載入;-I 另外會忽略 PYTHON 開頭的環境變數,把 PYTHONUTF8 一起關掉,Big5 這類語系下輸出就不是 UTF-8] [代價:主機的 python3 要 3.11 以上] [test:t_android_memstab_collect_edges]
  WHY:快照查詢回傳碼 0 但一列都沒有時 heap 記 failed,正常時 heap 帶 classes_seen(兩份快照各讀到幾個類別)與 class_names(mapping 有沒有還原),判定端沒有 classes_seen 就不判 [出處:2026-10-24 代碼審 r1 正確性席] [因:trace_processor 讀到壞檔或空檔時照樣回 0,不分開就會把「沒讀到」當成「零個實例」判通過] [test:t_android_memstab_collect_never_fakes_ok]
  WHY:收集腳本開跑前叫 lumos macrobench --check-config 驗設定,只用公開子命令與它的回傳碼;另外只從門檻檔讀 check 是 instances 的條目的 class(而且是 lumos 驗過格式之後) [出處:2026-10-24 代碼審 code-android-mem-stability r1 架構對齊席] [因:設定與門檻檔的格式規則只該有 lumos 那一份,範本自己再驗一次就是第二份;收集腳本留在消費專案的 scripts/templates/ 原地跑,跟 scripts/lumos 的相對位置是安裝固定的] [不選:像收據重跑腳本那樣完全不碰 lumos(收據重跑腳本要在沒裝 Lumos 的機器上跑,收集腳本跑完本來就要接 lumos macrobench --stability)] [代價:驗過之後收集腳本自己再讀一次 macrobench.json 取值,讀的是 lumos 驗過的那份;範本層第一次依賴 lumos 本體(收據重跑腳本完全不依賴);消費專案的 scripts/lumos 不在時收集腳本跑不了]
  WHY:專案根取目前目錄,不像收據重跑腳本那樣從腳本位置往上數 [出處:2026-10-24 代碼審 r1 架構對齊席] [因:收據重跑腳本被複製進收據目錄、位置固定在專案根下三層;收集腳本的使用方式是「在專案根目錄跑」,測試也從別處的副本對假專案跑;不在專案根跑時讀不到 .lumos/macrobench.json,回 2 擋下、不碰裝置] [不選:從腳本位置往上兩層推專案根(測試與手動拿副本跑時會推到錯的目錄)]
  PITFALL:日誌串流與錄製先從待收清單拿掉才開始停,停的那幾秒(等日誌跟上、等第一次 ps)被中斷時,cleanup 找不到它們:日誌串流變孤兒、錄製沒收到 TERM [出處:2026-10-24 代碼審 r2 正確性席、資源席] [根因:交接時先 pop 再停] [修法:停完才從待收清單刪] [test:t_android_memstab_collect_interrupt_windows]
  PITFALL:原始日誌 logcat.raw 只在正常路徑刪,串流斷了或被中斷時整份留在 run 目錄,而且 7 天清理只認快照檔 [出處:2026-10-24 代碼審 r2 正確性、資源、整合、兩席資安] [根因:刪檔寫在函式最後,提早回傳與中斷都跳過它] [修法:strictmode_result 用 finally 刪,cleanup 也刪] [test:t_android_memstab_collect_logcat_scope]
  PITFALL:只有驅動自成程序群組時,java_heap_dump、trace_processor 這類工具逾時只殺得到最外層,底下的程序握著輸出管線,收集腳本要等到它們自己結束(實測一份快照多卡 25 秒),逾時上限等於沒有 [出處:2026-10-24 代碼審 r2 資源席,r1 修補自己帶進來的] [根因:r1 改成自己 Popen 加 communicate,逾時後那次 communicate 沒有上限] [修法:每個子程序都自成程序群組、逾時整組殺,殺完再等管線也有上限] [test:t_android_memstab_collect_heap_timeout]
  WHY:同一個 run-id 已經有結果檔時回 2,不沿用舊目錄 [出處:2026-10-24 代碼審 r2 正確性席] [因:沿用時這次被中斷,舊的 stability.json 還在,看起來像這次的結果] [不選:開跑時刪舊結果檔(刪掉的是使用者之前那次的結果,不可逆)] [test:t_android_memstab_collect_edges]
  WHY:找工具有兩道:開跑前用 shutil.which 擋 ADB、TP(與宣告了測試資料時的快照工具),碰裝置前就回 2;執行時 run 再接 OSError [出處:2026-10-24 代碼審 r2 架構對齊席] [因:前一道讓工具沒裝時不會先動到裝置(停 App、推設定),後一道接驅動指令裡呼叫的其他程式] [不選:只靠執行時的 OSError(會在停過 App、開過錄製之後才發現)]
  PITFALL:dumpsys meminfo --unreachable 讀不到總量那行時,把裝置輸出的最後 200 字寫進失敗原因,那是每塊沒人指著的配置的十六進位傾印(App 的原生記憶體內容),再被 lumos macrobench 印給 AI [出處:2026-10-24 代碼審 code-android-mem-stability r3 資安席] [根因:失敗訊息照其他工具的慣例帶輸出尾巴] [修法:這支不帶標準輸出,只留回傳碼與標準錯誤的最後一行(adb 離線、逾時看得出來)] [test:t_android_memstab_collect_never_fakes_ok]
  PITFALL:只接 SIGTERM 時,關掉終端機分頁或 ssh 斷線(SIGHUP)、Ctrl-\(SIGQUIT)讓收集腳本直接結束:原始日誌留著、裝置錄製沒停;子程序各自成組收不到終端機的訊號,全變孤兒 [出處:2026-10-24 代碼審 r3 資源席、資安席,r2 讓子程序自成程序群組之後才會留孤兒] [根因:訊號處理只登記了 SIGTERM] [修法:SIGTERM、SIGHUP、SIGQUIT 都轉成例外走收尾;收尾一開始先忽略後面再來的中斷、先刪原始日誌] [test:t_android_memstab_collect_signals]
  PITFALL:查錄製在不在時在裝置上 grep,ps 偶發失敗與「沒找到」分不開,好的追蹤檔被當成錄製提早結束丟掉 [出處:2026-10-24 代碼審 r3 正確性席] [根因:ps 加 grep 的回傳碼兩種情況都是非 0] [修法:不在裝置上 grep、主機端比對 pid;ps 失敗連問三次,還是不知道就照樣停錄製但追蹤檔不採用(r4 正確性席:只當成還在跑會把到上限就停了的半份當完整收下)] [test:t_android_memstab_collect_record_alive]
  WHY:Python 版本另外查 3.11、殺子程序另寫 kill_group,不沿用 lumos 的 _PY_FLOOR 與 _kill_proc_group [出處:2026-10-24 代碼審 r3 架構對齊席] [因:收集腳本是 sh 外殼包的獨立 python,拿不到 lumos 的函式;3.11 是 -P 旗標的需求,不是專案下限,之後呼叫 lumos 時 lumos 會自己換到 3.14] [代價:兩份要各自維護;kill_group 照 _kill_proc_group 一樣在沒有 killpg 時退回只殺這一個(代碼審 r4 架構對齊席)] [不選:收集腳本 import lumos(範本要在消費專案裡原地跑,lumos 是單檔腳本不是套件)]
  WHY:快照裡的類別名照原樣寫進結果檔、印出時只清控制字元,不擋一般文字 [出處:2026-10-24 代碼審 r3 資安席] [因:合法的 Java 類別名可以是任何語言的字,擋了會誤擋;換行與控制字元已清,偽造不出一行判定] [不選:只收符合某種字元集的類別名(會把正常的非英文類別名當壞資料)]
  WHY:git rev-parse 回 128 而且錯誤不是「不是 git repo」時(safe.directory、權限)回 2 擋下,不當成不是 repo [出處:2026-10-24 代碼審 r4 資安席] [因:當成不是 repo 會整段跳過 git 忽略檢查,修好 git 之後一個 git add -A 快照就進版控] [test:t_android_memstab_collect_edges]
  WHY:收到第一個中斷就把所有中斷設成忽略、印一行「收尾中、最久約 4 分鐘」,收尾結束時照裝置有沒有回應改說法 [出處:2026-10-24 代碼審 r4 資源席、資安席] [因:兩個訊號同時到時第二個會打斷收尾;忽略期間按 Ctrl-C 沒反應要讓人知道;裝置離線時說「已停、已刪」會讓人以為裝置乾淨] [test:t_android_memstab_collect_signals]
  SEE:[[Systems/macrobenchmark-adapter]] [[Projects/Android記憶體與穩定性驗收_計劃]]
verified_by:
  - "[[Verification/2026-10-24_Android記憶體與穩定性實驗室驗收]]"
---
# android-stability-collector

白話:Android 記憶體與穩定性驗收的「收集」那一段。工具鏈範本 `scripts/templates/android-stability-collect.sh` 照抄進消費專案後,在專案根目錄跑,讀 `.lumos/macrobench.json` 的 stability 段,用 adb 對連著的裝置排好整個流程,寫出 `.lumos/artifacts/android/<run-id>/stability.json`;過不過交給 [[Systems/macrobenchmark-adapter]] 的 `lumos macrobench --stability`。它是第一支會接裝置的範本,外部工具用環境變數找:`ADB`、`TP`(trace_processor)、`JAVA_HEAP_DUMP`(skill 的 java_heap_dump,只有宣告了測試資料才用)。

`scripts/templates/android-stability-cycle.sql` 對量測期間那一份追蹤檔算峰值、凍結幀、主執行緒最長阻塞與幀數;`scripts/templates/android-heap-classes.sql` 對一份 Java 快照算每個類別還有人指著的實例數;`scripts/templates/android-stability-record.pbtxt` 是量測期間的 Perfetto 錄製設定。兩支查詢都只用標準 SQLite 語法,測試用 Python 內建的 sqlite3 照 Perfetto 文件建同名的表跑,真的 trace_processor 上跑不跑得動由實驗室人工驗收證明。設定欄位、七種檢查與判定規則的單源在 [[Projects/Android記憶體與穩定性驗收_計劃]]。
