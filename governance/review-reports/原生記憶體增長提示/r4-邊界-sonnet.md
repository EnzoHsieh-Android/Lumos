severity: major

審稿範圍:我逐節讀完 r4-snapshot.md,並對照 `scripts/templates/android-stability-collect.sh`、`android-stability-cycle.sql`、`android-e2e-run.sh`、`scripts/lumos` 與本機 trace_processor v58.2 驗過。Perfetto v57.2 原始碼只讀了 `profile_packet_sequence_state.cc`、`unwinding.cc`、`heapprofd_producer.cc` 三支。臨時目錄是 `/tmp/lumos-seat-work/原生記憶體增長提示/邊界-sonnet/`。

先講一句人話:這份 spec 把排行縮得很乾淨,問題都出在極端輸入的交界。第一是 trace_processor 印出的 csv 本身就壞了,第二是第二段跑太久時,第一段已量好的結果會被整份丟掉。

## 各節

- frontmatter、pending_questions、d1 到 d5:已讀,無 finding。
- 白話段與 PRIOR-ART:有 F2(單一 name 欄)和 F11(不需要的 continuous_dump)。其餘宣稱我對 v57.2 查過,一致。
  - delta 加總成未釋放量:對,見 `profile_packet_sequence_state.cc`。
  - 預設 heap 是 libc.malloc:對,見 `heapprofd_producer.cc`。
  - 停錄時會補最後一次傾印:對,走 socket 斷線路徑,stop_timeout_ms 到了就不補。
  - `no_startup` 要 Android 11 以上:⚠ 我讀到的原始碼沒寫最低版本,查不到。
- RETIRE-IF 與 REVISIT:已讀,無 finding。
- 實驗室實測與兩段查詢:已讀,無 finding。實驗查詢是 `create perfetto table` 多語句,正式版改成單語句,這點在 F7 處理。
- 排行怎麼算:有 F1、F2、F5、F6、F8、F9。
- 打算怎麼做第 1 到 3 步:有 F3、F4。
- 打算怎麼做第 4 到 7 步:有 F1、F7。
- 跟舊否決的差別:已讀,無 finding。
- 實務隱患:「中斷」那條有 F4,「時間」那條有 F3。
- 條款(草案):S4 與 S11 有 F3、F6、F9。其餘的引用我逐條核對,都存在。
- 回退與審計修正紀錄:已讀,無 finding。

### F1 csv.reader 解不了 trace_processor 的輸出,「引號」沒有被解決
severity: major
blocking: 是
引句:「「讀範本、換佔位、寫暫存檔、跑 TP、解析成列」抽成一支共用函式,裡面用 csv.reader(函式簽名會帶逗號與引號)」
file: `scripts/templates/android-stability-collect.sh:262`(現行 heap_counts 用逗號切、去掉引號)

1. spec 把 csv.reader 當成「函式簽名帶逗號與引號」的解法,但 trace_processor `-q` 的 csv 輸出根本不跳脫引號。
   - 我用本機 v58.2 實測 `select 'a"b,c'`,輸出是 `"a"b,c"`。
   - 字串一律加雙引號,數字不加,NULL 印成 `[NULL]`,字串裡的換行原樣輸出。
2. 實測結果:
   - `csv.reader(out.splitlines())` 把 `"a"b,c"` 解成 `['ab','c"']`,多出一欄。
   - `"operator()(int, a")"` 這種含引號的名字,欄位數一樣會錯位。
   - 含換行的欄位被 `splitlines` 先切成兩列,`['l1l2']` 被併成一格。
3. 照字面實作者會做出兩個東西:
   - 函式名帶 `"` 時(例如 `operator""_x`),每個欄位錯位,`retained` 讀成別的欄。
   - 以固定欄位位置取 func、so、caller、retained 的 sites 解析,會靜默錯位而不報錯。
