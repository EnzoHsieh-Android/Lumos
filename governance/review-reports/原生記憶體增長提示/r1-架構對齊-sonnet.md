severity: major

**注意**:`native-mem-growth` 工作樹裡的 `Projects/原生記憶體增長提示_計劃.md` 比 r1-snapshot 舊,我只用 r1-snapshot 的設計內容。

## 四問結論

**問 1 分層與依賴方向:不對齊(F1,另有 F2、F7)**
- 既有分工很一致。收集腳本只收原始數字,檔頭寫「不判過不過(判定在 lumos macrobench --stability)」(`scripts/templates/android-stability-collect.sh:5`)。
  - Java 增長只存前後兩份類別計數,`heap_result` 只做資料縮減(`:460-467`)。
  - 判增長的是 lumos 的 `_macrobench_stab_java_growth`(`scripts/lumos:40065` 起,位置依 `sed -n 40040,40135p` 輸出推估,前面還有 `_macrobench_stab_heap`)。
- 設計卻讓收集腳本在結果檔裡存「判法」(線性增長、停住、不增長),還用 1 MB 當列出下限。分類判定下放到了收集腳本。
- 其餘符合既有做法:
  - 判定在 lumos,不進 threshold_failures。
  - trace_processor 由收集腳本呼叫,結果寫進 stability.json。
  - lumos 不碰裝置。

**問 2 命名與錯誤處理:大致對齊,有 3 處未定(F3、F4,另見 F2)**
- 型別錯回 2 的寫法對齊 `strictmode`(`scripts/lumos:39564-39565`)。`native_growth` 也是 snake_case 選填布林鍵,命名不衝突。
- 狀態字樣與結果檔欄位名沒有照既有慣例寫(F4)。

**問 3 第二種做法:大致沒有,有 2 處沒定死(F2、F5)**
- 沿用的部分確實沿用:
  - `heap-*.pftrace` 的 7 天清理規則(`collect.sh:110-125`)。
  - `ARTIFACTS` 逐檔問 git check-ignore(`:28`、`:398`)。
  - `test_data` 閘(`:387`)。
  - 用裝置端 perfetto 加推送 pbtxt 設定錄製(`:281-296`),主機端用 `TP` 查詢(`:265-278`)。
  - Perfetto 版本沒釘,同既有做法。收集腳本只靠環境變數 `TP`;spec 的 REVISIT 也已自承(`r1-snapshot.md:77`)。
- 兩處有分叉風險:
  - 「只提醒」輸出管道沒指明走哪條(F2)。
  - 第二段錄製和既有錄製函式的關係沒說(F5)。
- skill L3 用 `heap_profile --heaps libc.malloc` 手動錄(`skills/lumos-android-evidence/SKILL.md:144`),spec 自動化則直接用 perfetto 加 pbtxt。這和收集腳本既有錄法一致,不算第二種做法。

**問 4 落點:部分合理(F7)**
- 收集腳本那一半寫進 `Systems/android-stability-collector` 合理:
  - 該篇 56 行,摘要約 31 條。
  - 管 4 支檔,責任是「在主機端排順序…收記憶體與穩定性資料」。
  - 新增的 heapprofd 錄製與結果欄位同屬這支腳本。
- lands_in 只列這一篇,漏了 lumos 那一半的家,新檔也沒說要掛到誰的 about_code。

### F1 收集腳本自己做分類判定,跨層
severity: major
blocking: 是
引句:「結果檔只存每個呼叫位置的數字(函式名、所在 .so、結尾未釋放、前半增、後半增、判法)」
file: `scripts/templates/android-stability-collect.sh:5`
1. spec 第 3 條讓收集腳本把「判法」(線性增長、停住、不增長)寫進結果檔。第 4 條又讓 lumos 只負責「照增長量排序列出」。分類(前半增、後半增至少一半)因此落在收集腳本。
2. 既有做法反過來:收集腳本存原始數字,分類在 lumos。
   - Java 增長:收集腳本存 before/after(`collect.sh:460-467`),lumos 的 `_macrobench_stab_java_growth` 判。
   - 判的函式表是 `MACROBENCH_CHECK_JUDGES`(`scripts/lumos:40158`)。
   - 結果檔形狀也由 lumos 驗(`_macrobench_stab_heap`,`:40040` 起)。
3. 接手的人要猜「改判法該改 sh 內嵌的 Python,還是改 lumos」,而且 lumos 這邊會變成只信任收集腳本給的分類字串。
4. 修法方向:收集腳本只存每個位置的各傾印時間點未釋放量,或前半增、後半增。「判法」字串與 1 MB 篩選改在 lumos 做。

### F2 「只提醒」輸出管道沒指明走哪一條
severity: minor
blocking: 否
引句:「lumos 讀結果檔,線性增長的照增長量排序列成優化建議」
file: `scripts/lumos:40312`
1. 既有「只提醒」有三條管道:
   - `threshold_skipped` 加 `_macrobench_print_thresholds` 印「(只提醒,不擋推送)」(`scripts/lumos:40237-40252`)。
   - `low_iterations` 欄位加獨立的印出函式(`:39808-39832`、`:40312`)。這一行還有註解「鍵固定」。
   - e2e 的 `notices`(`:40892-40945`)。
