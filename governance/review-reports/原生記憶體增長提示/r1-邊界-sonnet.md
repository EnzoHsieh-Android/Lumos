severity: major

審查範圍:逐節讀完 r1-snapshot.md(front matter、白話、PRIOR-ART、實測、查詢與錄製設定、草案 1 到 5、舊否決、實務隱患、條款 S1 到 S6、回退)。文件內部沒有壞的交叉引用。`d1` 到 `d4` 與 `#d1` 到 `#d3` 都存在,S1 到 S6 也都有對應段落。

我核對過的程式碼現況:
- `E2E_SCENARIO_KEYS`(`scripts/lumos:40474`)與驗證式(`scripts/lumos:40491`)的描述屬實。
- `load_config` 的覆蓋清單是寫死的元組(`scripts/templates/android-stability-collect.sh:130`)。
- `strictmode` 的型別驗證(`scripts/lumos:39564`)存在。
- 7 天清理的 regex(`scripts/templates/android-stability-collect.sh:148`)與 ARTIFACTS 清單(`scripts/templates/android-stability-collect.sh:28`)存在。

另外,我查證過 Perfetto v57.2 的 `heapprofd_config.proto`,spec 引用的欄位都存在。這次沒有查證的有兩項:`heaps` 的預設值,以及 heapprofd 的 stats 欄位名。

### F1 空結果、零傾印、錄到一半被截,都會被當成「不增長」
severity: major
blocking: 是
引句:「結尾還留著、前半有增、後半增量至少是前半的一半 → 線性增長;結尾還留著、但後半沒有跟著漲 → 停住;其他 → 不增長。」
file: `scripts/templates/android-stability-collect.sh:260-269`、`scripts/lumos:40081`
外部:https://raw.githubusercontent.com/google/perfetto/v57.2/protos/perfetto/config/profiling/heapprofd_config.proto

1. 判法的三分類以「其他 → 不增長」收尾,沒有「判不出」這一類。下面幾種情況都會讓 `heap_profile_allocation` 為空或不完整,照字面實作者只能得到「不增長」或「沒有任何呼叫位置」:
   - App 不是 profileable。S3 寫了「App 不是 profileable」就跳過,但 spec 沒講怎麼偵測。repo 裡沒有任何 profileable 偵測碼(`grep -rn profileable scripts` 零命中)。
   - 裝置是 Android 10 以下。`no_startup` 要 Android 11 以上,spec 只在 PRIOR-ART 提一句,條款與草案沒有任何依 `android_sdk`(`device_info` 已經取得)分流的規則。照字面會把 `no_startup: true` 推給舊 perfetto,得到「perfetto 開不了錄製」這種泛用 failed,而不是 unsupported。
   - `process_cmdline` 對不到。套件名只對得到主行程。
   - App 在量測中途閃退或被殺換了行程。`no_startup: true` 不會接新行程,傾印停在死亡前,新行程完全沒被錄。
   - shmem 滿了。proto 註解寫 `block_client` 沒開時,shmem 滿了會「ending the trace」(結束該行程的錄製)。spec 的錄製設定沒設 `block_client`,也沒檢查 heapprofd 的 stats(像 `heapprofd_buffer_overran` 之類;⚠ 欄位名未實查)。
2. 具體例:
   - 輸入:非 profileable 的 release 建置,打開 `native_growth`。
   - 照字面:trace 裡沒有 profile packet,查詢零列,結果檔寫成 ok 且零個呼叫位置。人讀到的是「查過了,沒漏」。
   - 應該:零傾印、傾印少於 3 次、行程在段內換 pid、stats 顯示緩衝溢位或客戶端斷線,這幾種都要有獨立狀態(failed 或 unsupported 加原因)。
   - 既有慣例也是這樣處理的:`stop_record` 把「半份追蹤檔」判為不採用,`pids` 與 `exits` 都有 failed 路徑。這個新段沒有對應條款。
