severity: minor

審查範圍:逐節讀完 spec,對照 `scripts/lumos` 的 `_kill_merge_ready`、`_choice_merge_cmd`、`_choice_merge_too_long`、`_kill_merge_base`、`_kill_merge_screen`、`_kill_merge_failed_first`、`_kill_run`、`_kill_cap`、`_isolated_worktree`、`_IS_WIN`,以及 `scripts/test_lumos.py` 的 `_CKM_GRADLE` 與相關測試。沒有 blocker 或 major。我沒上網查 Gradle 文件,Gradle 與 JVM 行為的判斷出自既有知識,判不準的處標 ⚠。

## 逐節結論

- 白話、用詞:已讀,無 finding。數字自洽:45+66+6=117,142-117=25,15+10=25,10760/14197 約 76%。
- 做法 1(初始化腳本):見 finding 1、2、3、4。
- 做法 2(事件排序):見 finding 5、6、7。
- 做法 3(斷路器):見 finding 8、9。
- 落點、預期效益、驗收條款、回退、實務隱患:見 finding 2、4、9、10、11。
- 依據來源、PRIOR-ART:已讀,無 finding。
- 內部交叉引用都對得上:第二段 S2 在,S13 是 `--no-merge` 不變,`t_choice_kill_merge_failed_first` 案 5 釘住「測試掛住」。
- 計劃提到的 `t_choice_kill_no_merge_unchanged` 在 `scripts/test_lumos.py` 已存在。

1.
severity: minor
blocking: 否 — 只多寫一個暫存檔、不影響判定,只是漏列改動範圍。
- 段落:〈落點〉最後一句。
- 問題:spec 只說「直接用 `SimpleNamespace(wt=<暫存>)` 呼叫 `_kill_merge_ready` 的既有測試」要改 `wt`,沒列有哪幾處。
引句:「直接用 `SimpleNamespace(wt=<暫存>)` 呼叫 `_kill_merge_ready` 的既有測試,`wt` 改成 `<暫存>/wt` 的形狀」
- 佐證:file: `scripts/test_lumos.py:146471`、`147461`,以及 `_ckm_ready_ctx`(約 `147726` 起,被 `147755`、`147948` 用)都寫 `wt=str(tmp)`。
- 後果:`dirname(c.wt)` 會落到系統 TMPDIR,初始化腳本寫進全域暫存。`_ck_cleanup(tmp)` 刪不到它,切片並行時多個程序會寫同一個檔名。這正好是全域規則在管的暫存累積。
- 要求:漏改任何一處就洩漏,應在 spec 列出全部呼叫點,並加一個測試斷言測試結束後 `dirname(wt)` 以外沒有殘檔。

2.
severity: minor
blocking: 否 — 初始化腳本壞了只是整平台退回逐支,不會判錯。
- 段落:〈做法〉1 的 `_CHOICE_MERGE_INIT`、驗收 S1、回退。
- 問題:S1 只斷言檔案內容含 `events "started", "passed", "failed", "skipped"` 那段子字串,假 Gradle 完全不讀初始化腳本。Groovy 語法錯、Gradle 拒收(例如專案設了警告即失敗)都不會被任何自動測試抓到,只剩 S5 手動。
引句:「常數 `_CHOICE_MERGE_INIT` 是腳本內容:`allprojects { tasks.withType(Test).configureEach { testLogging { events "started", "passed", "failed", "skipped" } } }`」
- 佐證:file: `scripts/test_lumos.py:146259`,`_CKM_GRADLE` 只解析 `--tests`,不處理 `--init-script`。
- 後果:腳本一旦被 Gradle 拒收,每次帶 `--init-script` 的呼叫都 rc≠0,表現成「合併基準 rc 不是 0」,整個平台不合併,三段累積的 3.6 倍加速全丟。
- 缺口:〈代價〉只講「建置腳本蓋掉事件」,沒講「初始化腳本本身被拒」,回退也說「沒有單獨開關」,只能用 `--no-merge` 連合併一起關。
- 要求:加一道失敗降級,帶腳本的合併基準失敗時不帶腳本重試一次,或至少加單獨開關。
- ⚠ 探針 FACT 有沒有用和 `_CHOICE_MERGE_INIT` 逐字相同的腳本,spec 沒寫。

3.
severity: minor
blocking: 否 — 只影響順序與事件覆蓋率。
- 段落:〈實務隱患〉第一條與〈代價〉。
- 問題:spec 說專案自己設了 `testLogging.events` 時「事件行沒有,退回原順序」,只講了全無的情況。常見的 Android 寫法 `unitTests.all { testLogging { events "passed","skipped","failed" } }` 會以「替換」方式蓋掉 `started`,事件行還在、但沒有 STARTED。
引句:「可能蓋掉事件;這時事件行沒有,退回原順序、逾時照舊計數,跟第三段一樣。」
- 後果:掛住的那支落進未知層而不是掛住層,被排在通過層之前;做法 3 也因為沒有 STARTED 而照舊計數。
- 缺口:這個半殘情況沒有驗收條款。
- 同類:`./gradlew -q`、`--warn` 這種 run_cmd 會讓 lifecycle 等級的事件整個不出,spec 沒提。
- 要求:spec 要明講部分覆蓋時的行為,或改在 `gradle.projectsEvaluated` 之後才設事件。

