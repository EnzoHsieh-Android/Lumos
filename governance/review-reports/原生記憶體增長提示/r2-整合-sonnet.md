severity: major

整份 spec 的 §〈實驗室實測〉〈跟舊否決的差別〉〈審計修正紀錄〉已讀,無 finding。其餘各節的 finding 如下。

### F1 stats 檢查規則「heapprofd_ 開頭、值非 0」會讓每次成功的錄製都被判 failed
severity: major
blocking: 是
引句:「stats 表裡名字以 heapprofd_ 開頭、值非 0 的錯誤計數(例如 heapprofd_buffer_overran、heapprofd_client_disconnected;完整名單實作時照 v57.2 的 stats 定義列進程式)」
file: https://raw.githubusercontent.com/google/perfetto/v57.2/src/trace_processor/storage/stats.h(約 405–435 行)
file: https://raw.githubusercontent.com/google/perfetto/v57.2/src/trace_processor/importers/proto/profile_module.cc(約 407–447 行)
1. v57.2 的 `heapprofd_*` stat 有 13 個,其中 `heapprofd_client_disconnected`、`heapprofd_sampling_interval_adjusted`、`heapprofd_unwind_time_us`、`heapprofd_unwind_samples`、`heapprofd_client_spinlock_blocked`、`heapprofd_last_profile_timestamp` 都是 `kInfo`。
2. profile_module.cc 每處理一筆 ProcessHeapSamples 就累加 `unwind_time_us` 與 `unwind_samples`,並把 `last_profile_timestamp` 設成 ts。所以錄製成功時這幾項必然非 0。
3. 照字面「前綴加非 0」實作,每次成功錄製都會被判 failed。
4. spec 自己舉的例子 `heapprofd_client_disconnected` 也是 info 等級,不是錯誤。
5. 「完整名單實作時列進程式」沒說名單依什麼挑。
6. `stats` 表有 `severity` 欄(`"info" | "data_loss" | "error"`,metadata_tables.py 的 STATS_TABLE)。應改成「名字以 heapprofd_ 開頭、`severity` 為 error 或 data_loss、且值非 0」。`client_disconnected` 這類 info 不進 failed 清單。

### F2 傾印時間若取自 heap_profile_allocation 的 distinct ts,沒有增量的傾印會消失
severity: major
blocking: 是
引句:「驅動量測開始前的最後一次傾印(開頭;〈打算怎麼做〉第 3 步先等到第一次傾印才開始驅動,所以一定有)」
file: https://raw.githubusercontent.com/google/perfetto/v57.2/src/trace_processor/importers/proto/profile_packet_sequence_state.cc(約 255–285 行)
1. v57.2 只在 `alloc_delta` 或 `free_delta` 非 0 時才 Insert 一列。一次傾印如果相對上次沒有任何增量,表裡就沒有那個 ts。
2. 〈打算怎麼做〉第 4 步只說「先取傾印時間」,沒說從哪張表取。實驗用的查詢是 `select distinct ts from site`,也就是取自 allocation 表。
3. 暖機後 App 閒置、取樣間隔 4096 位元組時,第一次傾印很可能沒有任何列。「一定有」不成立。
4. 「傾印少於 3 次」與「傾印 0 次」也會被低估,把正常的錄製誤判成「樣本不足」或「沒錄到」。
5. 傾印時間需要可靠來源。spec 要寫明,或接受只在有變化的傾印才算一次並改掉「一定有」。⚠ 閒置時零增量的機率沒在裝置上量過,所以標 ⚠。

### F3 單一「檔名後綴」參數做不出 heap-native.pftrace,本機錄檔會逃過 7 天清理
severity: major
blocking: 是
引句:「錄製沿用 `start_record`、`stop_record`(加兩個參數:設定範本、檔名後綴)」
file: `scripts/templates/android-stability-collect.sh:305-366`
1. `start_record` 本機設定檔寫死 `record.pbtxt`(第 308 行)。`stop_record` 本機追蹤檔寫死 `cycle.pftrace`(約 359 行)。
2. 只加一個「後綴」,結果是 `cycle-native.pftrace`。spec 要的本機檔名卻是 `heap-native.pftrace`,而且 d3 把「符合 `heap-*.pftrace` 樣式」當成 7 天自動刪的前提。
3. 清理規則是 `re.fullmatch(r"heap-.*\.pftrace", f)`(第 148 行)。`cycle-native.pftrace` 不符合,含個資的錄檔會永遠不被刪,違反 d3。
4. 兩個本機檔名(設定檔、追蹤檔)要各自參數化,或用前綴加後綴。spec 沒寫,實作者必須自己決定。
5. 附帶:`stop_record` 的失敗原因「錄製在 N 輪跑完前就到了上限」是第一段專用的措辭,第二段重用時要不要換字,spec 也沒說。

