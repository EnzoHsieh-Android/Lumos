---
type: project
status: doing
created: 2026-10-28
updated: 2026-10-28
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/android-stability-collector
  - Systems/macrobenchmark-adapter
related:
  - "[[Projects/Android記憶體與穩定性驗收_計劃]]"
  - "[[Projects/Android逐層診斷_計劃]]"
  - "[[Verification/2026-10-24_Android記憶體與穩定性實驗室驗收]]"
  - "[[Projects/原生記憶體增長判法_計劃]]"
pending_questions:
  - id: Q1
    text: heapprofd 要跟算凍結幀與峰值的那份追蹤檔同一段 N 輪一起錄,還是另外再跑一段 N 輪?(建議:另跑一段,驗收多花約一段量測的時間,但不干擾既有的幀與峰值數字)
    class: 成本
    stage: 架構
    status: 已決
    decision: "#d1"
  - id: Q2
    text: 這項提示要不要永遠只提醒、不擋推送?(建議:永遠只提醒;擋下要另開一題、有真實專案數字再裁)
    class: 產品行為
    stage: 需求
    status: 已決
    decision: "#d2"
  - id: Q3
    text: heapprofd 錄檔沿用 stability.test_data 的同一條保存規則(只在宣告測試資料時錄、本機留 7 天),還是要另外宣告?(建議:沿用同一條,錄檔一樣放 run 目錄、檔名 heap-*.pftrace)
    class: 個資
    stage: 需求
    status: 已決
    decision: "#d3"
decisions:
  - content: heapprofd 另跑一段 N 輪錄,不跟算凍結幀與峰值的那份追蹤檔同一段
    id: d1
    context: heapprofd 掛在 malloc 上取樣會拖慢 App;既有量測那段 N 輪錄的追蹤檔要算凍結幀、主執行緒阻塞與記憶體峰值
    why_chosen: Enzo 2026-10-28 選另跑一段:不干擾既有幀與峰值數字,判定那幾項照舊可信
    alternatives: 甲=另跑一段 N 輪只錄 heapprofd;乙=跟既有量測那段同一份追蹤檔一起錄
    trade_offs: 驗收多花約一段量測的時間(實驗室 8 輪約十幾秒加上停錄與拉檔);兩段量測之間 App 狀態可能不同(例如快取在第一段已填滿)
    decided: 2026-10-28
    valid: true
  - content: 原生記憶體增長提示永遠只提醒,不進判定、不影響回傳碼與推送前檢查
    id: d2
    context: 目的是找出可以優化的地方、不是找碴;判法(前後兩半增量)只在實驗室一台裝置驗過,快取上限大於量測輪數時會誤判
    why_chosen: Enzo 2026-10-28 選永遠只提醒:擋下要另開一題、有真實專案數字再裁
    alternatives: 甲=永遠只提醒;乙=線性增長超過門檻就擋推送
    trade_offs: 真的有漏也不會被擋下,要靠人看提醒;沒有誤報成本數字前不擋
    decided: 2026-10-28
    valid: true
  - content: heapprofd 錄檔沿用 stability.test_data 宣告與本機留 7 天的保存規則
    id: d3
    context: heapprofd 錄檔當含個資處理;既有 Java 快照已有人寫的測試資料宣告、heap-*.pftrace 檔名與開跑時刪 7 天前舊檔的做法
    why_chosen: Enzo 2026-10-28 選沿用:一條保存規則管兩種錄檔,不另立宣告
    alternatives: 甲=沿用 stability.test_data 與 heap-*.pftrace 7 天自動刪;乙=另立一個 heapprofd 專用的宣告
    trade_offs: 宣告了測試資料才錄,沒宣告的專案拿不到這項提示;專案不再跑收集腳本時舊錄檔不會被刪(既有代價照舊)
    decided: 2026-10-28
    valid: true
  - content: 原生記憶體增長提示按情境自己開、預設關:只有設定裡替那個情境打開的才多跑一段 heapprofd
    id: d4
    context: 前掃比對舊否決時撞到 Projects/Android逐層診斷_計劃 否決過的「每次都錄 Trace+CPU 取樣+記憶體」(慢、改變被量對象、留下不必要的敏感檔);原草稿是宣告了測試資料就每次都多錄一段
    why_chosen: Enzo 2026-10-28 選按情境開、預設關,維持 Projects/Android逐層診斷_計劃 的否決理由:慢與敏感檔只落在主動打開的情境上
    alternatives: 甲=按情境開、預設關;乙=宣告了測試資料就每次都錄
    trade_offs: 沒打開的情境照樣漏也看不到這項提示,要人先知道該查哪個情境(例如結帳)才打開;設定多一個選填鍵
    decided: 2026-10-28
    valid: true
  - content: 拆兩份:這份只做原生配置排行(結束時還留著最多的呼叫位置,不分漲停),分漲停的判法另開 Projects/原生記憶體增長判法_計劃 先做實驗
    id: d5
    context: 設計審跑滿三輪,判法換了兩次形狀(三個時間點、四等份窗口最小值)仍受 heapprofd 接上行程的延遲與傾印對齊左右,池子情境在 64 組時間參數下全判成在漲,也分不出一次性跳升
    why_chosen: Enzo 2026-10-28 到頂裁定選拆兩份:排行只用停錄時一定會寫的最後累計,不受時間對齊影響,能先交付;判法要用每輪記號切窗,得先在實驗室量準
    alternatives: 甲=拆兩份,先做排行;乙=原計劃加一輪,改用每輪記號切窗;丙=照第三版判法實作、接受池子誤報;丁=整題擱置
    trade_offs: 排行會列出快取與池,要人分辨哪個是漏;分漲停要等新計劃的實驗與審查做完才有
    decided: 2026-10-28
    valid: true
