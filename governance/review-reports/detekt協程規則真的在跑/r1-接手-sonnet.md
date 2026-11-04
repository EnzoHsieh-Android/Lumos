severity: major

# 設計審報告:detekt協程規則真的在跑_計劃(r1,接手-sonnet 席)

白話:這份 spec 的診斷是對的。detekt 沒拿到型別資訊時,要型別的規則會安靜地不跑,我在本機用 detekt 1.23.8 重現了。但它把「標準接法改帶型別參數」當成一句話帶過,沒說 Android 專案的 classpath 要從哪來。另外幾處對程式現況的宣稱和實際不符,還有幾處舊說法沒列進同步範圍。三個月後照這份去接 KDS 或 mOrangePos,會在「classpath 填什麼」這一步撞牆。

我實測用的是一支埋了錯的探針檔,加上本機 Gradle 快取裡的 coroutines、stdlib 和 Compose runtime 的 jar。實驗目錄已刪。

## 逐節結論

- 前言、白話、PRIOR-ART、RETIRE-IF:已讀,無 finding。三個交叉引用 `Projects/社群規則第二批_計劃`、`Systems/棧別提問表態閘`、`Systems/android-e2e-acceptance` 都存在。
- 用詞:見 F7(「detekt 指令列」沒定義)和 F8(規則名比對)。
- 範圍:見 F1、F5、F6、F7。
- 不做:已讀。「不替 Gradle 任務接法做探針」有寫,但 S4 的提醒判定留了洞,見 F3。
- 實務隱患:第四條有事實錯誤,見 F4。第二條(吞取消訊號)和第五條(舊否決對照)已核對,屬實。
- 驗收條款:見 F2、F3、F5、F8、F9。
- 回退、天花板、REVISIT:見 F6、F10。

---

**F1 標準接法只說「帶型別參數」,沒給 Android 專案能走通的 classpath 取得路徑**
- 位置:範圍第三、四條(「設定開頭的用法改成帶型別參數的標準接法」、「樣板改帶型別參數」)。
- 問題:
  - spec 沒說 `--classpath` 的值怎麼來。Android 的依賴 jar 散在 Gradle 快取,路徑帶版本號和雜湊目錄。
  - AAR 的 `classes.jar` 在 `transforms-3/<雜湊>/transformed/<名>/jars/classes.jar`,沒有穩定路徑。
  - `--classpath` 不展開萬用字元。我用 glob 傳入,InjectDispatcher 和 SuspendFunWithFlowReturnType 都沒響,只有不需要 classpath 的 SleepInsteadOfDelay 響了。
  - 樣板如果寫死快取路徑,依賴一升版或快取一清就失效,跟 spec 自己引用的 `/tmp` 放 jar 前科是同一類。
  - 現有的兩個消費專案 KDS 和 mOrangePos,`.lumos/lint.json` 都是無 classpath 的樣板。本案落地後,它們跑 `--smoke` 會從綠轉紅(S1),而文件沒有可抄的修法。
  - spec 要求 S1 訊息「給補型別參數的修法」,但沒定義那個修法的內容。
- 佐證:
  - file: `/Users/enzo/.gradle/caches/transforms-3/f7b2b5a01b24d53f08b69325d2fbbbf1/transformed/runtime-release/jars/classes.jar`(Compose runtime 的真實位置)。
  - file: `/Users/enzo/Citrus_KDS/.lumos/lint.json:2`(無 classpath 的樣板)。
  - detekt 官方 type-resolution 頁(我用 WebFetch 查的)只說 CLI 要自己提供 `--classpath` 和 `--jvm-target`,沒給 Android 的取法。
  - file: `docs/lumos-toolchain-knowledge/Projects/Android協程與API協同機械審_調研.md:57`(「Android 專案要嘛用 Gradle 外掛的 detekt<Variant> 任務,要嘛 CLI 帶 classpath」),沒有 recipe。
  - 可行的最小解其實存在(coroutines 加 stdlib 加 `--jdk-home`,我測過五條規則會響),但那不是 Android 完整 classpath。spec 沒選、也沒說明。
severity: major
- blocking: 是。核心交付物(標準樣板)的關鍵參數沒定義,照做的人走不通,且落地後會讓兩個現有消費端的冒煙翻紅。