### F4 「Android 11 以下」與「要 11 以上」自相矛盾,邊界差一
severity: major
blocking: 是
引句:「裝置 Android 11 以下(只接已在跑的行程要 11 以上)→ unsupported「Android 版本不支援」」
file: `scripts/templates/android-stability-collect.sh:322-324`(`ro.build.version.sdk` 讀成 `android_sdk`)
file: https://raw.githubusercontent.com/google/perfetto/v57.2/protos/perfetto/config/profiling/heapprofd_config.proto(`no_startup`:「Introduced in Android 11」)
1. 括號說要 11 以上才支援,前半卻寫「11 以下」不支援。S6 重複了「Android 11 以下」。
2. 照字面把 sdk≤30 擋掉,會誤擋 Android 11(SDK 30),而它支援 `no_startup`。
3. 應寫成 sdk<30(或「低於 Android 11」)。
4. `android_sdk` 是 `None` 時(getprop 讀不出)怎麼處理,spec 也沒寫。
5. 小項:〈判法〉第 2 條與〈打算怎麼做〉第 4 步都處理「傾印 0 次」。0 同時屬於「少於 3 次」,兩條訊息衝突時用哪條沒有優先序。

### F5 「照 low_iterations 的形狀」會讓只有 stability 段的專案收不到、看不到提示
severity: major
blocking: 是
引句:「照 `low_iterations` 的形狀:沒東西時是空清單,文字與 `--json` 都有),只要給了 `--stability` 就讀,不看門檻檔有沒有寫」
file: `scripts/lumos:40312-40323`(`low_iterations` 只在有結果目錄的主路徑填值)
file: `scripts/lumos:40255-40272`(`_macrobench_without_results` 不填也不印)
file: `scripts/lumos:40232-40235`(`_macrobench_print_thresholds` 沒有任何門檻條目就直接 return)
1. `low_iterations` 的鍵初始化在 res 裡(第 40312 行),但只有主路徑(有 `results_dirs`)才算值與印。
2. `_macrobench_without_results` 只做 `res.update(stab_res)`,然後印門檻區塊。純 stability/e2e 專案(`results_dirs` 可不填)走這條路,e2e 腳本呼叫 `macrobench --json --stability` 也走這條。
3. 照 `low_iterations` 的位置實作,這類專案的 `--json` 沒有填好的 `native_growth`,文字輸出也印不出提示。
4. 這類專案正是此功能的主要使用者。「不看門檻檔有沒有寫」更要求提示不能掛在 `_macrobench_print_thresholds` 內。
5. spec 要明講:算值要在 `stab` 載入後、主路徑與 without_results 兩條路都做,並且各自印出。

### F6 `native_growth` 的「名字對不到情境」檢查放在 `_macrobench_stab_optional_err`,但它拿不到 stability_scenarios
severity: minor
blocking: 否
引句:「lumos 在 `_macrobench_stab_optional_err` 驗:不是字串清單、或名字對不到情境 → 回 2 擋下」
file: `scripts/lumos:39476-39483`、`scripts/lumos:39542-39555`、`scripts/lumos:39557`
1. `_macrobench_stab_optional_err(st)` 只收 stability 段。唯一呼叫者 `_macrobench_stab_cfg_err(raw["stability"])` 也只傳這一段。
2. 要對情境名,得在 `_macrobench_stab_top_err(raw)`(有 `raw`)另加檢查,或改簽名。spec 指定的位置做不到。
3. `stability_scenarios` 的情境名規則允許 `default`(`[A-Za-z0-9_-]+`)。使用者自訂同名情境時,與保留字「default」撞名,spec 沒說誰優先。
4. 收集腳本的 `load_config` 在 `LUMOS_STABILITY_SCENARIO` 區域變數裡拿情境名,`measure(st, …)` 拿不到。步驟 2 判斷「這次的情境」要新增傳遞。

