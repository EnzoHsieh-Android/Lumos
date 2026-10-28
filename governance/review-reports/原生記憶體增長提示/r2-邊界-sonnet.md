severity: major

這份 spec 逐節讀完,對照 `native-mem-growth` repo 的程式碼查過。極端輸入的問題集中在判法的取樣點和幾處語意缺口。Perfetto 部分我抓了 v57.2 原始碼核對:
- https://raw.githubusercontent.com/google/perfetto/v57.2/protos/perfetto/config/profiling/heapprofd_config.proto
- https://raw.githubusercontent.com/google/perfetto/v57.2/src/profiling/memory/heapprofd_producer.cc

〈判法〉第 2 條的三個時間點是 spec 自己規定要用的做法,我照字面推算結果。

### F1 「開頭」不是收集腳本能算出來的,「一定有」不成立
severity: major
blocking: 是
引句:「驅動量測開始前的最後一次傾印(開頭;〈打算怎麼做〉第 3 步先等到第一次傾印才開始驅動,所以一定有)」
file: `scripts/templates/android-stability-collect.sh:485`

1. 問題一:〈判法〉第 2 條把「開頭」定義成「驅動開始前的最後一次傾印」。但驅動開始的時間點在主機端(`time.time()` 一類),傾印的 ts 在裝置的追蹤時鐘。spec 沒說兩邊怎麼對時,現有腳本也沒有裝置時鐘的讀取(只有 `date '+%m-%d %H:%M:%S.000'` 供 logcat 用)。照字面,實作者無法從追蹤檔裡找出「驅動開始前」是哪一筆。
2. 問題二:第 3 步說「等第一次傾印(dump_phase_ms 再加 1 秒)」。這是固定睡 2 秒,不是觀察到傾印。heapprofd 附掛慢、adb 抖動、裝置忙時,驅動開跑時還沒有任何傾印。這時「開頭」不存在,spec 沒定義。例:睡 2 秒,第一次傾印落在第 2.3 秒,驅動從第 2.0 秒開始,開頭 = 無。應該是:要嘛用 `/proc/uptime` 記驅動開始的裝置時刻,要嘛固定把第一次傾印當開頭,並明寫第一次傾印晚於驅動開始時的處理。
3. 問題三:「傾印少於 3 次」數的是全部傾印,包含驅動前的。例:3 次傾印裡有 2 次在驅動前,中間 = 開頭,前半增量恆為 0,後半 = 整段。判法退化成「整段 ≥ 1 MiB 就線性增長」,spec 沒擋這種情形。

### F2 三點取樣會把「開關配置、結尾剛好留著」誤判成線性增長
severity: major
blocking: 是
引句:「整段增量小於 1 MiB(1048576 位元組)→ 不增長;否則後半增量 ≥ 整段增量的三分之一 → 線性增長;其餘 → 停住」

1. 輸入:正常版的 2 MB 配置每輪開畫面配、關畫面還,在 0 與 2 MB 間來回(spec 的實驗表自己就有這一列)。
2. 照字面會得到:驅動剛好停在配置還留著的相位,結尾 = 2 MB、開頭 = 0,整段 = 2 MB ≥ 1 MiB。中間那次傾印若落在 0(關畫面中),後半 = 2 MB ≥ 2/3 MB,判成線性增長並列出。中間若落在 2 MB,後半 = 0,判成停住。誤報與否取決於相位,約一半機率。
3. 表中「正常版:不增長」只是剛好結尾落在 0。spec 沒寫相位假設,也沒說驅動一定結束在畫面全關的狀態。
4. 應該是:中間與結尾之外,加一條對所有傾印的單調條件,或取量測期間的最小值與最後值比較(只看不回落的量);或明寫驅動必須結束在配置全還的起點畫面,並在〈實務隱患〉列出這個前提。
5. 這與〈判法〉第 3 條「三類互斥、涵蓋全部」不衝突,但它顯示三點抽樣有盲區。「漲到一定量就停住的快取與物件池不報」這句承諾,對「週期性配置」的做不到。

### F3 `native_growth` 的名字檢查在 `_macrobench_stab_optional_err(st)` 裡做不到
severity: major
blocking: 是
引句:「lumos 在 `_macrobench_stab_optional_err` 驗:不是字串清單、或名字對不到情境 → 回 2 擋下」
file: `scripts/lumos:39557`、`scripts/lumos:39479`、`scripts/lumos:39542`

