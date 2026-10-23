---
type: project
status: doing
created: 2026-10-23
updated: 2026-10-23
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/macrobenchmark-adapter
related:
  - "[[Projects/Android逐層診斷_計劃]]"
  - "[[Projects/Macrobenchmark驗收門檻_計劃]]"
  - "[[Systems/compose-metrics-adapter]]"
---
# Android介面寫法分流_計劃

白話:同一套效能驗收要撐得住三種畫面——傳統 XML(View 系統)、Compose、XML 畫面裡嵌 Compose。卡頓時先把每一幀的主執行緒時間拆成四類:Compose 自己的、只有 XML 才有的元件(inflate、清單綁定列)、兩種寫法共用的畫面管線(input、animation、measure、layout、draw)、其他;跟基準比哪一類長最多,就往那一類的下一層工具走:Compose 往「哪個函式重組太多、參數穩不穩定」,其他三類照原本的 CPU 取樣指到行號。門檻檔格式不變:Compose 的重組次數直接寫成一條門檻。Enzo 2026-10-23 裁:「現在可以開始接線 XML 和 Compose 了,也要顧慮到混合寫法的狀態」「compose 通常不會嵌 XML,會是 XML 裡嵌 Compose 比較多」;各專案寫法不一樣,三種都要撐得住。

