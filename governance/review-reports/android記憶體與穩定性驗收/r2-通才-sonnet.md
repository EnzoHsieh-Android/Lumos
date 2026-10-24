severity: major

以下是第 2 版修訂稿的逐條 finding。

**1. 兩次 `am instrument` 會重啟目標 App,「同一個行程不殺」的前提不成立**
severity: major
blocking: 是——核心流程(暖機與量測在同一行程)在所指定的驅動指令上跑不出來。
引句:「收集腳本在主機端呼叫驅動兩次(暖機 W 輪、量測 N 輪),中間與前後由收集腳本自己用 adb 量」
- 官方 instrumentation 文件寫「通常目標 App 行程會被重啟」,`--no-restart` 才是例外。
- 一份 AOSP 變更紀錄也說明該旗標的作用是不重啟目標 App。
- 資料流第 1 點的驅動例用 `adb shell am instrument -w ...`,沒有帶 `--no-restart`。
- 因此第二次呼叫(量測輪)很可能殺掉暖機時的行程。後果有三:
  - 「記下 pid」之後 pid 會變,`pid_changed` 的判定永遠為真。
  - 暖機與快照之間多出一筆系統結束紀錄,`exits` 的判定(前後比對多出任何一筆)為真。
  - 跨輪累積的前提被破壞。
- 實驗室的 spike 分支已刪,實測紀錄只有「同一個行程開關畫面 5 輪」(看起來是單次 instrument 呼叫),沒有證明兩次呼叫之間行程仍活著。
- ⚠ 「instrumentation 結束時 AMS 會順手 force-stop 目標」我沒查到官方文字,但「開始時重啟」已足以成立。
- 子案二同理:Maestro 的 `launchApp` 預設會先停掉 App,而「只要換驅動指令」的宣稱沒驗過。
- 佐證:https://source.android.com/docs/core/tests/development/instrumentation 與 https://android.googlesource.com/platform/frameworks/base/+/99ba880e5559

**2. 實例上限的類別名寫錯或被混淆時,「算 0 個」會判通過(假綠)**
severity: major
blocking: 是——這是 spec 自己點名要防的「讀不到所以全綠」。
引句:「快照裡沒有那個類別時算 0 個」
- [S3] 規定類別不存在就算 0 個。類別名拼錯、R8 混淆(WHY 26 自己承認會發生)、或 SDK 換了套件名時,上限檢查會永遠通過。
- [S11] 只管來源的 `status` 與 -1,管不到「宣告的類別沒出現在快照」。
- 宣告位置也自相矛盾:WHY 26 與 [S3] 說「門檻檔」宣告上限;資料流第 1 點把 `declared_classes` 放在 `.lumos/macrobench.json`。
- `declared_classes` 在整份 spec 裡沒有任何用途描述,結果檔 `heap` 卻是「類別名對實例數」的全量。
- 該類別在暖機後那份快照也不存在時,應該列成跳過或警告,而不是通過。

**3. `.lumos/macrobench.json` 現行要求非空的 `results_dirs`,與 `stability` 段、S14 衝突**
severity: major
blocking: 是——只做穩定性驗收的專案(沒有 Macrobenchmark 結果目錄)會被回 2「擋下」。
引句:「`.lumos/macrobench.json` 加 `stability` 段」
- `_macrobench_config` 要求 `results_dirs` 是非空清單,否則回「要有 results_dirs」(`scripts/lumos:39402`)。
- 整份 spec 的「這次要改到的地方」沒有鬆綁這條。
- [S14] 只涵蓋「沒有這個檔」的情況。有檔、只有 `stability`、沒有 `results_dirs` 時會得到錯誤,不是判定。
- `_macrobench_mode` 在 `cfg is None` 時直接 return,早於門檻判定(`scripts/lumos:39717` 附近),所以 S14 需要重排主流程。spec 只寫「加 `--stability`」,沒提這個重排。
- 收集腳本是 sh,spec 沒說它用什麼讀這份 JSON。「零依賴」前提下得用 python3,但沒寫。

**4. REVISIT 的 `when-file` 條件在實作提交當下就成立,會擋住自己的推送**
severity: major
blocking: 是——條件語意與文字意圖相反。
引句:「REVISIT:[when-file:scripts/templates/android-stability-collect.sh][by:2027-04-30] 第一個真實專案用收集腳本跑過時」
- `when-file` 的意思是「樹上有這個路徑就成立」(`commands/03-寫回圖譜.md:107`)。
- 本計劃實作時就會新增這支檔,所以條件在落地那次推送即成立,而且預設擋下。
- 意圖卻是「第一個真實專案跑過」,那是人工事件,不是檔案事件。
- 這條應改成純日期型,或用 `when-status`。

