severity: major

我逐節讀了整份 spec,對照收集腳本、Perfetto v57.2 原始碼和固定席節點。下面是資源與併發鏡頭的結果。

### F1 以 heapprofd_ 開頭且非 0 就判 failed,每次成功的錄製都會被判失敗
severity: major
blocking: 是
引句:「名字以 heapprofd_ 開頭、值非 0 的錯誤計數」
file: `scripts/templates/android-stability-collect.sh:305`(新增的查詢要接在這支之後)。外部查證見 https://raw.githubusercontent.com/google/perfetto/v57.2/src/trace_processor/storage/stats.h

1. 〈打算怎麼做〉第 4 步的字面規則是「名字以 `heapprofd_` 開頭、值非 0」。v57.2 的 stats.h 裡有 14 個 `heapprofd_` 項目,其中 6 個嚴重度是 info,不是錯誤:
   - 這 6 個是 `heapprofd_client_disconnected`、`heapprofd_sampling_interval_adjusted`、`heapprofd_unwind_time_us`、`heapprofd_unwind_samples`、`heapprofd_client_spinlock_blocked`、`heapprofd_last_profile_timestamp`。
   - 成功的錄製裡 `heapprofd_unwind_samples`、`heapprofd_unwind_time_us`、`heapprofd_last_profile_timestamp` 本來就是非 0。照字面實作,每次都會判 failed,整項提示等於永遠不會出現。
2. spec 自己舉的例子 `heapprofd_client_disconnected` 就是 info。
3. 真正的錯誤是 `heapprofd_buffer_corrupted`、`hit_guardrail`、`client_error`、`malformed_packet`、`missing_packet`、`rejected_concurrent`、`non_finalized_profile`(嚴重度 error),以及 `heapprofd_buffer_overran`(data_loss)。
4. 「完整名單實作時列進程式」把名單推給實作者。改成用 `stats.severity in ('error','data_loss')` 且名字以 `heapprofd_` 開頭來篩,規則才算有寫清楚。
5. S7 也要補一條:正常成功錄製不應被判 failed。

### F2 傾印時間從 heap_profile_allocation 的列取,沒變動的傾印不會有列,傾印次數會少算
severity: major
blocking: 是
引句:「先取傾印時間挑出三個時間點,再一次掃描算每個 callsite 在三個時間點的累計」
外部查證:https://raw.githubusercontent.com/google/perfetto/v57.2/src/trace_processor/importers/proto/profile_packet_sequence_state.cc

1. 實驗查詢用 `select distinct ts from site` 當傾印時間,正式版第 4 步沿用同一個做法。
2. trace_processor 只在有變動時才寫列。配置差額寫入前的判斷是 `if (alloc_delta.count || alloc_delta.size)`,釋放差額是 `(free_delta.count || free_delta.size)`。
3. 所以「這一秒完全沒有新配置或釋放」的傾印,在表裡看不到。
4. 具體例子:池滿之後(情境③)或 App 在輪與輪之間閒置時,連續幾次傾印都沒有列。
   - 照 spec 字面,這些傾印不算數,「傾印少於 3 次」會誤判成樣本不足。
   - 「時間上最接近正中的那一次」只在剩下的傾印裡挑,中間點會偏掉。
   - 偏掉的中間點會直接改變後半增量,也就改變線性增長或停住的分類。
5. spec 要先說傾印時間從哪裡取才分得出「有傾印但沒變動」和「沒傾印」。我沒查到 v57.2 有沒有逐次傾印的表,這點標 ⚠,需要實作前核對。
6. 「傾印 0 次」的判斷也受影響:真的 0 次和全部沒變動無法區分。

### F3 「開頭」要用驅動開始時間,但 trace 裡沒有這個時間;「等第一次傾印」只是固定睡眠
severity: major
blocking: 是
引句:「驅動量測開始前的最後一次傾印」

