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

白話:記憶體與穩定性驗收現在用「沒人指著的原生記憶體」掃描抓 .so 忘了 release,但 SDK 自己留一份清單、還指著那塊記憶體時掃描是 0,抓不到;這種只剩 Native Heap 前後兩個數字(只寫在收集腳本的結果檔,lumos 判定不讀也不印)。這份計劃讓人替要查的情境(例如結帳)自己打開、預設關(d4),打開的情境在既有量測之後另跑一段 N 輪,只錄 Perfetto 的原生配置記帳(heapprofd,掛在 malloc/free 上記每個呼叫位置配了多少、還了多少;d1),按「malloc 上一層是哪個函式」彙總到每次傾印時還沒釋放的量,只把每輪都在漲的列成**優化建議**(哪支 .so 的哪個函式、App 哪個函式呼叫的、漲了多少),照增長量排序,**只提醒、不擋推送**;漲到一定量就停住的快取與物件池不報。2026-10-28 Enzo 要求「把能優化的效能問題抓出來優化,不是找碴」,並要求先查精準的世界解、再到實驗室實測。

PRIOR-ART: 最小解在既有的收集腳本裡:它已經有「暖機 W 輪 → 量測 N 輪」兩次驅動呼叫,量測期間本來就錄一份 Perfetto 追蹤檔;skill lumos-android-evidence 的 L3(逐層診斷的第四層「誰配置、誰留住」,要宣告測試資料才做)已經在用 heapprofd(`--heaps libc.malloc`)事後診斷原生漏法。世界解:①Perfetto heapprofd(Android 10 以上;user 建置只限 profileable 或 debuggable 的 App)的 HeapprofdConfig 欄位照 v57.2 的 protos/perfetto/config/profiling/heapprofd_config.proto(github.com/google/perfetto/blob/v57.2/…):`process_cmdline`、`sampling_interval_bytes`(預設 4096,不能是 0)、`shmem_size_bytes`(預設 8 MiB、2 的次方)、`no_startup`(只接已經在跑的行程,Android 11 以上)、`continuous_dump_config { dump_phase_ms dump_interval_ms }`(第一次傾印在 dump_phase_ms 毫秒後,之後每隔 dump_interval_ms 毫秒傾印一次);②trace_processor 的 `heap_profile_allocation` 每列是「這次傾印跟上一次比的差額」(配置正、釋放負;v57.2 src/trace_processor/importers/proto/profile_packet_sequence_state.cc 的 alloc_delta、free_delta),所以某個傾印時間點還沒釋放的量 = 同一呼叫位置、ts 不晚於那一刻的 size 加總,官方 stdlib 的 android.memory.heap_profile.summary_tree 也是 `sum(size)` 當沒釋放的量;③「重複回到同一個畫面、每輪都在漲才算漏」借 BLeak(Vilk & Berger,PLDI 2018,pldi18.sigplan.org)與 Square 的工具 LeakCanary 3.0 的堆積增長偵測(square.github.io/leakcanary/changelog:重複跑情境直到不再增長,另有暖機減少誤報)。裁定:錄製與查詢原樣借 Perfetto,增長判法借「重複情境、看每輪增量」的形狀,自己只寫前半/後半增量的比較;不採 dump_at_max(只有峰值那一刻,看不出趨勢)。
RETIRE-IF: 上線三個月後兩個真實專案的提示零觸發,或被點名的呼叫位置有一半以上查明是正常快取(誤報多過真報),就把這項提示拿掉、只留 L3 的手動診斷;每次驗收多花的時間超過量測本身的一倍,也拿掉。
REVISIT:2027-01-31 在實驗室埋一個每輪漏幾十次、每次小於 4096 位元組的小配置,量同一情境跑三次時增量抖多少,判法照實際抖動定下限
REVISIT:2027-01-31 拿兩個真實專案(帶第三方 .so 的)跑過之後,重定「後半增量至少前半的一半」這條判法與 1 MB 的列出下限;量測輪數 N 小於快取上限時快取會被判成線性增長,看真實 SDK 的池多大再決定 N 的建議值
REVISIT:2027-01-31 收集腳本與分析工具要對到 skill 釘的 Perfetto 版本:2026-10-28 實驗用的主機 trace_processor 是 v58.2(本機與 ~/.cache/lumos/tools 兩支都是)、裝置端是 Android 16 內建的 perfetto,不是 v57.2;正式做之前用 v57.2 重跑同一組實驗或改釘版本

## 實驗室實測(2026-10-28)