1. `_macrobench_stab_optional_err(st)` 只收 stability 段一個參數,呼叫鏈 `_macrobench_stab_top_err(raw)` → `_macrobench_stab_cfg_err(raw["stability"])` → `_macrobench_stab_optional_err(st)`。`stability_scenarios` 在 `raw` 裡,到不了這個函式。
2. 照字面,實作者寫不出「名字對不到情境」。要嘛改三層簽名,要嘛把檢查移到 `_macrobench_stab_top_err`,spec 兩者都沒選。
3. 還有一個語意洞:`stability_scenarios` 是 `None`(沒寫)時,`native_growth: ["checkout"]` 要擋、`["default"]` 要放。spec 沒寫。
4. 按功能跑的 `_e2e_scenarios_err` 在另一條路也會驗 `stability_scenarios`,不會替 `native_growth` 補查。

### F4 `--stability` 只有一條路徑在輸出新鍵,「照 low_iterations 的形狀」會漏掉只接 stability 的專案
severity: major
blocking: 是
引句:「照 `low_iterations` 的形狀:沒東西時是空清單,文字與 `--json` 都有」
file: `scripts/lumos:40312`、`scripts/lumos:40318`、`scripts/lumos:40253`

1. `low_iterations` 只在有 Macrobenchmark 結果目錄時才被填、被印:第 40318 行的 `_macrobench_low_iterations(current)` 在 `_macrobench_without_results` 的提前返回之後。
2. 只有 stability 段、沒有 `results_dirs` 的專案(`_macrobench_config` 明確允許)走 `_macrobench_without_results`,那裡不經 `_macrobench_print`,只印門檻。e2e 範本的 `--json --stability` 也走同一個出口。
3. 照字面「照 low_iterations 的形狀」實作,`native_growth` 在這類專案裡 `--json` 是 `null` 或根本沒有鍵,文字輸出沒有。而這類專案正是主要使用者。
4. 應該是:鍵放進 `res` 初始字典(與 `stability_unjudged` 同位置),兩條出口都帶,印的函式獨立於 `_macrobench_print`。

### F5 「Android 11 以下」與 `no_startup` 的最低版本矛盾,`android_sdk` 為 None 沒定義
severity: major
blocking: 是
引句:「裝置 Android 11 以下(只接已在跑的行程要 11 以上)→ unsupported「Android 版本不支援」」
file: `scripts/templates/android-stability-collect.sh:408`

1. 括號寫「要 11 以上」,正文寫「11 以下 → unsupported」,兩者互斥。上游 proto 寫 `no_startup`「Introduced in Android 11」,Android 11 本身是支援的。S6 同樣寫「Android 11 以下」。照字面實作成 `sdk <= 30`,Android 11 裝置就被錯擋;對的條件是 `sdk < 30`(Android 10 以下)。
2. `res["android_sdk"]` 在 `getprop` 讀不到時是 `None`(第 408 行)。Python 3 裡 `None <= 30` 會丟 `TypeError`,收集腳本整支崩,連既有結果檔都寫不出來。spec 沒說 None 要寫成 failed 還是 unsupported。S6、S7 都不在名單裡。

### F6 第二段的驅動失敗與暖機失敗,沒有定義對 `native_growth` 狀態的影響
severity: major
blocking: 是
引句:「第二段的 pid、驅動結果、前後結束紀錄寫在新段落裡,**不碰既有的 pids、exits、unreachable、native_heap_kb**」
file: `scripts/templates/android-stability-collect.sh:222`

1. `driver()` 失敗時回 `ok: False`(含 UI Automator 沒成功結束)。第二段的驅動失敗,spec 只說「驅動結果寫在新段落裡」。S7 的 failed 名單(傾印少於 3、0 次、stats 錯誤、逾時、App 結束、pid 不同)沒有「驅動失敗」。
2. 照字面,實作者可能對一次沒跑完的驅動照樣算增量,列出提示。例:暖機驅動回 1,量測驅動只跑了 2 輪,傾印 3 次,增量 ≥ 1 MiB,照列。應該是:任何一次驅動 `ok: False` 都寫 failed 並附 `why`,與第一段對 `driver.status` 的處理一致。
3. 第一段驅動已失敗、或第一段 `pids` 已出現 `None`(App 掛了)時,第二段還跑不跑,spec 也沒說。第二段開頭「停 App → 啟動」時,`pidof` 回 `None`(啟動失敗)也沒有 reason。

### F7 呼叫位置的彙總鍵、上限與無呼叫者沒寫死
severity: minor
blocking: 否
引句:「先取傾印時間挑出三個時間點,再一次掃描算每個 callsite 在三個時間點的累計(不做傾印數乘列數的連接),再取這些 callsite 的祖先框架」