WHY:混合畫面的時間一律算給最內層那一邊:每個區段扣掉子區段後的自身時間,依它自己的名稱分類;名稱分不出類的(App 自己打的區段、binder、鎖競爭),跟著最近一個分得出類的祖先;一路上都分不出的算「其他」 [出處:2026-10-23 Enzo 同意設計] [因:XML 裡嵌 Compose 時,Compose 的排版在 View 的 measure/layout 裡面跑,比外層區段大小永遠是外層大;官方沒有混合寫法的歸因說法(官方文件與 androidx 原始碼都查過,只證實 Compose 的幀掛在 Choreographer 的幀回呼上)] [不選:比哪個區段總長最大(外層必然最大);只看最外層區段名(嵌進去的 Compose 全算給外層)] [test:t_android_ui_attribution_innermost]
WHY:分四類,兩種寫法共用的畫面管線(input、animation、traversal、measure、layout、框架的 draw 與 draw-VRI 開頭、Record View#draw()、postAndWait;App 自己打的 draw 開頭區段不算)單獨一類,不算成 XML;XML 類只收只有 XML 寫法才有的元件區段 [出處:2026-10-23 實驗室真實 Trace 試跑(原設計三類)] [因:Compose 畫面也掛在 View 系統上跑,Compose 的繪製沒有自己的區段;照三類分,純 Compose 畫面卡在繪製會整段被算成 XML。實驗室正常版每幀約 95% 時間落在管線(多半是繪製時等系統的 binder),兩種寫法都一樣] [不選:三類(管線算 XML,純 Compose 畫面會被誤報成 XML);管線算其他(其他就分不出「框架排程」跟「畫面管線」)] [test:t_android_ui_attribution_pipeline]
WHY:往下走哪條路看「跟基準比,哪一類長最多」,不看「哪一類最大」;沒有基準才看最大,收據註明沒有基準 [出處:2026-10-23 實驗室四組注入的真實 Trace] [因:管線本來就佔每幀大半,看最大永遠是管線;注入「每列畫出前忙等」那組管線 1890 毫秒仍比 XML 元件 1430 大,但跟正常版比 XML 元件從 57 漲到 1430、管線幾乎沒動] [不選:看最大的一類]
WHY:Compose 的重組次數門檻用 `TraceSectionMetric("Compose:recompose", Mode.Count)`(結果檔叫 `Compose:recomposeCount`),不用 `Recomposer:recompose` [出處:2026-10-23 實驗室 Compose 清單正常版] [因:`Recomposer:recompose` 是每幀固定跑一次的排程迴圈,717 次對 712 幀,量到的是幀數;`Compose:recompose` 同一份 Trace 549 次對 808 幀,隨被重組的範圍變] [不選:Recomposer:recompose]
WHY:Compose 函式區段只認 composition tracing 的固定形狀「套件.函式 (檔.kt:行號)」,而且整個名稱只有一個空白 [出處:2026-10-23 實驗室鎖競爭那組真實 Trace] [因:ART 的鎖競爭區段也帶「(MainActivity.kt:65)」但是一整句話;只比括號時,純 XML 的 App 被算出 791 毫秒 Compose] [test:t_android_ui_attribution_compose_fn]
WHY:門檻檔格式不加「這條是哪種寫法」的欄位;Compose 的重組次數用 Macrobenchmark 的 TraceSectionMetric 輸出,當成一般的單值指標寫門檻 [出處:2026-10-23 設計討論] [因:TraceSectionMetric 輸出的格式跟啟動時間一樣有 median/minimum/maximum,現有讀檔程式吃得下(測試在實作前就是綠的,用來釘住現況);標寫法的欄位工具不會拿來判斷任何事,只是容易標錯的標籤] [不選:每條加 ui 欄位;XML 與 Compose 各開一個指令(多一種做法,混合畫面還是要另外處理)] [test:t_macrobench_threshold_trace_section_count]
WHY:歸因寫成工具鏈範本目錄裡的一支 SQL 查詢,只用標準 SQLite 語法;測試用 Python 內建的 sqlite3 餵假的 slice 表跑同一支檔 [出處:[[Projects/Android逐層診斷_計劃]] 的「執行與判斷放在 skill」與「重跑腳本放範本目錄」兩條 WHY] [因:Lumos 不跑第三方工具,trace_processor 只在 skill 裡用;CI 沒有 trace_processor,但 Perfetto 的查詢語法是 SQLite,只用 slice/thread_track/thread/process 四張表與遞迴 CTE 就兩邊都能跑;sqlite3 是標準函式庫,不違反零依賴;查詢是交給官方 trace_processor 跑,Lumos 不讀 Trace 檔,不違反 [[Projects/Android診斷證據接入_調研]] 否決的「Lumos 自己解析 Perfetto 檔」] [不選:做成 lumos 子指令讀 trace_processor 匯出的 CSV(多一層格式);用 Perfetto 專屬的 ancestor_slice 等表函式(SQLite 測不了)] [test:t_android_ui_attribution_sums]
WHY:歸因只看 App 主執行緒 [出處:2026-10-23 設計討論] [因:XML 與 Compose 的 inflate、measure、layout、重組都在主執行緒;RenderThread 的 DrawFrame 兩種寫法共用,分不出是哪一邊] [代價:卡在 RenderThread 的幀,主執行緒四類照樣加總等於 doFrame 長度,但 doFrame 之後的繪製看不到;這種情況照 [[Projects/Android逐層診斷_計劃]] 的 L1 規則看 RenderThread]
PITFALL:遞迴往下找子區段時查中間結果,區段一多變成平方級(12.6 萬個區段跑 234 秒) [出處:2026-10-23 實作時大量假資料實測] [根因:SQLite 的遞迴 CTE 一次處理佇列裡一列,每列都把中間結果整份掃一遍] [修法:遞迴那一步直接查 slice 表、分類先對不重複的區段名算一次、子區段總長先 GROUP BY 一次算好;同資料 0.5 秒,實驗室真實 Trace 41 萬個區段連載入 1.5 秒] [repro:造 3000 幀、每幀 42 個區段的假 slice 表跑範本,看秒數是否跟幀數成正比]
PITFALL:同一台 SM-X710 上混合畫面五輪裡有兩輪「每幀超時 > 0」的比例跳到 37%(其他三輪 2–3%),把 P90 拉到 7.3ms;主執行緒四類那兩輪跟正常輪幾乎一樣(XML 元件 465/470、Compose 185/193、管線 957/974 毫秒) [出處:2026-10-23 實驗室混合畫面正常版] [根因:整輪一起跳、主執行緒沒變,是平台那段(緩衝深度或刷新率)在跳,跟 [[Projects/Android逐層診斷_計劃]] 記過的 120Hz 兩群跳動同類;不是 App 退步] [影響:每幀超時的門檻在這個畫面會被雜訊觸發;歸因比較兩輪主執行緒四類就分得出來] [repro:跑 scrollHybrid 正常版,看結果檔 frameOverrunMs.runs 每輪大於 0 的比例]
PITFALL:每列綁定時多忙等 4ms,滑動基準完全沒退步、歸因的 XML 元件也沒漲 [出處:2026-10-23 實驗室混合畫面注入 bindDelayMs=4] [根因:RecyclerView 的預先綁定(`RV Prefetch`)利用幀與幀之間的空檔先綁下一列,綁定區段平均 0.2→3.7ms、Prefetch 0.13→0.71ms,但都在 doFrame 外面,使用者感覺不到卡;歸因只算 doFrame 裡的時間,所以這是對的「沒退步」] [影響:注入的變慢要大到空檔塞不下(這次改 12ms)才看得到;真實專案看到綁定變長但幀沒變慢,不算問題] [repro:scrollHybrid 帶 -e bindDelayMs 4,看結果檔 frameDurationCpuMs 與 Trace 裡 RV onBindViewHolder、RV Prefetch 的平均時間]
PITFALL:Kotlin 2.0.20 起預設開 strong skipping,參數不穩定的 composable 也標成 skippable,`lumos compose-metrics --audit` 的「不能跳過」清單是空的 [出處:2026-10-23 實驗室 Compose 清單,ComposeRow 的參數 RowModel 標 unstable 卻是 skippable] [根因:strong skipping 下不穩定參數改用「是不是同一個物件」比,每次傳新物件就跳不過,但編譯報告只記得到「可跳過」] [修法:skill 的 Compose 分支改成打開 *-composables.txt 看那個函式的參數有沒有 unstable] [防回歸:skills/lumos-android-evidence/SKILL.md 的 Compose 分支第 3 步]
PITFALL:L2 開 `debug.generate-debug-info true` 後,RecyclerView 加 Compose 的畫面一啟動就 SIGSEGV,CPU 取樣等不到行程 [出處:2026-10-23 實驗室混合畫面 L2,SM-X710 / Android 16] [根因:ART 即時編譯器替每個載入的類別寫除錯資料(`JitCompiler::TypesLoaded` → `ElfCompilationUnitWriter::Write`)時崩潰;純 ListView 畫面同一台沒事,哪個類別觸發的沒查;未 root 改不了 `dalvik.vm.dex2oat-flags` 繞過] [修法:skill L2 第 1 步先確認行程活著,崩了就只 `compile -f -m speed` 錄,用函式名加「函式裡只有一處對得上」推行號、標 [INFERRED];這次推到 `HybridAdapter.onBindViewHolder` 裡的 `LabWork.busyWait`(5296 個主執行緒樣本有 5294 個在它底下讀時鐘)] [repro:實驗室 setprop debug.generate-debug-info true、compile -f -m speed 後 am start HybridListActivity,logcat -b crash]
PITFALL:收據重跑腳本逐處加 UTF-8 編碼參數,macOS 上測試全綠,Linux 的 CI 上照樣崩潰 [出處:2026-10-24 代碼審 code-android-ui-kind r3,三席各自在 python:3.14-slim 容器重現] [根因:macOS 的檔案系統編碼永遠是 UTF-8;Linux 在 LC_ALL=C 下檔案系統編碼是 ascii,傳給分析工具的中文路徑在參數編碼那一步就失敗,逐處加的編碼參數管不到] [修法:改成一條規則——腳本用 PYTHONUTF8=1 的 UTF-8 模式跑,拿掉逐處參數;測試在 Linux 容器另跑一次] [test:t_android_ui_attribution_receipt_rerun]
PRIOR-ART: Jetpack Macrobenchmark 的 FrameTimingMetric(兩種寫法共用)與 TraceSectionMetric(Mode.Sum/Count,Count 從 1.3.0-alpha03 起;輸出名=label 加 Count/SumMs 等後綴,androidx benchmark-macro Metric.kt);Compose runtime 內建打的 `Recomposer:recompose`、`Compose:recompose` 等區段(Recomposer.kt、GapComposer.kt),androidx 自己的 MacrobenchUtils 拿 Sum 模式量;composition tracing(runtime-tracing + tracing-perfetto,區段名「套件.函式 (檔.kt:行號)」,官方範例 `TraceSectionMetric("%EntryRow (%", Mode.Sum)`);View 框架內建打的 `Choreographer#doFrame`、`traversal`、`measure`、`layout`、`draw`、`inflate`,ListView 的 `obtainView`、`setupListItem`,RecyclerView 函式庫打的 `RV ` 開頭區段;官方 Compose 穩定性診斷頁「不要只靠重組次數判斷效能,用 Macrobenchmark 或 composition tracing 驗證」;官方 ComposeView 互通頁:預設策略 DisposeOnDetachedFromWindowOrReleasedFromPool 在 RecyclerView 裡不會因捲出畫面就丟掉 Composition。裁定:指標與區段全借用;官方沒有的只有混合寫法的歸因,這部分自建成一支查詢。
RETIRE-IF: Perfetto 或 Android Studio 內建「每幀依 UI 寫法拆時間」的分析,或官方 android-profiler skill 加了同樣的歸因,就撤掉這支查詢改指向官方;或連續兩個真實專案的卡頓案例,歸因結果都沒有改變往下走的方向,就撤掉歸因、直接照原 L1 規則走。
REVISIT:2026-12-21 RecyclerView 綁定與建列的區段名,新版是「RV onBindViewHolder type=…」、官方文件還寫「RV OnBindView」;查詢用「RV 」開頭比對兩種都收,真實專案的 Trace 出現第三種寫法時補進測試
REVISIT:2027-04-23 第一個真實專案出現 Compose 裡嵌 XML(AndroidView)時,在實驗室補一個那種畫面跑一次歸因;規則本身兩個方向都適用,但這次只測 XML 嵌 Compose

## 四類怎麼分

| 類 | 區段名(主執行緒) | 來源 |
|---|---|---|
| Compose | 開頭是 `Compose:`、`compose:`(LazyColumn 預先組合 `compose:lazy:prefetch:*`)或 `Recomposer:`;composition tracing 的函式區段(「套件.函式 (檔.kt:行號)」,整個名稱只有一個空白) | Compose runtime 內建;composition tracing 要另外開 |
| XML 元件 | `inflate`、ListView 的 `obtainView` 與 `setupListItem`、`RV ` 開頭(新舊名都收) | View 框架、ListView、RecyclerView 函式庫內建 |
| 畫面管線(共用) | `input`、`animation`、`traversal`、`measure`、`layout`、框架的 `draw` 與 `draw-VRI` 開頭、`Record View#draw()`、`postAndWait` | View 框架內建,Compose 畫面也走這條;App 自己打的 draw 開頭區段(例 drawChart)不算,跟祖先 |
| 其他 | 分不出類又沒有分得出類的祖先,含 `Choreographer#doFrame` 本身與排 vsync 的自身時間 | — |

- 每幀輸出一列:幀的起點、幀長、四類各自的自身時間總和,以及 Compose 那類自身時間最多的那個函式區段名(同名的加總後比;有開 composition tracing 時才有)。
- 範本在工具鏈的 `scripts/templates/android-ui-attribution.sql`,用法寫在檔頭;skill 的 L1 段指到它。
- 卡頓幀由 L1 官方 triage 挑;查詢輸出全部的幀,判讀時比較基準與候選兩邊同一批卡頓幀(或全部的幀)的四類總和。

## 往下一層怎麼走(接進 L1)

- 跟基準比 Compose 長最多:先看門檻檔裡重組次數那條有沒有超;再用 composition tracing 重錄同一個情境,看查詢指出的函式與行號;最後跑 [[Systems/compose-metrics-adapter]] 的編譯報告,看那個函式是不是參數不穩定所以跳不過重組。官方提醒:重組次數本身不是判準,要配幀時間一起看。
- XML 元件、畫面管線或其他長最多:照 [[Projects/Android逐層診斷_計劃]] 原本的 L1 → L2 規則。
- XML 嵌 Compose 的清單:每列是 ComposeView 時,先查有沒有把策略改成 DisposeOnDetachedFromWindow(捲回來就整棵重建);Trace 上的樣子是每次綁定都跟著一段完整的初次組合。

## 實務隱患

- 已排除:金流:不碰任何交易或點數,只讀效能量測資料。
- 已排除:對外送出:查詢與測試都在本機跑,不送出任何資料;只讀區段名與時間,不碰記憶體快照。
- 已排除:不可逆:查詢唯讀、單次執行,不寫任何狀態;實驗室 App 的改動在本機 git、可撤回。
- 已排除:守衛面:門檻照舊只提醒不擋推送,這次不新增任何擋推送或擋提交的檢查。
- 區段名會隨函式庫版本改(RecyclerView 已改過一次):比對用開頭而不是全名,改名紀錄見上面的 REVISIT。
- 自身時間會因為子區段跟父區段時間重疊算錯:Perfetto 同一條執行緒上的區段一定是巢狀、不會交錯,假資料照這個寫。
- 名稱是 NULL 的區段照「分不出類、跟祖先」(接回分類時用 IS)[test:t_android_ui_attribution_inherit];沒收尾(dur -1)的區段連同底下整棵子樹都不走,時間留給最近一個已收尾的祖先,結果不隨名稱在別處有沒有出現而變 [test:t_android_ui_attribution_sums];子區段總長比自己長的壞資料,自身時間取 0 [test:t_android_ui_attribution_sums];draw 只認框架的 draw 與 draw-VRI 開頭 [test:t_android_ui_attribution_pipeline];同一幀 Compose 函式自身時間同分時照名稱排、取第一個 [test:t_android_ui_attribution_compose_fn]。
- 範本註解一律不以分號結尾(收據的重跑腳本拿第一個以分號結尾的行當查詢結尾);收據的重跑腳本用 Python 的 UTF-8 模式跑、檔頭 BOM 照讀、分析工具執行不了回 2(範本帶中文,LC_ALL=C 的環境原本會崩潰)[test:t_android_ui_attribution_receipt_rerun]。這幾條都是 2026-10-24 代碼審抓到的。
- 別的系統區段也可能長得像 Compose 函式(鎖競爭就是):新的誤判先在真實 Trace 上用分類查詢找出名稱,補進 compose_fn 那支測試。

## 條款

- [S1] 當一幀裡外層區段(畫面管線或 XML 元件)底下包著 Compose 區段時,查詢應把 Compose 區段的自身時間算給 Compose、外層只算扣掉子區段後剩下的時間 [test:t_android_ui_attribution_innermost]
- [S2] 當區段名分不出類時,查詢應把它的自身時間算給最近一個分得出類的祖先;一路上都分不出時算其他 [test:t_android_ui_attribution_inherit]
- [S3] 當區段是只有 XML 才有的元件(清單綁定的舊名「RV OnBindView」與新名「RV onBindViewHolder type=0x0」、ListView 的 obtainView 與 setupListItem、inflate)時,查詢應算 XML 元件 [test:t_android_ui_attribution_rv_names]
- [S4] 當幀裡有 composition tracing 的函式區段時,查詢應輸出同名加總後 Compose 自身時間最多的函式區段名;名稱帶檔名行號但不是那個形狀的系統區段(例:鎖競爭)不得算成 Compose [test:t_android_ui_attribution_compose_fn]
- [S5] 當一幀只有某一類時,其他類應為 0,四類加總應等於該幀 doFrame 的長度;只算這個 App 的主執行緒,沒收尾的幀不輸出,doFrame 掛在 Looper 訊息區段底下照樣算 [test:t_android_ui_attribution_sums]
- [S6] 當查詢範本加進工具鏈時,應登記在工具組複製清單、跟其他範本一起進消費專案 [test:t_android_ui_attribution_vendored]
- [S7] 當門檻檔有一條寫 TraceSectionMetric 輸出的次數指標(例 Compose:recomposeCount 的 median),這次結果超過上限時,lumos macrobench 應列成沒達驗收門檻 [manual:現有讀檔程式本來就吃得下,這次沒改程式,所以沒有實作前會紅的測試;測試 t_macrobench_threshold_trace_section_count 釘住現況;2026-10-23 實驗室 Compose 清單注入那次重組次數 30489 列為沒達]
- [S8] 當區段是兩種寫法共用的畫面管線(input、animation、traversal、measure、layout、框架的 draw 與 draw-VRI 開頭、Record View#draw()、postAndWait)時,查詢應算畫面管線、不算 XML 元件 [test:t_android_ui_attribution_pipeline]
- [S9] 當 L1 triage 挑出卡頓幀時,skill 應指示對基準與候選兩邊跑歸因查詢、依跟基準比長最多的那類決定往下走哪條路,並把兩邊的四類數字寫進收據該層的 why_escalated [manual:實驗室三種假錯各走一次 skill,收據的 L1 那筆都引兩邊的歸因數字;2026-10-23 通過,見 [[Verification/2026-10-23_Android介面寫法分流實驗室驗收]]]
- [S10] 當實驗室 App 加上 Compose 清單與「XML 清單每列嵌 Compose」兩個畫面時,兩個都應有滑動基準、人裁門檻,並綁到節點的測試 [manual:macrobench-lab 跑一次兩支滑動基準,lumos macrobench 判得出兩個畫面的門檻,節點綁定測試真跑;2026-10-23 通過,同上]
- [S11] 當實驗室分別埋入 Compose 參數不穩定造成重組過多、XML 綁定列太慢、每列 ComposeView 改成 DisposeOnDetachedFromWindow 三種假錯時,每種都應觸發門檻提醒、歸因歸對那一類、往下一層指到注入的那一行 [manual:三種各跑一次,收據存進 macrobench-lab;2026-10-23 通過,同上]
- [S12] 當派一個不知道注入內容的代理只拿三份量測資料時,它應還原出至少兩種注入 [manual:盲測代理報告存進卷證,對照注入清單;2026-10-23 三種都還原,同上]
