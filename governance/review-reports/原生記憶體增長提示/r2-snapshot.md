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
---
# 原生記憶體增長提示_計劃

白話:記憶體與穩定性驗收現在用「沒人指著的原生記憶體」掃描抓 .so 忘了 release,但 SDK 自己留一份清單、還指著那塊記憶體時掃描是 0,抓不到;這種只剩 Native Heap 前後兩個數字(只寫在收集腳本的結果檔,lumos 判定不讀也不印)。這份計劃讓人替要查的情境(例如結帳)自己打開、預設關(d4),打開的情境在既有量測之後另跑一段 N 輪,只錄 Perfetto 的原生配置記帳(heapprofd,掛在 malloc/free 上記每個呼叫位置配了多少、還了多少;d1),按呼叫位置(從 malloc 往上跳過 libc、libc++ 這些配置器,第一個不是配置器的函式)彙總到每次傾印時還沒釋放的量,只把整段持續在漲(到後半還在漲)的列成**優化建議**(哪支 .so 的哪個函式、App 哪個函式呼叫的、漲了多少),照整段增量排序,**只提醒、不擋推送**;漲到一定量就停住的快取與物件池不報。2026-10-28 Enzo 要求「把能優化的效能問題抓出來優化,不是找碴」,並要求先查精準的世界解、再到實驗室實測。

PRIOR-ART: 最小解在既有的收集腳本裡:它已經有「暖機 W 輪 → 量測 N 輪」兩次驅動呼叫,量測期間本來就錄一份 Perfetto 追蹤檔;skill lumos-android-evidence 的 L3(逐層診斷的第四層「誰配置、誰留住」,要宣告測試資料才做)已經在用 heapprofd(`--heaps libc.malloc`)事後診斷原生漏法。世界解:①Perfetto heapprofd(Android 10 以上;user 建置只限 profileable 或 debuggable 的 App)的 HeapprofdConfig 欄位照 v57.2 的 protos/perfetto/config/profiling/heapprofd_config.proto(github.com/google/perfetto/blob/v57.2/…):`process_cmdline`、`sampling_interval_bytes`(預設 4096,不能是 0)、`shmem_size_bytes`(預設 8 MiB、2 的次方)、`no_startup`(只接已經在跑的行程,Android 11 以上)、`continuous_dump_config { dump_phase_ms dump_interval_ms }`(第一次傾印在 dump_phase_ms 毫秒後,之後每隔 dump_interval_ms 毫秒傾印一次);②trace_processor 的 `heap_profile_allocation` 每列是「這次傾印跟上一次比的差額」(配置正、釋放負;v57.2 src/trace_processor/importers/proto/profile_packet_sequence_state.cc 的 alloc_delta、free_delta),所以某個傾印時間點還沒釋放的量 = 同一呼叫位置、ts 不晚於那一刻的 size 加總,官方 stdlib 的 android.memory.heap_profile.summary_tree 也是 `sum(size)` 當沒釋放的量;③「重複回到同一個畫面、每輪都在漲才算漏」借 BLeak(Vilk & Berger,PLDI 2018,pldi18.sigplan.org)與 Square 的工具 LeakCanary 3.0 的堆積增長偵測(square.github.io/leakcanary/changelog:重複跑情境直到不再增長,另有暖機減少誤報)。裁定:錄製與查詢原樣借 Perfetto,增長判法借「重複情境、看增量有沒有停」的形狀,自己只寫整段增量與後半增量的比較;不採 dump_at_max(只有峰值那一刻,看不出趨勢)。
RETIRE-IF: 上線三個月後兩個真實專案的提示零觸發,或被點名的呼叫位置有一半以上查明是正常快取(誤報多過真報),就把這項提示拿掉、只留 L3 的手動診斷;每次驗收多花的時間超過量測本身的兩倍,也拿掉(d1 本來就多一段量測,一倍是預期成本)。
REVISIT:2027-01-31 在實驗室埋一個每輪漏幾十次、每次小於 4096 位元組的小配置,量同一情境跑三次時增量抖多少,判法照實際抖動定下限
REVISIT:2027-01-31 拿兩個真實專案(帶第三方 .so 的)跑過之後,重定「後半增量至少前半的一半」這條判法與 1 MiB 的列出下限;量測輪數 N 小於快取上限時快取會被判成線性增長,看真實 SDK 的池多大再決定 N 的建議值
REVISIT:2027-01-31 收集腳本與分析工具要對到 skill 釘的 Perfetto 版本:2026-10-28 實驗用的主機 trace_processor 是 v58.2(本機與 ~/.cache/lumos/tools 兩支都是)、裝置端是 Android 16 內建的 perfetto,不是 v57.2;正式做之前用 v57.2 重跑同一組實驗或改釘版本

