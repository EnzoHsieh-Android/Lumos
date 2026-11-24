severity: major

## 總結

這份設計的方向沒有跟既有圖譜衝突。推送閘讀治理帳的那一道,不會因為合併或平行寫出的帳而改變判法,理由在逐節走查。

照字面實作會出事的有三處:
- 退回逐支時的基準與逾時沒定義清楚。
- 合併基準對「結果檔裡缺一支測試」沒有規則。
- `cmd_guard_kill` 跟 choice-kill 之間,合併或退回的計數與印字沒有傳遞通道。

其餘是精度與可測性問題。

我沒有跑 Gradle,所以 Gradle 多個 `--tests` 時某個樣式沒對到的行為,標 ⚠ 交編排者。T29、T41、T44 在實驗專案私有庫,這裡查不到,同樣標 ⚠。

## Findings

### 退回逐支時要重量單支基準,但此時壞法已經套在工作樹上
severity: major
blocking: 是

spec 段落:〈做法〉1「乾淨才採信」與「逾時」。

問題:
- 「乾淨才採信」寫退回逐支發生在「同一次套壞法之內」。
- 「逾時」又寫退回逐支時「那支有單支基準就用它,沒有就先量」。
- 合併基準全綠的常見情況下,只有合併那一筆基準,單支基準根本不存在。所以退回時幾乎每支都落在「先量」。
- 現行 `cmd_guard_kill` 的單支基準是在套壞法之前量的。退回時壞法已寫進檔,這時量「基準」量到的是壞法版本。

例子:
- 壞法讓第 3 支測試紅,合併結果檔缺一支所以退回。
- 逐支跑第 3 支前先量它的基準,結果紅,記 abort 並從 live 拿掉。
- 其餘測試都綠,整個壞法被判成 survived,而這支測試明明是殺掉它的那一支。
- 若實作者改成先還原再量再重套,spec 沒寫。逾時退回同樣無從定上限。

引句:「任一不成立 → 同一次套壞法之內,照現在的方式逐支跑」
引句:「退回逐支時每支的上限照現在(那支有單支基準就用它,沒有就先量)」
佐證: `scripts/lumos:28397`(基準在套壞法之前量,以指令為鍵存進 `baselines`)

### 合併基準遇到「某支測試在結果檔裡根本沒出現」沒有規則,會被記綠
severity: major
blocking: 是

spec 段落:〈做法〉1「合併基準」。

問題:
- 基準只分三種:全綠、有測試紅、逾時或結果檔讀不出。
- 「每支要跑的測試都對到至少一筆 testcase」只列在壞法那段,基準沒有。

例子:
- 守的測試有幾支在 `:app` 以外的模組,或名字樣式沒對到任何 class。
- 多個 `--tests` 時其他樣式有對到,Gradle rc 為 0 ⚠(我沒驗過 Gradle 對單一樣式沒對到的處理)。
- 這些測試在 XML 裡沒有 testcase,但依「全綠 → 每支的基準都記綠」被記成綠。
- 逐支跑時同一支測試會因 No tests found 讓 rc 不是 0、基準記 abort 拿掉。判定已經不一致。
- 之後每個壞法都因「某支沒對到 testcase」退回逐支。每個壞法付一次白跑的合併,比現在更慢。
- 這個狀況會在 RETIRE-IF ① 累積成「退回超過三成」,讓功能自己被判撤。

引句:「全綠 → 每支的基準都記綠、耗時記這一次的。」
引句:「每支要跑的測試都對到至少一筆 testcase」

### `cmd_guard_kill` 回報合併或退回與印字的通道沒定義,而且印字會被整段收起來
severity: major
blocking: 是

spec 段落:〈做法〉1「接線」、〈做法〉2「輸出」、「run 那筆多三欄」、S3、S7。