1. 〈判法〉第 2 條要求「驅動量測開始前的最後一次傾印」。查詢只吃錄檔,腳本沒有說明怎麼把主機端記下的驅動開始時間換成 trace 的時鐘,也沒有標記事件。
2. 〈打算怎麼做〉第 3 步是「開 heapprofd → 等第一次傾印(dump_phase_ms 再加 1 秒)→ 驅動」。這是固定睡眠 2 秒,不是偵測到傾印才動手。
3. 這樣會有兩個問題:
   - heapprofd 的 `dump_phase_ms` 從資料來源啟動算起,不是從 client 連上行程算起(heapprofd_producer.cc 的 `StartDataSource` 排程第一次連續傾印)。
   - 已在跑的 App 要先被送訊號載入 client,時間不固定。第一次傾印時行程可能還沒連上,那次傾印就是空的。
4. 加上 F2:空的傾印在表裡不存在,所以「一定有」不成立。睡 2 秒後驅動開始時,表裡可能只有 0 到 2 個傾印,也分不出哪個在驅動前。
5. 實驗(〈實驗室實測〉第 82 行)是「開 heapprofd → 直接驅動量測 8 輪」,沒有等待步驟。「等第一次傾印」是正式版新加、沒有被實驗驗證過的機制。
6. 在 spec 說清楚三件事前,實作者無法決定「開頭」是什麼:
   - 是記錄驅動開始的 trace 時間戳,還是直接取第一次傾印。
   - 取第一次傾印時,「驅動跑完前最後一次」這句要改寫。
   - 等第一次傾印要怎麼偵測,不能用睡眠。

### F4 「驅動一跑完就停錄」和實驗的「等 3 秒停錄」不同;結尾傾印靠停錄時才有的最後一次傾印
severity: minor
blocking: 否
引句:「驅動一跑完就停錄」
外部查證:https://raw.githubusercontent.com/google/perfetto/v57.2/src/profiling/memory/heapprofd_producer.cc

1. 實驗是等 3 秒再停錄,正式版改成立刻停,spec 沒說為什麼。
2. 原始碼顯示 `ShutdownDataSource` 不主動做最後傾印。最後一次傾印發生在 client socket 斷線的處理裡(`HandleSocketDisconnected`),等待上限是 `stop_timeout_ms`,預設 5000 毫秒。
3. 超時的話會記「Final dump timed out.」並直接清掉,沒有最後傾印。
4. 這時「結尾」只是停錄前最近一次連續傾印,最多差 1 秒。
5. 現有 `stop_record` 的 `STOP_WAIT` 預設 30 秒,夠等這 5 秒;但它只看 perfetto 行程退出,沒看最後傾印有沒有成功。
6. 錯誤統計 `heapprofd_non_finalized_profile` 會記這件事,所以修完 F1 後可以靠它偵測。我沒有實機驗證這條,標 ⚠。

### F5 第二段出任何例外,第一段已算好的結果整份丟掉
severity: major
blocking: 是
引句:「前提是第二段排在既有讀取之後、pid 與結束紀錄另存」
file: `scripts/templates/android-stability-collect.sh:542`、`scripts/templates/android-stability-collect.sh:548`、`scripts/templates/android-stability-collect.sh:552`

1. 結果檔只在 `measure()` 回傳後才寫:`json.dump` 在 `main()` 最後,`measure()` 中途丟出任何例外就進 `except BaseException: cleanup; raise`,不寫 `stability.json`。
2. 第二段加在 `measure()` 裡、第一段 `res` 已經組好之後。任何一個沒被包起來的例外(csv 解析、TP 輸出格式、記憶體不足、空欄位)都會讓第一段全部白費。
3. 「守衛面」宣稱第二段不改任何判定、回傳碼;d2 說永遠只提醒。這跟「第二段的例外會吃掉第一段」矛盾。S4 只測「第二段期間 App 結束」,沒測第二段程式本身出錯。
4. 被中斷(Ctrl-C、SIGTERM、SIGHUP)時也一樣:第二段多了暖機、約 2 秒等待、N 輪、停錄,最差又多等一段 `STOP_WAIT` 和拉檔,第一段整份結果在這段時間被中斷就全丟(`die` 回 2,沒寫結果檔)。
5. spec 要說明兩件事:
   - 第二段全部包進 `try/except Exception` 轉成 failed,並寫進 S7。
   - 中斷時要不要先把第一段結果寫出。如果決定不寫,這是跟現行行為一致,但要在〈實務隱患〉明講。

