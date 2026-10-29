severity: major

資源與併發鏡頭。已逐節讀完整份 spec,也對照了收集腳本與 Perfetto v57.2 原始碼。

圖譜固定席:派工附件裡沒有附上任何固定席節點。`lands_in` 的 `Systems/android-stability-collector` 在會談目錄不存在(只在凍結提交裡),我無法逐條判。對照 `Projects/Android記憶體與穩定性驗收_計劃` 的合約,判法是這樣:只有 F2 的順序問題會破壞「不影響判定」。如果「多跑一段」放在讀 `read_exits` 之前,heapprofd 造成的 ANR 或崩潰會被當成測試期間的結束紀錄,進入有判定的 `exits`。F2 修好後我判「不影響」,原因是新段落只寫新欄位、不碰 `threshold_failures`。

### F1 第二段 heapprofd 錄製沒有登記進中斷清理,命名、停錄、上限也無法重用既有 `stop_record`
severity: major
blocking: 是
引句:「收集腳本在既有量測之後另跑一段 N 輪、只錄 heapprofd(d1),錄檔直接放 run 目錄第一層、檔名 `heap-*.pftrace`」
file: `scripts/templates/android-stability-collect.sh:485`、`:335-354`、`:371`、`:527-528`

1. 清理只認 `state["rec"]` 這一個槽。`cleanup()` 的 `rec = state.get("rec")` 只收一份錄製。第二段 heapprofd 要是不另外登記,Ctrl-C、逾時或例外時,裝置上會留下孤兒 heapprofd 錄製。它是 120 秒的 `duration_ms`,還會把 malloc 掛鉤留在 App 裡,連同 `/data/misc/perfetto-configs/` 的設定檔和 `/data/misc/perfetto-traces/` 的錄檔都清不掉。
2. spec 沒寫第二段登記在哪、怎麼命名。現有遠端路徑是 `lumos-stability-{run_id}.pbtxt` 和 `.pftrace`。第二段要是沿用同名,會覆蓋第一段的設定檔與錄檔,`pkill -f {remote_trace}` 也會互殺。
3. spec 只寫「等 3 秒停錄」,那是實驗室做法,不是機制。現有 `stop_record` 的做法是:先確認它還活著、送 `kill -TERM`,每秒看 `ps` 直到它消失(最多 `STOP_WAIT` 30 秒)、逾時補 KILL,最後才拉檔。
   - 照 spec 字面實作,沒有「怎麼知道寫完」的判準。
   - `perfetto` 收到 TERM 後會先做最後一次 flush 再收尾(`perfetto_cmd.cc`:「SIGINT/SIGTERM received: disabling tracing」,接著 `Flush(0, kTraceStop)`)。64 MB 緩衝加上很多 callsite 時,3 秒不保證寫得完,拉到截斷的檔案就會得到少了尾端傾印的結論。
4. `stop_record` 不能原封重用,有兩處寫死:
   - 本機檔名寫死 `cycle.pftrace`(`:350`)。
   - 「到了上限」的訊息寫死 `stability.max_record_s`(`:349`),但 heapprofd 的設定是固定 `duration_ms: 120000`,不跟 `max_record_s` 走。
   - 要把檔名與上限當參數,spec 得寫明。

### F2 第二段放在哪個位置沒寫,放錯會污染有判定的 `exits`、`unreachable`、`native_heap_kb` 和 Java 快照
severity: major
blocking: 是
引句:「收集腳本在既有量測之後另跑一段 N 輪、只錄 heapprofd(d1)」
file: `scripts/templates/android-stability-collect.sh:487-498`

1. 現行順序是:驅動 N 輪 → 停錄 → `unreachable` / `native_heap_kb` / 快照 after → `read_exits`。「既有量測之後」有兩種讀法,兩種都出事:
   - 插在讀 after 之前:after 值變成 2N 輪的累積,「前→後」增量被灌水,會誤判。
   - 插在讀 `exits` 之前:heapprofd 掛在 malloc 上很慢(spec 自己承認),可能讓 App ANR 或被殺。這筆結束紀錄會被 `exit_diff` 當成「測試期間新增」,進入有判定的 `exits`。