4. 應該是:
   - SQL 端用 `replace(x,'"','')` 和 `replace(x,char(10),' ')` 先清掉引號與換行,再輸出。
   - 或每個文字欄位改輸出 hex、再由 Python 解碼。
   - spec 要寫明解析函式吃的是 trace_processor 這種「不跳脫」的方言,並加一條含引號、逗號、換行的名字測試。S20 現在只守「走同一支函式」,守不到這點。

### F2 `stack_profile_frame` 只有一個 name 欄,「demangle 名」與「mangle 名」兩個判準沒說比對哪一欄
severity: minor
blocking: 否
引句:「或 demangle 名以「operator new」開頭、mangle 名以 _Znw 或 _Zna 開頭」
file: `profile_packet_sequence_state.cc`(https://raw.githubusercontent.com/google/perfetto/v57.2/src/trace_processor/importers/proto/profile_packet_sequence_state.cc)

1. 我查本機 TP 的欄位:`stack_profile_frame` 有 id、name、mapping、rel_pc、symbol_set_id、deobfuscated_name、type,沒有獨立的 mangled name 欄。
2. v57.2 的 AddFrame 原樣收進 producer 送來的字串,TP 不 demangle。
3. producer 實際送的是已 demangle 還是 mangled,⚠ 我查不到(`unwinding.cc` 只呼叫 libunwindstack)。
4. spec 沒說兩種前綴都對同一個 name 欄比。
   - 照字面實作者可能只寫其中一條,或去找不存在的 mangled 欄。
   - 應寫明:name 一欄同時比兩種前綴,測試兩種形式各一筆。

### F3 e2e 單步逾時(3600 秒)會讓第一段已量好的結果被丟棄,跟 S4 與 d2 衝突
severity: major
blocking: 是
引句:「e2e 的收集步驟單步上限是 3600 秒,長情境打開前先估一次。」
file: `scripts/templates/android-e2e-run.sh:411`、`scripts/templates/android-e2e-run.sh:477-484`

1. `step()` 逾時時回傳 `None`。呼叫端遇到 `None` 會 `device_stuck=True` 然後 `break`,後面的 `stability_judge` 與其餘情境、效能整批都不跑。
2. 收集步驟單步 3600 秒裡,現在要塞第一段加第二段,第二段又多一次暖機和量測。驅動單次上限 `LUMOS_STABILITY_LONG_TIMEOUT` 是 1800 秒,一次收集最多 2×1800 加第二段 2×1800。
3. 具體例:一個一輪要 5 分鐘的情境,W+N 共 10 輪是 50 分鐘。打開 native_retained 後,第二段在第一段之上再跑 50 分鐘,整步超過 3600 秒。
   - 第一段 `stability.json` 已經寫好,但 e2e 把這步當逾時,不跑 judge。
   - 該情境與其後的情境、效能全記成沒判完。
   - 這等於「一項只提醒的功能,讓原本會判的記憶體判定消失」。
   - S4 的「被中斷時判定不變」和 d2 的「不影響判定」都在這裡被破壞。
4. spec 只寫「長情境打開前先估一次」。這是人為估算,不是機械守衛。
   - 應改成:第二段有自己的總時間上限,超過就放棄第二段、寫 failed。
   - 並保證整步留給第一段的 judge 空間。
   - 或讓 e2e 對 native_retained 情境把 timeout 另算。
   - 逾時時 `run` 是否先送 TERM 讓 cleanup 跑,⚠ 我沒查到,逾時路徑的裝置清理未驗證。

### F4 中斷合約:腳本檔頭與擋下訊息仍寫「不寫結果檔」,spec 卻要求結果檔已存在
severity: major
blocking: 是
引句:「中斷:第二段被 Ctrl-C 或逾時打斷時,第一段的結果檔已經先寫好(native_retained 段是 failed「第二段沒跑完」),App 被停掉。」
file: `scripts/templates/android-stability-collect.sh:12-13`、`scripts/templates/android-stability-collect.sh:541-543`

1. 現行檔頭寫「被中斷都回 2 並印『擋下:』,不寫結果檔」。`main()` 的中斷訊息也印「收集被中斷,沒寫結果檔」並 `sys.exit(2)`。
2. spec 改成第二段中斷時結果檔已經在。
   - 它沒列要改檔頭、擋下訊息、`Systems/android-stability-collector` 的對應說法。
   - 沒說回傳碼是否仍為 2。
   - e2e 對 rc=2 且有檔的情況會照常跑 judge(`android-e2e-run.sh:481`),那份中斷的結果就被當完整一次收集來判。
3. 照字面實作會得到說謊的訊息,例如「沒寫結果檔」但檔其實存在。
4. 第一段中斷與第二段中斷也無法分辨:前者仍無檔,後者有檔,而 spec 的 S8 只談 cleanup。
   - 應明寫:
     - 第二段中斷時回傳碼與訊息怎麼說。
     - 檔頭與訊息要改。
     - 這份中斷時寫出的檔,在 e2e 要被判成「這次被中斷」,不是完整結果。
     - 補一條條款與測試。
5. cleanup 要「另外停 App」,但 `cleanup(state)` 目前拿不到套件名。spec 沒說 pkg 放進 state 的哪一格,實作者要自己猜。

### F5 apk 內嵌的 .so,mapping 名可能是 base.apk
severity: minor
blocking: 否
引句:「.so 只記檔名(SQLite 字串函式取最後一段)」

1. ⚠ 我無法離線驗證:extractNativeLibs=false 的現代 App,從 apk 直接載入的 .so 在 mapping name 裡是 `…/base.apk` 還是 `base.apk!libfoo.so`。這取決於 libunwindstack 怎麼命名,我沒找到來源。
2. 若是前者,「取最後一段」得到 `base.apk`。
   - 所有 App 內的 .so 都顯示成同一個名字,排行上看不出是哪支 SDK。
   - 「libc++_shared.so 全部框架都跳過」的比對對 apk 內的它也比不到。
3. 若是後者,取最後一段得到 `base.apk!libfoo.so`,不是 `libfoo.so`。
4. 實驗用的假 SDK 是從磁碟路徑載入,沒涵蓋這條路。
   - 建議列成 REVISIT,並用 extractNativeLibs=false 的建置重跑一遍。

### F6 零個呼叫位置的 ok 情況沒有規格
severity: minor
blocking: 否
引句:「[S1] 當某個呼叫位置的結束累計至少 1 MiB 時,排行應列出它」

1. 沒有任何呼叫位置過 1 MiB 時,狀態是 ok、`sites` 是空清單。
   - lumos 要印什麼?
   - S1 只規定「有的時候」怎麼印,「最上面一行寫明含快取與池」寫在 S1 裡,所以空清單時不確定要不要印。
2. 這是最常見的好結果(正常版),spec 沒說。照字面實作者可能什麼都不印,使用者分不出「跑過、沒有」與「根本沒跑」。
   - 應規定空清單時印一行「原生配置排行:沒有結束累計 ≥ 1 MiB 的呼叫位置」。
3. 邊界我順便核對了:
   - 剛好 1048576 位元組:「至少」,列出。S1 與 S2 一致。
   - 剛好 200 個:不裁。
   - 201 個:裁掉最小的一個。這兩個邊界是否有測試,spec 沒寫。

### F7 查詢要同時出排行、stats、「有沒有任何一列」,但「每次 TP 呼叫只跑一條回傳列的語句」沒說怎麼拆
severity: minor
blocking: 否
引句:「每次 TP 呼叫只跑一條回傳列的語句;跟第一段用同一個 TP」
file: `scripts/templates/android-stability-cycle.sql:36-43`(現行範本的形狀)

1. 檢查順序是「逾時 → stats → 沒有任何一列 → ok」。三項要三次 TP 呼叫,或一條語句用 UNION ALL 加第一欄標籤。
2. spec 沒選,也沒說哪個欄位區分排行列與 stats 列。
   - 現行 cycle 範本用第一欄 `"cycle"` 當鍵。
   - 若三次 TP 呼叫,重載同一份可能很大的追蹤檔三次,逾時預算(T_LONG)是每次還是合計,也沒寫。
3. 「沒有任何一列」與「沒有呼叫位置過 1 MiB」要分得開,需要一個獨立的 count。
4. 標準 SQLite 端:
   - `WITH RECURSIVE` 往上走 parent_id 寫得出來。
   - 取最後一段用 `substr(n, length(rtrim(n, replace(n,'/','')))+1)`,兩邊都跑得動。
   - 十六進位用 `printf('%x')`,兩邊都有。
   - 一個要注意的差別:實驗版用了 `create perfetto table`,TP 專有,正式版必須改回純 SQL。
   - 另外 `-q` 檔案裡多語句只印最後一條,所以不能偷渡。

### F8 「不同路徑的同名 .so 不會混在一起」與「.so 只記檔名」互相矛盾
severity: minor
blocking: 否
引句:「所以不同路徑的同名 .so 不會混在一起」

1. 鍵是(函式、.so 檔名、系統旗標)。兩個都在 App 目錄下、路徑不同但檔名相同的 .so(例如兩個 split 各帶一份 libfoo.so),系統旗標一樣,會被併成同一個呼叫位置。
2. 能分開的只有「一個在 /system、一個不在」。
3. 照字面實作會併。把句子改成「系統與非系統的同名 .so 不混」,或把鍵改成完整路徑。

### F9 並列排序在第 200 名與 lumos 前 20 名都沒有完整的決勝規則
severity: minor
blocking: 否
引句:「照結束累計降冪、函式名升冪、.so 升冪取前 200 個」

1. 鍵是三元組(函式、.so、系統旗標)。函式與 .so 都相同、只有系統旗標不同的兩項,在第 200 名邊界上順序不確定,同一份追蹤檔重跑可能列出不同的那一項。
2. lumos 端「由大到小最多印 20 個」沒寫並列規則。收集腳本排好順序的話,lumos 要保持原序還是重排,也沒說。
3. 各補一個末位決勝欄(系統旗標),並寫明 lumos 保持收集腳本的順序。

### F10 沒有符號、沒有 mapping 的組合名,規則有洞
severity: minor
blocking: 否
引句:「name 是 NULL 或空字串都當沒有符號,寫成「.so 檔名+0x相對位址」並標沒有符號;mapping 沒有名字時 .so 記成「?」、不是系統函式庫」

1. 函式名 NULL 且 mapping 也沒名字時,字面結果是 `?+0x…`。
   - `rel_pc` 也可能是 NULL,spec 沒說這時寫什麼。
   - 這樣的呼叫位置函式名各不相同,不會被併成一格。
   - 另一個例子:ART 與 JIT 的框架沒有 mapping,可能一堆不同位址各自上榜,把前 200 名擠滿。
2. 超長函式名(模板展開動輒數 KB)與帶換行的名字:
   - lumos 端有 `_events_clean(…, 500)` 和 `_macrobench_stab_scrub`,印出是安全的。
   - 但收集腳本存的 `func` 沒有長度上限,200 項 × 數 KB 寫進結果檔。
   - 結果檔會變大,而且「沒有符號的 caller」同樣要有規則。
3. 補一條:rel_pc 為 NULL 時寫 `+0x?`,收集腳本端截長(例如 500 字元)後再存。

### F11 continuous_dump_config 對只用「最後累計」的排行沒有用處,還有多餘成本
severity: minor
blocking: 否
引句:「continuous_dump_config { dump_phase_ms: 1000 dump_interval_ms: 1000 } } } }」