問題:
1. 通道缺。`on_row` 交出的列欄位是固定的:recipe_id、group、invariant、test、platform、verdict、weak、weak_why、detail、fail_excerpt、compile_error。沒有「這列是合併判的還是退回的」。`_ChoiceKillRun` 因此算不出 `merged` 與 `fallback`。
2. 印字被吞。S3 要求「資料夾不在時印一行」,這行在 `cmd_guard_kill` 裡印。choice-kill 在啟動各份前把 stdout 整段 `redirect_stdout(io.StringIO())`,全程收起來。那行會被吞掉。spec 沒說改印 stderr。
3. 欄位定義與 S7 的等式不成立。S7 寫「`merged` 加 `fallback` 等於判定數」。判定數還包含:
   - 非 Gradle 形狀(不合併、也不算退回)。
   - 檔不在平台 repo 而直接判的壞法。
   - S5 那種部分測試另外逐支、其餘合併的壞法,歸 merged 還是 fallback 沒定。
4. S9 說記「跑不出結果:測試程序被系統收掉」。實際 judge 對 `error` 列的 reason 是 `error(…)` 加冒號後的 detail。`gov --stats` 的 `nores` 依冒號前那段分組,會全併進 `error`,看不到這個原因。

引句:「資料夾不在時 應 印一行並讓這次呼叫之後的壞法都逐支跑」
引句:「`merged` 加 `fallback` 等於判定數」
引句:「判定那一行照舊印到 `_ChoiceKillRun` 建立時記下的標準輸出。」
佐證: `scripts/lumos:78543`(`cmd_guard_kill` 包在 `redirect_stdout(io.StringIO())` 裡)
佐證: `scripts/lumos:28673`(`_KillHooks.flush` 交出列的固定欄位)
佐證: `scripts/lumos:78232`(`_choice_kill_judge` 對 `error` 的 reason 形式)

### 合併組指令前沒說要先過 per-recipe 的名稱與撞名檢查,判定會跟逐支不同
severity: minor
blocking: 否

spec 段落:〈做法〉1「組指令」「合併基準」。

問題:
- 逐支路徑在展開指令前有 `_test_name_ok`(不合法記 error)與 `_name_collision_reason`(撞名記 error)。
- spec 的「全部守的測試一次 Gradle 呼叫」沒說先過這兩關。
- 沒先過就會把本該記 error 的測試直接跑進合併。逐支判 no_result,合併可能判 survived。

例子:測試名含逗號或方括號。逐支是 error,合併組進指令。shlex 引號擋得住注入,但判定不一致,S2 或 S3 沒有案例涵蓋。

引句:「每支測試用既有的 `_run_cmd_expand` 各展開一次」
佐證: `scripts/lumos:28422`(`_test_name_ok` 與撞名檢查在逐支路徑裡)

### 掛住的壞法要先吃滿 5 倍合併基準逾時,預期效益表沒算,逾時後的背景程序也沒驗
severity: minor
blocking: 否

spec 段落:〈做法〉1「逾時」、〈預期效益〉。

問題:
- 讓測試無窮迴圈的壞法很常見。現在逐支跑時掛住的那一支只吃自己的基準 5 倍(例如 25 秒)。
- 合併後上限是合併基準耗時的 5 倍。合併基準含冷編譯與 64 支測試,數分鐘到十幾分鐘,所以 5 倍可達數十分鐘。之後還要退回逐支再跑一次。
- 〈預期效益〉表沒有這一類壞法的耗時。
- `_kill_proc_group` 只收 gradlew 用戶端所在的群組。Gradle 背景程序與測試行程在不在這個群組 ⚠(我沒驗)。
- 若測試行程繼續空轉,會在多份同時跑時持續佔 CPU。〈實務隱患〉只講「閒置的背景程序」,沒講卡住的測試行程。

引句:「合併跑壞法的上限 = max(合併基準耗時 × 5, 下限)」

### 逐支模式下其餘各份的冷編譯逾時,spec 宣稱的緩解不成立
severity: minor
blocking: 否

spec 段落:〈做法〉2「基準只量一次」。