1. 第 4 步以 callsite 為單位累計,〈判法〉第 1 條以(函式,.so)為呼叫位置。同一函式從兩個呼叫者進來是兩個 callsite,spec 沒說合併時以誰為鍵、是否把呼叫者列在鍵裡。S11 的「最大 200 個」在合併前還是合併後截,結果不同:合併後截才是對的。
2. 所有框架都是配置器(例:執行緒進入點直接進 libc malloc)時沒有「第一個不是配置器的框架」,spec 沒說丟棄還是寫「?」。沒有上層時呼叫者欄位也沒定義。實驗查詢用 `coalesce(…,'?')`,正式版沒寫。
3. 函式名可帶逗號、換行、引號。第 4 步說「用 csv 模組解析」,但現有腳本都是 `out.splitlines()`,逐行切會把含換行的欄位切碎。應該是整個 stdout 交給 `csv.reader(io.StringIO(...))`。函式名長度沒有上限:C++ 展開名可到數 KB,200 個全存進結果檔,印出的 `_out_clean` 預設限 4000 字,spec 沒說印出行長。
4. 呼叫位置剛好 200 與 201 個時,spec 沒說要不要讓使用者知道有被截斷。

### F8 平局、等距與整除的邊界沒定義
severity: minor
blocking: 否
引句:「時間上最接近兩者正中的那一次(中間)」

1. 兩次傾印與正中等距時取哪次,spec 沒說。取前一次或後一次,前半與後半增量各不同,可能一邊在三分之一線上、另一邊不在。
2. ts 相同的兩次傾印:`ts <= 那一刻` 會一起算,但「傾印次數」若用 `distinct ts` 數,會少算一次。
3. 剛好 1 MiB 與剛好三分之一:`後半 ≥ 整段/3` 用整數比較 `3*後半 >= 整段` 才精確,用浮點除法在大數字上可能差 1 位元組。spec 沒寫哪種。
4. 整段增量為負:「小於 1 MiB → 不增長」已涵蓋,沒問題。
5. 傾印次數 ⚠:`heap_profile_allocation` 每列是跟上次傾印的差額,沒變動的呼叫位置那次傾印沒有列。若整段量測某幾次傾印時 App 完全閒置,這幾次在表裡不出現,以 `distinct ts` 數傾印會少算,導致誤報「樣本不足」。我沒能核對 v57.2 的 `heap_tracker` 是否會對沒變動的呼叫位置也寫列,標 ⚠。

### F9 `"default"` 保留字與合法情境名撞名,清單內容沒驗重複
severity: minor
blocking: 否
引句:「`"default"` 代表沒指定情境的那一段(沒設 LUMOS_STABILITY_SCENARIO)」
file: `scripts/lumos:40488`

1. `stability_scenarios` 的情境名只收 `[A-Za-z0-9_-]+`,`default` 是合法名字。專案真有一個叫 `default` 的情境時,`native_growth: ["default"]` 同時指兩件事:收集腳本拿到 `LUMOS_STABILITY_SCENARIO=default`(有名字)與沒設(stability 段本身),spec 的「判斷順序」分不開。應該是:`stability_scenarios` 不准用 `default` 當名字(`_e2e_scenarios_err` 加一條),或改用不合法於情境名的保留字。
2. `native_growth` 清單裡有重複名字(`["a","a"]`)、空字串、非字串元素:spec 只說「不是字串清單」就擋。重複與空字串是否擋沒寫。`[]` 等於沒寫,spec 已寫明。
3. `LUMOS_STABILITY_SCENARIO` 設了但值不在清單(`stability_scenarios`):`load_config` 在第 128 行已經 `die`,第二段根本到不了。這個邊界不是洞,照現有行為即可。
4. 取不到 `LUMOS_STABILITY_SCENARIO` 時空字串(`export X=`)被 Python 判成沒設,等同 `default`。spec 沒提,但行為合理。

### F10 `max_record_s`、W 或 N 是 1、錄製緩衝區與整支腳本的上限
severity: minor
blocking: 否
引句:「設定範本另開 `android-stability-heapprofd.pbtxt`(`__PROCESS__`、`__DURATION_MS__` 佔位,時長照 `stability.max_record_s`)」
file: `scripts/templates/android-e2e-run.sh:58`