2. 這直接違反 d2「不進判定、不影響回傳碼」和條款 S4,而且 S4 的測試只驗「列出或沒列出」,抓不到順序問題。
3. 應該是:第二段放在 `read_exits` 之後,或第二段前後各自讀一次 `exits` 並明講它不計入判定;另外 `pids` 也要說清楚第二段是否追加。
4. 第二段跑在 App 已被 heapprofd 掛鉤、且已連跑 N 輪的狀態,和實驗室「暖機 2 輪就開錄」不同。spec 沒說第二段前要不要先 `force-stop` 重啟,而這會決定要不要再暖機。

### F3 heapprofd 起不來、被拒、掉資料時,照 spec 會判成「不增長」,是靜默偽陰性
severity: major
blocking: 是
引句:「`process_cmdline: "<套件名>" sampling_interval_bytes: 4096 shmem_size_bytes: 8388608 no_startup: true`」
file: https://github.com/google/perfetto/blob/v57.2/src/profiling/memory/heapprofd_producer.cc

1. 同一個行程同時只能有一個 heapprofd 工作階段。原始碼:`Rejecting concurrent session for %d`,輸出的 ProfilePacket 帶 `rejected_concurrent = true`。
   - 專案若有人正跑 L3 的 `heap_profile`、Android Studio profiler、上一次被中斷後沒清掉的錄製,這次錄到的是空的。
   - spec 裡只有「user 建置要 profileable」一條前提,沒有「被拒」這條跳過路徑。
2. `process_cmdline` 是和行程 cmdline 精確比對(非 glob)。只填套件名時,多行程 App 的 `:service` 子行程不在內。App 的主行程名不等於套件名時也錄不到。
3. 空錄檔或沒有 `libc.malloc` 列時,查詢結果是 0 列。spec 的判法「其他 → 不增長」會把它當成「沒問題」,而不是「沒錄到,跳過」。
4. `buffers { fill_policy: DISCARD }` 加上 65536 KB:緩衝滿了之後,新傾印被丟掉,尾段傾印遺失。「最後一次比中間多多少」就變成「已丟失的最後」,後半增被低估,漏判成「停住」。實驗室 4 個情境都沒碰到上限,spec 沒有任何偵測。
   - trace_processor 的 `stats` 表有 `heapprofd_buffer_overran`、`heapprofd_client_disconnected`、`heapprofd_buffer_corrupted` 等計數,沒人讀。
   - 偵測缺口要補:要不要把 `stats` 裡這幾項非 0、或 `rejected_concurrent` 時,列成「資料不全,跳過」。
5. 傾印數量不夠(例如少於 3 次)時,「前半、後半」沒定義,spec 沒寫該回什麼。

### F4 N 很大時超過固定 120 秒上限,heapprofd 提前結束,後半增量失真
severity: major
blocking: 是
引句:「duration_ms: 120000」
file: `scripts/lumos:39520`(`MACROBENCH_MAX_CYCLES = 10000`)

1. 現行 `cycles` 可以到 10000,既有第一段錄製的上限則是設定鍵 `max_record_s`(預設 600、可調到 86400)。第二段的 120 秒是寫死的,和 N 沒有關聯。
2. N 輪跑超過 120 秒(慢裝置、每輪複雜情境、heapprofd 本身拖慢),錄製在驅動還在跑時就自己結束:
   - 「前半、後半」只涵蓋 120 秒,後面的輪數沒有被錄到。
   - 沒有人偵測它提早結束。既有 `stop_record` 的「錄製在 N 輪跑完前就到了上限」判斷,對應的是第一段的訊息與 `max_record_s`,第二段沒有對應。
3. 實驗室 8 輪約十幾秒,沒有這個問題,所以實測不能證明這條設計在 N 大時成立。
4. 應該是:duration 依 N 或 `max_record_s` 計算,或錄製提前結束時列成「資料不全,跳過」。

### F5 `--background` 返回時資料源不一定已啟動,heapprofd 開頭幾輪可能沒掛上
severity: minor
blocking: 否
引句:「`perfetto --txt -c … -o /data/misc/perfetto-traces/… --background`,停錄用 `kill -TERM`」
file: https://github.com/google/perfetto/blob/v57.2/src/perfetto_cmd/perfetto_cmd.cc

