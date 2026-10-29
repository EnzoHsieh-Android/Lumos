severity: major

## 四問

**1. 分層與依賴方向:大致對齊,有一處宣稱與做法對不上。**
- 收集腳本在主機端排順序、用 adb 與 trace_processor 縮減資料,寫進 stability.json。lumos 讀結果檔並分類。skill 寫往下條件。這跟鄰居一樣。
  - 對照:`scripts/templates/android-stability-collect.sh:460-468`(`heap_result` 只縮減不判定)和 `scripts/lumos:40024-40035`(判定在 lumos)。
  - 設定由 lumos 驗,收集腳本不自驗,這點也一樣(Systems/android-stability-collector 的 WHY「設定與門檻檔的格式規則只該有 lumos 那一份」)。
  - 沒有跨層直呼。收集腳本沒有 import lumos,仍只走 `--check-config`(`collect.sh:112-114`)。
- 不對齊一處:〈判法〉標題寫「由 lumos 判」,但第 1、2 條(跳過配置器、挑三個時間點)實際在收集腳本裡做。見 F7。

**2. 命名與錯誤處理:大致對齊,有若干 minor。**
- 對齊的部分:
  - 段名 `native_growth` 是 snake_case,跟 `native_heap_kb`、`cycle_trace` 同形。
  - 狀態只用 ok、failed、unsupported 加 reason,沿用 `src()`(`collect.sh:441`)。
  - 固定鍵、空清單的形狀照 `low_iterations`(`scripts/lumos:40312`)。
  - 清單值是情境名字串,跟 `e2e.features` 的 cases.stability 同形(`scripts/lumos:40533-40535`)。
  - 擋下用回 2 的路徑。
- 不對齊的部分見 F4、F5、F6、F8。

**3. 第二種做法:有一條 major 疑似,其餘沿用屬實。**
- 沿用屬實的部分(開兩邊的碼對照過):
  - `start_record`、`stop_record`、`state["rec"]` 槽:`collect.sh:305-366`、`measure` 的 `del state["rec"]`(約 `collect.sh:493`)。
  - ARTIFACTS 與 7 天清理的 `heap-.*\.pftrace` 樣式:`collect.sh:28`、`collect.sh:148`。
  - `test_data` 判法:`collect.sh:387`。
  - 同一個 `TP` 環境變數:`collect.sh:21`。
  - `abort_record` 清理:`collect.sh:516-531`。
- 疑似第二種做法:Perfetto 查詢怎麼放,見 F1。
- 兩個 minor:`csv` 解析見 F2,`start_record`、`stop_record` 的參數不夠見 F3。

**4. 落點:合理,有一處漏寫。**
- Systems/android-stability-collector 現在 56 行,管 4 支檔,責任是「收集腳本、兩支查詢範本、錄製設定」。新 pbtxt 和第二段都落在它的責任範圍內。
- Systems/macrobenchmark-adapter 現在 66 行,about_code 有 `scripts/lumos`,責任含「讀 stability.json 判記憶體與穩定性」,並且記著 `_VENDORED_TREE_FILES` 的 PITFALL。提示的驗證與輸出落這裡合理,不必另開一篇。
- 漏寫的部分見 F8。

### F1 ⚠ 新查詢沒有登記成範本檔,內嵌的話是第二種寫法
severity: major
blocking: 是
引句:「收集腳本用跟第一段同一個 TP 查」
file: `scripts/templates/android-stability-collect.sh:252`
file: `scripts/templates/android-stability-collect.sh:290`
1. 既有的兩個 trace_processor 查詢都是範本檔。`android-heap-classes.sql`、`android-stability-cycle.sql` 用 `open(os.path.join(here, "….sql"))` 讀,換掉 `__PROCESS__` 後寫暫存檔,再用 `run([TP, trace, "-q", f.name])` 跑。Systems/android-stability-collector 也寫「兩支查詢都只用標準 SQLite 語法,測試用 Python 內建 sqlite」。
2. 這份 spec 第 4 步要做三段查詢(取傾印時間、算三個時間點的累計、取祖先框架),中間夾 Python 處理。但第 7 步和 r1 紀錄只把新的 pbtxt 列為新範本檔、登記進 `_VENDORED_TREE_FILES`,沒有任何新 `.sql` 範本。查詢只寫在 spec 的 markdown 實驗區塊裡。
3. r1 自己的理由是「內嵌在收集腳本會是第二種寫法」,所以 pbtxt 另開範本。同一個理由套在 SQL 上,spec 沒答。接手的人要猜:SQL 是內嵌字串,還是範本檔。範本檔的話,`_VENDORED_TREE_FILES` 和 about_code 沒登記就會讓守衛測試紅。
4. 實驗查詢用 `create perfetto table`,不是標準 SQLite。「測試用 sqlite3 驗查詢」那條既有做法套不上,spec 也沒說測試怎麼驗。
5. ⚠ 交編排者:spec 沒明說 SQL 放哪裡,我是依「新檔只列 pbtxt」推定它內嵌。若編排者確認新增了 `.sql` 範本,這條降為 minor(只缺登記)。

### F2 輸出解析另寫一套 csv 模組
severity: minor
blocking: 否
引句:「輸出用 csv 模組解析(函式簽名會帶逗號)」
file: `scripts/templates/android-stability-collect.sh:258-267`
1. 既有的 `heap_counts` 和 `cycle_numbers` 用 `split(",")` 加 `strip('"')`。`heap_counts` 遇到類別名帶逗號時,用 `",".join(cells[:-1])` 處理。
2. spec 改用 `csv` 模組,接手的人會有兩種解析寫法。csv 本身合理,但 spec 沒說要不要順手把 `heap_counts` 的拼接也換掉。