4.
severity: minor
blocking: 否 — 只影響 Windows 與特殊暫存路徑。
- 段落:〈做法〉1 第二個子項(`_choice_merge_cmd` 引號)。
- 問題:spec 自創「`_IS_WIN` 用雙引號」。既有慣例是 `_run_cmd_expand` 的 `subprocess.list2cmdline([x])`,有空白才包引號,且程式碼註解提到過 Windows 特殊字元處理。
引句:「路徑照 `_IS_WIN` 用雙引號或 `shlex.quote`」
- 佐證:file: `scripts/lumos:28071`,`_run_cmd_expand` 對 `{python}`、`{method}` 在 Windows 用 `list2cmdline`。
- 後果:暫存路徑若含 `%`(cmd.exe 在雙引號內仍會展開),spec 沒處理。`_test_name_ok` 對測試名擋了 `_WIN_CMD_SPECIAL`,但路徑沒有同等檢查。
- 要求:改用既有那組,並在路徑含 `%` 或 `^` 時 `sh["init"]=None`。

5.
severity: minor
blocking: 否 — 只影響順序。
- 段落:〈用詞〉事件行解析。
- 問題:規則是以 ` > ` 切開、倒數第二段是類別。`_test_name_ok` 在 POSIX 允許測試名含 `>`,Kotlin 反引號名如 `` `a > b` `` 合法。
引句:「`Outer > Inner > c STARTED` → `Inner.c`(後兩種寫法 11-26 探針沒測到,照字面處理;對不到就落未知層,只影響順序)」
- 佐證:file: `scripts/lumos:` 的 `_test_name_ok`(搜尋函式名定位),只擋 `[`、`]`、`,`,不擋 `>`。
- 輸入:事件行 `FooTest > a > b FAILED`。
- 後果:類別被解成 `a`、名字解成 `b`,對不到 `a > b`,掉進未知層。
- 同類:這個規則與 S2 那條「`Outer > Inner > c` 對到 c」的巢狀規則本身互相衝突。
- ⚠ 真實 Gradle 對 JUnit 4 巢狀類別輸出的是 `Outer$Inner > c`(`$` 寫法),三段式可能根本不存在。

6.
severity: minor
blocking: 否 — 只影響順序。
- 段落:〈用詞〉對到、事件行(非 ASCII 測試名)。
- 問題:測試名可以是中文,JUnit 結果 XML 一律 UTF-8,但控制台事件行用 JVM 的 stdout 編碼。`_kill_run` 以 `errors="replace"` 讀回 UTF-8。
引句:「類別先把 `$` 換成 `.`、再取最後一個 `.` 之後的字;測試名去掉參數尾巴(第一個 `(` 或 `[` 起)」
- 佐證:file: `scripts/lumos:28186`,`_kill_run` 暫存檔以 utf-8、`errors="replace"` 開啟。
- 輸入:Windows 上 Gradle 以 cp950 輸出中文測試名。
- 後果:名字變成亂碼,事件全落未知層;而「跑到測試」只看 STARTED 字樣,不受影響,結果是排序靜默失效、斷路器照常不計。
- ⚠ JVM 實際輸出編碼我沒驗。
- 要求:加一案非 ASCII 測試名的驗收。

7.
severity: minor
blocking: 否 — 只多跑已知會通過的測試,耗時有限,不影響判定。
- 段落:〈做法〉2、S2 的「b、a、c」例。
- 問題:順序是紅、未知、通過、掛住。合併裡已經 PASSED 的測試對同一個壞法確定不會殺掉,卻排在掛住那支之前。掛住那支遇單支逾時就判「跑不出結果」並停(FACT 第三條)。
引句:「應 是 b、a、c(通過層在掛住層之前)」
- 佐證:file: `scripts/test_lumos.py:147526`,`t_choice_kill_merge_failed_first` 案 5 釘住單支逾時即「測試掛住」。
- 後果:通過層的每一支(約 6 秒)都白跑。spec 沒說為何通過層要在掛住層之前,〈預期效益〉也沒把這筆算進去。
- 要求:補理由(例如防止單次 PASSED 是偶發),或改成掛住層排在通過層之前。