3. 建議補一條條款:有效傾印數與行程存活是採用 heapprofd 結果的前提。

### F2 N 很小與尾端閒置時間,讓「前後兩半」判法失效
severity: major
blocking: 是
引句:「把量測期間的傾印依時間切成前後兩半,每個呼叫位置算「中間那次傾印比第一次多多少」(前半增)與「最後一次比中間多多少」(後半增)」
file: `scripts/templates/android-stability-collect.sh:487`、`scripts/templates/android-stability-collect.sh:485`

1. 傾印數少於 3 次時,「中間那次」沒有定義。
   - `dump_phase_ms` 與 `dump_interval_ms` 都是 1000。量測不到 1 秒,傾印數就是 0。
   - 傾印 1 次或 2 次時,第一次、中間、最後三個點重合。傾印偶數次時,「中間」是哪一次也沒講。
2. 切分是依時間,不是依輪數,而且尾端有固定 3 秒閒置,會稀釋後半。
   - 實驗流程是「驅動量測 8 輪 → 等 3 秒停錄」,所以最後幾次傾印落在驅動已結束的閒置期。
   - 實驗表裡後半增 6 對前半增 8(比例 0.75)已經顯示被稀釋。
   - 以實驗室約 1.5 秒一輪的節奏推算:N=2 時驅動約 3 秒、尾端 3 秒閒置,約 6 次傾印,中間點約在第 3 秒。所有增長都落在前半,後半增為 0,判成「停住」,真漏被漏報。⚠ 這是依 spec 自己的數字推算,沒有重跑實驗。
   - 閾值「至少一半」其實隱含 N 要夠大、閒置尾巴要短,spec 沒寫這個前提。
3. 還有三件事未定義:
   - 錄製啟動沒有就緒等待。目前程式是 `start_record` 之後立刻 `driver`(`scripts/templates/android-stability-collect.sh:485` 與 `scripts/templates/android-stability-collect.sh:487`)。heapprofd 對已在跑的行程要先 attach,前幾輪的配置可能沒被記到。N=1 到 3 時損失比例很大。
   - 某呼叫位置在第一次或中間那次傾印沒有列(晚才出現的洩漏點)時,要當 0 還是當缺。查詢的 join 只產出該位置已有資料的 ts。
   - 「前半有增」是 >0 還是 ≥0,誤差正負怎麼處理。
4. 應該:
   - 先寫最少傾印數與最少輪數。
   - 用「驅動結束的時間點」而不是停錄時間切半,或排除閒置尾巴的傾印。
   - 缺列當 0。
   - 最少傾印數不夠時狀態為「樣本不足」,不是「不增長」。

### F3 「malloc 上一層」只對直接呼叫 malloc 的 C 程式成立
severity: major
blocking: 是
引句:「按「malloc 上一層是哪個函式」彙總到每次傾印時還沒釋放的量」
file: `/Users/enzo/orca/workspaces/macrobench-lab-native-growth/app/src/main/cpp/fakesdk.c:7`、`skills/lumos-android-evidence/SKILL.md:164`

1. 查詢只取一層 `p.parent_id`,並且 `coalesce(pf.name,'?')`、`coalesce(pm.name,'?')`。實驗室的 `fakesdk.c` 在 JNI 函式裡直接呼叫 `malloc`,所以上一層剛好就是 SDK 函式。
2. 真實第三方 .so 常見的路徑不是這樣:
   - C++ 的 `operator new`、`calloc`、`posix_memalign`、`std::allocator` 包裝。
   - 靜態連結的分配器。
   - Rust、Go 等執行環境的包裝。
3. 照字面會得到兩種壞結果:
   - malloc 的上一層是 `operator new`(在 libc++ 或 libc)。所有 C++ SDK 的洩漏塌縮成同一個 `operator new @ libc++_shared.so` 呼叫位置,看不出是誰。
   - .so 沒有匯出符號(第三方多半如此)。`pf.name` 為 NULL,全部變成 `? @ libx.so`,同一支 .so 裡所有函式混成一列,增量被加總。