### F7 TP 查詢的放置沒定:多段回傳列的語句、sqlite 測試、輸出解析三者互相卡住
severity: minor
blocking: 否
引句:「先取傾印時間挑出三個時間點,再一次掃描算每個 callsite 在三個時間點的累計(不做傾印數乘列數的連接),再取這些 callsite 的祖先框架;輸出用 csv 模組解析」
file: `skills/lumos-android-evidence/reference.md:89`
file: `scripts/test_lumos.py:18425`(`_ms_sql` 用 sqlite3 測範本)
file: `scripts/templates/android-stability-collect.sh:299-310`
1. reference.md 實測 v57.2 的 `-q` 一個檔裡有兩條回傳列的語句會報錯。spec 的三段查詢要拆成多次 TP 呼叫,每次各自佔 `T_LONG`。
2. 既有查詢放在 .sql 範本,由 `_ms_sql` 用 sqlite3 測。實驗版查詢用 `create perfetto table`,sqlite3 跑不了。
3. 查詢是內嵌 Python、還是新增 .sql 範本?spec 的 `_VENDORED_TREE_FILES` 只說「新範本檔」(指 pbtxt)。若再多一支 .sql,又要登記、補 SPDX 檔頭,並過 `t_android_memstab_vendored` 的逐檔清單。
4. S1、S2、S3 全是 `[test:待定]`。測試只能對 TP 輸出的假資料做,spec 沒說。
5. 現行 `cycle_numbers` 用 `split(",")` 解析。spec 改用 csv 模組是對的,但兩種解析並存,要說明不回頭改第一段。

### F8 新範本沒有進收集腳本那篇 Systems 筆記的 about_code,違反「每支檔有家」
severity: minor
blocking: 否
引句:「新範本檔登記進 `_VENDORED_TREE_FILES`(還有它的測試清單)。」
file: `docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md`(about_code 只列四支)
1. 專案鐵則 5:每支程式檔要有一篇 Systems 節點的 about_code 列它。提交時會擋新違規。
2. spec 只提 `_VENDORED_TREE_FILES` 與測試清單,沒提把 `android-stability-heapprofd.pbtxt` 加進 collector 的 about_code。
3. reference.md 的「保留」清單與「只清自己的 `lumos-stability-<run-id>.*`」那句,也要涵蓋新的 `-native.*`。

### F9 輸出清理函式與鄰近約定不一致,筆記沒同步
severity: minor
blocking: 否
引句:「印的時候標「只提醒,不擋推送」、每行過 `_out_clean`」
file: `scripts/lumos:19371`、`scripts/lumos:40242`、`scripts/lumos:40249`、`scripts/lumos:40252`
file: `docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:35`
1. 既有 `--stability` 文字輸出一律過 `_events_clean(…, 500)`。macrobenchmark-adapter 筆記第 35 行有 WHY,並寫「不選:另寫一支清理函式」。
2. spec 選 `_out_clean`(存在,更嚴格)。這與鄰近約定及筆記不同,spec 沒說為何不沿用 `_events_clean`。
3. 若維持 `_out_clean`,要在 macrobenchmark-adapter 筆記補一句原因,否則三個月後的人會以為是漏改。
4. `--json` 路徑上 `native_growth` 的字串靠 `_macrobench_stab_scrub`(`_esc_clean`)。`_esc_clean` 會留下 U+2028(筆記 r4 資安席已指出),`--json` 輸出 spec 沒要求再清一次。