---
# 原生記憶體增長提示_計劃

白話:記憶體與穩定性驗收現在用「沒人指著的原生記憶體」掃描抓 .so 忘了 release,但 SDK 自己留一份清單、還指著那塊記憶體時掃描是 0,抓不到;這種只剩 Native Heap 前後兩個數字(只寫在收集腳本的結果檔,lumos 判定不讀也不印)。這份計劃讓人替要查的情境(例如結帳)自己打開、預設關(d4),打開的情境在既有量測之後另跑一段 N 輪,只錄 Perfetto 的原生配置記帳(heapprofd,掛在 malloc/free 上記每個呼叫位置配了多少、還了多少;d1),按呼叫位置(從 malloc 往上跳過 libc、libc++ 這些配置器,第一個不是配置器的函式)彙總量測結束時還沒釋放的量,列成**原生配置排行**(哪支 .so 的哪個函式、App 哪個函式呼叫的、結束時還留著多少),照留著的量排序,**只提醒、不擋推送**。排行不分「在漲」還是「停住」:快取與物件池也會上榜,要人看;分漲停的判法三輪設計審都被時間對齊打穿,拆到 [[Projects/原生記憶體增長判法_計劃]] 先做實驗(d5)。2026-10-28 Enzo 要求「把能優化的效能問題抓出來優化,不是找碴」,並要求先查精準的世界解、再到實驗室實測。

PRIOR-ART: 最小解在既有的收集腳本裡:它已經有「暖機 W 輪 → 量測 N 輪」兩次驅動呼叫,量測期間本來就錄一份 Perfetto 追蹤檔;skill lumos-android-evidence 的 L3(逐層診斷的第四層「誰配置、誰留住」,要宣告測試資料才做)已經在用 heapprofd(`--heaps libc.malloc`)事後診斷原生漏法。世界解:①Perfetto heapprofd(Android 10 以上;user 建置只限 profileable 或 debuggable 的 App)的 HeapprofdConfig 欄位照 v57.2 的 protos/perfetto/config/profiling/heapprofd_config.proto(github.com/google/perfetto/blob/v57.2/…):`process_cmdline`、`sampling_interval_bytes`(預設 4096,不能是 0)、`shmem_size_bytes`(預設 8 MiB、2 的次方)、`no_startup`(只接已經在跑的行程,Android 11 以上)、`continuous_dump_config { dump_phase_ms dump_interval_ms }`(第一次傾印在 dump_phase_ms 毫秒後,之後每隔 dump_interval_ms 毫秒傾印一次);②trace_processor 的 `heap_profile_allocation` 每列是「這次傾印跟上一次比的差額」(配置正、釋放負;v57.2 src/trace_processor/importers/proto/profile_packet_sequence_state.cc 的 alloc_delta、free_delta),所以某個傾印時間點還沒釋放的量 = 同一呼叫位置、ts 不晚於那一刻的 size 加總,官方 stdlib 的 android.memory.heap_profile.summary_tree 也是 `sum(size)` 當沒釋放的量;③判斷「在漲還是停住」的世界解(BLeak、LeakCanary 3.0 的堆積增長偵測)隨判法搬到 [[Projects/原生記憶體增長判法_計劃]]。裁定:錄製與查詢原樣借 Perfetto,自己只寫按呼叫位置歸併與排行;不採 dump_at_max(只有峰值那一刻,不是結束時還留著的量)。
RETIRE-IF: 上線三個月後兩個真實專案的提示零觸發,或兩個真實專案沒有一次靠排行找到可優化的呼叫位置,就把這項排行拿掉、只留 L3 的手動診斷;每次驗收多花的時間超過量測本身的兩倍,也拿掉(d1 本來就多一段量測,一倍是預期成本)。
REVISIT:2027-01-31 在實驗室埋一個每輪漏幾十次、每次小於 4096 位元組的小配置,量同一情境跑三次時結束累計抖多少,照實際抖動定 1 MiB 這條列出下限
REVISIT:2027-01-31 拿兩個真實專案(帶第三方 .so 的)跑過之後,看排行前 20 名裡快取與池佔幾成,佔多數就優先做 [[Projects/原生記憶體增長判法_計劃]]
REVISIT:2027-01-31 收集腳本與分析工具要對到 skill 釘的 Perfetto 版本:2026-10-28 實驗用的主機 trace_processor 是 v58.2(本機與 ~/.cache/lumos/tools 兩支都是)、裝置端是 Android 16 內建的 perfetto,不是 v57.2;正式做之前用 v57.2 重跑同一組實驗或改釘版本