**F2 S5 的 [manual] 證據指向的「做法」,調研筆記裡其實沒有**
- 位置:S5 的 `[manual:…做法記在調研筆記]`。
- 引句:「兩條皆響、設定驗證通過;做法記在調研筆記」
- 問題:調研筆記只有兩句結論,沒有實際指令、classpath 內容、探針檔內容。尤其 collectAsState 要響,classpath 裡得有 Compose runtime 的 `classes.jar`,筆記完全沒寫。接手的人重現不了,也沒法驗證「設定驗證通過」是不是對著當時那份 `android.yml`。
- 我自己補跑驗證了:補開兩條加上 `ForbiddenMethodCall` 後設定通過。
  - 帶 `classes.jar` 時,SuspendFunWithCoroutineScopeReceiver 和 ForbiddenMethodCall 會響。
  - 沒帶 `classes.jar` 時,collectAsState 那條完全不響,也不報錯。
- 佐證:file: `docs/lumos-toolchain-knowledge/Projects/Android協程與API協同機械審_調研.md:46`、`:49`(僅有結論句)。
severity: major
- blocking: 是。這是唯一的驗收證據,影響所有消費專案的共用設定,而它指向的重現方法不存在。

**F3 S4 把「命令走 Gradle」一律當成不用提醒,但 `./gradlew detekt` 本身沒有型別解析**
- 位置:S4。
- 引句:「命令走 Gradle 或已帶 classpath 時兩處都 應 不提醒」
- 問題:
  - detekt Gradle 外掛的純 `detekt` 任務明文是「Runs detekt WITHOUT type resolution」。只有 `detektMain`、`detektTest`、`detekt<Variant>` 才有型別。
  - 所以宣告成 `./gradlew detekt` 的消費專案,會出現本案要消滅的那種靜默不跑,卻被 S4 明確豁免。
  - 同一個靜態函式只要比對 `gradlew\s+detekt(\s|$)` 就能提醒,成本很低。
  - spec 的天花板 2 只說「Gradle 任務接法驗不到」。但 S4 的措辭加上 RETIRE-IF 的「都改走 Gradle 任務」,會讓接手的人以為 Gradle 是安全路徑。