2. spec 說不進 threshold_failures,卻沒說是新欄位(照 `low_iterations` 的寫法)、塞進 `threshold_skipped`,還是進 e2e notices。
3. `lumos-android-evidence` 走 `--json`(`SKILL.md:69`)。spec 沒寫 JSON 鍵名,也沒寫 e2e 流程(`android-e2e-run.sh:481`)看不看得到。
4. ⚠ 交編排者:實作前要定管道。照 `low_iterations` 的形狀走最貼近既有做法。

### F3 情境覆蓋欄位清單混進一個開關
severity: minor
blocking: 否
引句:「寫在 `stability_scenarios` 的某個情境裡只開那個情境」
file: `scripts/lumos:40474`
1. `E2E_SCENARIO_KEYS` 只含工作負載欄位 `scenario`、`driver`、`warmup`、`cycles`。lumos 以 `[2:]` 當整數驗(`:40491`)。
2. 既有 WHY 寫明情境以外的設定(套件、測試資料、StrictMode)沿用 stability 段(`docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md:47`)。`strictmode` 與 `test_data` 都不能按情境覆蓋。
3. `native_growth` 是第一個能按情境覆蓋的「開關」。spec 自己已承認要另外驗布林,不能接在清單尾端,而且 `[2:]` 的假設會破。
4. 同一個鍵可寫兩處,接手的人要猜「情境沒寫時是否繼承 stability 段的值」。spec 只寫了「沒寫等於 false」。

### F4 狀態字樣和結果欄位名沒對齊既有詞彙
severity: minor
blocking: 否
引句:「沒打開的情境不錄、結果檔那一段寫成沒打開」
file: `scripts/templates/android-stability-collect.sh:376`
1. 既有來源狀態只有 `ok`、`failed`、`unsupported` 三種,附 `reason`(`collect.sh:376`、`:448`)。
   - `strictmode` 沒宣告就寫 `{"status":"unsupported","reason":"設定沒宣告 strictmode"}`(`:447-448`)。
   - Java 快照沒宣告測試資料也是 `unsupported`(`:462`)。
2. spec 用「跳過」與「沒打開」兩個新字樣,沒說是新增 status 值,還是沿用 `unsupported`。
3. lumos 的 `_macrobench_stab_src`(`scripts/lumos:40010-40016`)把任何非 ok 都印成「沒收到(status)」。新字樣會原樣漏進輸出。
4. 結果檔那一段的鍵名沒定。既有鍵是英文 snake_case:`unreachable`、`heap`、`cycle_trace`、`native_heap_kb`。spec 欄位只寫了中文描述。

### F5 第二段錄製和既有錄製函式的關係沒說
severity: minor
blocking: 否
引句:「收集腳本在既有量測之後另跑一段 N 輪、只錄 heapprofd(d1)」
file: `scripts/templates/android-stability-collect.sh:281`
1. 既有錄製是 `start_record` 與 `stop_record` 一組(`:281-296`、`:335-352`)。
   - 設定放在範本檔 `android-stability-record.pbtxt`,用 `__PROCESS__` 與 `__DURATION_MS__` 佔位。
   - 追蹤檔硬寫成 `cycle.pftrace`。
   - 登記在單一 `state["rec"]`,`cleanup` 只收這一個(`:516-528`)。
2. spec 的 heapprofd 設定直接內嵌在計劃裡,`duration_ms: 120000` 寫死,和 `max_record_s` 不是同一條。
3. spec 沒說要不要新增 pbtxt 範本檔、`start_record` 與 `stop_record` 是否參數化、第二段錄製被中斷時 `state` 怎麼登記。
4. ⚠ 實作若另寫一套 start、stop、登記、cleanup,就是第二種做法,屆時可升 major。

### F6 判法數字寫死,不走人裁的門檻檔
severity: minor
blocking: 否
引句:「結尾超過 1 MB 時,提示應列出它(函式、所在 .so、結尾未釋放、兩半增量),照結尾未釋放量由大到小排」
file: `scripts/lumos:40054`
1. 既有 check 的數字多放在門檻檔的欄位,附預設值,例如 `min_per_cycle`、`exclude_prefixes`、`max_bytes`、`max_block_ms`(`MACROBENCH_CHECK_FIELDS`)。
2. 1 MB 與「後半至少前半的一半」寫死在程式。
3. 因為永遠只提醒(d2),這點影響小,所以只列 minor。接手的人要猜「調數字該改程式還是門檻檔」。

### F7 lands_in 只列收集腳本那一篇,漏了 lumos 與 skill 那一半的家
severity: minor
blocking: 否
引句:「Systems/android-stability-collector」
file: `docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md:6`
1. 收集腳本、pbtxt 與 sql 範本是該篇的 `about_code`(`:8-12`),寫進它合理。
2. spec 動到的其他檔,家在別篇:
   - `scripts/lumos` 的提示輸出和設定驗證,家是 `Systems/macrobenchmark-adapter`(66 行,`about_code` 含 `scripts/lumos`)。
   - `E2E_SCENARIO_KEYS`,另屬 `Systems/android-e2e-acceptance`(`about_code` 含 `scripts/lumos` 與 `android-e2e-run.sh`)。
3. 若新增 pbtxt 或 sql 範本,要補進 collector 的 `about_code`。若「判法」留在收集腳本(F1),該篇 responsibility 裡「不負責判過不過」也要改。

不對齊共 7 條,其中 major 1 條