8.
severity: minor
blocking: 否 — 屬於 spec 自己承認的代價,缺的是上限與驗收。
- 段落:〈做法〉3、〈代價〉、RETIRE-IF 2。
- 問題:不計斷路器的條件是「輸出至少一行 STARTED」。它分不出三種情況:真有一支沒結束的測試、機器過載而測試只是慢、所有測試都結束了才在收尾卡住。
引句:「輸出裡至少一行 `STARTED` 事件行。」
- 佐證:file: `scripts/lumos:28800`,`_choice_merge_screen_cap` = `min(max(m_el*5, floor), max(remaining,1))`;`scripts/lumos:28392` 的 floor 預設 20 秒,可由環境變數調高。
- 後果:每個壞法都逾時時,斷路器永遠不跳,每個壞法都付一次完整上限(實驗專案約 90 秒,基準大的專案更高),直到總時限到。
- 缺口:RETIRE-IF 2 要到 2026-12-31 才讀帳,沒有執行期上限。
- 要求:加一個較高門檻的獨立連續計數(例如連續 15 次才跳)。

9.
severity: minor
blocking: 否 — 只是驗收條款缺邊界案例。
- 段落:〈做法〉3 與驗收 S3。
- 問題:做法 3 寫了停用中試探不計不恢復、啟用中不歸零 streak。S3 只測「連續 5 個逾時、都有 STARTED」與「都沒有 STARTED」兩案。
引句:「斷路器停用中的試探也照這條:不計、不恢復。」
- 佐證:file: `scripts/lumos:29131`,`_kill_merge_breaker` 的半開分支與 `streak` 邏輯。
- 缺口:沒有任何條款釘住這兩句,例如先 4 個沒 STARTED 的逾時、再 1 個有 STARTED、再 1 個沒 STARTED 是否在第 5 個計數時跳開。
- 要求:補混合序列與半開試探兩案,否則實作寫成歸零或恢復,測試照綠。

10.
severity: minor
blocking: 否 — 實作時會當場踩到並修掉,只是 spec 沒寫。
- 段落:〈落點〉第二項(`__events__`)。
- 問題:假 Gradle 用沒有 flush 的 `print`,輸出重導到檔案時是區塊緩衝。spec 要求事件「在逾時睡眠之前印」,但 `_kill_run` 以 SIGKILL 收程序。
引句:「只在合併呼叫而且帶 `--init-script` 時照順序印 `x.VmTest > <名> <事件>`,在逾時睡眠之前印」
- 佐證:file: `scripts/test_lumos.py:146259`,`_CKM_GRADLE` 的 `print` 都沒有 `flush=True`;`scripts/lumos:28186` 的 `_kill_proc_group` 用 SIGKILL。
- 後果:緩衝區沒寫出去,S3 的「有 STARTED」那案在假 Gradle 上讀到空輸出,逾時案會被判成沒有事件行。
- 要求:spec 要寫明事件行必須 `flush=True`。

11.
severity: minor
blocking: 否 — 只是估算偏樂觀,S5 會實測。
- 段落:〈預期效益〉。
- 問題:說停用期間那 10 個壞法會回到平均 30 秒以內。但斷路器是被連續 5 個逾時的壞法跳開的,這類壞法會成群出現(同一塊程式、同一支測試掛住)。
引句:「斷路器不再被這種逾時跳開,停用期間那 10 個回到平均 30 秒以內。」
- 佐證:file: `scripts/lumos:29131`,`_kill_merge_breaker` 以連續計數跳開,所以被跳開的前 5 個必然連續逾時。
- 後果:後面這 10 個很可能一樣掛住,每個仍要付快篩上限加逐支盲找,約 2 分鐘,與同一段「15 個沒跑乾淨約 2 分鐘一個」自相矛盾。整體 1.5 小時的估算因此偏低。

## 固定席:`Systems/guard-kill`

- 兩條 INVARIANT 都判「不影響」。
- rc 優先序(`t_guard_kill_rc_precedence`):設計只改 choice-kill 合併呼叫的指令、逐支順序與斷路器計數,`cmd_guard_kill` 在 `merge=None` 時行為不變;弱證據(逾時)的歸類規則沒動。
- `--json` 純度(`t_guard_kill_json_purity`):spec 沒新增任何標準輸出,寫檔失敗也是靜默,所以 stdout 仍恰一行 JSON 的條件不受影響。

## 實務隱患逐類

- **併發**:無。一次呼叫一棵 `_isolated_worktree`、初始化腳本放在各自的 mkdtemp 上層資料夾,多個平台組各有各的暫存目錄。唯一的洩漏是 finding 1,在測試裡。
- **效能**:事件解析是 O(名字數 × 事件行數),但輸出被 `_kill_cap` 限在 256KB、合併道受指令長度上限約束,只在沒跑乾淨時做,可以忽略。被砍掉中段的事件只影響順序,spec 已寫。
- **資源**:腳本檔很小,收尾連同暫存資料夾刪除。無界成本在 finding 8。
- **回滾**:見 finding 2,沒有單獨開關,初始化腳本被拒時降級路徑沒寫。
- **資安**:無。腳本內容是固定常數、放在 mkdtemp 建的私有資料夾,路徑用引號包起來,不碰網路與付款。

最高 minor,blocking 0 條