4. spec 的實測段只寫「這支 .so 沒拿掉匯出符號」,沒有把這個列為適用前提。skill 的 L3 自己也寫了第三方沒有符號時的處理:「呼叫鏈只到哪支 .so、哪個位移」,標 `[INFERRED] 第三方沒有符號`。新提示的彙總規則卻沒有對應的退路。
5. 應該:
   - 往上走過配置器包裝(libc、libc++ 的 `operator new/delete`、`malloc` 家族),取第一個非配置器的框架。
   - name 為 NULL 時退回 `mapping + rel_pc`。
   - 結果檔要註明符號缺失。
   - 另外,這條規則在實驗室的真 SDK 以外沒有驗證過。REVISIT 只提了「小配置」和「兩個真實專案」,沒提這個風險。

### F4 第二段 N 輪與既有判定的交互沒寫:pids 長度、exits 窗口、錄製上限、中斷清理
severity: major
blocking: 是
引句:「收集腳本在既有量測之後另跑一段 N 輪、只錄 heapprofd(d1)」
file: `scripts/lumos:40098-40101`、`scripts/templates/android-stability-collect.sh:491-498`、`scripts/templates/android-stability-collect.sh:366-373`、`docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md:35`

1. 「之後」沒指明相對於哪些讀值。`measure()` 在第一段結束後依序讀 `pidof`、`unreachable`、`native_heap_kb`、Java 快照 after、`read_exits` after。
   - 若第二段插在這些讀取之前,第二段的 N 輪會讓 `native_heap_kb`、`unreachable`、`heap-after` 與 exits 都包含額外輪數。這直接違反 d1 想要的「既有數字不受影響」,以及 S4(判定結果、回傳碼不變)。
   - 若插在之後,第二段的閃退、ANR、low_memory 完全不在 exits 窗口內,沒人看。
   - 反過來,heapprofd 拖慢 App 造成的 ANR(spec 自己的「量測干擾」段承認會拖慢)若落進 exits 窗口,會讓主判定因為「工具的觀測成本」而變紅。
2. pid 的記法會影響判定。
   - `res["pids"]` 是三個值,而 `_macrobench_stab_pids` 要求 `len(vals) == 3`(`scripts/lumos:40098-40101`)。
   - 若實作者把第二段的 pid 追加進同一個清單,pids 變成 None,exits 檢查會落到「pid 有讀不到的」而被標為沒判到。這就改了判定,違反 S4。
   - spec 沒講第二段的 pid 要存在哪裡。
3. 第二段的前置條件沒定義:
   - 要不要重新 `force-stop` 或重新暖機。既有 PITFALL「收集腳本沒先停 App 時上一次留下的物件算進這一次」的修法是 force-stop。
   - 若第一段把 App 殺了(low_memory),`pidof` 為空,`no_startup` 不會接新行程。這個情況會落回 F1 的空結果。
   - 第二段 driver 失敗要不要略過。
4. 錄製上限寫死。
   - 錄製設定寫 `duration_ms: 120000`,既有範本是 `__DURATION_MS__`(來自 `stability.max_record_s`,預設 600 秒,`scripts/templates/android-stability-record.pbtxt`)。
   - N 輪超過 120 秒時,perfetto 自己提早停。照 `stop_record` 的語意,這會被判成「錄製在 N 輪跑完前就到了上限」而丟掉。spec 沒說新段用不用 `max_record_s`,也沒說用不用同一套 `stop_record`(ps 存活判斷、補 KILL、半份不採用)。
5. 中斷清理只有單槽。
   - `state["rec"]` 與 `abort_record` 只收一份錄製。第二份錄製(另一個遠端設定檔與追蹤檔路徑)若不另登記,被 SIGTERM 或 SIGHUP 打斷時,裝置上會留下 heapprofd 與暫存。
   - 這正是知識圖譜 PITFALL(圖譜 `Systems/android-stability-collector.md:35`,「停的那幾秒被中斷時 cleanup 找不到它們」)描述過的洞。要在推設定之前先登記,停完才從 state 拿掉。