1. 官方說明:`--background` 是「Exits immediately and continues in the background」,不等資料源啟動;`--background-wait` (`-D`) 才是「waits (up to 30s) for all data sources to be started before exiting」。
2. heapprofd 的 `no_startup` 流程要先對目標行程送訊號、等它重新初始化 malloc 掛鉤。spec 在 `--background` 返回後立刻開始驅動 N 輪。
3. 開頭幾輪的配置可能沒被記到。這種遺漏會讓「前半增」偏低,導致線性增長被判成「停住」。
4. 實驗室每秒傾印、`dump_phase_ms: 1000` 吸收了這段延遲,但那是巧合,不是設計。應該用 `--background-wait`,或明寫等待條件。
5. 現行第一段也用 `--background`(`:314`),只是幀數據對起點延遲不敏感。

### F6 判法在固定尾段被稀釋,且「依時間切半」和查詢實作不一致
severity: minor
blocking: 否
引句:「把量測期間的傾印依時間切成前後兩半」
file: spec 第 90 行與第 107-108 行的查詢

1. spec 說依時間切半,但查詢只產生 `select distinct ts from site`,也就是有列的傾印時間。沒有變化的傾印不會有列,所以「傾印次數」不等於時間。
2. 停錄前還要等一段(實驗室 3 秒),這段尾巴也在「後半」裡,但 App 已經閒置。N 小時尾巴占比高,後半增被稀釋;N 大時才可忽略。
3. 實驗室的 8 輪情境:前半增 8、後半增 6,6 ≥ 8/2 勉強過。把尾端 3 秒閒置加進來,後半增更小,有可能掉到門檻以下而漏判。
4. spec 沒定義「中間那次傾印」怎麼取(偶數次傾印時取哪一個)。

### F7 查詢是 dumps × site 的不等值 join,callsite 多時時間無上限,也沒有逾時分類
severity: minor
blocking: 否
引句:「from dumps d join site s on s.ts <= d.ts group by d.ts, s.site order by s.site, d.ts;」
file: spec 第 107-108 行

1. 這個 join 的成本約為「傾印次數 × `heap_profile_allocation` 總列數」。傾印 120 次、每次有變化的 callsite 幾千個時,量級是幾千萬次比較。
2. 實驗室只有幾列,沒量過。真實第三方 SDK 會有大量 callsite。
3. `T_LONG`(1800 秒)是既有上限,但 spec 沒寫逾時後怎麼辦(跳過還是 failed)。
4. 輸出是「每個 site 每次傾印一列」,全部灌回 CSV 再丟給 Python 算前後半。可以改成 window 累計和,或在 SQL 內直接算前半、後半,輸出每個 site 一列。
5. 我沒實跑量測,量級是推算,⚠。

### F8 C++ SDK 的呼叫位置會全部折疊成 `operator new`,查詢的「malloc 上一層」對真實 SDK 失效
severity: major
blocking: 是
引句:「查詢(trace_processor;malloc 上一層的函式當呼叫位置):」
file: spec 第 95-105 行

1. 查詢把 callsite 的 `parent_id` 當呼叫位置,也就是 `malloc` 的直接呼叫者。實驗室的假 SDK 是 C 直接呼叫 `malloc`,所以這一層就是 `nativeCreate`。
2. 真實的第三方 SDK 大多是 C++:`new` / `std::make_shared` / `std::vector` 的配置都經過 `operator new`(`libc++_shared.so` 或 `libc.so`)再呼叫 `malloc`。這時 malloc 上一層永遠是 `_Znwm @ libc++_shared.so`。
3. 照 spec 字面,所有 C++ 配置會被歸到同一個呼叫位置。多個漏點的增量加總成一列,輸出是「`operator new` 在漲」,沒有人能據此優化,這違反整份計劃「哪支 .so 的哪個函式」的目的。
4. 同理 `calloc`、`realloc`、`strdup`、`posix_memalign` 的 libc 包裝層,以及去除符號的 .so(函式名拿不到,`coalesce` 成 `?`,多個 site 也被併成 `? @ ?`),都會折疊。
5. 應該是:往上跳過 libc / libc++ 的配置包裝層(用 mapping 名稱過濾),取第一個不屬於系統配置器的 frame。這個設計決策 spec 沒有,實驗室也沒覆蓋。