問題:
- 逐支模式(`--no-merge --jobs N`,以及退回逐支)的基準是每支測試各一筆。只有第一支量到的那筆含冷編譯。
- 第 2 份以後的第一個壞法若先跑到另一支測試(`_choice_test_order` 依被改的檔排序,每個壞法順序不同),它的基準只有幾秒,上限只有 max(5×幾秒, 20 秒)。
- 新工作樹要冷編譯數分鐘,會被判 `timed_out_weak`,壞法記「測試掛住」。這不是危險方向,但要多跑一輪。
- spec 說「第一份的基準本來就含冷編譯」只對合併基準成立。

引句:「其餘各份的第一個壞法要付冷編譯,逾時上限由基準耗時(第一份的基準本來就含冷編譯)的 5 倍蓋過」

### 「用既有的 `_gradle_task_list` 切段」拿不到 `--tests` 那個詞
severity: minor
blocking: 否

spec 段落:〈做法〉1「認得出才合併」「組指令」。

問題:
- 我實測 `_gradle_task_list`,它只回 `[(專案目錄, [任務名])]`。`--tests` 的值被當帶值選項濾掉,沒有字詞位置。
- 「把 `--tests` 加上含 `{method}` 的那個詞當片段、換回原處」需要在原字串上定位,spec 沒說用什麼切。
- `cd android && ./gradlew …` 或 `sh -c "…"` 時,片段位置與結果檔資料夾公式(`<執行目錄>/<-p 的值>/…`)都要另外處理。
- 後者 spec 有退回路徑,所以只是白付一次合併。

引句:「用既有的 `_gradle_task_list` 切段,那一段恰好一個測試任務」

### 不用 `_BtProcs` 的理由寫的是「沒有 started 路徑」,而 `_kill_run` 本來就有 `started` 參數
severity: minor
blocking: 否

spec 段落:〈PRIOR-ART〉④、〈做法〉2「中斷」。

問題:
- `_kill_run(cmd, cwd, timeout, keep_re=None, started=None)` 已經接受 `started`。
- 合約測試閘並行執行計劃專門處理過「收尾立標記後不准再開、並等正在開的開完再一起收」。
- 現在的 `_KILL_RUN_LIVE` 是 `Popen` 之後才登記。第二個訊號的強制結束先抄一份快照再 `os._exit`,剛開但還沒登記的那一支會成孤兒。這個窗口很小,但就是那份計劃修過的同一類問題。
- 這裡拿一個不成立的理由否決了已有的解法。

引句:「程序登記沿用 guard kill 自己的 `_KILL_RUN_LIVE`(`cmd_guard_kill` 沒有傳 started 的路徑,不改用 `_BtProcs`)」
佐證: `scripts/lumos:28168`(`_kill_run` 簽名帶 `started`)

### S6 到 S9 與預設記憶體上限互相牽制,S10 的下限也沒定
severity: minor
blocking: 否

spec 段落:〈做法〉2「份數與記憶體保護」、S6 到 S10。

問題:
- S6 到 S9 都要在 `--jobs 3` 下真的開三份。預設每份估 6144MB、記憶體乘 0.6。
- 16GB 的 CI 機器只會開 1 份,S6 的「三棵不同的隔離工作樹同時存在」會失敗。
- 不到約 10GB 的機器,floor 算出 0 份,`min(N, 壞法數, 0)` 變 0,沒有規則寫「至少 1 份」。
- 這幾個條款要寫明測試固定 `LUMOS_CHOICE_SHARD_MB=0`。
- `LUMOS_CHOICE_SHARD_MB` 給非數字或負數沒定義。
- S4 的「上限 50 秒」要真等 10 秒基準或換掉 `_kill_run`,spec 沒說用哪種。

引句:「`--jobs 3` 時 應 觀察到三棵不同的隔離工作樹同時存在」
引句:「實際份數 = min(N, 這次要跑的壞法數, 記憶體上限)」

### RETIRE-IF 與 REVISIT 要讀的欄位和一條聲稱的量測,現有讀帳沒有
severity: minor
blocking: 否

spec 段落:〈做法〉1「取捨」、RETIRE-IF ②、「run 那筆多三欄」。