6. 應該:規定第二段插在所有既有讀值與 exits 之後、用自己的 pid 與 exits 窗口(存在新欄位,不碰 `pids`、`exits`)、沿用 `max_record_s`、沿用 `stop_record` 與 `abort_record` 的完整語意,並各寫一支先紅的測試。

### F5 設定鍵在 stability 段與情境兩處衝突、以及 test_data 的取用規則沒寫
severity: minor
blocking: 否
引句:「寫在 `stability_scenarios` 的某個情境裡只開那個情境、寫在 `stability` 段等於整套量測都開」
file: `scripts/templates/android-stability-collect.sh:130`、`scripts/lumos:39560-39566`

1. 兩處同時出現且值相反時,spec 沒講誰贏。
   - 既有的 `dict(st, **{...})` 是情境覆蓋 stability 段,所以情境寫 false 會關掉整套寫的 true。
   - 這是合理的預設,但條款 S6 沒覆蓋「兩處衝突」這個案例,也沒說情境裡的 false 是明確關閉。
2. `native_growth` 現在寫在 stability 段是靜默收下。
   - `_macrobench_stab_optional_err` 對不認得的鍵不報錯,spec 草案 1 只說「型別照 strictmode 驗」。
   - 驗證要放在 `_macrobench_stab_optional_err`(stability 段)與情境驗證兩處,而且 `E2E_SCENARIO_KEYS[2:]` 的整數驗證要先改,否則布林鍵會被當 warmup 驗而擋掉。這點 spec 自己有寫,沒有問題。
3. `stability.test_data` 只能寫在 stability 段,情境不能覆蓋。
   - S3 的「沒宣告測試資料」依 stability 層級判。test_data 是 false 與整個缺席,兩者在程式上都是 `bool(... .get("value"))` 為 False,結果相同。這點成立。
   - 但 spec 沒有明說「只看 stability 層」,建議在條款補一句。
4. 「逐檔清單」寫成 `heap-*.pftrace` 只是樣式。
   - 既有清單用實際檔名(`heap-before.pftrace` 等)給 `git check-ignore` 問。
   - 草案 3 要寫的是一個具體檔名(例如 `heap-native.pftrace`),不是 glob。照字面把 `heap-*.pftrace` 放進去,查的是字面含星號的路徑,只在 `.gitignore` 有 `*.pftrace` 類規則時才答對。
5. 草案 4 說「照增長量排序」、白話段也說「照增長量排序」,S1 說「照結尾未釋放量由大到小排」。
   - 實測段列的門檻是「結尾或增量超過 1 MB」,S1 是「結尾超過 1 MB」。
   - 1 MB 是 1,000,000 還是 1,048,576,也沒定義。
   - 這三處不一致,實作者會挑一個,測試與文件對不上。應統一排序鍵與門檻口徑。

### F6 多行程 App 與呼叫位置數量沒有上限
severity: minor
blocking: 否
引句:「結果檔只存每個呼叫位置的數字(函式名、所在 .so、結尾未釋放、前半增、後半增、判法)」
file: `scripts/templates/android-stability-collect.sh:251-269`

1. 多行程。
   - `process_cmdline` 填套件名,只對得到主行程。放在 `:remote` 之類子行程裡的原生 SDK 完全沒被錄,結果卻是「沒有增長」(又落回 F1 的靜默)。
   - 若實作者改用 v57 之後支援的萬用字元(proto 說只能搭配 `no_startup=true`),會同時匹配到名字相近的別的行程。
   - 查詢沒有 `upid` 維度,多行程的傾印時間互相穿插,「中間那次」會混。
   - 建議 spec 明寫「只量主行程」,並在結果檔註明。