- 佐證:
  - file: `scripts/test_lumos.py:36076`(測試本身就用 `./gradlew detekt` 當範例宣告)。
  - file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:80`(KDS 的 `detektMain` 在 Android 模組並不存在)。
  - detekt type-resolution 官方頁:`detekt` 任務是 WITHOUT type resolution。
severity: major
- blocking: 是。靜默失效的同一類缺口,被條款明文豁免,而且很容易靜態補上。

**F4 實務隱患第四條對新增告警閘的描述,與程式現況不符**
- 位置:實務隱患第四條。
- 引句:「之後新寫的 collectAsState 或掛在 CoroutineScope 上的 suspend 函式會被擋」
- 問題:
  - 推送前的新增告警閘只執行含 `{LINT_FILES}` 佔位符的宣告,沒帶的降級成「只報不擋」。標準樣板用 `--input <src 目錄>`,沒有該佔位符,兩個現有消費專案也都沒有。
  - 所以對標準樣板而言,補開的兩條規則在推送時只會顯示,不會擋。spec 說「這是本案要的效果」,實際沒有這個效果。
  - 這一條還影響第二個前提:「合併基準與這次改動各跑一次、只擋新增」對這種宣告根本沒發生。
- 佐證:
  - file: `scripts/lumos:38889`(`_LINT_NEW_FILES_TOKEN not in cmd` 時進 `report_only`,並印「逐命令降級」註解)。
  - file: `scripts/lumos:58862`(`_push_gate_covers` 只在命令含佔位符時成立)。
  - file: `scripts/lumos:38287`(「命令沒有這個佔位=核心無法為它做基準比對」)。
severity: major
- blocking: 是。spec 對實際擋推行為的事實宣稱是錯的,接手的人會以為 `collectAsState` 已被擋。

**F5 知識同步範圍:舊說法散在 lands_in 之外,特別是「已開」會被讀成「有在擋」**
- 位置:範圍的「文件」條,以及 frontmatter 的 `lands_in`(只有兩篇)。
- 問題:受影響的地方不只 spec 列的兩個:
  1. `Systems/效能檢核目錄.md`
     - 第 61 行「GlobalScope 裸用(…⚠預設關——2026-07-27 起共用 config 已開…)」
     - 第 63 行「SuspendFunSwallowedCancellation,⚠預設關——共用 config 已開」
     - 第 64 行「CouldBeSequence … 共用 config 已開」
     - 第 67 行「ArrayPrimitive/ForEachOnRange 現成規則」
     - 這些寫「已開」,讀起來就是有在擋。實際上除了 GlobalCoroutineUsage,其餘都要型別資訊才跑。
     - 第 63 行還把 SuspendFunSwallowedCancellation 描述成「withContext 內 catch CancellationException」。實際規則是 `runCatching` 內呼叫 suspend,描述本身也不準。
     - 這篇不在 `lands_in`。
  2. `skills/kotlin-idioms/SKILL.md`
     - spec 只列 R12 和機檢接線段。
     - 但還有第 68 行(SuspendFunWithFlowReturnType「預設開」)、第 82 行(InjectDispatcher「預設開」)、第 95 行(SuspendFunSwallowedCancellation「預設關,要開」)、第 98 行(GlobalCoroutineUsage「預設關,要開」)、第 101 行(R12 的 SleepInsteadOfDelay、RedundantSuspendModifier「預設開」)、第 108 行(R13 `ForbiddenMethodCall` 配置 `collectAsState`)。
     - 這些「預設開」同樣在無型別資訊時不響。
     - 第 101 行的標題「寫進 detekt 設定就好」本身就是錯誤暗示。
     - 這個檔沒有任何 Systems 節點掛它(我 grep 過 `skills/kotlin-idioms`),所以沒有圖譜把關能提醒要改哪幾行。
  3. `Systems/linter精選目錄.md`
     - 第 28 行 KEY(「標準接法立=…開預設關的 GlobalCoroutineUsage/SuspendFunSwallowedCancellation/CouldBeSequence」)和第 122 行(同樣只講「有裝≠有開」)。
     - 需補「有開≠有跑」。這篇在 `lands_in`,但 spec 只說「樣板改帶型別參數」,沒說這兩處要改。
  4. `Systems/lint-declaration-health.md`
     - 第 26 行(KDS 案)、第 48 至 50 行的冒煙層描述、第 55 至 61 行的範例、第 80 行(「KDS … `lint-check --smoke` 綠」)。
     - 本案落地後,KDS 和 mOrangePos 的冒煙會翻紅,第 80 行變成過期陳述。
     - 冒煙層現在也會驗「規則有沒有響」,不只「有沒有 SARIF」。
  5. `Projects/Android協程與API協同機械審_調研.md`
     - 現況表第 27、28 行寫「共用 detekt 設定已開」,第 33、34 行寫「共用設定沒禁」。本案落地後後兩條立刻過期。
     - 表格自己標了「(2026-11-04 盤點,以程式碼為準)」,不算謊言,但接手的人會先讀到它。
- 同族漏網:CouldBeSequence 和 ArrayPrimitive 也要型別資訊,我實測不帶 classpath 時兩條都不響,帶了 stdlib 才響。
  - CouldBeSequence 是 `android.yml` 自己主動開的三條之一(「效能三問⑤前半」)。
  - spec 只點名 SuspendFunSwallowedCancellation,探針五條也沒包含它。
  - 探針五條通過只能間接推斷 CouldBeSequence 在跑,沒有明說。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:61`
  - file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:63`
  - file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:64`
  - file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:67`
  - file: `skills/kotlin-idioms/SKILL.md:68`
  - file: `skills/kotlin-idioms/SKILL.md:82`
  - file: `skills/kotlin-idioms/SKILL.md:95`
  - file: `skills/kotlin-idioms/SKILL.md:98`
  - file: `skills/kotlin-idioms/SKILL.md:101`
  - file: `skills/kotlin-idioms/SKILL.md:108`
  - file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:122`
  - file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:80`
  - file: `configs/detekt/android.yml:14`(CouldBeSequence 開啟處)
severity: major
- blocking: 是。這是本席主題:改了「標準接法」卻只更新兩篇,最容易被讀到的「已開」字樣會留在原地誤導後人。

**F6 S4 的靜態提醒只看「有沒有帶 `--classpath`」,指到過期或不存在的路徑照樣通過;守衛只剩手動冒煙**
- 位置:S4,以及天花板。
- 引句:「當 kt 命令是 detekt 指令列且沒帶 `--classpath` 或 `-cp` 時」
- 問題:
  - 我給 `-cp /nonexistent.jar`,detekt 沒有任何警告、也沒有報錯,所有要型別的規則靜默不響。
  - 所以 Gradle 快取路徑因依賴升版或快取清理而失效後,S4 提醒不會出現。
  - 唯一能抓到的是冒煙探針,而冒煙是手動執行,不在 doctor 也不在 CI。
  - 天花板第 1 條寫的是「`--input` 指錯目錄」,沒涵蓋這種 classpath 失效。這正是 spec 自己引用的 `/tmp` jar 前科的同一個形狀。
  - REVISIT 兩條都沒有「定期跑冒煙」的回頭條件。
- 佐證:
  - 我的實驗:`-cp "/nonexistent.jar"` 無輸出、無錯誤。
  - file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:22`(冒煙維持手動)。
  - file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:69`(冒煙不進 `doctor --ci`)。
severity: minor
- blocking: 否。spec 有承認冒煙是手動層,但回頭條件缺,屬於可補的缺口。

**F7 「detekt 指令列」沒有定義判準,樣本之間會互相打臉**
- 位置:範圍第一、二條,S3、S4。
- 引句:「任何 kt 的 detekt 指令列(不限引用共用設定」
- 問題:
  - 現存宣告形狀至少有四種:`detekt …`、`/opt/homebrew/bin/detekt …`、`java -jar …detekt-cli-1.23.7-all.jar …`(`lint-declaration-health.md` 第 55 行的 KDS 前身)、`./gradlew detekt`。
  - 共用設定路徑本身含字串 `detekt`(`configs/detekt/android.yml`),子字串比對會把任何引用它的命令都判成 detekt 指令列。
  - S3「命令不是 detekt 時完全不跑探針」靠的就是這條判準。沒定義的話,測試和實作會各寫各的。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:55`
  - file: `scripts/test_lumos.py:36067`
  - file: `scripts/test_lumos.py:36076`