### F6 第二段共用 max_record_s,而 heapprofd 會拖慢 App,N 輪可能超過上限
severity: minor
blocking: 否
引句:「設定範本另開 `android-stability-heapprofd.pbtxt`(`__PROCESS__`、`__DURATION_MS__` 佔位,時長照 `stability.max_record_s`)」
file: `scripts/lumos:39568`(`max_record_s` 允許 1 到 86400)

1. 錄製是在暖機之後才開始,所以暖機不佔這個時長,這點沒問題。
2. 但專案調 `max_record_s` 時是對著第一段(沒有 heapprofd 的 N 輪)調的。第二段的 N 輪因取樣被拖慢,spec 自己承認拖慢程度沒量(REVISIT 2027-01-31),還要加上約 2 秒的等待。
3. 上限調得貼近第一段實際時間的專案,第二段會在 N 輪跑完前到上限。`stop_record` 會回「錄製在 N 輪跑完前就到了上限(stability.max_record_s)」,整段 failed,但訊息沒提到是 heapprofd 讓它變慢。
4. 此時錄檔其實有最後傾印、可以用,卻被 `stop_record` 的規則丟掉。

### F7 第二段被中斷時 App 留在被掛 malloc 鉤子的狀態,也沒收本機半檔
severity: minor
blocking: 否
引句:「當第二段進行中被中斷時,裝置上第二段的設定檔與錄檔應被 cleanup 收掉」
file: `scripts/templates/android-stability-collect.sh:516`

1. `cleanup` 只停錄製、刪裝置暫存,不停 App。第一段被中斷時 App 沒有被掛鉤,影響小。第二段被中斷時,App 行程上載入了 heapprofd client,持續拖慢,留到下一次 `am force-stop`。
2. 〈打算怎麼做〉第 3 步最後的「停 App」只在正常路徑上。S8 只涵蓋裝置上的檔,沒有涵蓋這個 App 狀態,也沒有涵蓋本機 `heap-native.pftrace` 拉到一半被中斷的半檔。
3. 時序確認:第一段 `del state["rec"]` 到第二段 `start_record` 登記之間,沒有裝置端的錄製,這個空窗安全。`start_record` 在推設定前就登記,「中斷時的 cleanup 不用改」的說法對錄製檔成立,對 App 狀態不成立。
4. 〈回退〉也沒提到這件事。

### F8 檔名後綴 `-native` 和 run-id 可能撞名;跟其他 perfetto 錄製同時存在只靠失敗訊息
severity: minor
blocking: 否
引句:「遠端檔名 `lumos-stability-<run-id>-native.*`」

1. run-id 規則允許連字號。run-id 是 `X` 的第二段檔名 `lumos-stability-X-native.pftrace`,會跟另一次 run-id 是 `X-native` 的第一段檔名撞在一起。同一台裝置同時兩個收集本來就不安全,但這個撞名讓原本不衝突的兩個 run-id 變成衝突。
2. 現有 `pkill -TERM -f <遠端檔名>` 的模式是正規表示式。我確認過「`X.pftrace`」不會誤中「`X-native.pftrace`」。反方向也不會。這部分不是問題。
3. 同一行程已有別的 heapprofd 工作階段(例如 L3 手動 `heap_profile`)時,spec 只靠 `heapprofd_rejected_concurrent`(F1 修正後可以擋)和 0 次傾印的原因文字交代。這次的收集腳本沒有事前偵測,可接受,但上面的檔名撞名要處理。