## 實驗室實測(2026-10-28)

在 macrobench-lab 另開工作目錄與分支 native-growth-lab(不推送、不合併)做:假原生 SDK 多兩種情境,SM-X710 / Android 16,benchmark 建置(profileable、非除錯版)。每種:停 App → 啟動 → 驅動暖機 2 輪 → 讀「沒人指著的原生記憶體」與 Native Heap → 開 heapprofd(只接已在跑的行程、每秒傾印一次)→ 驅動量測 8 輪 → 等 3 秒停錄 → 再讀兩個對照數字。每輪開畫面配 2 MB。

| 情境 | 沒人指著(前→後) | Native Heap KB(前→後) | heapprofd 判法 | 點到的呼叫位置 |
|---|---|---|---|---|
| ①沒呼叫 release、記憶體沒人指著 | 0 → 16 MB(8 塊) | 9176 → 26468 | 線性增長:結尾 16 MB,前半增 8、後半增 6 | `nativeCreate` @ libfakesdk.so |
| ②SDK 全域清單留著每個 handle、App 沒 release | 0 → 0(抓不到) | 11576 → 30860 | 線性增長:結尾 16 MB,前半增 8、後半增 6 | `nativeCreateTracked` @ libfakesdk.so ← `PlayerActivity.onCreate` |
| ③上限 4 塊的池(暖機已配 2 塊) | 0 → 0 | 11244 → 16268 | 停住:結尾 4 MB,前半增 2、後半增 0 | `nativePoolAcquire` @ libfakesdk.so |
| 正常版(都有 release) | 0 → 0 | 7220 → 6264 | 不增長 | `nativeCreate`(開關之間在 0 與 2 MB 來回) |

- 當時的草稿判法(已由下面〈判法〉取代,四種情境用新判法重算結果相同):把量測期間的傾印依時間切成前後兩半,每個呼叫位置算「中間那次傾印比第一次多多少」(前半增)與「最後一次比中間多多少」(後半增);結尾還留著、前半有增、後半增量至少是前半的一半 → 線性增長;結尾還留著、但後半沒有跟著漲 → 停住;其他 → 不增長。只列結尾或增量超過 1 MB 的。四種情境都分對。
- heapprofd 只記開始記帳之後的配置,所以暖機期間配的(包括池已經配好的那 2 塊)本來就不算進來,不用另外扣基線。
- 呼叫鏈看得到 .so 匯出的 JNI 函式名(這支 .so 沒拿掉匯出符號)與 App 的函式,跟既有 L3 的結論一樣只到函式、沒有行號。
- 錄檔與暫存都已刪掉(錄檔當含個資處理,只留上面的數字)。

實驗當時的查詢(trace_processor;malloc 上一層的函式當呼叫位置;正式版改法見〈判法〉第 1、2 條與〈打算怎麼做〉第 4 步):

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

## 判法

由 lumos 判(收集腳本只交數字,見〈打算怎麼做〉第 4、5 步):

