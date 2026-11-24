severity: major

## 總結

我讀完整份 spec,並對照 `/Users/enzo/harness/lumos-choice-speed/scripts/lumos` 查證。spec 引用的 `_gradle_task_list`、`_run_cmd_expand`、`_kill_run`、`_KILL_RUN_LIVE`、`_KILL_WT_LIVE`、`_KILL_COMPILE_RE`、`LUMOS_KILL_TIMEOUT_FLOOR` 都存在。`os.sysconf('SC_PHYS_PAGES')` 在 macOS 讀得到(實測回 2097152 頁、頁大小 16384)。

極端輸入下照 spec 字面寫不出正確行為的地方有 3 處(下面前三條)。另有兩處留白會讓兩種寫法都說得通,其中一種是錯的。

## 逐節走查

- 白話、WHY、PRIOR-ART、舊否決比對、實測(來源):已讀,無 finding。
- 〈做法〉1 合併呼叫:有 finding,見下。
- 〈做法〉2 平行分片:有 finding,見下。
- 〈做法〉3 基線、預期效益、不做、回退:已讀,無 finding。
- 驗收條款與預期值表:S10 沒涵蓋記憶體小於 10GB 的情形,見第 1 條。
- 實務隱患:指令長度與 500 支分批的說法和〈做法〉沒有對上,見最後一條。

## Findings

### 記憶體上限可算出 0 份,連預設 `--jobs 1` 都不會跑
severity: major
blocking: 是

spec 段落:〈做法〉2「份數與記憶體保護」。

問題:實際份數 = min(N, 壞法數, 記憶體上限),記憶體上限取 floor。每份估計用預設 6144MB 時,實體記憶體在 10239MB 以下會算出 0(例:8GB 機器,8192×0.6÷6144=0.8,floor 後是 0)。spec 只寫了「讀不到 → 只開 1 份」,沒寫「算出 0 份時至少給 1 份」。S10 只驗了 16GB 與 32GB。

具體例子:8GB 筆電,不帶任何參數跑 `lumos choice-kill`,`--jobs` 預設 1,min(1, 壞法數, 0)=0。照字面實作會開 0 份、一個壞法都不跑,而現在的單份跑法可以跑。這是預設路徑的回歸。壞法數是 0(todo 為空)時 min 也是 0,「先只啟動第一份,等旗號立起」會沒有第一份可等,spec 沒寫這種情況。

另外兩點 spec 也沒定義:
- `LUMOS_CHOICE_SHARD_MB` 設成非整數或負數時怎麼辦。既有的 `LUMOS_KILL_TIMEOUT_FLOOR` 是 ValueError 就退回預設值。
- Windows 沒有 `os.sysconf`,會丟 AttributeError。spec 寫「macOS 與 Linux 都有」,但 repo 有 Windows 分支。

引句:「記憶體上限 = floor(實體記憶體 × 0.6 ÷ 每份估計)」
引句:「實際份數 = min(N, 這次要跑的壞法數, 記憶體上限)」
佐證 file: `/Users/enzo/harness/lumos-choice-speed/scripts/lumos:67`(`_IS_WIN`)

### 共用基準表的鍵不含平台、內容與「填好了」的粒度都沒定義
severity: major
blocking: 是

spec 段落:〈做法〉2「基準只量一次」、〈做法〉1「合併基準」。

問題 a:鍵不含平台。spec 的鍵只有展開後的指令字串。現有 `baselines = {}` 是每個平台各一份(`/Users/enzo/harness/lumos-choice-speed/scripts/lumos:28437`,在每平台的工作樹區塊裡)。多平台或多模組專案若兩個平台的 run_cmd 字串相同、平台根不同(例:`app/` 與 `lib/` 都是 `./gradlew test --tests '*{method}'`),指令字串一樣。照 spec 共用,後一個平台會直接拿前一個平台的基準,不會自己量,可能把紅的當綠或把綠的當紅。

問題 b:「表是空的 / 已填」只有整張表一個粒度。第一份量完第一個平台就立旗號,其他份啟動後遇到第二個平台時表不是空的,但沒有那一把鍵。spec 沒說這時是各份自己量、還是等第一份。

問題 c:合併基準量完的結果不只「rc 與耗時」。「紅的那幾支再單量、單綠的不進合併、單紅的 abort」這三個集合,其他份必須知道,否則它們會拿全部測試組出的指令去跑,每個壞法都「不乾淨」而退回逐支。spec 沒寫這些集合存在表的哪裡。表裡現有的 tuple 形狀(rc, tail, elapsed, to, unsure)裝不下。