**5. StrictMode 檢查有兩個假綠路徑**
severity: major
blocking: 是——同樣是「讀不到所以全綠」。
引句:「收集腳本開跑前清日誌緩衝、跑完讀出 StrictMode 那幾行,一筆就不過」
- logcat 預設環形緩衝很小。N 輪期間 App 日誌量大時,早期的 StrictMode 行會被擠掉。
- spec 沒有並行擷取、沒有放大緩衝,也沒有緩衝溢位的偵測。
- `stability.strictmode` 只是人寫的宣告,沒有任何機械驗證 App 真的開了 `penaltyLog`。宣告了但沒開時,零筆就判通過。
- 零筆時 `status` 照 WHY 35 是 ok,與「收得到的證明」的精神不符。
- 另外 `logcat -c` 會清掉整台裝置共用的緩衝,影響同機其他使用者或程序。

**6. 各 `check` 的必填欄位、情境對應與數值驗證沒定義,[S13] 無法實作也無法測**
severity: major
blocking: 是——測試條款指向未定義的欄位。
引句:「寫了不認得的 check 或缺了那種的必填欄位時應回 2 並說原因」
- 七種檢查各自要哪些欄位(`native_unreachable` 的門檻欄位名、`instances` 的類別與上限、`frozen` 的阻塞上限欄位)全文沒有列出。
- 現行判定用 `current.get(t["scenario"])` 對情境鍵,並用 `device_model` 篩裝置(`scripts/lumos:39668` 起)。
- 結果檔雖有 `scenario`,spec 沒說門檻的 `scenario` 要不要與結果檔相符,也沒說不相符時怎麼處理。
- 結果檔數值沒有「只收有限數」的要求。既有節點已記過 PITFALL:NaN 讓「現值 > 門檻」恆假而永遠判達標(`Systems/macrobenchmark-adapter.md:28`)。
- `bytes: NaN` 或 `bytes: true` 會讓 `native_unreachable` 直接過關,而 [S11] 只擋 -1。
- 固定席判定:這條會破壞該節點 `t_macrobench_rejects_nonfinite` 守的行為(新增的判定路徑若沒走同一個只收有限數的函式),需要補條款。

**7. `native_unreachable` 預設門檻 0、只在 N 輪後讀一次,在真實 App 上很脆**
severity: minor
blocking: 否——可由 REVISIT 與校準後調整,不影響設計成立。
引句:「大於 0 就不過」
- 證據只有實驗室一個 App 的「0 位元組」。
- 真實 App(WebView、GPU 驅動、第三方 .so)常見少量 libmemunreachable 報告。
- 只有後值,沒有暖機後的前值可扣。
- 41 行的 REVISIT 只校準 W、N 與 Java 門檻,沒涵蓋這一項。⚠ 我沒有真實 App 的資料,只能指出缺口。

**8. `java_growth` 沒有預設排除平台型別**
severity: minor
blocking: 否——spec 已用 REVISIT 承認並預留排除清單。
引句:「增加量達到「N × 每輪至少多幾個」(預設 1)的類別判不過並列出」
- `String`、`byte[]`、`Object[]` 這類型別在任何真實 App 的 N 輪裡幾乎必增長。
- [S16]「七種檢查應全過」只在實驗室簡單 App 驗,沒覆蓋這一類。
- 預設行為對真實專案很可能第一次就全紅。

**9. 保存規則的替代與刪除範圍有缺口**
severity: minor
blocking: 否——威脅模型是單人、AI 依序操作,屬已接受的風險類,但兩個缺口值得補。
引句:「用人寫的宣告取代 AI 自述,無人看顧時照樣有根據」
- 現行 skill 要的「人裁的保存規則」包含「保存多久、誰看得到、能不能離開本機」三題(`skills/lumos-android-evidence/SKILL.md:111`)。`test_data: true` 只是布林,沒有 `decided_by`、`decided_at`,也不是人裁的紀錄。AI 自己改 JSON 就能打開。
- 7 天刪除只刪主機端 `heap-*.pftrace`。裝置端(`/data/misc/perfetto-traces/`)的快照殘留沒處理。
- L3 診斷另錄的 heapprofd、java_hprof 檔名不在這個樣式內,也不在這個刪除範圍裡。
- 刪除只在「下一次跑收集腳本」時發生,專案不再跑就永遠不刪。

**10. 測試條款可能是套套邏輯**
severity: minor
blocking: 否——manual 的 [S16]、[S17] 補了真實覆蓋,但 S9、S10 單獨成立不了。
引句:「[test:t_android_memstab_cycle_query]」
- 既有測試是用 Python 內建 sqlite3 手建 Perfetto 表來跑範本(`scripts/test_lumos.py:17794`)。
- 查詢能在作者自建的表上通過,不能證明它在真的 trace_processor 的表結構與函式上可用。
- [S6] 與 [S15] 測的是 sh 收集腳本,假 adb 的做法 spec 沒寫。