1. 呼叫位置:從 malloc 那一框往上走,跳過配置器那幾層(所在 .so 檔名是 libc.so、libc++.so、libc++_shared.so、libstdc++.so,或函式名是 malloc、calloc、realloc、posix_memalign、memalign、aligned_alloc、operator new 系列),第一個不是配置器的框架就是呼叫位置,再往上一框記成呼叫者;沒有符號時寫成「.so 檔名+0x相對位址」並標「沒有符號」;.so 只記檔名,不記裝置上的完整路徑。
2. 三個時間點:驅動量測開始前的最後一次傾印(開頭;〈打算怎麼做〉第 3 步先等到第一次傾印才開始驅動,所以一定有)、驅動跑完緊接著停錄後的最後一次傾印(結尾)、時間上最接近兩者正中的那一次(中間);每個呼叫位置在某個時間點的未釋放量 = 那個呼叫位置 ts 不晚於那一刻的 size 加總,那一刻之前沒有列就是 0。傾印少於 3 次 → 收集腳本把這段寫成 failed「樣本不足(傾印少於 3 次)」,不判任何呼叫位置。
3. 整段增量 = 結尾 − 開頭,後半增量 = 結尾 − 中間。整段增量小於 1 MiB(1048576 位元組)→ 不增長;否則後半增量 ≥ 整段增量的三分之一 → 線性增長;其餘 → 停住。三類互斥、涵蓋全部(前半沒漲、後半才漲的落在線性增長;前後都非負時這條等於草稿的「後半至少是前半的一半」)。
4. 只列線性增長,照整段增量由大到小排,最多印 20 個。

## 打算怎麼做