引句:「基準表的鍵是展開後的指令字串(不含工作樹路徑,各份相同)」
引句:「表是空的 → 這一份照常量基準」

### 退回逐支時單支基準何時量沒寫,壞法已套上時量會量到紅燈
severity: major
blocking: 是

spec 段落:〈做法〉1「乾淨才採信」、「逾時」。

問題:合併基準全綠時,各支沒有單支基準。任一條件不成立就要「同一次套壞法之內,照現在的方式逐支跑」,而逐支的上限寫「那支有單支基準就用它,沒有就先量」。現有程式是先量基準、再套壞法(`/Users/enzo/harness/lumos-choice-speed/scripts/lumos:28455` 先於套壞法與 `m_timeout` 的 `:28504`)。spec 沒說「先量」是先還原壞法、量完再重套,還是在壞法已套上的樹裡量。

具體例子:合併跑逾時(壞法造成無窮迴圈,變異測試很常見)後退回逐支。若在壞法仍套著時量單支基準,殺掉這個壞法的那幾支會量到紅燈,被記成基準不綠(abort)拿掉。判定就變成 no_result,或是只剩沒被拿掉的測試跑出 survived。這會誤判,而且發生在每次合併失敗。

另外,合併逾時的上限是 5 倍的合併基準,64 支冷編譯時可達 25 分鐘以上才退回。spec 把這個壞法的等待成本算進了〈預期效益〉嗎?沒有算。

引句:「那支有單支基準就用它,沒有就先量」
引句:「同一次套壞法之內,照現在的方式逐支跑」

### 合併組指令跳過了現有逐測試的前置檢查(名稱不合法、撞名、基準不綠)
severity: major
blocking: 是

spec 段落:〈做法〉1「組指令」、「接線」。

問題:現有迴圈在組指令與跑基準之前,對每支測試各做三道檢查。
- `_test_name_ok`:不合法就記 error,拒絕注入(`/Users/enzo/harness/lumos-choice-speed/scripts/lumos:28444`)。
- `_name_collision_reason`:篩選會連帶選中別支時記 error(`:28449`)。
- 基準非綠時記 abort。

spec 的「組指令」是「每支測試用既有的 `_run_cmd_expand` 各展開一次、依測試名排序、接起來」,沒說被這三道檢查擋下的測試要不要排除、該記成什麼列、`order` 裡怎麼處理。「句子名」(含空白、引號的自由字串名稱)也能綁,不排除就會把它拼進同一條 shell 指令。

具體例子:守的測試有 `aCase` 與撞名的 `bCase`。照字面把兩支都拼進去,Gradle 會連帶選中別的測試。其失敗歸不到任何一支,所以每個壞法都退回逐支,合併永遠不生效且沒有提示。更糟的是:名稱不合法的那支若被拼進指令,既有的拒絕注入保護失效。⚠ 要看 `guard["tests"]` 上游有沒有先濾掉這類名稱(`_choice_kill_guard` 在 `/Users/enzo/harness/lumos-choice-speed/scripts/lumos:78411`),我讀的結論是不能假設。

引句:「每支測試用既有的 `_run_cmd_expand` 各展開一次,依測試名排序後用空白接起來、換回原處」

### 認得出 `--tests` 那個詞時看的是切詞後的結果,組指令要換回原字串,兩者對不上
severity: minor
blocking: 否

spec 段落:〈做法〉1「認得出才合併」與「組指令」。

問題:認形狀用 `_gradle_task_list` 與 `_gradle_args_tasks`,拿到的是去掉引號後的詞(`*{method}`)。「組指令」卻要在原始 run_cmd 字串上把「`--tests` 加上含 `{method}` 的那個詞」換成多份。spec 沒說怎麼回到原始字串,也沒說要保留引號。

具體例子:
- `--tests '*{method}'`、`--tests "*{method}"`、`--tests='*{method}'`:展開後的片段各不同。
- `-pfoo`(`-p` 與值黏在一起):`_gradle_args_tasks` 讀不到,當成任務名之外的選項。
- `sh -c '…'` 展開一層後,片段落在內層字串。

兩種寫法都說得通,實作者會各自選一種。

引句:「把 run_cmd 裡「`--tests` 加上含 `{method}` 的那個詞」這一段當片段」