**11. 大快照與大追蹤檔的效能、逾時值未定**
severity: minor
blocking: 否——逾時失敗會落到 `failed` 而被跳過,不會誤判通過,但可能讓真實專案的 Java 檢查長期跳過。
引句:「每個 adb 與 trace_processor 呼叫都有逾時」
- 逾時數值沒寫。實驗室快照 15 MB,真實 App 的 java_hprof 動輒數十到上百 MB,trace_processor 載入的記憶體與時間成倍。
- 結果檔 `heap` 存的是全量「類別名對實例數」,量大時 JSON 也大。
- 「跟收據重跑腳本同一個做法」不含逾時:重跑腳本的 `subprocess.run` 沒有 timeout(`scripts/templates/android-receipt-rerun.sh:60`),這條類比只對路徑查找成立。

**12. 結束紀錄的原因分類與 [S5] 不一致,環形緩衝上限沒處理**
severity: minor
blocking: 否——判定偏嚴不偏鬆,影響的是誤報。
引句:「把崩潰、原生崩潰、ANR、描述含 MemoryLimiter 分成四種」
- [S5] 說「多出任何一筆」就不過。[S6] 只定義四種分類,其他原因(LOW_MEMORY、USER_REQUESTED、SIGNALED、DEPENDENCY_DIED)是留是丟沒說。
- 驅動自己停 App 也會產生 USER_REQUESTED 一類的紀錄,與第 1 點相連。
- ApplicationExitInfo 對每個套件只保留有限筆數(約 16 筆)。⚠ 這個數字我憑記憶,沒查文件。測試期間新增筆數超過上限時,用 pid 加 timestamp 比對會漏掉被擠掉的。

**13. 驅動指令從設定檔直接執行,Maestro 環境變數傳法有誤**
severity: minor
blocking: 否——單人威脅模型,但屬實務隱患。
引句:「收集腳本把輪數用環境變數 `CYCLES` 傳給它」
- `driver_warmup` 與 `driver_cycles` 是設定檔裡的任意 shell 字串,由收集腳本執行。誰能改 PR 裡的 `.lumos/macrobench.json`,就能在跑腳本的機器上執行任意指令。
- Maestro 的流程參數要用 `-e CYCLES=5` 傳,不是行程環境變數。「子案二只換指令」的說法並不精確。
- 多台裝置同時連線時 spec 沒有 `adb -s` 序號的欄位。

**14. 官方記憶體分級表的來源我沒有查證成功**
severity: minor
blocking: 否——標 ⚠。
引句:「可用記憶體 3200–4800 MB 為 2.00 GB、4800–6800 MB 為 2.25 GB」
- 我嘗試讀 `developer.android.com/google/play/vitals/memory` 得到 404,無法逐字核對該表的區間與數字。
- 搜尋到的旁證只有:Android 17 的 Memory Limiter 確實存在(https://android-developers.googleblog.com/2026/08/app-broader-memory-limits.html),以及二手報導的 2.0/2.25/3.25/4.25 GB 數字。
- 3200、4800、6800 這些區間邊界我沒找到任何來源。
- 另外「裝置可用記憶體」用 `/proc/meminfo` 的 MemTotal 代入,MemTotal 比標示的 RAM 小。邊界附近(例如標示 4 GB 的裝置)可能落進錯的級距。

**固定席逐條判(`Systems/macrobenchmark-adapter`)**
- 「不接裝置」:會破壞字面,spec 已自己提出把負責範圍改成「本體不接裝置、範本腳本才接」。這個改法可行,不影響。
- 「不擋推送」:判定回 0、只提醒,不影響。
- 「不從量測產生門檻」:新增的各 `check` 都是人寫的 `decided_by` 門檻,不影響。
- 「門檻 NaN 不得當達標」(PITFALL):會影響。新增路徑沒有明講走只收有限數的函式,見第 6 點。
- 「新增範本必須登記 `_VENDORED_TREE_FILES`、帶 SPDX」:[S12] 已涵蓋,不影響。
- 範本進入工具檔後,推送閘的風險分級會被降低(`scripts/lumos:31908` 的註解),收集腳本含 `rm` 與 adb 呼叫,卻可能逃過代碼審的 tier 判定。⚠ 這點我沒實測風險分級的行為。

已讀,無 finding 的節:回退、PRIOR-ART、RETIRE-IF 與其他 REVISIT 行(2026-11-21、2027-01-31、2027-02-28),以及實務隱患的金流、對外送出兩行。

總結:最高嚴重度 major,blocking 共 6 條(第 1 至 6 點)。