1. d5 已經說排行只用停錄時一定會寫的最後累計,不受時間對齊影響。
2. 我查 `heapprofd_producer.cc`:`dump_interval_ms` 為 0 時只有停錄時那一次傾印。
3. 保留每秒傾印,會讓 N 很大、max_record_s 很長時 `heap_profile_allocation` 列數與追蹤檔大小跟著長,查詢變慢。這跟 spec 第 4 步自己擔心的效能是同一件事。
4. 另一個小邊界:`max_record_s` 小於 W+N 輪所需時間時,錄製到期自己結束,走 `stop_record` 的「到了上限」failed 路徑。這是正確的,但條款沒有單獨的例子。
5. 建議在「打算怎麼做」第 3 步的設定範本裡不放 continuous_dump_config,或寫明為什麼要留。

## 固定席逐篇判

- `Systems/android-stability-collector.md`:會被影響。
  - 它的負責範圍與說法要改:結果檔不再只有一次寫出,第二段中斷時結果檔已存在(F4)。
  - spec 的 `lands_in` 已列這篇,回寫時要同步改檔頭註解與擋下訊息。
  - 它的 WHY「同一個 run-id 已有結果檔就回 2」(第 38 行)仍然成立:第二段中斷後同一個 run-id 不能重用,行為一致。
