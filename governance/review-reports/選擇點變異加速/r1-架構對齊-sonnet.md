severity: major

我只比對「一不一致」,不找 bug。對照的 repo 是 `/Users/enzo/harness/lumos-choice-speed`,spec 是凍結快照 `r1-snapshot.md`。

## 四問結論

**1. 分層與依賴方向:大致對齊。**
- 新機制放在 choice-kill 這層(`_ChoiceKillRun`、`cmd_choice_kill`),判法留在 `cmd_guard_kill` 裡,只加選用參數 `merge`、`baseline_share`。
- 這跟既有做法一致:`cmd_guard_kill` 簽名已有 `recipes_override, source, stop_group_on, on_row, should_stop`(`scripts/lumos:28301-28303`),`_KillHooks` 是不傳就什麼都不做(`scripts/lumos:28648-28652`)。
- 治理帳由主程序串行寫,仍經既有的 `_choice_gate_event`(`scripts/lumos:78601-78606` 一帶)。
- 隔離工作樹仍走 `_isolated_worktree`(`scripts/lumos:28070`),沒有繞過入口直呼內部。
- 一個不一致:讀 JUnit 結果檔繞過了既有的 JUnit 讀取入口,見 finding 1。

**2. 命名與錯誤處理:大致對齊,有幾處小差異。**
- 治理帳新欄位 `jobs`、`merged`、`fallback` 照 `_GOV_FIELD_TYPES` 登記,放在 `scripts/lumos:18462` 那種整數欄位的位置,對齊。
- `--jobs` 範圍不合法時 rc 2,這跟 `_choice_kill_base` 的 `say()` 慣例一致(`scripts/lumos:78370-78371`)。
- 旗標命名、環境變數與中斷收尾有出入,見 finding 3、4。

**3. 第二種做法:不對齊。**
- 專案已有「JUnit XML → 案例」的單一讀取入口,spec 另寫一套。這是 major,見 finding 1。
- 其他兩處是小差異:`--tests` 片段的改寫與測試任務判斷(finding 2)、程序登記機制(finding 4)。

**4. 落點合不合理:部分不對齊。**
- choice-kill 的執行端(份數、記憶體上限、工作佇列)寫進 `規格閘`,那篇已經很大。
- spec 要動共用的 `_isolated_worktree`,它的另一個家 `代碼審修正關卡` 不在 `lands_in` 裡。
- 見 finding 5。

## Findings

### 1. 判誰殺掉的 JUnit 結果檔,另寫了一套讀取,沒用專案既有的 JUnit 讀取入口
severity: major
blocking: 是

位置:〈做法〉1「對回哪一支」與〈實務隱患〉「結果檔讀法」。

spec 要求讀 `TEST-*.xml` 的 `testcase`,自行把「完整名 = classname + `.` + name」去掉結尾 `()` 與 `[…]`,「XML 用標準函式庫剖析」,單檔超過 16MB 視為讀不了。

引句:「XML 用標準函式庫剖析;讀不了、檔案過大(單檔超過 16MB 視為讀不了)一律退回逐支,不當掉。」

專案已有加固過的 JUnit 讀取:
- `test_quality.junit(raw)` 邊解析邊數深度,超過 `JUNIT_MAX_DEPTH=64` 立刻停。
- 它不先建整棵樹,有拒收代碼 `JUnitRejected`,並檢查重複身分、suite 層錯誤與計數一致。
- `_secev_junit_facts` 的註解明寫「讀法沿用 test_quality.junit()」,也就是專案其他讀 JUnit 的地方都經這一支。

對照:`scripts/test_quality.py:148-151`、`scripts/test_quality.py:250-273`、`scripts/lumos:9046-9052`。

具體例子:
- 一個深層巢狀或超大的 `TEST-*.xml` 進來。
- 既有入口會用深度上限、拒收代碼擋下。
- 照 spec 實作的新讀法只有 16MB 大小閘,沒有深度閘,`ET` 整棵樹照建。
- 兩套讀法對同一份結果檔可能給出不同的「讀不出來」邊界。
- 這會直接影響「退回逐支」與「判殺掉」的守衛面判定。