## 實驗室實測(2026-10-28)

在 macrobench-lab 另開工作目錄與分支 native-growth-lab(不推送、不合併)做:假原生 SDK 多兩種情境,SM-X710 / Android 16,benchmark 建置(profileable、非除錯版)。每種:停 App → 啟動 → 驅動暖機 2 輪 → 讀「沒人指著的原生記憶體」與 Native Heap → 開 heapprofd(只接已在跑的行程、每秒傾印一次)→ 驅動量測 8 輪 → 等 3 秒停錄 → 再讀兩個對照數字。每輪開畫面配 2 MB。

| 情境 | 沒人指著(前→後) | Native Heap KB(前→後) | heapprofd 判法 | 點到的呼叫位置 |
|---|---|---|---|---|
| ①沒呼叫 release、記憶體沒人指著 | 0 → 16 MB(8 塊) | 9176 → 26468 | 線性增長:結尾 16 MB,前半增 8、後半增 6 | `nativeCreate` @ libfakesdk.so |
| ②SDK 全域清單留著每個 handle、App 沒 release | 0 → 0(抓不到) | 11576 → 30860 | 線性增長:結尾 16 MB,前半增 8、後半增 6 | `nativeCreateTracked` @ libfakesdk.so ← `PlayerActivity.onCreate` |
| ③上限 4 塊的池(暖機已配 2 塊) | 0 → 0 | 11244 → 16268 | 停住:結尾 4 MB,前半增 2、後半增 0 | `nativePoolAcquire` @ libfakesdk.so |
| 正常版(都有 release) | 0 → 0 | 7220 → 6264 | 不增長 | `nativeCreate`(開關之間在 0 與 2 MB 來回) |

- 當時的草稿判法(分漲停的判法已拆到 [[Projects/原生記憶體增長判法_計劃]];這份只用表裡的結尾累計):把量測期間的傾印依時間切成前後兩半,每個呼叫位置算「中間那次傾印比第一次多多少」(前半增)與「最後一次比中間多多少」(後半增);結尾還留著、前半有增、後半增量至少是前半的一半 → 線性增長;結尾還留著、但後半沒有跟著漲 → 停住;其他 → 不增長。只列結尾或增量超過 1 MB 的。四種情境都分對。
- heapprofd 只記開始記帳之後的配置,所以暖機期間配的(包括池已經配好的那 2 塊)本來就不算進來,不用另外扣基線。
- 呼叫鏈看得到 .so 匯出的 JNI 函式名(這支 .so 沒拿掉匯出符號)與 App 的函式,跟既有 L3 的結論一樣只到函式、沒有行號。
- 錄檔與暫存都已刪掉(錄檔當含個資處理,只留上面的數字)。

實驗當時的查詢(trace_processor;malloc 上一層的函式當呼叫位置;正式版改法見〈排行怎麼算〉第 1、2 條與〈打算怎麼做〉第 4 步):

```
create perfetto table site as
select a.ts, a.size, coalesce(pf.name, '?') || ' @ ' || coalesce(pm.name, '?') as site
from heap_profile_allocation a
join stack_profile_callsite c on c.id = a.callsite_id
left join stack_profile_callsite p on p.id = c.parent_id
left join stack_profile_frame pf on pf.id = p.frame_id
left join stack_profile_mapping pm on pm.id = pf.mapping
where a.heap_name = 'libc.malloc';
create perfetto table dumps as select distinct ts from site;
select d.ts, s.site, sum(s.size) as unreleased
from dumps d join site s on s.ts <= d.ts group by d.ts, s.site order by s.site, d.ts;
```

實驗當時的錄製設定(正式版時長與檔名見〈打算怎麼做〉第 3 步;推到裝置 `/data/misc/perfetto-configs/`,`perfetto --txt -c … -o /data/misc/perfetto-traces/… --background`,停錄用 `kill -TERM`):

```
buffers { size_kb: 65536 fill_policy: DISCARD }
data_sources { config { name: "android.heapprofd" heapprofd_config {
  process_cmdline: "<套件名>" sampling_interval_bytes: 4096 shmem_size_bytes: 8388608 no_startup: true
  continuous_dump_config { dump_phase_ms: 1000 dump_interval_ms: 1000 } } } }
duration_ms: 120000
```

## 排行怎麼算

收集腳本取數、lumos 排與印(收集腳本照既有慣例只縮減資料、不判過不過):