severity: minor
- blocking: 否。實作時可補,但驗收條款的分類邊界要先寫清楚。

**F8 探針比對規則名時,SARIF 的 ruleId 帶前綴,而 CI 沒有 detekt、測試只能用假 SARIF**
- 位置:範圍第一條,S1。
- 引句:「比對探針五條有沒有響」
- 問題:
  - 真實 detekt 1.23.8 的 SARIF `ruleId` 是 `detekt.coroutines.GlobalCoroutineUsage` 這種帶前綴形式,不是裸規則名。
  - CI 是零依賴、沒有 detekt(`ci.yml` 沒有任何 detekt 步驟)。S1 的測試必須用假 SARIF。
  - 若假 SARIF 寫裸名,測試會綠、實機全部判「缺」。
  - 前綴對照在 spec 沒有提到。
- 佐證:
  - 我的實驗:同一份探針檔的 SARIF `ruleId` 全部帶 `detekt.<規則集>.` 前綴。
  - file: `scripts/lumos:38209`(`_lint_run_and_parse` 原樣回傳 `ruleId`)。
severity: minor
- blocking: 否。

**F9 健檢 F 段新判斷要求「不管格式有沒有問題」,但畸形宣告形狀會讓新碼崩潰**
- 位置:範圍第二條。
- 引句:「只要宣告讀得出來(合法 JSON)就判,不管格式有沒有問題」
- 問題:
  - `_lint_load_and_validate` 只在 JSON 解析成功時給 `config`,但沒保證是 dict。`{"kt": 5}`、`{"kt": [5]}` 或頂層是 list,迭代或對 int 做字串比對會 TypeError 或 AttributeError。
  - 既有冒煙碼有 `isinstance(config, dict)` 和 `isinstance(cmds, list)` 兩層守衛,新碼要明寫一樣的守衛。
  - 同族:KDS 曾經寫過 `{"detekt": {"kt": {"cmd": …}}}` 這種畸形形狀,有測試。