在 macrobench-lab 另開工作目錄與分支 native-growth-lab(不推送、不合併)做:假原生 SDK 多兩種情境,SM-X710 / Android 16,benchmark 建置(profileable、非除錯版)。每種:停 App → 啟動 → 驅動暖機 2 輪 → 讀「沒人指著的原生記憶體」與 Native Heap → 開 heapprofd(只接已在跑的行程、每秒傾印一次)→ 驅動量測 8 輪 → 等 3 秒停錄 → 再讀兩個對照數字。每輪開畫面配 2 MB。

| 情境 | 沒人指著(前→後) | Native Heap KB(前→後) | heapprofd 判法 | 點到的呼叫位置 |
|---|---|---|---|---|
| ①沒呼叫 release、記憶體沒人指著 | 0 → 16 MB(8 塊) | 9176 → 26468 | 線性增長:結尾 16 MB,前半增 8、後半增 6 | `nativeCreate` @ libfakesdk.so |
| ②SDK 全域清單留著每個 handle、App 沒 release | 0 → 0(抓不到) | 11576 → 30860 | 線性增長:結尾 16 MB,前半增 8、後半增 6 | `nativeCreateTracked` @ libfakesdk.so ← `PlayerActivity.onCreate` |
| ③上限 4 塊的池(暖機已配 2 塊) | 0 → 0 | 11244 → 16268 | 停住:結尾 4 MB,前半增 2、後半增 0 | `nativePoolAcquire` @ libfakesdk.so |
| 正常版(都有 release) | 0 → 0 | 7220 → 6264 | 不增長 | `nativeCreate`(開關之間在 0 與 2 MB 來回) |

- 判法:把量測期間的傾印依時間切成前後兩半,每個呼叫位置算「中間那次傾印比第一次多多少」(前半增)與「最後一次比中間多多少」(後半增);結尾還留著、前半有增、後半增量至少是前半的一半 → 線性增長;結尾還留著、但後半沒有跟著漲 → 停住;其他 → 不增長。只列結尾或增量超過 1 MB 的。四種情境都分對。
- heapprofd 只記開始記帳之後的配置,所以暖機期間配的(包括池已經配好的那 2 塊)本來就不算進來,不用另外扣基線。
- 呼叫鏈看得到 .so 匯出的 JNI 函式名(這支 .so 沒拿掉匯出符號)與 App 的函式,跟既有 L3 的結論一樣只到函式、沒有行號。
- 錄檔與暫存都已刪掉(錄檔當含個資處理,只留上面的數字)。

查詢(trace_processor;malloc 上一層的函式當呼叫位置):

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

錄製設定(推到裝置 `/data/misc/perfetto-configs/`,`perfetto --txt -c … -o /data/misc/perfetto-traces/… --background`,停錄用 `kill -TERM`):

```
buffers { size_kb: 65536 fill_policy: DISCARD }
data_sources { config { name: "android.heapprofd" heapprofd_config {
  process_cmdline: "<套件名>" sampling_interval_bytes: 4096 shmem_size_bytes: 8388608 no_startup: true
  continuous_dump_config { dump_phase_ms: 1000 dump_interval_ms: 1000 } } } }
duration_ms: 120000
```

## 打算怎麼做(草案,設計審前會再改)

1. 預設關,按情境打開(d4):設定加一個選填布林鍵 `native_growth`(沒寫等於 false),寫在 `stability_scenarios` 的某個情境裡只開那個情境、寫在 `stability` 段等於整套量測都開;型別照 `strictmode` 的寫法驗(不是 true 或 false 就回 2 擋下)。要寫進 `stability_scenarios` 就得把它加進那份「情境可蓋過的欄位」清單(收集腳本與 lumos 的 E2E_SCENARIO_KEYS 兩邊逐字相同,有測試比對;那份清單以外的欄位會被當成不認得的欄位擋下);lumos 驗情境欄位時把清單第三個以後的欄位一律當 warmup、cycles 那種 1 到上限的整數驗,布林鍵不能直接接在清單尾端,要另外照 `strictmode` 驗。鍵名與放的位置照既有 stability 段的命名慣例自擬,**請審查席看**:是不是該用別的名字、該不該允許寫在 stability 段整套打開。
2. 打開了還要專案宣告了測試資料(`stability.test_data` 的 value 是 true,跟 Java 快照同一條保存規則,d3)才錄;沒宣告、或 App 不是 profileable,就把結果檔那一段列成跳過並說原因;沒打開的情境不錄、結果檔那一段寫成沒打開。
3. 收集腳本在既有量測之後另跑一段 N 輪、只錄 heapprofd(d1),錄檔直接放 run 目錄第一層、檔名 `heap-*.pftrace`(既有的 7 天自動刪只看各 run 目錄第一層、這個檔名樣式),並加進收集腳本開跑前「產物有沒有被 git 忽略」那份逐檔清單;結果檔只存每個呼叫位置的數字(函式名、所在 .so、結尾未釋放、前半增、後半增、判法)。
4. lumos 讀結果檔,線性增長的照增長量排序列成優化建議;只提醒,不進 threshold_failures、不影響回傳碼與推送前檢查。
5. skill lumos-android-evidence 的 L3 原生那段改成先看這份提示,沒打開的情境照舊手動錄。