1. 呼叫位置(收集腳本):從 malloc 那一框往上走,跳過配置器那幾層——所在 .so 檔名是 libc.so、libc++.so、libc++_shared.so、libstdc++.so(這幾支裡的全部框架都跳過,歸責給呼叫它們的 SDK),或函式名精確等於 malloc、calloc、realloc、posix_memalign、memalign、aligned_alloc、__libc_malloc、je_malloc、tc_malloc、__wrap_malloc,或 demangle 名以「operator new」開頭、mangle 名以 _Znw 或 _Zna 開頭——第一個不是配置器的框架就是呼叫位置,再往上一框是呼叫者;整條都是配置器時呼叫位置記成「?」,沒有上一框時呼叫者記成「?」。name 是 NULL 或空字串都當沒有符號,寫成「.so 檔名+0x相對位址」並標沒有符號;mapping 沒有名字時 .so 記成「?」、不是系統函式庫;.so 只記檔名(SQLite 字串函式取最後一段),完整路徑在 /system/ 或 /apex/ 底下的另標系統函式庫。
2. 數字(收集腳本):每個 callsite 結束時還沒釋放的量 = 它所有列的 size 加總(heapprofd 只記開錄之後的配置;停錄時會再傾印一次,5 秒內沒寫完就不補、stats 記 heapprofd_non_finalized_profile,照〈打算怎麼做〉第 4 步寫 failed;查證記在 governance/review-reports/原生記憶體增長提示/r3-intake.md);先歸併到呼叫位置(函式、.so、系統旗標三者當鍵,所以不同路徑的同名 .so 不會混在一起),再篩結束累計至少 1 MiB(1048576 位元組)的,照結束累計降冪、函式名升冪、.so 升冪取前 200 個;呼叫者取「從它進來的那些 callsite 結束累計加總」最大的那個,並列照呼叫者名字升冪。1 MiB 只在這裡篩一次。
3. 排與印(lumos):照結束累計由大到小,最多印 20 個;每行印函式、所在 .so、呼叫者、結束時還留著多少、有沒有符號、是不是系統函式庫;最上面一行寫明「量測結束時還留著的原生配置,含快取與池,不代表漏」。

## 打算怎麼做

