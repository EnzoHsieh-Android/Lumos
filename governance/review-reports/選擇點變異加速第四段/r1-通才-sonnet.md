severity: minor

我逐節讀完整份 spec,函式、旗標、交叉引用都對照過程式碼。每條 finding 的 blocking 欄與嚴重度一致。這次只補了每條的引句行,內容與等級沒改。

**固定席判讀**(`Systems/guard-kill`)
- `t_guard_kill_rc_precedence` 這條合約不受影響。spec 沒碰 `cmd_guard_kill` 的 rc 判定,只改合併快篩的排序、斷路器計數與指令組裝。
- `t_guard_kill_json_purity` 這條合約不受影響。新增程式沒有任何輸出寫到標準輸出。事件行只在記憶體裡解析,初始化腳本寫進檔案,診斷照舊走標準錯誤。

**節的逐節判讀**
- 白話、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding。數字自洽:117 加 25 等於 142,15 加 10 等於 25,25 個慢壞法佔 10760/14197 約四分之三,142 個整體從 3.9 小時估到 1.5 小時。
- 實測、用詞、人裁紀錄:見 finding 2、3、5。
- 做法、落點、驗收條款、預期值表、回退、實務隱患:見 finding 1 到 6。
- 依據來源:已讀,無 finding。
- 交叉引用:`[[Projects/選擇點變異加速_計劃]]`、第二段、第三段、其〈用詞〉與 S13、第二段 S1 和 S2、`Systems/guard-kill` 都存在。
- 引用的函式與常數:`_kill_merge_ready`、`_choice_merge_cmd`、`_kill_merge_base`、`_kill_merge_screen`、`_kill_merge_breaker`、`_kill_merge_failed_first`、`_choice_merge_classify`、`_isolated_worktree`、`_IS_WIN`、`LUMOS_SKIP_CHOICE_MERGE`、`merge_why` 都存在。
- 新增名稱:`_choice_merge_events`、`_CHOICE_MERGE_INIT`、`c.merge_back` 目前不存在,spec 本來就說要新增。

1. 既有測試的 `wt` 改法會讓那幾支測試直接退出合併
severity: minor
blocking: 否。實作者照做會先看到測試紅,不會做出壞系統。
- 段落:〈落點〉「直接用 `SimpleNamespace(wt=<暫存>)` 呼叫 `_kill_merge_ready` 的既有測試,`wt` 改成 `<暫存>/wt` 的形狀」。
引句:「`wt` 改成 `<暫存>/wt` 的形狀,初始化腳本才寫進那支測試自己的暫存資料夾。」
- 問題:`_choice_merge_results_dir` 要求結果資料夾落在 `wt` 底下,否則 `_kill_merge_ready` 回 None(原因「結果資料夾不在工作樹」)。這幾處測試同時給 `run_dir=str(tmp)`。只把 `wt` 改成 `tmp/wt`,結果資料夾 `tmp/app/build/...` 就跑到 `wt` 外面,測試會全部走「不合併」。
- 還漏了第三處:`_ckm_ready_ctx`。
- file: `scripts/test_lumos.py:146470`、`scripts/test_lumos.py:147457`、`scripts/test_lumos.py:147730`,三處都是 `run_dir=str(tmp), wt=str(tmp)`。
- file: `scripts/lumos:28774`,`_choice_merge_results_dir` 的 `startswith` 圍欄。
- 修法:`run_dir` 要跟著搬進 `tmp/wt`,並先建好該資料夾。

2. 假 Gradle 在逾時睡眠前印事件行,沒要求立刻沖出緩衝,逾時案會讀不到事件
severity: minor
blocking: 否。實作者會在測試紅時發現。
- 段落:〈落點〉「在逾時睡眠之前印」。
引句:「在逾時睡眠之前印;沒有這個鍵的既有案例輸出不變」
- 問題:`_CKM_GRADLE` 是 Python 腳本,輸出重導到檔案時是區塊緩衝。逾時走 `_kill_proc_group`,送的是 SIGKILL,緩衝內容全丟。不加 `flush=True`,S2、S3 的掛住案輸出裡沒有事件行,測的是「沒事件行」那條路,不是 spec 要的那條。
- file: `scripts/lumos:28166`,SIGKILL。
- file: `scripts/test_lumos.py:146259`,假 Gradle 現有的 print 都沒有 flush。