1. 預設關,按情境打開(d4):`stability` 段加一個選填鍵 `native_growth`,值是情境名的清單,`"default"` 代表沒指定情境的那一段(沒設 LUMOS_STABILITY_SCENARIO),其他名字要在 `stability_scenarios` 裡;沒寫等於空清單。lumos 在 `_macrobench_stab_optional_err` 驗:不是字串清單、或名字對不到情境 → 回 2 擋下。**不寫進 `stability_scenarios`、不動 E2E_SCENARIO_KEYS**:舊版 lumos 不驗 stability 段的未知鍵,退回舊版時設定不會被擋下(寫進情境的話,舊版會把它當不認得的欄位擋下整份設定)。
2. 判斷順序寫死,第一個不成立的就是結果檔那段的狀態與原因:這次的情境不在 `native_growth` 裡 → unsupported「設定沒替這個情境打開 native_growth」;`stability.test_data` 的 value 不是 true(d3,只看 stability 段)→ unsupported「沒宣告測試資料」;裝置 Android 11 以下(只接已在跑的行程要 11 以上)→ unsupported「Android 版本不支援」;其餘才錄。
3. 收集腳本在既有量測**全部讀完之後**(第二次讀結束紀錄之後)另跑一段(d1):停 App → 啟動 → 讀結束紀錄與 pid → 暖機 W 輪 → 開 heapprofd → 等第一次傾印(dump_phase_ms 再加 1 秒)→ 驅動量測 N 輪 → 驅動一跑完就停錄 → 讀 pid 與結束紀錄 → 停 App。第二段的 pid、驅動結果、前後結束紀錄寫在新段落裡,**不碰既有的 pids、exits、unreachable、native_heap_kb**,所以既有判定不受第二段影響;第二段期間 App 結束、或前後 pid 不同 → failed「第二段期間 App 結束(類型)」或「行程換了」。錄製沿用 `start_record`、`stop_record`(加兩個參數:設定範本、檔名後綴):設定範本另開 `android-stability-heapprofd.pbtxt`(`__PROCESS__`、`__DURATION_MS__` 佔位,時長照 `stability.max_record_s`),遠端檔名 `lumos-stability-<run-id>-native.*`,本機 `heap-native.pftrace`(放 run 目錄第一層、符合既有 7 天刪的樣式)與 `record-native.pbtxt`,兩個都加進 ARTIFACTS;第一段的錄製從 state 拿掉之後才開第二段,沿用同一個 `state["rec"]` 槽,中斷時的 cleanup 不用改。
4. 收集腳本用跟第一段同一個 TP 查(這次用到的表與欄位:heap_profile_allocation 的 ts、size、callsite_id、heap_name,stack_profile_callsite、stack_profile_frame、stack_profile_mapping 的 name 與 rel_pc,stats;v57.2 與 v58.2 都有):先取傾印時間挑出三個時間點,再一次掃描算每個 callsite 在三個時間點的累計(不做傾印數乘列數的連接),再取這些 callsite 的祖先框架;輸出用 csv 模組解析(函式簽名會帶逗號)。stats 表裡名字以 heapprofd_ 開頭、值非 0 的錯誤計數(例如 heapprofd_buffer_overran、heapprofd_client_disconnected;完整名單實作時照 v57.2 的 stats 定義列進程式) → failed 附那幾項;傾印 0 次 → failed「沒錄到原生配置記帳(App 不是 profileable、同一行程已有別的 heapprofd 工作階段、或主行程名不是套件名)」;查詢超過既有的 T_LONG → failed「查詢逾時」。事前不偵測 profileable:沒有可靠的事前判法,沒錄到時照上一句寫原因。
5. 結果檔新段落 `native_growth`:狀態只用既有的 ok、failed、unsupported 加 reason;ok 時存傾印數、三個時間點、只量主行程(process_cmdline 是套件名)的註記,以及每個呼叫位置的函式、所在 .so、呼叫者、有沒有符號、開頭、中間、結尾未釋放量(位元組);照整段增量排、最多存 200 個。收集腳本不分類、不套下限。
6. lumos 讀結果檔的 `native_growth`,照〈判法〉分類後放進 macrobench 結果的固定鍵 `native_growth`(照 `low_iterations` 的形狀:沒東西時是空清單,文字與 `--json` 都有),只要給了 `--stability` 就讀,不看門檻檔有沒有寫;印的時候標「只提醒,不擋推送」、每行過 `_out_clean`;數字照 `_macrobench_stab_val` 擋負數與非數字;結果檔沒有這段(舊收集腳本)時不印。只提醒,不進 threshold_failures、不影響回傳碼與推送前檢查(d2)。
7. skill lumos-android-evidence:L0 的往下條件加一條「`native_growth` 有列出呼叫位置」;L3 原生那段改成先看這份提示,沒打開的情境照舊手動錄;reference.md 的設定表、「driver 跑幾次」、保留清單一起改;收據裡從提示來的呼叫位置標 [INFERRED](heapprofd 是取樣估計)。提示不寫進 e2e 的本機總表。實作後把 [[Projects/Android記憶體與穩定性驗收_計劃]] 那句「只剩 Native Heap 前後數字當線索」改成指到這份提示。新範本檔登記進 `_VENDORED_TREE_FILES`(還有它的測試清單)。

## 跟舊否決的差別

- [[Projects/Android逐層診斷_計劃]] 否決過「每次都錄 Trace+CPU 取樣+記憶體」(慢、改變被量對象、留下不必要的敏感檔):那條仍成立,本計劃照它改成按情境打開、預設關(d4),慢與錄檔只落在人主動打開的情境上,不是每次驗收都錄。
- [[Projects/Android記憶體與穩定性驗收_計劃]] 原生洩漏判法否決過「只看 Native Heap 趨勢」:那條否決的對象是整個行程的 Native Heap 總量(有升有降,判不出是誰);本計劃看的是 heapprofd 按呼叫位置記的未釋放量,而且只提醒不擋(d2),實驗室四種情境分得開。
- 同一篇 Java 洩漏判法否決過「每輪結束值判趨勢」:那條的對象是每輪結束時的 Java 堆積總量(實驗室沒有洩漏時五輪忽高忽低兩倍);本計劃比的是同一個呼叫位置的整段與後半未釋放增量,不是總量,同樣只提醒。