### 結果對回測試用「`.` 加測試名」結尾,巢狀測試類別(`Outer$Inner`)會永遠對不到
severity: minor
blocking: 否

spec 段落:〈做法〉1「對回哪一支」。

問題:JUnit XML 的 `classname` 對巢狀類別是 `pkg.Outer$Inner`(`@Nested` 或 Kotlin 內層類別)。測試綁成 `Inner.method` 時,Gradle 的 `*Inner.method` 篩選會選到它,但完整名 `pkg.Outer$Inner.method` 不以「`.Inner.method`」結尾(前一個字元是 `$`)。結果是「每支要跑的測試都對到至少一筆 testcase」不成立,每個壞法都退回逐支。這是安全的退路,但沒有任何提示,合併對這類專案永遠白付一次。

同族:參數化測試只處理了 `[…]` 與 `()`。JUnit 5 帶參數的顯示名,例如 `aCase(int)` 與 `[1] foo`,不在去除規則裡。

spec 也沒寫同一支測試名在多筆 testcase(參數化)下怎麼合成一支的結果。實作者容易寫成「任一筆失敗就強殺掉」,但沒寫。

引句:「完整名等於測試名、或以「`.` 加測試名」結尾,就算那支測試的結果」

### `merged` 與 `fallback` 兩欄加起來不等於判定數
severity: minor
blocking: 否

spec 段落:〈做法〉2「run 那筆多三欄」、S7。

問題:S7 要求 `merged` 加 `fallback` 等於判定數。但有些壞法不經過合併也不經過退回就判完了。
- 檔不在平台 repo 裡(`add()` 直接記 error 列)。
- `old` 命中不是恰好一次而記 drifted。
- 單支綠而不進合併、每個壞法另外逐支跑的那幾支。

具體例子:7 個壞法裡有 1 個檔不在平台 repo,則 `merged`+`fallback` 最多是 6,S7 的相等斷言會紅。照字面實作的測試與 spec 互相打架。

引句:「`merged` 加 `fallback` 等於判定數」

### 〈實務隱患〉說逾時用各份自己的基準,〈做法〉2 卻是各份共用第一份的基準
severity: minor
blocking: 否

spec 段落:〈實務隱患〉第一條、〈做法〉2「基準只量一次」。

問題:〈做法〉2 讓其他份直接用第一份量好的表。〈實務隱患〉卻說「逾時照各份自己的基準耗時算(第一份量的基準含冷編譯,倍數寬)」。兩處互相矛盾。「由基準耗時的 5 倍蓋過」的「蓋過」是取代還是取較大值也沒寫。第一份是單獨量的、沒有搶 CPU;其他份同時跑才是被拉慢的,這個倍數邊界沒有數字支持。

引句:「逾時照各份自己的基準耗時算」

### 超過 500 支分批只在〈實務隱患〉提到,〈做法〉與驗收完全沒有對應
severity: minor
blocking: 否

spec 段落:〈實務隱患〉「指令長度」。

問題:合併基準寫成「全部守的測試一次 Gradle 呼叫」,基準逾時上限是 30 秒乘以測試支數。〈實務隱患〉卻說超過 500 支分成多次合併呼叫、結果合起來判。spec 沒寫:
- 基準是否也分批。
- 「乾淨才採信」是每批各判還是合併判。
- 合併跑的逾時上限算哪一批的基準。
- 這一情況沒有任何 S 條款。

指令長度的論據只考慮 macOS 的上限,Windows cmd 的上限約 8191 字元,500 支的片段會超過。

引句:「守的測試超過 500 支時分成多次合併呼叫(每次最多 500 支),結果合起來判」

### 分片沒有配方時行為沒寫
severity: minor
blocking: 否

spec 段落:〈做法〉2「分工」。

問題:壞法照順序輪流分給各份,但有些壞法沒有任何配方(每支測試都不在平台 repo,`add()` 直接記 error 列)。若某一份分到的全是這種壞法,`cmd_guard_kill` 收到空配方會印「擋下:沒有任何突變配方可跑」並回 rc 2(`/Users/enzo/harness/lumos-choice-speed/scripts/lumos:28340` 附近的 `if not recipes` 分支)。spec 沒說這算不算「某份當掉」,也沒說份數是用壞法數還是有配方的壞法數來算。

具體例子:3 個壞法、其中 2 個無配方,份數算出 3 份,但只有 1 份有事做,另 2 份各印一行擋下訊息。

發現共 9 條