3. 事件行的比對沒規定是否要頂格,也沒規定 `<誰>` 的形狀,測試自己印的字串可能騙過解析
severity: minor
blocking: 否。誤判只影響排序,以及讓一次逾時不計斷路器(每個壞法多付約 90 秒),不會讓結論變錯。
- 段落:〈用詞〉事件行、〈做法〉3 的「跑到測試」。
引句:「合併呼叫輸出裡一行(去掉行尾空白)符合 `<誰> > <測試名> <事件>`」
- 問題一:spec 只說「去掉行尾空白」,沒說行首不可有空白。專案開 `showStandardStreams` 時,測試的 `println` 內容在 Gradle 輸出裡縮排 4 格;失敗訊息也是縮排。實作若用 `re.search` 或 `lstrip`,一行 `Foo > x PASSED` 的測試輸出就被當成事件。
- 問題二:「跑到測試」只要有一行 `STARTED`,所以偽造一行就能讓斷路器不跳開。
- 問題三:測試名含 ` > `(例如 Kotlin 反引號名)時,以 ` > ` 切段會錯位,正確的行只會落到未知層。
- 建議的條款:事件行必須整行頂格匹配,行首不得有空白;`STARTED` 要有對應類別形狀。
- 佐證:Gradle `testLogging` 的事件預設在 lifecycle 層級記錄(Gradle 官方 `TestLoggingContainer` 文件:未指定層級的選項套用於 LIFECYCLE)。縮排是我的推斷,沒有實測。⚠

4. 初始化腳本一旦讓合併基準失敗,整個平台退回逐支,spec 沒有單獨的退路,也沒有重試
severity: minor
blocking: 否。結果仍正確,只是速度退回舊水準(約 360 秒一個)。
- 段落:〈回退〉「只想關事件:沒有單獨開關」;〈實務隱患〉只列「專案自己設了 `testLogging` 會蓋掉事件」。
引句:「只想關事件:沒有單獨開關;還原功能提交。」
- 問題:`--init-script` 讓 `_kill_merge_base` 的基準呼叫不是「通過」時(Gradle 版本不吃、專案開了 isolated projects、`allprojects` 被拒),整個平台組變成「合併基準:找不到 JUnit 結果檔」之類,印出的原因不會指到初始化腳本。spec 沒有「帶腳本失敗就不帶腳本重試一次」,也沒有只關事件的環境變數。
- file: `scripts/lumos:29024` 到 `scripts/lumos:29028`,合併基準不通過就整組不合併。
- Gradle 8/9、設定快取、Kotlin DSL:
  - Groovy 的 `.init.gradle` 不受專案用不用 Kotlin DSL 影響。
  - `testLogging.events(...)` 是 `TestLogging` 的方法,官方 javadoc 有列。
  - `--init-script` 會進設定快取的指紋,路徑每次跑都是新的 mkdtemp,所以每次 lumos 呼叫的第一個合併呼叫會失去設定快取命中。我沒能查到官方對「指紋用路徑還是內容雜湊」的說法。⚠
  - isolated projects 下 init 腳本裡的 `allprojects` 跨專案設定不相容,spec 沒提。⚠

5. 新舊計劃的句子互相矛盾,沒有標註被取代
severity: minor
blocking: 否。不影響程式,影響下一個讀者。
- 段落:〈落點〉、〈做法〉3。
引句:「其他結果 `c.merge_back` 維持空(`c.merge_failed` 照第二段)。」
- 問題:第二段 S2 寫「合併快篩結果是沒跑乾淨……照原排序逐支跑」。第三段〈用詞〉和 `選擇點變異加速_計劃.md` 的〈用詞〉寫「斷路器只數逾時……」。第四段把「逾時且已跑到測試」改成不計數,又讓沒跑乾淨在有事件時改排序,但〈落點〉沒列要在這些既有句子標「部分被取代」。第三段做這件事時有列。
- file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第二段_計劃.md:123`。
- file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:55`。
- file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第三段_計劃.md:75`,第三段處理方式的先例。

6. 預期效益依賴兩個沒有實測支撐的前提
severity: minor
blocking: 否。S5 本來就是人工實測,RETIRE-IF 也有撤除條件。
- 段落:〈預期效益〉。
引句:「沒跑乾淨的 15 個改成先跑紅層,多半一兩支就殺掉,約 2 分鐘一個」
- 問題一:「多半一兩支就殺掉」假設紅層(逾時前已 FAILED 的測試)通常不空。掛住之後的測試根本沒開始,殺掉壞法的測試可能全在未知層。
- 問題二:零案例 4 個也假設輸出裡有事件行。FACT 只證實了掛住探針的情況,零案例有沒有印事件沒有證據。
- 這兩點只影響 30 到 40 分鐘的估算,不影響設計對錯。

**實務隱患逐類**
- 併發:無。一次呼叫一棵工作樹,初始化腳本寫在該工作樹自己的上層暫存資料夾,不跟別的平台組共用。
- 效能:事件解析的比對次數約為行數乘以測試名數,輸出上限 256KB,量級可忽略。
- 大輸出:中段被截掉只影響層級(spec 已寫)。另外,通過路徑的 `tail` 現在會多出事件行,`_kill_res_excerpts` 在弱證據時會拿它做摘錄,內容變多但不改判定。
- 資源:無新子程序。腳本檔隨隔離工作樹的上層資料夾一起刪,`--keep-worktree` 時保留。
- 回滾:見 finding 4。

最高 minor,blocking 0 條。