### F3 `start_record`、`stop_record` 加兩個參數不夠
severity: minor
blocking: 否
引句:「加兩個參數:設定範本、檔名後綴」
file: `scripts/templates/android-stability-collect.sh:305-312`
file: `scripts/templates/android-stability-collect.sh:361`
1. `stop_record` 把拉回的本機檔名寫死成 `cycle.pftrace`(第 361 行)。spec 要的是 `heap-native.pftrace`,不是 `cycle` 加後綴,所以「檔名後綴」換不出這個名字。
2. `stop_record` 的原因字串「錄製在 N 輪跑完前就到了上限」(第 349 行)也是量測段專用的措辭。
3. 實作時要多改本機檔名這個參數,或在 `stop_record` 內另做分支。spec 該把參數寫成「設定範本、遠端檔名後綴、本機追蹤檔名、本機設定檔名」。

### F4 設定鍵驗證的落點跟鄰居的簽名對不上
severity: minor
blocking: 否
引句:「lumos 在 `_macrobench_stab_optional_err` 驗」
file: `scripts/lumos:39557`
file: `scripts/lumos:39475-39483`
file: `scripts/lumos:40533-40535`
1. `_macrobench_stab_optional_err(st)` 只收 stability 段。它驗的全是單欄位型別(test_data、strictmode、category、max_record_s、adb_serial、mapping)。
2. 「名字對得到 `stability_scenarios`」是跨欄位檢查。鄰居把這種檢查放在拿得到 raw 或 `scen=` 的地方:`_macrobench_stab_top_err` 和 `_e2e_case_*`。
3. spec 的寫法要改簽名,或讓 `_macrobench_stab_optional_err` 去取 `stability_scenarios`。這會讓同一個函式一半單欄位、一半跨欄位,接手的人要猜該放哪一層。

### F5 "default" 變成新的保留字,沒擋同名情境
severity: minor
blocking: 否
引句:「代表沒指定情境的那一段」
file: `scripts/lumos:40488`
file: `scripts/templates/android-stability-collect.sh:121-130`
1. 既有的「沒指定情境」是 `LUMOS_STABILITY_SCENARIO` 沒設、直接用 stability 段本身。它沒有名字。
2. spec 新增 `"default"` 這個虛擬名字。但 `_e2e_scenarios_err` 的情境名樣式(英數字、底線、連字號)允許使用者自己命名 `default`。
3. 使用者若有名為 `default` 的情境,`native_growth: ["default"]` 會同時指兩個東西。spec 沒說要擋,也沒說誰優先。

### F6 錄不到的原因和壞行不會讓使用者看到
severity: minor
blocking: 否
引句:「lumos 應不採用那個呼叫位置」
file: `scripts/lumos:40010-40016`
file: `scripts/lumos:40250-40252`
file: `scripts/lumos:40030-40033`
1. 鄰居的做法是:來源不是 ok 就回 `(None, 原因)`,印成 `[沒判] … 原因`;數字缺、非有限數或負數時整條列「沒判」並寫原因。使用者永遠看得到「為什麼沒判」。
2. spec 的 S10 是靜默丟掉那一列。S7、第 6 步也只說「不列任何呼叫位置」和「沒東西時是空清單」。`native_growth` 段是 failed 或 unsupported 時,lumos 要不要印出原因沒寫。
3. 固定鍵照 `low_iterations` 是空清單的形狀,沒有地方放 status 和 reason。使用者無法分辨「沒增長」和「沒錄到」。這樣花一段量測時間、結果卻看不出原因,跟 `threshold_skipped` 附 reason 的做法不一樣。

### F7 〈判法〉標題說由 lumos 判,第 1、2 條實際在收集腳本做
severity: minor
blocking: 否
引句:「由 lumos 判(收集腳本只交數字,見〈打算怎麼做〉第 4、5 步):」
file: `scripts/templates/android-stability-collect.sh:460-468`
1. 鄰居的收集腳本只做縮減,不含領域規則。`heap_result` 只做保留有變的類別。
2. 這份 spec 的第 5 步要收集腳本存「每個呼叫位置的函式、所在 .so、呼叫者、有沒有符號、三個時間點的未釋放量」。要產生這些,收集腳本得自己跳過配置器清單(判法第 1 條)並挑時間點(第 2 條)。
3. 所以配置器清單和「沒有符號」的標記在收集腳本裡,S3 測的也是收集腳本。標題卻說由 lumos 判。接手的人不知道該改清單時去哪一支檔。

### F8 新 pbtxt 沒說進誰的 about_code,結果檔欄位名沒定
severity: minor
blocking: 否
引句:「設定範本另開 `android-stability-heapprofd.pbtxt`」
file: `docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md:8-13`
1. 鐵則 5 要求每支程式檔有家。spec 登記了 `_VENDORED_TREE_FILES`,但沒說 `android-stability-heapprofd.pbtxt`(或 F1 的 SQL 範本)要加進 Systems/android-stability-collector 的 about_code。該篇的 responsibility 寫「兩支查詢範本、錄製設定」,現在會變成兩份錄製設定,字句也要改。
2. 第 5 步用中文描述欄位(傾印數、三個時間點、開頭、中間、結尾),沒給結果檔的英文鍵名。鄰居的 before/after 是兩點,這裡有三點,不能直接照抄。命名要不要跟 `before`、`after` 對齊(例如 start、mid、end),spec 沒定。

不對齊共 8 條,其中 major 1 條