- 佐證:
  - file: `scripts/lumos:37768`(`lf.get("config")` 取用方式)。
  - file: `scripts/lumos:37775`(冒煙迴圈的 `isinstance` 守衛)。
  - file: `scripts/test_lumos.py:36104`(畸形宣告測試)。
severity: minor
- blocking: 否。

**F10 S1 的訊息和回頭條件對「collectAsState 那條在跑」給了過強的保證**
- 位置:S1 與不做清單。
- 引句:「五條都響時 應 退出碼 0 並印一行探針確認規則有在跑」
- 問題:
  - 探針五條都不含 ForbiddenMethodCall(collectAsState 那條)。只用 coroutines 加 stdlib 通過探針後,印出「規則有在跑」。
  - 但我實測:classpath 沒有 Compose runtime 的 `classes.jar` 時,`ForbiddenMethodCall` 對 `collectAsState` 完全不響。
  - 不做清單有說探針不驗它,但訊息文字沒有限縮範圍。接手的人看到「規則有在跑」會當成共用設定全部有效。
  - 實務隱患第四條還說會擋,兩者疊在一起(見 F4)。
- 佐證:
  - 我的實驗:帶 coroutines 加 stdlib、不帶 Compose,collectAsState 不響;補上 `classes.jar` 後響。
severity: major
- blocking: 是。印出的保證語句和實測行為不一致,可能讓人誤信 `collectAsState` 已受檢查。修法是改文字限縮範圍,代價很低。

---

## 圖譜固定席逐條判

- `Systems/lint-declaration-health`
  - 判:不影響它宣稱的合約和行為。
    - 「只准有一處替換 `{LINT_FILES}`」的白名單守衛 `t_lint_files_substitution_has_one_implementation`:只要新增的探針碼不提到 `{LINT_FILES}` 字面或 `_LINT_NEW_FILES_TOKEN` 就不會翻紅。spec 說探針是整段換 `--input` 值,是不同的替換。實作時別去讀取該 token 就好。
    - 冒煙維持手動的前提不變。
  - 文字層有舊說法要更新,見 F5 第 4 項。
- `Systems/linter精選目錄`
  - 判:不影響它的行為宣稱,標準接法本來就是要被本案改寫的。
  - 但 KEY 行和第 122 行的措辭要加「有開≠有跑」,且 F1 的樣板值要先決定。
- `Systems/android-e2e-acceptance`
  - 判:不影響。它的 WHY(第 41 行,不選 `shlex.quote` 換進使用者指令)講的是 `{{TEST}}` 佔位符。spec 的「整段換掉 `--input 值`、只有一層引號」確實不疊引號,類比成立。

---

## 實務隱患鏡頭(此功能碰的風險類)

- 靜默失效(探測盲區):有隱患,見 F1、F3、F6、F10。
- 向下相容與既有消費端:有隱患。KDS 和 mOrangePos 冒煙翻紅卻無修法(F1)。新增告警閘降為只報不擋(F4)。
- 知識同步與過期宣稱:有隱患,見 F5。
- 測試可驗性:有隱患。CI 沒有 detekt,S1 到 S4 只能用假檔,S5 是手動且做法沒存(F2、F8)。
- 輸入邊界(shell 引號、`--input=x` 寫法):spec 實務隱患第三條有處理,未見新洞。
- 安全:無。探針跑的是消費專案自己宣告的命令,風險等同它自己的 CI;暫存目錄是獨立建的,跑完刪;沒有外部輸入進入 shell。
- 併發與暫存殘留:無。暫存目錄每次獨立建、跑完刪;spec 沒提共用目錄。
- 效能:無。只在冒煙多跑一次 detekt,冒煙本來就慢而且手動。
- 回退:無。沒寫入任何消費專案的檔,退提交即可。

---

最嚴重 severity 是 major,blocking 共 5 條(F1、F2、F3、F4、F5、F10 中標 blocking 是者:F1、F2、F3、F4、F5、F10,共 6 條)。

更正:blocking:是 的共 6 條(F1、F2、F3、F4、F5、F10),blocking:否 的共 4 條(F6、F7、F8、F9)。