2. 呼叫位置數量。
   - 查詢的 `dumps d join site s on s.ts <= d.ts` 複雜度約為「傾印數 × 資料列數」,資料列數本身又約等於「呼叫位置數 × 傾印數」。
   - 傾印數隨 N 與驅動時間線性增加。呼叫位置有幾千個、N 有幾百輪時,量級約為呼叫位置數乘傾印數的平方。⚠ 這是複雜度推算,沒有實測。
   - 結果檔也沒有上限。
   - 只需要第一次、中間、最後三個時間點,可以用視窗函式直接取,不必對每次傾印都做累加。
   - 要寫明誰做 1 MB 篩選(收集腳本還是 lumos),並對結果檔列數設上限。
3. 零個呼叫位置(完全沒有 `libc.malloc` 配置)的情況落回 F1。

### 各節結論
- front matter、白話、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding。我核對過 proto 欄位。
- 實驗室實測:判法的數字合理,但範圍只限 C 直呼 malloc、N=8(見 F2、F3)。
- 打算怎麼做 1 到 5:見 F4、F5。
- 跟舊否決的差別:已讀,無 finding。
- 實務隱患、條款 S1 到 S6、回退:見下方風險類逐類回答與 F1、F2、F4。S1 到 S3 缺「樣本不足」與「空結果」條款(F1、F2)。

### 實務隱患逐類
- 併發:有隱患,見 F4 第 5 點。第二份錄製在中斷時沒人收,且並行的別的 perfetto 錄製(同一裝置)路徑要避免撞名,run-id 已進路徑,這部分沒問題。
- 效能:有隱患,見 F6 第 2 點(查詢複雜度),以及 F4 第 1 點(heapprofd 拖慢造成 ANR 污染主判定)。
- 資源:有隱患,裝置端 64 MB 緩衝加 8 MiB shmem,shmem 滿了是結束錄製而非阻塞(F1)。本機端錄檔當含個資處理沿用 7 天清理,清理邏輯本身可套用。
- 回滾:無,只多寫被忽略的檔,回退節可行。
- 遷移:無,新選填鍵預設關,舊設定檔不受影響。
- 「已排除」四條的理由審查:
  - 金流:站得住,只在測試裝置上量自家 App。
  - 對外送出:站得住。heapprofd 的錯誤訊息若被 lumos 印出,要像 `unreachable` 的 PITFALL 那樣不帶輸出尾巴,條款裡沒寫(minor,併入 F4 的實作時一併注意)。
  - 不可逆:站得住。
  - 守衛面:「只提醒,不改任何判定」這個理由,F4 第 1、2 點指出照字面實作可以改到判定(pids 長度、exits 窗口),所以這條排除理由目前不成立,要靠 F4 的補寫才成立。

### 圖譜固定席
- `Systems/android-stability-collector`(會談目錄只在凍結提交裡有,我讀的是本機 `docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md`)的 PITFALL。
  - 「收集腳本沒先停 App」「日誌串流與錄製先 pop 才停」「ps 失敗連問三次不採用半份追蹤檔」這三條:不影響的前提是第二段沿用同樣的做法,目前 spec 沒寫(F4),判「有條件影響」。
  - 「meminfo 輸出不留標準輸出」:不影響,新段不讀 `unreachable`。
  - `am dumpheap` 與 `/data/local/tmp` 兩條:不影響,新段用 `/data/misc/perfetto-configs/`,spec 的錄製設定寫的就是這個路徑。
- `Projects/Android逐層診斷_計劃` 的否決(每次都錄):不影響,d4 預設關已處理。
- `Projects/Android記憶體與穩定性驗收_計劃` 的否決(只看 Native Heap 趨勢、每輪結束值判趨勢):不影響,spec 的區分成立,而且只提醒。
- `Verification/2026-10-24_...`:不影響。

總結:整份最高嚴重度為 major,blocking 共 4 條(F1、F2、F3、F4)。