### F9 主機 trace_processor 來源與版本和 skill 釘的不一致,spec 只留 REVISIT
severity: major
blocking: 是
引句:「收集腳本與分析工具要對到 skill 釘的 Perfetto 版本:2026-10-28 實驗用的主機 trace_processor 是 v58.2」
file: `scripts/templates/android-stability-collect.sh:21`、`skills/lumos-android-evidence/SKILL.md:15`

1. 收集腳本的 `TP` 是 `os.environ.get("TP", "trace_processor")`,即 `PATH` 上的任何版本。preflight 只用 `shutil.which(TP)` 檢查存在,不檢查版本。
2. skill 釘的是 `$SKILL_ROOT/references/perfetto/bin/trace_processor`(包裝腳本,第一次會下載並驗雜湊)。本 repo 的 `skills/lumos-android-evidence/` 只有 `SKILL.md` 與 `reference.md`,沒有這支包裝腳本。
3. spec 把這個缺口登記成 REVISIT(2027-01-31),但那只處理實驗室重跑,沒定義正式實作時怎麼讓收集腳本拿到 v57.2:
   - 新查詢依賴的表(`heap_profile_allocation`、`stack_profile_callsite` 等)和欄位在 v58.2 與 v57.2 之間是否一致,spec 沒驗證。
   - 若包裝腳本第一次執行要下載:下載失敗、驗雜湊失敗、離線環境,都發生在裝置已被動過(App 重啟、錄製已跑完)之後,spec 沒寫該怎麼辦。
4. 照 spec 字面,正式版的行為是「用 PATH 上任意版本」,結果在不同機器上可能不同。

### F10 多跑一段 N 輪的總時間影響與 RETIRE-IF 的撤除條件幾乎自動成立
severity: minor
blocking: 否
引句:「每次驗收多花的時間超過量測本身的一倍,也拿掉。」
file: spec 第 74 行

1. 第二段 N 輪本身約等於一倍量測,再加啟動、停錄(最多 30 秒)、拉檔(最大 64 MB 經 `adb pull`)、`trace_processor` 查詢(F7),加上 heapprofd 自己的拖慢(spec 自己的 REVISIT 說還沒量過)。
2. 所以只要有任何額外成本,「超過量測本身的一倍」這條就會觸發。撤除條件實際上不是「出事才撤」,而是「一上線就觸發」。
3. 這是閾值定得過低,不是設計錯誤。要是一倍已被接受(d1 trade_offs 寫「驗收多花約一段量測的時間」),那撤除條件應該是兩倍或有絕對秒數。

### F11 條款 S1 與前文、步驟 4 的排序依據矛盾,列出下限也有出入
severity: minor
blocking: 否
引句:「照結尾未釋放量由大到小排」
file: spec 第 71、90、126、150 行

1. 第 71 行與第 126 行(步驟 4):「照增長量排序」。S1:「照結尾未釋放量由大到小排」。
2. 第 90 行:「只列結尾**或**增量超過 1 MB 的」。S1:「結尾超過 1 MB」(沒有「或增量」)。
3. 實作者會不知道採哪一個。S1 的測試要綁哪一個也不確定。

## 各節總結

- **frontmatter 與 pending_questions / decisions(d1-d4)**:已讀,無 finding(交叉引用 d1-d4 都在,「回退節」存在)。
- **白話與 PRIOR-ART**:F9(版本)、F8(查詢假設)。
- **實驗室實測表**:F3、F4、F6、F8。實驗只覆蓋 C 直接 malloc、無第三方 profile 衝突、N=8。
- **打算怎麼做(1-5)**:F1、F2、F3、F4。
- **跟舊否決的差別**:已讀,無 finding。
- **實務隱患 / 已排除**:
  - 守衛面「只提醒,不改任何判定」成立的前提是 F2 的順序處理,現有寫法不足以保證,排除理由站不住。
  - 不可逆:殘留的裝置端錄製與 malloc 掛鉤見 F1,「撤掉照回退節刪程式」沒涵蓋裝置端狀態,排除理由不完整。
  - 金流:站得住。
  - 對外送出:站得住,錄檔只在本機 run 目錄。
- **條款**:F11。S3 / S6 沒涵蓋 F3 的「被拒、空錄檔、資料遺失」跳過路徑。

總結:整份最高嚴重度為 major,blocking 共 6 條(F1、F2、F3、F4、F8、F9)