1. 預設關,按情境打開(d4):`stability` 段加一個選填鍵 `native_retained`,值是情境名的清單,`"@default"` 代表沒指定情境的那一段(沒設 LUMOS_STABILITY_SCENARIO;情境名只收英數字、底線、連字號,這個名字不會跟情境撞),其他名字要在 `stability_scenarios` 裡;沒寫等於空清單。lumos 在 `_macrobench_stab_top_err` 驗(那裡拿得到 `stability_scenarios`):不是清單、元素不是非空字串、有重複、或名字對不到情境 → 回 2 擋下。**不寫進 `stability_scenarios`、不動 E2E_SCENARIO_KEYS、不改既有情境名規則**:舊版 lumos 不驗 stability 段的未知鍵,退回舊版時設定不會被擋下。收集腳本的 `load_config` 把這次的情境名一起回傳給 `measure`。
2. 判斷順序寫死,第一個不成立的就是結果檔那段的狀態與原因:這次的情境不在 `native_retained` 裡 → unsupported「設定沒替這個情境打開 native_retained」;`stability.test_data` 的 value 不是 true(d3,只看 stability 段)→ unsupported「沒宣告測試資料」;android_sdk 讀不到 → unsupported「讀不到 Android 版本」;android_sdk 低於 30(只接已在跑的行程要 Android 11 以上)→ unsupported「Android 版本不支援」;第一段驅動失敗或 pid 讀不到 → failed「第一段沒跑成,不跑第二段」;其餘才跑第二段。
3. 收集腳本先把第一段的結果寫成結果檔(這時 `native_retained` 段寫 failed「第二段沒跑完」),再在既有量測全部讀完之後另跑一段(d1),跑完原子替換結果檔:停 App → 啟動 → 讀結束紀錄與 pid → 暖機 W 輪 → 開 heapprofd → 驅動量測 N 輪 → 停錄(heapprofd 在停錄時一定補最後一次傾印,上限 stop_timeout_ms 預設 5000 毫秒,既有 stop_record 最多等 30 秒,夠)→ 讀 pid 與結束紀錄 → 停 App。第二段整段包在 try/except Exception 裡,任何意外都寫成 failed 附例外類型,不會讓第一段的結果檔寫不出來。第二段的 pid、驅動結果、前後結束紀錄寫在新段落裡,**不碰既有的 pids、exits、unreachable、native_heap_kb**;任何一次驅動回 ok false → failed「驅動失敗」附 why;第二段期間 App 結束 → failed「第二段期間 App 結束(類型)」;前後 pid 不同 → failed「行程換了」。錄製沿用 `start_record`、`stop_record`,參數改成設定範本、遠端檔名前綴、本機錄檔名、本機設定檔名、上限訊息裡的設定鍵(第一段照舊傳原本的值):設定範本另開 `android-stability-heapprofd.pbtxt`(`__PROCESS__`、`__DURATION_MS__` 佔位,時長照 `stability.max_record_s`),遠端檔名 `lumos-native-<run-id>.*`(跟第一段的 `lumos-stability-` 前綴不同,不會跟某個 run-id 撞名),本機 `heap-native.pftrace`(放 run 目錄第一層、符合既有 7 天刪的樣式)與 `record-native.pbtxt`;這兩個檔名只在這次情境打開時才加進開跑前的 git 忽略檢查。第一段的錄製從 state 拿掉之後才開第二段,沿用同一個 `state["rec"]` 槽;state 另記「第二段進行中」,被中斷時 cleanup 照舊收錄製與裝置暫存,另外停 App(App 身上還掛著 heapprofd)。
4. 收集腳本的查詢放新的範本 `android-stability-native.sql`(照既有兩支 .sql 範本,用標準 SQLite 與 android-ui-attribution.sql 用過的 WITH RECURSIVE;用到的表與欄位:heap_profile_allocation 的 size、callsite_id、heap_name,stack_profile_callsite、stack_profile_frame 的 name 與 rel_pc、stack_profile_mapping 的 name,stats 的 name、severity、value),每次 TP 呼叫只跑一條回傳列的語句;跟第一段用同一個 TP;測試照既有 .sql 範本的做法,用 Python 內建 sqlite 對假表跑。照〈排行怎麼算〉第 1、2 條在 SQL 裡算到呼叫位置層,不做傾印數乘列數的連接。「讀範本、換佔位、寫暫存檔、跑 TP、解析成列」抽成一支共用函式,裡面用 csv.reader(函式簽名會帶逗號與引號),既有的 heap_counts、cycle_numbers 一起改用它(行為不變,用既有測試守),整支檔只剩一種解析。跑完的檢查順序寫死:查詢超過收集腳本的 T_LONG → failed「查詢逾時」;stats 表裡 severity 是 error 或 data_loss、值非 0 的 → failed 附那幾項的名字(例如 heapprofd_rejected_concurrent 是同一行程已有別的 heapprofd 工作階段、heapprofd_buffer_overran 是緩衝溢位、heapprofd_non_finalized_profile 是最後一次傾印沒寫完);heap_profile_allocation 沒有任何一列 → failed「沒錄到原生配置記帳(App 不是 profileable、或主行程名不是套件名)」;其餘 ok。事前不偵測 profileable:沒有可靠的事前判法,沒錄到時照上一句寫原因。
5. 結果檔新段落 `native_retained`:狀態只用既有的 ok、failed、unsupported 加 reason(沿用 `src()`);ok 時另存 `main_process_only: true`(process_cmdline 是套件名,只量主行程),以及 `sites` 清單,每一項有 `func`、`so`、`caller`、`symbol`(true/false)、`system`(true/false)、`retained`(結束時還沒釋放的位元組整數);照 retained 排、最多 200 項。收集腳本不判漲停。
6. lumos 讀結果檔的 `native_retained`,放進 macrobench 結果的固定鍵 `native_retained`:物件 `{status, reason, sites}`,一開始就放進結果的初始字典(跟 stability_unjudged 同處),有給 `--stability` 就在載入結果檔之後算,有結果目錄的主路徑與只有 stability 的路徑都算、都印;讀來源段沿用 `_macrobench_stab_src`;印的函式獨立於門檻輸出,標「只提醒,不擋推送」,照〈排行怎麼算〉第 3 條印,每行過 `_events_clean(…, 500)`(跟鄰近 stability 輸出同一支)。結果檔沒有這段(舊收集腳本)→ status 寫 unsupported「結果檔沒有 native_retained 段」、不印;打開了但 status 不是 ok → 印一行「原生配置排行沒跑成:<原因>」;retained 用 `_secev_int` 驗整數、再擋負數,不合格的呼叫位置不採用,但印一行「有 N 個呼叫位置的數字不合格,沒採用」。只提醒,不進 threshold_failures、不影響回傳碼與推送前檢查(d2)。
7. skill lumos-android-evidence:L0 的往下條件不變(排行一定會列出快取與池,拿它當往下條件會每次都往下);`native_retained` 鍵不存在 = lumos 太舊,照舊手動錄 L3,不當成零筆;L3 原生那段改成先看這份排行,沒打開的情境照舊手動錄;收據裡從排行來的呼叫位置標 [INFERRED](heapprofd 是取樣估計);reference.md 的設定表、「driver 跑幾次」、保留清單、「收集腳本只清自己的 lumos-stability-<run-id>.*」那句(加上 lumos-native-<run-id>.*)一起改。排行不寫進 e2e 的本機總表。兩支新範本檔登記進 `_VENDORED_TREE_FILES`(還有它的測試清單)、加 SPDX 檔頭,並加進 Systems/android-stability-collector 的 about_code、改它的負責範圍。實作後把 [[Projects/Android記憶體與穩定性驗收_計劃]] 那句「只剩 Native Heap 前後數字當線索」改成指到這份提示、「用同一條驅動指令呼叫兩次」補上打開時的第二段;[[Projects/Android逐層診斷_計劃]] 的分層 WHY 補一條例外:打開 native_retained 的情境在收集階段就錄 heapprofd。

## 跟舊否決的差別