### F10 其他已查證的假設與小遺漏
severity: minor
blocking: 否
引句:「第一段的錄製從 state 拿掉之後才開第二段,沿用同一個 `state["rec"]` 槽,中斷時的 cleanup 不用改。」
file: `scripts/templates/android-stability-collect.sh:305-312`、`scripts/templates/android-stability-collect.sh:490-493`、`scripts/templates/android-stability-collect.sh:516-530`
1. 屬實:`start_record` 先把 `(None, cfg, trace)` 登記進 `state["rec"]` 才推檔,`abort_record` 用 `pkill -f <遠端檔名>`。
2. 第二段檔名 `…-native.pftrace` 與第一段 `….pftrace` 的 pkill 樣式不互相命中,可共用槽。
3. `start_record` 與 `stop_record` 只在 `measure()` 各被呼叫一次。測試是以 sh 對假工具黑箱跑,沒有直接 import。預設關閉時加參數不會破壞既有測試。
4. 但第二段的任何未預期例外會走 `except BaseException: cleanup; raise`,整份 `stability.json` 都寫不出來。S4 要求「第二段出事時既有欄位不變」,spec 沒要求把第二段包進 try 並轉成 failed 狀態。
5. 第二段被 Ctrl-C 中斷時,第一段約 W+N 輪的結果也一起丟失(既有行為,但受影響時間窗約加倍)。
6. 查證屬實的假設:
   - `T_LONG` 在收集腳本確實存在(第 23 行)。e2e 腳本另有同名但值不同的 `T_LONG`(3600 秒),後者是整個收集步驟的逾時,第二段會讓收集腳本更容易逼近它。
   - `_VENDORED_TREE_FILES`、`E2E_SCENARIO_KEYS`、`_macrobench_stab_val`、`_out_clean` 都存在。
   - 舊版 `_macrobench_stab_optional_err` 確實不驗未知鍵,`_e2e_scenarios_err` 確實擋情境裡的未知欄位。因此「不寫進 `stability_scenarios`」的理由成立。
   - 指紋(`_e2e_mem_canon` 與 `memory-config` 雜湊)確實含整段 stability,spec 的〈遷移〉成立。
   - `native_heap_kb` 不被 lumos 讀(`scripts/lumos` 無出現)。
   - Perfetto v57.2 的 `heap_profile_allocation`(`ts`、`heap_name`、`callsite_id`、`size`)、`stack_profile_frame.rel_pc`、`mapping` 與 `stack_profile_mapping.name`、`summary_tree` 的 `sum(size)` 都存在。`alloc_delta`、`free_delta` 在 `profile_packet_sequence_state.cc`,`free_delta` 為負。

## 固定席逐篇判

1. **Systems/android-stability-collector:受影響,不破壞合約,但筆記要補**
   - 該節點宣稱「先掃再錄快照」「停完才從待收清單刪」「中斷時 cleanup 收錄製」,第二段排在全部讀取之後並重用 `state["rec"]`,都不違反。
   - 要補:about_code 加新 pbtxt(F8)。「收集腳本排全部順序」那條 WHY 要加第二段。檔名後綴要設計成 `heap-native.pftrace`(F3)。
2. **Systems/macrobenchmark-adapter:受影響**
   - 「stability_unjudged 鍵一開始就放好」「`low_iterations` 列出」的約定可延伸到 `native_growth`。
   - 風險在 without_results 路徑與印出條件(F5)、清理函式約定(F9)。
3. **Systems/android-e2e-acceptance:不影響**
   - 指紋含整段 stability 與 stability_scenarios,記憶體設定變動會要求整套重跑,與 spec〈遷移〉一致。
   - e2e 判定不讀 `native_growth`,`--json` 多一個固定鍵不改 e2e 判定。
   - 唯一要留意:收集步驟時間約加倍,逼近 e2e 的 3600 秒步驟逾時。
4. **Projects/Android記憶體與穩定性驗收_計劃:受影響,需同步改句**
   - 「驅動跑兩次」「只剩 Native Heap 前後數字當線索」兩處要改。
   - 它的 WHY「驅動要在同一個行程裡做完、不殺行程」要加註範圍:第二段是獨立的一輪量測,含 force-stop 與重啟,不破壞第一段。
   - 它的 S 條款與判定行為不變。
5. **Projects/Android逐層診斷_計劃:不影響**
   - 第 20 行否決的是「每次都錄 Trace+CPU 取樣+記憶體」。d4 的按情境、預設關,符合其理由。
   - L0 到 L3 的 `test_data` 閘門也由 spec 沿用。
   - 但此計劃未列入 `lands_in`,而 skill 的 L0、L3 要改,必須在兩篇 Systems 之外另補寫回。

總結:整份最高嚴重度為 major,blocking 共 5 條(F1、F2、F3、F4、F5)。