1. `max_record_s` 允許到 1 秒(`1 <= x <= 86400`)。第二段在開錄之後還要多睡 2 秒才開驅動,`max_record_s` 小於 2 + N 輪時間,perfetto 在驅動跑完前自己結束,`stop_record` 的 `alive is False` 分支回「錄製在 N 輪跑完前就到了上限」。這是對的失敗,但 spec 沒說第二段的預算要把等第一次傾印的 2 秒算進去,實作者可能照第一段的預設 600 秒不改。
2. W 或 N 是 1:一輪驅動通常不到 2 秒,傾印每秒一次,幾乎必定少於 3 次,一律失敗。spec 在〈實務隱患〉只寫「驅動跑不到 2 秒時傾印不到 3 次」,沒給使用者可行的建議(拉長 N 或縮短 `dump_interval_ms`),`dump_interval_ms` 固定 1000,沒有設定鍵。
3. 範本的緩衝區 `fill_policy: DISCARD`、`size_kb: 65536`,量測很長(N 到 10000 輪)或每秒變動的呼叫位置很多時會寫滿,後面的傾印被丟掉,而 stats 的錯誤計數檢查只看 `heapprofd_` 開頭,不含 `traced_buf_*` 的丟包計數。結果是「結尾」其實是緩衝區滿之前的某次傾印,卻被當成真的結尾,沒有任何失敗訊號。
4. 整支收集腳本在 e2e 範本裡有單一步驟上限 3600 秒(`scripts/templates/android-e2e-run.sh:58`)。第二段把驅動與錄製時間再加一倍,長情境逾時時 e2e 會判 `device_stuck` 並略過後面的所有情境與效能。〈實務隱患〉的「量測干擾」與「回退」都沒提這個上限。

### 逐節狀況
- 前言與 front matter、`pending_questions`、`decisions`:已讀,無 finding(F5 是 d4/〈打算怎麼做〉第 2 步的文字問題,不是決策本身)。
- 白話、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding。
- 〈實驗室實測〉:已讀,F2 指出「正常版」那一列是相位巧合。
- 〈判法〉:F1、F2、F8。
- 〈打算怎麼做〉:F3、F4、F5、F6、F7、F9、F10。
- 〈跟舊否決的差別〉:已讀,無 finding。
- 〈實務隱患〉:
  - 「已排除:對外送出」:`stop_record` 的 `finally` 確實刪裝置檔,成立;該條「中斷時沿用既有 cleanup」要靠 S8 把設定檔一併收,spec 已列。
  - 「已排除:不可逆」:成立。
  - 「已排除:守衛面」:前提(第二段排在讀取之後、pid 另存)我核對過 `measure()` 的順序,成立。
  - 「金流(不排除)」:理由本身站得住。但 F10 第 4 點的步驟上限也是副作用(整套被標 `device_stuck`),應補進這一節。
- 〈條款〉:S6 的「Android 11 以下」同 F5;S7 缺「驅動失敗」(F6);S5 以外條款的 `[test:待定]`,不另報。
- 〈回退〉、〈審計修正紀錄〉:已讀,無 finding。交叉引用我手動核了:`#d1`–`#d4`、S1–S11、〈判法〉第 1、2 條、〈打算怎麼做〉第 3、4、5 步,都存在。

### 固定席
- `Systems/android-stability-collector.md`:不破壞,但要補寫。它的 WHY「開跑前對 run 目錄每種檔名各問一次 `check-ignore`」要求新增檔名進 `ARTIFACTS`,spec 已列。「state["rec"] 被中斷時 cleanup」的合約,在 S8 補測後成立。F6 寫成 failed 後與該節「收集腳本不偽造 ok」的精神一致。
- `Systems/macrobenchmark-adapter.md`:有影響,F4。它宣稱 `stability_unjudged` 這類鍵「一開始就放好,讀取端不用判斷鍵在不在」,新鍵要照這條放進 `res` 初始字典並兩條出口都輸出,否則違反該節合約。
- `Systems/android-e2e-acceptance.md`:不影響合約。指紋把 `stability` 與 `stability_scenarios` 一起雜湊,`native_growth` 在 `stability` 內,指紋會變,spec 的〈遷移〉已寫。要補的是 F10 第 4 點:單一步驟 3600 秒上限。
- `Projects/Android記憶體與穩定性驗收_計劃.md`:不破壞,需同步改。它的 WHY 寫「Native Heap 前後兩個數字只回報」,以及流程「用同一條驅動指令呼叫兩次」,加了第二段後兩句都過時,spec 第 7 步只提到前一句。
- `Projects/Android逐層診斷_計劃.md`:不破壞。該節 WHY「分層往下、每層有觸發條件,不一次全錄」有明列例外格式,d4 的「預設關、按情境開」維持否決理由。建議在該節 WHY 的例外行補上一條,否則「heapprofd 在 L0 收集階段就錄」跟 L3「事後觸發」的分層描述並存。

總結:整份最高嚴重度為 major,blocking 共 5 條(F1、F2、F3、F4、F5、F6 之中 F1、F2、F3、F4、F5、F6 全為 blocking,實計 6 條)。

更正:blocking 條數以 6 為準(F1、F2、F3、F4、F5、F6),F7 到 F10 為 minor、非 blocking。

總結:整份最高嚴重度為 major,blocking 共 6 條