- [[Projects/Android逐層診斷_計劃]] 否決過「每次都錄 Trace+CPU 取樣+記憶體」(慢、改變被量對象、留下不必要的敏感檔):那條仍成立,本計劃照它改成按情境打開、預設關(d4),慢與錄檔只落在人主動打開的情境上,不是每次驗收都錄。
- [[Projects/Android記憶體與穩定性驗收_計劃]] 原生洩漏判法否決過「只看 Native Heap 趨勢」:那條否決的對象是整個行程的 Native Heap 總量(有升有降,判不出是誰);本計劃看的是 heapprofd 按呼叫位置記的未釋放量,不判趨勢,只列結束時留著最多的,而且只提醒不擋(d2)。
- 同一篇 Java 洩漏判法否決過「每輪結束值判趨勢」:那條的對象是每輪結束時的 Java 堆積總量(實驗室沒有洩漏時五輪忽高忽低兩倍);本計劃不判趨勢、只列每個呼叫位置結束時的未釋放量,同樣只提醒。

## 實務隱患

- 量測干擾:heapprofd 掛在 malloc 上取樣,會拖慢 App;照 d1 另跑一段,而且第二段排在既有量測全部讀完之後、pid 與結束紀錄另存,既有數字與判定不受影響。
REVISIT:2027-01-31 在實驗室量 heapprofd 那段 N 輪比不錄時慢多少,寫回本節
- 排行的邊界:排行列的是結束時還留著的量,快取、物件池與一次性初始化也會上榜,不代表漏,要人看;小於取樣間隔(4096 位元組)的配置是取樣估計,小量的數字會抖;heapprofd 接上已在跑的行程要等「下一次配置之後幾百毫秒」才開始記(官方文件),量測一開始那一下的配置可能漏記;排行分不出漲停的已知形狀(池在前段填滿、一次性初始化、輪長不均、大基底加少量漏)列在 [[Projects/原生記憶體增長判法_計劃]]。
- 呼叫位置:SDK 自己包一層配置器(不在〈排行怎麼算〉第 1 條名單裡)、或 SDK 自己的模板配置沒內聯時,呼叫位置會落在那層上,要人往上看呼叫者;同一呼叫位置有好幾個呼叫者時只記結束累計加總最大的那個;系統函式庫(例如 Bitmap 的原生記憶體)也可能被列出,標系統函式庫讓人分辨。
- 時間:打開的情境多一段暖機加量測(W+N 輪)再加停錄時最後一次傾印(最多 5 秒)與查詢;e2e 的收集步驟單步上限是 3600 秒,長情境打開前先估一次。
- 中斷:第二段被 Ctrl-C 或逾時打斷時,第一段的結果檔已經先寫好(native_retained 段是 failed「第二段沒跑完」),App 被停掉。
- 多行程:只量主行程;SDK 放在其他行程時這段看不到,結果檔寫明只量主行程。
- 個資:heapprofd 記的是呼叫鏈、大小與時間,這次查的欄位裡沒有記憶體內容;錄檔仍照 heap-*.pftrace 的保存規則當含個資處理。官方文件裡沒找到明講「不含內容」的那一句。
- 版本:實驗用的主機分析工具是 v58.2、裝置端是內建 perfetto,不是 skill 釘的 v57.2(見 REVISIT);收集腳本照第一段用同一個 TP。
- 前提:user 建置只能錄 profileable 或 debuggable 的 App;沒錄到時列成 failed 並寫出可能原因。
- 金流(不排除):第二段會把情境再驅動 W+N 次;情境含下單(例如結帳)時,會在測試後端多下 W+N 次單,跟既有量測的 W+N 次同性質。前提是 `stability.test_data` 的人裁(只在測試帳號與假資料下跑)成立;替某個情境打開 `native_retained` 的人要確認那個情境重複跑沒有測試環境以外的副作用。
- 遷移:專案把 `native_retained` 寫進設定,等於改了記憶體設定,e2e 的記憶體設定指紋會變,推送前要重跑整套。
- 已排除:對外送出:錄檔先寫在測試裝置的 `/data/misc/perfetto-traces/`,停錄後拉回本機 run 目錄、刪掉裝置上那份(沿用 stop_record);中斷時沿用既有 cleanup;主機當掉或 adb 斷線時裝置上可能留著,跟第一段同一個天花板,reference.md 寫怎麼查。都不離開測試裝置與本機。
- 不可逆(不排除):檔案只寫被 git 忽略的 run 目錄、結果檔與測試裝置的暫存,本機錄檔靠下次開跑時刪 7 天前的(d3 的既有代價:專案不再跑收集腳本就不會刪);但情境在測試後端造成的副作用(同上一條金流)回退也還原不了。
REVISIT:2027-01-31 看兩個真實專案的 run 目錄有沒有超過 7 天還在的 heap-native.pftrace,有就把刪舊檔改到 lumos doctor 也會提醒
- 已排除:守衛面:只提醒,不改任何判定、回傳碼或推送前檢查;前提是第二段排在既有讀取之後、pid 與結束紀錄另存(〈打算怎麼做〉第 3 步),S4 的測試連第二段出事(App 結束、驅動失敗、意外例外、被中斷)的情況一起驗。

## 條款(草案)