- `Systems/macrobenchmark-adapter.md`:不影響其既有行為。
  - 這份只談效能基準比較與裝置換了不比,spec 沒碰。
  - 另一個原因:spec 只在 macrobench 結果的固定鍵加 `native_retained`,不改任何基準比較邏輯。
  - 但「固定鍵 + 只有 stability 的路徑也算」要在這篇的負責範圍補一句,不然這個鍵的家不明。
- `Systems/android-e2e-acceptance.md`:會被影響,見 F3 與 F4。
  - 單步逾時會把還能判的第一段整個吃掉。
  - 中斷時留下的結果檔,e2e 會當完整結果判。
  - 該篇的記憶體設定指紋也會因 `native_retained` 變動(spec 的「遷移」那條已承認)。
- `Projects/Android記憶體與穩定性驗收_計劃.md`:不破壞它的合約,但有兩處要同步改。
  - 第 25 行「Native Heap 前後兩個數字只回報」。
  - 第 31 行「用同一條驅動指令呼叫兩次」,打開時變成呼叫兩次再加第二段。
  - 它否決過「只看 Native Heap 趨勢」,這份看的是 heapprofd 按呼叫位置的最後累計,不是同一條,不衝突。
- `Projects/Android逐層診斷_計劃.md`:不影響其否決。
  - 它否決「每次都錄 Trace+CPU 取樣+記憶體」,這份用 d4(預設關、按情境開)繞開了,理由成立。
  - 唯一會變的是分層 WHY 要補「打開 native_retained 的情境在收集階段就錄 heapprofd」,spec 已寫。