⚠ 交編排者:`test_quality.junit` 會因「重複身分」「zero_cases」整份拒收,而 choice-kill 要的是「每個類別一檔、分檔讀、對回測試名」。
- 可能要先對每個檔各呼叫,或在該入口擴充一個模式。
- 但這是「改既有入口」與「另寫一套」的取捨,spec 完全沒提既有入口,也沒寫為何不能用。
- 光這一點就算引入第二種結果判讀。

### 2. 組合併指令的片段改寫與「測試任務」判斷,沒有走既有的單一入口
severity: minor
blocking: 否

位置:〈做法〉1「認得出才合併」「組指令」。

spec 切段用了既有的 `_gradle_task_list`(`scripts/lumos:76986`),這點對齊。後面有兩件事是另寫的:
- 在 run_cmd 文字裡找出「`--tests` 加上含 `{method}` 的那個詞」,每支展開後用空白接起來,「換回原處」。既有函式只回傳 `(專案目錄, [任務名])`,不回傳詞在字串中的位置。spec 沒說這個定位怎麼做,等於新增一個 run_cmd 文字層的改寫路徑。
- 「測試任務」另寫一支判斷(`test` 或 `test*UnitTest`),spec 自己承認既有 `_gradle_test_module` 只認 `<模組>:test`(`scripts/lumos:77001-77010`)。同類判斷還有 `_gradle_blocked_tasks`(`scripts/lumos:77013` 起)與 `_SR_MODULE_PART`。

具體例子:
- 現在專案裡「這是不是 test 任務」已有兩處各自的判法。
- 新增第三支只認 `testDebugUnitTest` 這個形狀,日後改任務名規則要改三處。
- 單一 `{method}` 的替換目前一律走 `_run_cmd_expand`(`scripts/lumos:28053-28068`,註解寫明「三處都經這一支」),這點 spec 有沿用,對齊。

⚠:結構上沒有另起一套完整解析,所以只判 minor。若實作時為了定位片段而自寫 shell 斷詞,就會變成「另一套 Gradle 指令解析」,屆時應升為 major。

### 3. 平行度與記憶體保護的旋鈕,命名與合法性處理跟既有的平行旋鈕不同
severity: minor
blocking: 否

位置:〈做法〉2「份數與記憶體保護」。

既有的並行旋鈕 `_bound_tests_parallel`(`scripts/lumos:74112-74126`):
- 放在 `.lumos/config.json` 的 `bound_tests.parallel`。
- 只收 2 到 16 的整數。
- 其他值一律當 1,並在 stderr 講一句用了 1。

spec 的旋鈕:
- 是 CLI `--jobs`,收 1–8。
- 不合法 rc 2。
- 另有環境變數 `LUMOS_CHOICE_SHARD_MB`。

這三點在 choice-kill 自己的範圍內對齊:它有 `--max-mutants` 等 CLI 旗標,`LUMOS_CHOICE_SINCE`(`scripts/lumos:78023`)也是 `LUMOS_CHOICE_*` 命名。但跟專案裡同概念的「並行份數」相比:
- 名稱不同(jobs 對 parallel)。
- 範圍不同(1–8 對 2–16)。
- 不合法時的處理不同(rc 2 對靜默當 1 加警告)。

具體例子:使用者在 `.lumos/config.json` 設了 `bound_tests.parallel: 4`,對 choice-kill 沒有任何作用,也沒提示。

另外名稱不一致:CLI 叫 `--jobs`,spec 文字與環境變數叫「份/SHARD」,同一概念兩個名字。

⚠:此處不是缺陷,屬命名一致性;`--jobs` 預設 1 是使用者已裁定的,不動。