- [S1] 當某個呼叫位置的結束累計至少 1 MiB 時,排行應列出它(函式、所在 .so、呼叫者、結束時還留著多少、有沒有符號、是不是系統函式庫),照結束累計由大到小排、最多 20 個,最上面一行寫明含快取與池、不代表漏 [test:待定]
- [S2] 當某個呼叫位置的結束累計不到 1 MiB 時,收集腳本應不存它、排行不列 [test:待定]
- [S3] 當 malloc 的上一層是配置器(〈排行怎麼算〉第 1 條列的那幾支 .so 與函式)時,呼叫位置應是第一個不是配置器的框架;name 是 NULL 或空字串時應寫成 .so 檔名加相對位址並標沒有符號;mapping 沒有名字時 .so 應記成「?」、不是系統函式庫;整條都是配置器時呼叫位置應記成「?」 [test:待定]
- [S21] 當同一個呼叫位置從幾個呼叫者進來時,caller 應是從它進來的 callsite 結束累計加總最大的那個,並列照呼叫者名字升冪,沒有上一框時是「?」 [test:待定]
- [S22] 當收集腳本寫出 ok 的 `native_retained` 段時,應帶 `main_process_only: true`,錄檔應是 run 目錄第一層的 heap-native.pftrace(符合既有 7 天刪的樣式) [test:待定]
- [S12] 當同一個函式從幾條不同的呼叫鏈進來、每條都不到 1 MiB 但加總至少 1 MiB 時,排行應把它當一個呼叫位置列出 [test:待定]
- [S4] 當排行列出或沒列出呼叫位置、或第二段 App 結束、驅動失敗、丟出意外例外、被中斷時,lumos 的判定結果、回傳碼、推送前檢查,以及結果檔既有的 pids、exits、unreachable、native_heap_kb 應都不變,結果檔也應照樣寫出 [test:待定]
- [S6] 當設定沒寫 `stability.native_retained`、這次的情境不在清單裡、沒宣告測試資料、android_sdk 讀不到、或 android_sdk 低於 30 時,收集腳本(用 load_config 回傳的這次情境名比對)應不跑第二段、不錄檔,結果檔那段寫 unsupported 並照〈打算怎麼做〉第 2 步的順序寫第一個不成立的原因 [test:待定]
- [S13] 當 `stability.native_retained` 不是清單、元素不是非空字串、有重複、或名字對不到 `stability_scenarios` 也不是 "@default" 時,lumos 應回 2 擋下 [test:待定]
- [S7] 當查詢逾時、stats 有 severity 是 error 或 data_loss 而且值非 0 的項目、heap_profile_allocation 沒有任何一列、第一段沒跑成、第二段任何一次驅動回 ok false、第二段丟出意外例外、或第二段期間 App 結束、或第二段前後 pid 不同時,結果檔那段應寫 failed 附原因,跑完後的三項照〈打算怎麼做〉第 4 步的順序取第一個 [test:待定]
- [S14] 當錄製成功、stats 只有 info 等級的 heapprofd 計數非 0 時,結果檔那段應寫 ok [test:待定]
- [S17] 當第二段開始時,結果檔應已寫出第一段的全部欄位,`native_retained` 段是 failed「第二段沒跑完」;第二段跑完後結果檔應整份原子替換 [test:待定]
- [S18] 當這次的情境沒有打開 `native_retained` 時,開跑前的 git 忽略檢查應不檢查 heap-native.pftrace 與 record-native.pbtxt [test:待定]
- [S8] 當第二段進行中被中斷時,cleanup 應收掉裝置上第二段的設定檔與錄檔,並停掉 App [test:待定]
- [S9] 當結果檔沒有 `native_retained` 段時,lumos 的 `native_retained` 鍵應是 unsupported 並附原因、不印排行、回傳碼不變 [test:待定]
- [S15] 當 `native_retained` 段打開了但 status 不是 ok 時,lumos 應印一行「原生配置排行沒跑成」加原因,回傳碼不變 [test:待定]
- [S16] 當專案只有 stability 段、沒有 Macrobenchmark 結果目錄時,lumos 的文字與 `--json` 輸出應照樣帶 `native_retained` [test:待定]
- [S10] 當 `native_retained` 段裡某個呼叫位置的 retained 不是非負整數時,lumos 應不採用那個呼叫位置,並印出沒採用的個數 [test:待定]
- [S11] 當呼叫位置超過上限時,收集腳本應只存結束累計最大的 200 個(並列照函式名、.so 升冪)、lumos 應只印前 20 個,函式名裡的控制字元印出前應已清掉 [test:待定]
- [S20] 當收集腳本解析任何一支 .sql 範本的輸出時,應走同一支共用函式、用 csv.reader;既有 heap_counts 與 cycle_numbers 的結果應不變 [test:待定]
- [S19] 當 lumos 的輸出沒有 `native_retained` 鍵時,skill 應照舊手動錄 L3、不當成零筆 [manual:讀 skill lumos-android-evidence 的 L3 原生那段,核對有這句,而且 L0 的往下條件沒有加排行]
- [S5] 當實驗室分別埋入三種情境(沒人指著的漏、SDK 內部留登記、上限固定的池)與正常版時,前兩種應列出並點到埋的那個 JNI 函式,池照實列出(含快取與池),正常版不列 [manual:macrobench-lab 實機各跑一次,正式版程式寫完後重跑]

