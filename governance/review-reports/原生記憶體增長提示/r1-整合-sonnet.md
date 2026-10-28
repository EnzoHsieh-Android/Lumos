severity: major

整份讀完。我先把已核對成立的宣稱列出來,再列 finding。

已核對成立:
- Native Heap 前後兩個數字只寫在結果檔,lumos 判定不讀也不印。我在 `scripts/lumos` 搜 `native_heap_kb` 沒有命中。
- 7 天自動刪只看 run 目錄第一層、檔名符合 `heap-.*\.pftrace`,而且不刪捷徑,見 `scripts/templates/android-stability-collect.sh:134`。
- `E2E_SCENARIO_KEYS[2:]` 確實一律當 1 到 `MACROBENCH_MAX_CYCLES` 的整數驗,見 `scripts/lumos:40491`。布林鍵不能直接接在清單尾端,spec 說對了。
- 收集腳本與 lumos 兩邊清單的比對測試存在,見 `scripts/test_lumos.py:19494`。
- Perfetto 的設定欄位與表名在 v57.2 都查得到:`heapprofd_config.proto` 有 `no_startup`、`dump_phase_ms`、`dump_interval_ms`、`shmem_size_bytes`,`profile_packet_sequence_state.cc` 有 `alloc_delta` 和 `free_delta`。`heap_profile_allocation.heap_name` 在 v57.2 與 v58.2 都在。所以 v57.2 對 v58.2 的版本差,在設定欄位與表名上我沒查到衝突。

### F1 第二段 heapprofd 擺在流程哪裡沒定義,擺錯會弄壞既有的 pid 判定與 exits 判定
severity: major
blocking: 是
引句:「收集腳本在既有量測之後另跑一段 N 輪、只錄 heapprofd」
file: `scripts/templates/android-stability-collect.sh:478-512`、`scripts/lumos:40098-40102`

1. **pids 長度被寫死為 3。** `_macrobench_stab_pids` 要求 `len(vals) == 3`。第二段如果順手 `pids.append(pidof(pkg))`,變成 4 個,所有需要完整 N 輪的檢查(`native_unreachable`、`java_growth`、`instances`、`peak_vitals`、`frozen`)都會被判成「pid 有讀不到的」而跳過。spec 沒說第二段要不要記 pid,也沒說 `no_startup` 接的是不是同一個行程。
2. **擺放位置決定既有數字會不會被污染。** spec 只寫「既有量測之後」。`measure()` 在 `u_after`(第 495 行)、`nh_after`、Java 後快照、`read_exits`(第 498 行)之後才結束。
   - 第二段若插在 `read_exits` 之前,heapprofd 拖慢 App 造成的 ANR 或 LMK 會進 `exits.new`。這會讓 `exits` 判定沒過,而且是由被量對象以外的東西造成的。
   - 這直接推翻 d1「既有數字不受影響」和 S4「判定不變」的前提。
   - 第二段若插在 `read_exits` 之後,崩潰又無人記錄。
3. 照字面實作,兩種擺法都有洞。應該寫死位置,並寫明第二段的 pid、驅動結果和 exits 要不要納入既有的 `driver`、`pids`、`exits` 欄位。

### F2 錄製時長寫死 120 秒,跟既有的 max_record_s 機制不一致,N 稍大就整段作廢
severity: major
blocking: 是
引句:「duration_ms: 120000」
file: `scripts/templates/android-stability-collect.sh:336-350`、`scripts/templates/android-stability-record.pbtxt`