## 實務隱患

- 量測干擾:heapprofd 掛在 malloc 上取樣,會拖慢 App;照 d1 另跑一段,而且第二段排在既有量測全部讀完之後、pid 與結束紀錄另存,既有數字與判定不受影響。
REVISIT:2027-01-31 在實驗室量 heapprofd 那段 N 輪比不錄時慢多少,寫回本節
- 判法的邊界:量測輪數小於快取上限時,快取在整段量測都在漲,會被判成線性增長;小於取樣間隔(4096 位元組)的配置是取樣估計,小量漏法的數字會抖;驅動跑不到 2 秒時傾印不到 3 次,列成樣本不足。
- 呼叫位置:SDK 自己包一層配置器(不是上面列的那幾支 .so)時,呼叫位置會落在那層包裝上,要人往上看呼叫者。
- 多行程:只量主行程;SDK 放在其他行程時這段看不到,結果檔寫明只量主行程。
- 個資:heapprofd 記的是呼叫鏈、大小與時間,這次查的欄位裡沒有記憶體內容;錄檔仍照 heap-*.pftrace 的保存規則當含個資處理。官方文件裡沒找到明講「不含內容」的那一句。
- 版本:實驗用的主機分析工具是 v58.2、裝置端是內建 perfetto,不是 skill 釘的 v57.2(見 REVISIT);收集腳本照第一段用同一個 TP。
- 前提:user 建置只能錄 profileable 或 debuggable 的 App;沒錄到時列成 failed 並寫出可能原因。
- 金流(不排除):第二段會把情境再驅動 W+N 次;情境含下單(例如結帳)時,會在測試後端多下 W+N 次單,跟既有量測的 W+N 次同性質。前提是 `stability.test_data` 的人裁(只在測試帳號與假資料下跑)成立;替某個情境打開 `native_growth` 的人要確認那個情境重複跑沒有測試環境以外的副作用。
- 遷移:專案把 `native_growth` 寫進設定,等於改了記憶體設定,e2e 的記憶體設定指紋會變,推送前要重跑整套。
- 已排除:對外送出:錄檔先寫在測試裝置的 `/data/misc/perfetto-traces/`,停錄後拉回本機 run 目錄、刪掉裝置上那份(沿用 stop_record);中斷時沿用既有 cleanup;主機當掉或 adb 斷線時裝置上可能留著,跟第一段同一個天花板,reference.md 寫怎麼查。都不離開測試裝置與本機。
- 已排除:不可逆:只寫被 git 忽略的 run 目錄、結果檔與測試裝置的暫存;本機錄檔靠下次開跑時刪 7 天前的(d3 的既有代價:專案不再跑收集腳本就不會刪)。
REVISIT:2027-01-31 看兩個真實專案的 run 目錄有沒有超過 7 天還在的 heap-native.pftrace,有就把刪舊檔改到 lumos doctor 也會提醒
- 已排除:守衛面:只提醒,不改任何判定、回傳碼或推送前檢查;前提是第二段排在既有讀取之後、pid 與結束紀錄另存(〈打算怎麼做〉第 3 步),S4 的測試連第二段出事的情況一起驗。

## 條款(草案)