- `Projects/原生記憶體增長判法_計劃.md`:不影響。
  - 這份縮範圍後,與它的分界是「排行只列最後累計」,spec 內的引用都存在。
  - 它的實驗要用每輪記號切窗,這份的設定範本若不放 continuous_dump(F11),將來那份要自己加,不衝突。

## 實務隱患鏡頭

- 併發:第二段的 heapprofd 與第一段已停的錄製不會同時存在(第一段從 state 拿掉才開第二段)。多個 e2e 情境依序跑,沒有並行。「同一行程已有別的 heapprofd 工作階段」已列在 stats 失敗清單。風險無,理由是流程循序。
- 效能:
  - 查詢用 callsite 層彙總,不做傾印數乘列數的連接,方向對。
  - `heap_profile_allocation` 很多列時,瓶頸在 F11 的每秒傾印和 WITH RECURSIVE 往上走。
  - 實際上要走到第一個非配置器,通常只有幾層。
  - 有「整條都是配置器」的長鏈時,要走到根,最差是深度 × callsite 數,沒給上限。
- 資源:
  - 追蹤檔 64 MiB 緩衝,拉回本機後留在 run 目錄,靠 7 天刪。
  - 結果檔 200 項函式名沒長度上限(F10)。
  - 逾時路徑的裝置清理(F3)。
- 回滾:spec 的「回退」逐項寫得完整。
  - 唯一缺口:舊版 lumos 讀到有第二段殘留的結果檔會忽略,沒問題。
  - 但 F4 的「中斷時留下的檔」在舊版 lumos 看起來像完整的正常結果,回滾後這份檔沒有標記。
- 遷移:指紋會變,spec 已寫。

總結:整份最高嚴重度為 major,blocking 共 3 條(F1、F3、F4)。