問題:
- RETIRE-IF ② 要算 `secs ÷ ran`。`_gov_row` 的 `ck` 白名單只有 `file, fp, killing_test, changed, mutant_lines, secs, reasons, site`,沒有 `ran`。spec 只說加 `jobs`、`merged`、`fallback`。
- `gov --stats` 不會印這幾個數,只能手讀帳。
- 〈取捨〉聲稱「RETIRE-IF 與 REVISIT 量到被殺掉的壞法合併後比現在慢兩倍以上再加」。兩者都沒有依判定分開量秒數的欄位,這條沒有量測機制。
- ② 的比較有混淆:`--jobs 1` 與 `--jobs 3` 的呼叫,每呼叫的基準攤提份量不同,`--max-mutants` 預設 30 又讓批量大小不一。

引句:「RETIRE-IF 與 REVISIT 量到被殺掉的壞法合併後比現在慢兩倍以上再加」
佐證: `scripts/lumos:18574`(`_gov_row` 裡 choice-kill 的 `ck` 白名單)

### lands_in 與文件落點不全,規格閘那條「不選平行」要改寫沒寫明,有一處懸空的節名引用
severity: minor
blocking: 否

spec 段落:`lands_in`、〈舊否決比對〉。

問題:
1. `Systems/規格閘` 的 choice-kill WHY 行寫著「`[不選:每個壞法一棵工作樹平行跑…]`」。plan 把它窄化詮釋後沒說上線時要改這行 WHY。留著會變成跟現況矛盾的舊否決。
2. 改動選擇點計劃的限制 3 寫「我們是一棵工作樹依序跑」,執行摘要裡也寫「同一平台一次呼叫一棵工作樹」。這兩處也會失真,舊否決比對沒列。
3. `skills/lumos-project-notes/commands/06-代碼審與推送.md` 的 choice-kill 指令列與 `skills/lumos-code-loop/SKILL.md` 都會出現 `--jobs` 與 `--no-merge`,lands_in 與〈不做〉都沒提。
4. 「判定時的順序仍照〈用詞〉守的測試排序」的〈用詞〉在本文沒有這一節。它指的是改動選擇點計劃的〈用詞〉,卻寫成本文的節名引用。

引句:「[[Systems/規格閘]] 記 choice-kill 那行的」
引句:「判定時的順序仍照〈用詞〉守的測試排序」

### 共用基準表在第一份提早結束時,後面兩份會同時各量一次
severity: minor
blocking: 否

spec 段落:〈做法〉2「基準只量一次」。

問題:
- 第一份在旗號立起前結束(例如工作樹建不起來、`_KillHalt`)時,其餘各份才一起啟動。
- 「表是空的 → 這一份照常量基準」沒有互斥。第 2、3 份會同時量一次,違反 S6「基準指令在整次呼叫只跑一次」。
- 共用表存的 `tail` 是第一份量的。`_kill_fail_excerpt(b_tail, wt)` 把第一份的工作樹路徑遮掉。第 2 份用這筆基準記 abort 時,摘錄裡的路徑不是它自己的,會原樣寫進進版控的治理帳。

引句:「表是空的 → 這一份照常量基準」
佐證: `scripts/lumos:28402`(abort 列用 `_kill_fail_excerpt(b_tail, wt)` 遮路徑)

### 強證據升級的歸因比「確實在結果檔失敗」寬,編不過判讀的條件前後不一
severity: minor
blocking: 否

spec 段落:〈做法〉1「對回哪一支」「判讀順序」「乾淨才採信」、S14。

問題:
1. 「完整名等於測試名、或以『.』加測試名結尾」,綁的測試是只寫方法名時,別的 class 同名的失敗 testcase 也會算它的。
   - 逐支路徑 `_kill_attribute` 也有同樣的寬度,所以不是新增的風險。
   - 但 S14 把弱證據升為強證據,依據換成這個比對。使用者裁示的是「被歸因的那支要確實在結果檔裡失敗」。