## 回退

逐項:
- 收集腳本:拿掉第二段、`android-stability-heapprofd.pbtxt`、`android-stability-native.sql`,以及 start_record、stop_record 加的參數(同一支檔同一次還原);結果檔不再有 `native_retained` 段,新版 lumos 讀到沒有這段的結果檔把鍵寫成 unsupported、不印。
- lumos:拿掉排行與 `native_retained` 鍵的驗證;設定裡已寫的 `stability.native_retained` 會被舊版忽略(stability 段不驗未知鍵),不會擋下。**預設留著那個鍵**:刪掉會讓 e2e 的記憶體設定指紋再變一次、每條分支推送前要整套重跑,要刪就等下次本來就要改記憶體設定時一起刪。
- 舊新版本錯配:舊收集腳本配新 lumos → 鍵是 unsupported「結果檔沒有 native_retained 段」;新收集腳本配舊 lumos → 照樣多跑一段、留下錄檔,但舊版不讀(純成本,退回時兩邊一起退);skill 新、lumos 舊 → skill 讀不到鍵,照舊手動錄 L3。
- 已經寫出的 `heap-native.pftrace`、`record-native.pbtxt`:在被忽略的 run 目錄,錄檔照 7 天自動刪(要還有人跑收集腳本),設定檔不自動刪;要手動清就刪各 run 目錄第一層這兩個檔名。
- 消費專案:`lumos update` 只補不刪,退回後專案裡的 `scripts/templates/android-stability-heapprofd.pbtxt`(新增)與 `android-stability-native.sql` 會留著,要各專案手動刪這兩支(在專案根目錄,寫字面路徑)。
- 裝置上:正常與中斷時都沿用既有清理;懷疑有殘留時用 `adb shell ls /data/misc/perfetto-traces/ /data/misc/perfetto-configs/` 查 `lumos-native-*`,舊版收集腳本不認得這個前綴,要自己刪。
- 測試後端:第二段多跑的情境造成的資料(例如多下的單)回退還原不了,要靠測試環境自己的重置。
- skill、reference.md、Systems 筆記:照 git 還原。

## 審計修正紀錄

- r1(2026-10-28,6 席):51 條/blocking 29/判法、呼叫位置、錄不到被當沒事、第二段位置與清理、分層、設定鍵退回、已排除理由、落點與文件、查詢效能、分析工具版本、撤除條件十一類全折,a6(門檻數字寫死)放行;折完派校對代理對差異核鏡像段,14 處不一致當輪改掉;席報告在 governance/review-reports/原生記憶體增長提示/
- r1 新增機制與「不加的最小解為什麼不夠」:新設定範本 pbtxt——內嵌在收集腳本會是第二種寫法(既有錄製設定就是範本檔);start_record 加兩個參數——另寫一支會有第二套開錄、停錄、登記清理;結果檔 `native_retained` 段與 macrobench 結果鍵——沒有它 lumos 讀不到、使用者看不到;`stability.native_retained` 清單——d4 要按情境開,寫進情境會讓退回舊版時整份設定被擋。
- r2(2026-10-28,6 席):54 條/blocking 24/三個時間點的做法本身站不住(傾印清單取不到沒變動的傾印、開頭要對時、單點碰到配了又還會誤報),換成「起點固定 0、兩個窗口取最小值」;stats 篩法、版本邊界、失敗原因看不到、只有 stability 的專案收不到、例外會吃掉第一段、檔名參數、查詢放範本、回退細節全折;席報告在 governance/review-reports/原生記憶體增長提示/
- r2 新增機制與「不加的最小解為什麼不夠」:查詢範本 android-stability-native.sql——內嵌是第二種寫法(既有兩支查詢都是範本);先寫第一段結果檔再原子替換——不先寫,第二段任何意外都會丟掉第一段已量好的結果;cleanup 多停 App——不停,被中斷時 App 一直掛著 heapprofd;結果鍵改成物件——空清單分不出「沒增長」與「沒錄到」。
- r3(2026-10-28,3 席,使用者裁只審新判法):18 條/blocking 8/判法換了兩次形狀仍受時間對齊左右(池子情境編排者自跑 64 組參數全判成在漲)、分不出一次性跳升;到頂攤人,使用者裁拆兩份(d5):這份縮成排行、分漲停的判法搬到 [[Projects/原生記憶體增長判法_計劃]];篩選與前 200 改在呼叫位置層、沒有符號與 mapping 缺名、配置器名單比對方式、跑完後檢查順序、共用解析函式、整數驗證全折;不確定的事照使用者要求上網查證(最後一次傾印、stats 等級、接上行程的延遲、錄完後 App 的負擔),結果寫在 r3-intake.md
- r3 新增機制與「不加的最小解為什麼不夠」:共用的「跑範本並解析成列」函式——不抽的話同一支檔會有 split 與 csv.reader 兩種解析,新查詢的多個文字欄又不能用 split。