### F9 「一次掃描」的查詢怎麼拿祖先框架沒寫,大錄檔的時間與記憶體沒有上限
severity: minor
blocking: 否
引句:「再取這些 callsite 的祖先框架」
file: `scripts/templates/android-stability-collect.sh:215`

1. 實驗查詢只往上走一層(`c.parent_id`),〈判法〉第 1 條要跳過多層配置器,需要走多層。第 4 步沒寫用什麼機制往上走多層。
2. 「這些 callsite」沒說是全部有列的 callsite,還是先在 SQL 裡把整段增量不到 1 MiB 的濾掉再取祖先。實驗用的 `join ... on s.ts <= d.ts` 會做傾印數乘列數的連接,正式版要改成條件聚合。這在 SQLite 做得到,但最好寫進 spec。
3. heapprofd 的呼叫鏈很深。若對所有 callsite 展開全部祖先,輸出列數可能很大,全數經標準輸出傳回 Python 再解析,現有程式在 `T_LONG` 內沒有輸出大小上限(`run` 用 `communicate` 全部讀進記憶體)。建議先在 SQL 裡篩到增量夠大的前幾百個 callsite,再取祖先。
4. 這項我沒實機驗證,標 ⚠。

### 各節
- frontmatter 與 pending_questions / decisions:已讀,無 finding。
- 白話段、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding。Perfetto 欄位 `process_cmdline`、`sampling_interval_bytes`、`shmem_size_bytes`、`no_startup`、`continuous_dump_config` 的存在,我沒有逐一對 proto 驗證。
- 實驗室實測:有 F3 的發現(實驗沒有等待步驟)。
- 判法:F2、F3。
- 打算怎麼做:F1、F3、F4、F5、F6、F7、F8、F9。
- 跟舊否決的差別:已讀,無 finding。
- 實務隱患:有 F5(守衛面前提)與 F7(已排除:不可逆,漏了 App 狀態)。「金流」、「對外送出」兩條的理由我讀過,這個鏡頭沒新發現。
- 條款:S4、S7、S8 要補(F1、F5、F7)。S5 是人工驗收,沒問題。
- 回退:有 F7 的缺口。
- 審計修正紀錄:已讀,無 finding。

### 實務隱患逐類
- 併發:有,見 F8,以及「同一行程已有別的 heapprofd 工作階段」的失敗原因文字。
- 效能:有,見 F6、F9。
- 資源:有,見 F7(App 被掛鉤、本機半檔)。
- 回滾:有,見 F5、F7。
- 遷移:無新發現,設定指紋會變這件事 spec 已寫。

### 固定席
- `Systems/android-stability-collector.md`:會受影響。第二段新增 `ARTIFACTS` 項與 `start_record` 簽名,合約行「停完才從待收清單刪」(第 35 行 PITFALL)要沿用到第二段;F5 提到的「結果檔只在最後寫」也要寫進這篇。
- `Systems/macrobenchmark-adapter.md`:不影響其既有行為。新範本要登記 `_VENDORED_TREE_FILES`(第 34 行 PITFALL),spec 第 7 步已寫。
- `Systems/android-e2e-acceptance.md`:大致不影響。收集步驟的逾時是 `T_LONG` 3600 秒(`scripts/templates/android-e2e-run.sh:58`),第二段多出的時間實務上遠小於這個上限。記憶體設定指紋會變,spec 已寫在遷移。
- `Projects/Android記憶體與穩定性驗收_計劃.md`:spec 第 7 步已說要改那句「只剩 Native Heap 前後數字當線索」。我只對照了摘要與 grep,沒有逐段讀全文,標 ⚠。
- `Projects/Android逐層診斷_計劃.md`:d4 已處理「每次都錄」的否決,沒看到新衝突。同樣只讀了摘要,標 ⚠。

總結:整份最高嚴重度為 major,blocking 共 4 條。