### 4. 程序登記沿用 `_KILL_RUN_LIVE` 而非 `_BtProcs`;分工方式與錯誤策略跟合約測試閘不同
severity: minor
blocking: 否

位置:〈PRIOR-ART〉④與〈做法〉2「分工」「某份當掉」。

spec 明說「程序登記沿用 guard kill 自己的 `_KILL_RUN_LIVE`」,不改用 `_BtProcs`;這與既有 choice-kill、人裁的做法一致(`scripts/lumos:28162`、`scripts/lumos:28184`),結構上算對齊。

但跟合約測試閘的並行形狀有三點差異:
- 合約測試閘用共用佇列讓工作者自己拉工作;spec 改成預先輪流分配。
- 合約測試閘有 `_BtProcs.launch/reap` 的「正在開」計數與期限收尾(`scripts/lumos:74059-74100`);`_KILL_RUN_LIVE` 只是 pid→Popen 字典,沒有「收尾中不准再開」的標記。
- 錯誤策略相反:合約測試閘「出錯不再派新的」,spec 明說不學。

spec 在〈PRIOR-ART〉④與〈舊否決比對〉都有交代理由,所以不判第二種做法。

具體例子:第二個訊號強制結束時,若某份剛好在開程序、還沒登記進 `_KILL_RUN_LIVE`,收程序群組會漏掉它;`_BtProcs` 的設計正是為了擋這種情況(見該類 docstring 的「高風險代碼審 r3 併發席」)。

⚠ 交編排者:這是「既有已有更完整機制」的對照,不是新增機制;是否要補一道,屬併發席的判斷。

### 5. 落點:choice-kill 執行端沒有專屬的家,`_isolated_worktree` 加鎖會動到不在 `lands_in` 的節點
severity: minor
blocking: 否

位置:front matter 的 `lands_in`,與〈做法〉2「建與收工作樹排隊」。

現況:
- `Systems/規格閘.md` 227 行、約 99KB,已提到 choice-kill 38 次。
- 它的負責範圍是「判門…改動選擇點的語法樹掃描與每行挑壞法(choice-points)」,沒有寫 choice-kill 的批次執行。
- choice-kill 的執行端(`_ChoiceKillRun`、`cmd_choice_kill`)目前沒有任何 Systems 節點專管。`grep` 只在 `guard-kill.md` 的一條 PITFALL 提到 `_ChoiceKillRun`。
- `Systems/guard-kill.md` 154 行、約 45KB,responsibility 已寫成「也是人裁與 choice-kill 臨時配方的唯一判法(它們只用選用參數接上)」。
- spec 要把「合併判讀、基準共用、結果檔讀法、各份工作樹」塞進去,但 `--jobs` 的佇列、記憶體上限、中斷、帳寫序屬於 choice-kill 端,不是 guard kill 的判法。
- `_isolated_worktree` 的家還有 `Systems/代碼審修正關卡.md`(該篇與 `guard-kill.md` 都提到它)。spec 要在這支共用函式加模組層鎖,而 `lands_in` 沒列它。

具體例子:
- 照 spec 實作後,「`--jobs` 的記憶體上限與份數」會寫進規格閘(已很大)或 guard-kill(責任範圍外)。
- 修正關卡的讀者看不到「工作樹建立現在會排隊」這件事。

⚠:機器附加資料寫 guard-kill「沒寫負責範圍」,但該檔 frontmatter 第 8 行有 responsibility,兩者不符,以檔案為準。

建議的落點:
- 合併判讀與 `baseline_share` 寫進 `Systems/guard-kill`。
- 份數、記憶體上限、佇列、中斷與帳寫序,另開一篇 choice-kill 執行端的節點。
- `_isolated_worktree` 加鎖補一行進 `Systems/代碼審修正關卡`。

## 總結

Q1 對齊(JUnit 入口例外見 finding 1);Q2 大致對齊(finding 3);Q3 不對齊(finding 1 為 major,finding 2、4 為小差異);Q4 部分不對齊(finding 5)。

不對齊共 5 條