- [S1] 當某個呼叫位置的整段增量至少 1 MiB、而且後半增量至少是整段增量的三分之一時,提示應列出它(函式、所在 .so、呼叫者、開頭、中間、結尾未釋放量),照整段增量由大到小排、最多 20 個 [test:待定]
- [S2] 當某個呼叫位置整段增量至少 1 MiB、但後半增量不到整段增量的三分之一時(快取或物件池),提示不應列出它;整段增量不到 1 MiB 的也不列 [test:待定]
- [S3] 當 malloc 的上一層是配置器(〈判法〉第 1 條列的那幾支 .so 與函式)時,呼叫位置應是第一個不是配置器的框架;沒有符號時應寫成 .so 檔名加相對位址並標沒有符號 [test:待定]
- [S4] 當提示列出或沒列出呼叫位置、或第二段期間 App 結束時,lumos 的判定結果、回傳碼、推送前檢查,以及結果檔既有的 pids、exits、unreachable、native_heap_kb 應都不變 [test:待定]
- [S6] 當這次的情境不在 `stability.native_growth` 裡、沒宣告測試資料、或裝置是 Android 11 以下時,收集腳本應不跑第二段、不錄檔,結果檔那段寫 unsupported 並照〈打算怎麼做〉第 2 步的順序寫第一個不成立的原因;`native_growth` 不是字串清單、或名字對不到情境時 lumos 應回 2 擋下 [test:待定]
- [S7] 當傾印少於 3 次、傾印 0 次、stats 有 heapprofd 的錯誤計數、查詢逾時、第二段期間 App 結束、或第二段前後 pid 不同時,結果檔那段應寫 failed 附原因,lumos 不列任何呼叫位置 [test:待定]
- [S8] 當第二段進行中被中斷時,裝置上第二段的設定檔與錄檔應被 cleanup 收掉 [test:待定]
- [S9] 當結果檔沒有 `native_growth` 段時,lumos 應不印這項提示、回傳碼不變 [test:待定]
- [S10] 當 `native_growth` 段裡某個呼叫位置的數字是負數或不是數字時,lumos 應不採用那個呼叫位置 [test:待定]
- [S11] 當呼叫位置超過上限時,收集腳本應只存整段增量最大的 200 個、lumos 應只印前 20 個,函式名裡的控制字元印出前應已清掉 [test:待定]
- [S5] 當實驗室分別埋入三種情境(沒人指著的漏、SDK 內部留登記、上限固定的池)時,前兩種應被列出、第三種不列 [manual:macrobench-lab 實機各跑一次,2026-10-28 草稿實驗已分對,正式版程式寫完要重跑]

## 回退

逐項:
- 收集腳本:拿掉第二段、`android-stability-heapprofd.pbtxt` 與 ARTIFACTS 那兩項;結果檔不再有 `native_growth` 段,新版 lumos 讀到沒有這段的結果檔不印。
- lumos:拿掉提示與 `native_growth` 鍵的驗證;設定裡已寫的 `stability.native_growth` 會被舊版忽略(stability 段不驗未知鍵),不會擋下;要清乾淨就請各專案刪掉那個鍵。
- 已經寫出的 `heap-native.pftrace`、`record-native.pbtxt`:在被忽略的 run 目錄,錄檔照 7 天自動刪(要還有人跑收集腳本),設定檔不自動刪。
- 裝置上:正常與中斷時都沿用既有清理;懷疑有殘留時用 `adb shell ls /data/misc/perfetto-traces/ /data/misc/perfetto-configs/` 查 `lumos-stability-*-native.*`。
- skill、reference.md、Systems 筆記:照 git 還原;消費專案照抄的收集腳本要各自更新(lumos update)。

## 審計修正紀錄

- r1(2026-10-28,6 席):51 條/blocking 29/判法、呼叫位置、錄不到被當沒事、第二段位置與清理、分層、設定鍵退回、已排除理由、落點與文件、查詢效能、分析工具版本、撤除條件十一類全折,a6(門檻數字寫死)放行;折完派校對代理對差異核鏡像段,14 處不一致當輪改掉;席報告在 governance/review-reports/原生記憶體增長提示/
- r1 新增機制與「不加的最小解為什麼不夠」:新設定範本 pbtxt——內嵌在收集腳本會是第二種寫法(既有錄製設定就是範本檔);start_record 加兩個參數——另寫一支會有第二套開錄、停錄、登記清理;結果檔 `native_growth` 段與 macrobench 結果鍵——沒有它 lumos 讀不到、使用者看不到;`stability.native_growth` 清單——d4 要按情境開,寫進情境會讓退回舊版時整份設定被擋。