1. 既有錄製用 `__DURATION_MS__`,由 `stability.max_record_s`(預設 600 秒)換入。spec 的 heapprofd 設定寫死 120000 毫秒。
2. `stop_record` 在量測結束時若 `perfetto_alive` 為 False,就回「錄製在 N 輪跑完前就到了上限」。第二段沿用這個邏輯時,N 輪只要超過 120 秒(實驗室 8 輪約十幾秒,真實專案每輪好幾秒、N 為 20 以上很常見),結果就是 heapprofd 永遠被丟棄。
3. 另有三個細節 spec 沒寫:
   - `max_record_s` 要不要管這一段。
   - 設定檔用佔位換入,還是在 .sh 內嵌。
   - `dump_interval_ms` 每秒一次時,N 輪若耗時 10 分鐘就有約 600 次傾印。
4. 緩衝區 `fill_policy: DISCARD` 且 64 MB。滿了丟新資料,尾端傾印消失,「最後一次傾印」變成中途某次。
5. heapprofd 的 `shmem_size_bytes` 預設 8 MiB。proto 註解寫明共享記憶體滿了又沒設 `block_client` 時「ending the trace」(https://github.com/google/perfetto/blob/v57.2/protos/perfetto/config/profiling/heapprofd_config.proto)。這會讓配置量大的真實 App 的數字提前停止成長。判法會把這種情況當成「停住」而不列,而且不會留下任何跳過原因。
6. spec〈實務隱患〉只講了取樣誤差,沒講這兩種靜默截斷。

### F3 裝置端錄製的收尾與命名全都假設只有一份,第二份錄製會撞名、中斷時漏收
severity: major
blocking: 是
引句:「錄檔直接放 run 目錄第一層、檔名 `heap-*.pftrace`」
file: `scripts/templates/android-stability-collect.sh:305-360,516-528`

1. `start_record` 的裝置端路徑固定為 `lumos-stability-{run_id}.pbtxt` 和 `.pftrace`。`stop_record` 拉回的本機檔名固定 `cycle.pftrace`。本機設定檔固定 `record.pbtxt`。第二份錄製若直接呼叫它們,會蓋掉第一份。
2. `state["rec"]` 只有一格。`cleanup` 只收 `state.get("rec")`。第二段錄製被中斷時,heapprofd 還掛在 App 上拖慢,裝置上的設定檔與追蹤檔也沒人收。
3. 既有測試 `t_android_memstab_collect_cleanup` 和 `t_android_memstab_collect_interrupt_windows` 守的就是「先登記、停完才移除」的順序。第二個 `state` 鍵要照同一順序,spec 完全沒提。
4. spec 說檔名是 `heap-*.pftrace`,那是 glob 樣式,不是檔名。實作者必須挑出一個確切名字(例如 `heap-native.pftrace`)。

### F4 產物逐檔清單要的是確切檔名,spec 給的是樣式;第二份設定檔也沒列
severity: minor
blocking: 否
引句:「並加進收集腳本開跑前「產物有沒有被 git 忽略」那份逐檔清單」
file: `scripts/templates/android-stability-collect.sh:28,398`

`ARTIFACTS` 是確切檔名元組,每個都用 `git check-ignore` 問一次。spec 沒寫確切名字,也沒提第二份本機設定檔(如 `record-heap.pbtxt`)要不要進清單。7 天自動刪的樣式 `heap-.*\.pftrace` 和 `reference.md` 的「保留」清單也要同步。

### F5 Skill 的 L0 往下條件從不引導到 L3,spec 只改 L3 內文,抓不到它自己的動機情境
severity: major
blocking: 是
引句:「skill lumos-android-evidence 的 L3 原生那段改成先看這份提示」
file: `skills/lumos-android-evidence/SKILL.md:69,140-152`

1. 這份計劃的動機是情境②:SDK 留著清單,`native_unreachable` 是 0。SKILL 步驟 8 的「往下條件」只看 `threshold_failures` 的 `check`。提示不進 `threshold_failures`(d2),所以這個情境永遠不會觸發進 L3。
2. L3 第 3 步以「`native_unreachable` 沒過」為前提。spec 只改 L3 內文,沒有任何一條會讓 agent 讀到提示。
3. skill 還需要定下提示的 JSON 欄位名稱、沒打開、跳過與有提示三種狀態怎麼寫進收據(`[GAP]` 或 `[INFERRED]`)。
4. `reference.md:98-120` 是設定欄位表與「driver 跑兩次」的說明,「保留」清單也列舉了產物檔名。spec 要改的檔沒有列 `reference.md`。

### F6 lumos 端的輸出位置、JSON 欄位與消毒都沒定義;現有判定路徑只在有門檻檔時才讀 stability
severity: major
blocking: 是
引句:「lumos 讀結果檔,線性增長的照增長量排序列成優化建議」
file: `scripts/lumos:40313,40255-40277,40292,39983-40000`、`scripts/templates/android-e2e-run.sh:481`

1. `_macrobench_mode` 呼叫 `_macrobench_judge_stability(thresholds, stab)`。內容全由門檻檔的 `check` 條目驅動。沒有 `check` 條目時回的是 `stability_unjudged`。提示若寫在這條路,沒門檻的專案永遠看不到。若獨立於門檻,要說在哪裡讀、在哪一份輸出(`--json` 與文字兩路,`_macrobench_without_results` 另有一條)。
2. e2e 的 `android-e2e-run.sh` 以 `--json` 呼叫 `lumos macrobench --stability`。提示欄位名和是否進 steps.json 沒定。
3. 函式名和 .so 路徑是裝置回來的字串(App 或第三方的符號)。現有做法是「印出前走 `_events_clean`」,`_macrobench_stab_detail` 也有 500 字上限。spec 的〈打算怎麼做〉第 4 步沒有要求消毒,也沒有列表長度上限。真實 App 的呼叫位置可能很多,而且輸出會被餵給 AI。
4. `pm.name` 是完整路徑(`/data/app/.../libfakesdk.so`)。spec 稱「所在 .so」,沒說要不要取 basename。
5. 結果檔的新段落若欄位型別不對(數字變字串、負數、缺鍵),要怎麼處理沒寫。現有檢查有 `_macrobench_stab_val` 擋負數與非數字,新段落應照辦。

### F7 結果檔那段的狀態字彙和「不是 profileable」怎麼偵測都沒定義
severity: major
blocking: 是
引句:「release 建置沒宣告 profileable 時錄不到,要列成跳過」
file: `scripts/lumos:40010-40019`、`scripts/templates/android-stability-collect.sh:116-117`

1. 現有來源狀態是 `ok`、`failed`、`unsupported`。`_macrobench_stab_src` 把非 ok 都說成「沒收到(狀態)」。spec 發明了「跳過」「沒打開」兩個詞,沒對應到任何一個狀態值。實作者要自己決定,lumos 端和測試會不一致。
2. 收集腳本沒有任何地方偵測 profileable。spec 在 S3 與〈前提〉要「不是 profileable 就不錄並列成跳過」,卻沒說怎麼偵測:`dumpsys package` 的旗標?看 heapprofd 錄出空檔?沒偵測的話,只能錄完才發現空 trace,這時候的原因要怎麼寫?這是照字面無法實作的條款。
3. 空檔判定可以參考 `heap_counts` 回傳 0 列時記 failed 的做法。spec 沒提。

### F8 條款與正文對「排序」「列出下限」「判法邊界」說法不同,漏掉的組合沒人負責
severity: major
blocking: 是
引句:「後半至少是前半的一半、結尾超過 1 MB 時」
file: `r1-snapshot.md` 第 71、90、126、150 行

1. **排序依據不同。** 第 71、126 行寫「照增長量排序」,S1 寫「照結尾未釋放量由大到小排」。「增長量」是前半加後半,還是結尾?
2. **列出下限的條件詞不同。** 第 90 行(判法)寫「只列結尾或增量超過 1 MB 的」,S1 寫「結尾超過 1 MB」。
3. **判法的分支沒補齊。** 判法寫:前半有增、後半至少一半 → 線性增長;結尾還留著、後半沒跟著漲 → 停住;其他 → 不增長。
   - 「前半沒漲、後半才漲」(暖機後晚點才開始漏)被歸到「其他→不增長」,S1 和 S2 都沒覆蓋這個組合。
   - 後半增量比前半的一半少但仍為正的情況,屬於哪一類也沒條款。
4. **傾印次數的下限沒定義。** 「中間那次傾印」在傾印次數為偶數、少於 3 次(N 極小或錄製提早結束)時沒定義。
5. 條款全是 `[test:待定]`,這些分支沒有人負責測。

### F9 查詢輸出的 CSV 解析和查詢複雜度
severity: minor
blocking: 否
引句:「select d.ts, s.site, sum(s.size) as unreleased」
file: `scripts/templates/android-stability-collect.sh:252-262`

1. 現有 `heap_counts` 用 `line.split(",")` 解 trace_processor 的 CSV 輸出。這份查詢輸出 `d.ts, s.site, unreleased` 三欄,`s.site` 是 `函式 @ 路徑`,C++ 簽名常帶逗號和引號,同一個切法會把欄位切錯。建議由 SQL 先把前後半的增量算好,輸出固定欄位。
2. `dumps d join site s on s.ts <= d.ts group by d.ts, s.site` 是傾印數乘以列數的連接。N 輪若有幾百次傾印,耗時是平方級。spec 的「效能與記憶體」沒說上限,`T_LONG` 是 1800 秒。

### F10 E2E 的記憶體設定指紋會因為新鍵而變,舊的查證紀錄整批作廢
severity: minor
blocking: 否
引句:「設定加一個選填布林鍵 `native_growth`(沒寫等於 false)」
file: `scripts/lumos:40747`

指紋 `memory-config` 取整份 `stability` 與 `stability_scenarios` 的 JSON 雜湊。專案把 `native_growth` 寫進設定,就等於改了記憶體設定,既有「通過」的查證紀錄失效,推送前要重跑整套(`scripts/lumos:41568` 的「記憶體設定跟分岔點不一樣」)。這不是 bug,但 spec〈實務隱患〉的「遷移」和「守衛面」都沒提。

### F11 lands_in 與要改的檔的「家」不齊;三個既有筆記的敘述會被這個功能改掉
severity: major
blocking: 是
引句:「收集腳本拿掉 heapprofd 那段錄製與結果檔欄位,lumos 拿掉提示的輸出」
file: `docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:8-11`、`docs/lumos-toolchain-knowledge/Systems/android-e2e-acceptance.md:8-10`

1. frontmatter 的 `lands_in` 只列 `Systems/android-stability-collector`。專案鐵則要求每支改到的程式檔先有家。改動會落在:
   - `scripts/lumos`:家是 `macrobenchmark-adapter` 和 `android-e2e-acceptance`(`E2E_SCENARIO_KEYS` 在這裡)。
   - `skills/lumos-android-evidence/SKILL.md`、`reference.md`。
   - 若新增 `.pbtxt` 或 `.sql`:家是 collector。
2. 新增的範本檔還要登記進 `scripts/lumos:31976-31982` 的 `_VENDORED_TREE_FILES`,測試清單 `scripts/test_lumos.py:22368` 也要補;不登記,`lumos update` 不會把它發到消費專案。spec 沒說設定檔與查詢是放新檔還是內嵌。
3. 三處既有敘述被改動,但沒列在 spec 要更新的清單裡:
   - `Systems/android-stability-collector` 第一條 WHY 的流程順序。
   - `Projects/Android記憶體與穩定性驗收_計劃` 第 25 行「代價:… 抓不到,只剩 Native Heap 前後數字當線索」,以及第 71–73 行流程與 S27 的欄位。
   - `reference.md` 的「driver 跑兩次」和「保留」。
4. 補充:派工附註說會談目錄「還沒有這篇」,但本 repo 工作樹裡 `Systems/android-stability-collector.md` 已存在,也有對應 `about_code`。落點本身是對的。

### F12 與舊版 lumos 的相容和新舊交替
severity: minor
blocking: 否
引句:「型別照 `strictmode` 的寫法驗(不是 true 或 false 就回 2 擋下)」
file: `scripts/lumos:40493-40495`

專案設定先寫了 `native_growth`、但 lumos 還沒更新時,`_e2e_scenarios_err` 會回「不認得的欄位」並擋下 `--check-config`。反方向(新 lumos 讀沒有該段的舊結果檔)要確保不報錯。spec 的〈回退〉只講程式拿掉,沒講設定檔裡已寫入的 `native_growth` 在回退後會變成擋下全部驗收的錯誤。

## 逐節結論
- frontmatter、決策、〈白話〉與 PRIOR-ART:已讀,無 finding。版本與欄位宣稱屬實,v57.2 對 v58.2 在表名與設定鍵上無衝突,REVISIT 已涵蓋版本差。
- 〈實驗室實測〉:已讀。F9 的查詢性質與 F2 的緩衝區都出在這一節的設定與 SQL。
- 〈打算怎麼做〉第 1 步(鍵名與驗法):核對屬實,「照 strictmode 驗」可行。鍵名 `native_growth` 在 stability 段整套打開,與 `stability_scenarios` 可蓋過成 false 是一致的,沒有問題。
- 〈打算怎麼做〉第 2–5 步:F1、F3、F4、F5、F6、F7。
- 〈跟舊否決的差別〉:已讀,無 finding。三條引用的否決在對應計劃中都存在。
- 〈實務隱患〉:各類逐項見下一節。
- 〈條款〉:F8。
- 〈回退〉:F12。

## 實務隱患逐類
- **併發**:裝置單鎖不變;第二段 heapprofd 只能接當時存在的行程。App 在第一段結束時崩潰或被重啟,第二段 `no_startup` 接不到或接到新行程。spec 沒處理(F1)。
- **效能與資源**:拖慢驗收時間(spec 已列 REVISIT)。另外有錄製時長(F2)、緩衝區溢出(F2)、查詢平方級(F9)。
- **回滾**:F12 與〈回退〉缺設定檔那一半。
- **遷移**:F10、F12。
- **已排除的四類**:
  - 金流:站得住。
  - 對外送出:站得住,錄檔留本機。但提示文字會經 lumos 輸出餵給 AI,與現有 `_events_clean` 慣例相接,見 F6。
  - 不可逆:站得住。
  - 守衛面:「不改任何判定」這句,在 F1 描述的擺放位置下站不住。heapprofd 造成的 ANR 或 LMK 可能進入 `exits` 判定,e2e 指紋也會變(F10)。

## 圖譜固定席逐條判
- `Systems/android-stability-collector`:
  - 影響:會牽動它的流程順序 WHY、清理 WHY、git 忽略清單 WHY 與 7 天清理 WHY。只要依 F3、F4 實作並更新該筆記,不會破壞它宣稱的行為。
  - 不影響:「先掃原生再錄快照」這條,因為第二段在其後。
  - 未驗證:我沒有逐條核對它所列的 `[test:]` 名稱在新流程下是否仍綠。
- `Projects/Android記憶體與穩定性驗收_計劃`:
  - 「Native Heap 只回報」的否決不被破壞,因為新判法按呼叫位置看,不是看總量。
  - 第 25 行的「代價」句與 S27 的結果檔欄位要同步改。
- `Projects/Android逐層診斷_計劃`:d4 把「每次都錄」的否決照做了,不破壞。但它的 L0 往下條件(F5)沒有被這份計劃改到。
- `Verification/2026-10-24_Android記憶體與穩定性實驗室驗收`:歷史紀錄,不影響。

總結:整份最高嚴重度為 major,blocking 共 8 條(F1、F2、F3、F5、F6、F7、F8、F11)