2. 判讀順序②:「編不過」只看「rc 不是 0、輸出符合 `_KILL_COMPILE_RE`」。「乾淨才採信」的例外寫「rc 不是 0、沒有新的結果檔、輸出符合」,多一個「沒有新的結果檔」。
   - 實測合併後輸出可能是 64 支測試的完整輸出(最多 256KB),含 `Compilation error` 字樣的機會更高。
   - 兩條擇一沒寫。

引句:「完整名等於測試名、或以「.」加測試名結尾」
引句:「例外:rc 不是 0、沒有新的結果檔、輸出符合 `_KILL_COMPILE_RE` → 壞法編不過」

## 逐節走查

- 白話、WHY 兩條、PRIOR-ART、RETIRE-IF、REVISIT:已讀。
  - 未驗外部依據:T29/T41/T44、論文與 PIT 的引句(⚠ 外部,未查)。
  - 內部算術驗過:6 分鐘約 64×5.5 秒、183 個壞法的 15–18 小時與 37 段。
  - 發現見上面的第 10 條。
- 舊否決比對:已讀。
  - 引用的規格閘那行否決原文確實存在。
  - guard-kill 三處「不另抽共用函式」否決:本案不改 `cmd_guard_kill` 判法,只加選用參數,沒有衝突。
  - 合約測試閘並行計劃「不用標準執行緒池」存在。
  - 漏列的比對見第 10 條。
- 實測:已讀。引用的 `_kill_run` 經 shell 開程序、`LUMOS_KILL_TIMEOUT_FLOOR`、`_gradle_test_module` 只認 `:test`、`_KILL_COMPILE_RE` 都核對屬實。
- 〈做法〉1:發現見第 1、2、3、4、7、13 條。
- 〈做法〉2:發現見第 5、6、8、9、12 條。
- 〈做法〉3:已讀,無 finding。
- 〈預期效益〉、〈不做〉:已讀,無 finding(算術對得上,不確定性有自己註明)。
- 驗收條款與預期值表:交叉引用都找得到對應的節。可測性問題見第 9、3 條。
- 回退:已讀。新三欄舊讀者會略過;型別表未登記前,`_gov_event_types_ok` 只檢查已登記的鍵,所以不會讓整行被跳過。
- 實務隱患:風險類逐項走過。
  - 併發:帳只由主程序寫。
  - 資源:工作樹與背景程序(第 4 條)、磁碟容量沒評估:每份一棵完整工作樹加 build 目錄,Android 專案可能每份數 GB,沒寫。
  - 回滾:有。
  - 守衛面:見下。
  - 金流、外送、不可逆:spec 已排除,同意。

### 推送閘讀帳不受合併或平行影響的理由
- 推送閘讀的是 `_choice_push_ledger` 讀回的 choice-kill 事件,取每個 (檔, 行指紋) 的檔內最後一筆(`_choice_disposition` 的 `evs[-1]`)。
- 帳由主程序單一寫入,每個壞法一筆、鍵不重複。平行只改誰去跑,不會讓同一鍵出現交錯寫入。檔內順序語意沒變。
- 守的測試雜湊(`tests_sha`)在啟動時算一次,不受影響。
- `killing_test` 仍是排序第一支強殺掉的那支,所以「過期」判法(殺掉它的測試仍被條款綁著)照舊。
- 唯一會改變帳內容的地方是使用者已裁示的「弱證據升為強證據」。這讓更多壞法直接記 killed。它的正確性取決於第 13 條的歸因精度,不是帳寫入方式。
- 跨分支合併帳檔造成的順序問題是既有行為,本案不改變。

### 固定席節點逐條判
- `Systems/guard-kill`:兩條 ★INVARIANT★ 都不受影響。
  - rc 優先序:合併與共用基準只由 choice-kill 傳新參數,`guard kill` 指令本身不傳,S12 守這一點。
  - `--json` 純度:新增的印字只在 merge 為真時出現,`as_json` 路徑不傳 merge。
  - 前提是第 3 條那行印字不印到 stdout。
- `Systems/規格閘`:沒有合約,不影響行為。
  - choice-kill 那行 WHY 的「不選平行」在上線後需改寫,見第 10 條。

發現共 13 條