## 跟舊否決的差別

- [[Projects/Android逐層診斷_計劃]] 否決過「每次都錄 Trace+CPU 取樣+記憶體」(慢、改變被量對象、留下不必要的敏感檔):那條仍成立,本計劃照它改成按情境打開、預設關(d4),慢與錄檔只落在人主動打開的情境上,不是每次驗收都錄。
- [[Projects/Android記憶體與穩定性驗收_計劃]] 原生洩漏判法否決過「只看 Native Heap 趨勢」:那條否決的對象是整個行程的 Native Heap 總量(有升有降,判不出是誰);本計劃看的是 heapprofd 按呼叫位置記的未釋放量,而且只提醒不擋(d2),實驗室四種情境分得開。
- 同一篇 Java 洩漏判法否決過「每輪結束值判趨勢」:那條的對象是每輪結束時的 Java 堆積總量(實驗室沒有洩漏時五輪忽高忽低兩倍);本計劃比的是同一個呼叫位置前後兩半的未釋放增量,不是總量,同樣只提醒。

## 實務隱患

- 量測干擾:heapprofd 掛在 malloc 上取樣,會拖慢 App;照 d1 另跑一段,不跟算凍結幀與峰值的那份追蹤檔同一段,既有數字不受影響。
REVISIT:2027-01-31 在實驗室量 heapprofd 那段 N 輪比不錄時慢多少,寫回本節
- 判法的邊界:量測輪數小於快取上限時,快取在整段量測都在漲,會被判成線性增長;小於取樣間隔(4096 位元組)的配置是取樣估計,小量漏法的數字會抖。
- 個資:heapprofd 記的是呼叫鏈、大小與時間,這次查的欄位裡沒有記憶體內容;錄檔仍照 heap-*.pftrace 的保存規則當含個資處理。官方文件裡沒找到明講「不含內容」的那一句。
- 版本:實驗用的主機分析工具是 v58.2、裝置端是內建 perfetto,不是 skill 釘的 v57.2(見 REVISIT)。
- 前提:user 建置只能錄 profileable 或 debuggable 的 App;release 建置沒宣告 profileable 時錄不到,要列成跳過。
- 已排除:金流:只在測試裝置上量自家 App,不碰交易。
- 已排除:對外送出:錄檔與結果只在本機 run 目錄,不上傳。
- 已排除:不可逆:只多寫被忽略的 run 目錄與結果檔,撤掉照回退節刪程式即可。
- 已排除:守衛面:只提醒,不改任何判定、回傳碼或推送前檢查。

## 條款(草案)

- [S1] 當 N 輪量測期間某個呼叫位置的未釋放量前後兩半都在漲、後半至少是前半的一半、結尾超過 1 MB 時,提示應列出它(函式、所在 .so、結尾未釋放、兩半增量),照結尾未釋放量由大到小排 [test:待定]
- [S2] 當某個呼叫位置前半有漲、後半沒漲時(快取或物件池),提示不應列出它 [test:待定]
- [S3] 當專案沒宣告測試資料、或 App 不是 profileable 時,收集腳本應不錄 heapprofd,並把結果檔那一段列成跳過、說原因 [test:待定]
- [S6] 當設定沒有替這個情境打開 `native_growth` 時,收集腳本應不跑那一段 heapprofd、不錄檔,結果檔那一段寫成沒打開;`native_growth` 不是 true 或 false 時應回 2 擋下 [test:待定]
- [S4] 當提示列出或沒列出呼叫位置時,lumos 的判定結果、回傳碼與推送前檢查應都不變 [test:待定]
- [S5] 當實驗室分別埋入三種情境(沒人指著的漏、SDK 內部留登記、上限固定的池)時,前兩種應被列出、第三種不列 [manual:macrobench-lab 實機各跑一次,2026-10-28 草稿實驗已分對,正式版程式寫完要重跑]

## 回退

收集腳本拿掉 heapprofd 那段錄製與結果檔欄位,lumos 拿掉提示的輸出;已經寫出的錄檔在被忽略的 run 目錄,照既有 7 天自動刪。
