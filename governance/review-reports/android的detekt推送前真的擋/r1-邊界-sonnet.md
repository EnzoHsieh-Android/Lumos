severity: blocker

固定席節點(五篇)判讀:
- `Issues/推送閘對Android的detekt只記錄不擋`:本案正是要結它,不衝突。
- `Systems/pitfalls-lint-adapter`、`Systems/linter精選目錄`、`Systems/lint-declaration-health`、`Systems/android-e2e-acceptance`:我沒有逐篇打開節點全文,只依 spec 引用的主張判讀。判讀為不影響,因為 spec 只新增佔位符與探針,不改既有 `{LINT_FILES}` 行為。唯一例外是 finding 6(寫死 `{LINT_FILES}` 的提示文字漏列的處所)。

下面的 detekt 實驗都用本機 detekt 1.23.8、JDK 17,在 `/tmp/lumos-seat-work/` 底下做,做完已刪。

**1. 型別參數檔不存在時,推送閘靜默放行,不會擋**
severity: blocker
blocking: 是(「真的擋」的核心承諾在最常見情境下落空)
- spec 段落:用詞「型別參數檔」、範圍 3「探針」、範圍 6 的 `@<路徑>` 提醒、「不做」第三條。
- 問題:宣告命令帶 `@build/lumos/detekt-typeinfo.args`,而該檔不存在。
- 情境:新 git worktree、`./gradlew clean`、剛 clone、Gradle 初始化腳本失敗或沒有網路。
- 實驗:`detekt @nonexist.args --input src/A.kt --report sarif:o1.sarif` 印出用法說明、不產生 SARIF 檔。
- 程式行為:file: `scripts/lumos:38355` 的 `_lint_run_and_parse` 讀不到 SARIF 就回 `([], False)`。file: `scripts/lumos:39146` 把它記成 `kind:"env"`。file: `scripts/lumos:38996` 的 `_lint_new_classify` 對 env 類自動放行並記帳。
- 後果:`probe-missing` 的擋下路徑根本到不了,因為探針只在 detekt 有產出時才判。
- spec 對這件事只在 lint-check 與健檢加「檔案不存在」提醒(範圍 6),推送閘本身沒處理。
- 引句:「只看檔在不在,不讀內容。」

**2. 型別參數檔內容壞掉時,同樣靜默放行**
severity: major
blocking: 是(同一根因,輸入不同,各要一條先紅測試)
- spec 段落:用詞「型別參數檔」、初始化腳本、實務隱患「多模組聯集」。
- 實驗(三種輸入都是 detekt 印用法、不產生 SARIF):
  - classpath 路徑含空白(例如 `/Users/John Smith/.gradle/...`,一個參數一行也一樣,加雙引號也沒用,`quoted rc=1`),detekt 印用法、不產生 SARIF。
  - `--classpath` 後面是空行,detekt 印用法、不產生 SARIF。
  - `--classpath` 後面直接接 `--jdk-home`,detekt 印用法、不產生 SARIF。
- 純 Kotlin/JVM 專案,或初始化腳本只認 Android 外掛而聯集為空時,腳本很可能寫出空 classpath。這一點是我從 spec 推得,沒有跑 Gradle 驗證。
- 後果:每次推送都走 env 自動放行,看起來像「有檢查」,實際零檢查。
- spec 完全沒寫初始化腳本在「零個 Android 模組」時的行為,也沒寫寫出的檔案要先驗證。
- 引句:「所有模組聯集成一份、去重、只留存在的路徑。」

**3. `--jvm-target` 取自跑 Gradle 的 JDK 版本,新 JDK 讓 detekt 拒跑,又走 env 放行**
severity: major
blocking: 是
- spec 段落:用詞「初始化腳本」。
- 情境:Gradle 跑在 JDK 25(或任何高於 22 的版本)。
- 實驗:`--jvm-target 21` 正常(探針兩條都響)。`--jvm-target 25` 時 detekt 拋出 `Invalid value (25) passed to --jvm-target, must be one of [1.6, ..., 22]`,不產生 SARIF。
- 後果:這跟 finding 1 一樣是靜默放行。
- spec 只寫「JDK 用跑 Gradle 的那個 JDK」,沒有限制或夾住 jvm-target 的上限。
- 引句:「JDK 用跑 Gradle 的那個 JDK。」

**4. 命令列長度:數百到上千支檔時,整道閘例外放行**
severity: major
blocking: 是
- spec 段落:用詞「逗號佔位符」(整串一次加引號)。
- 問題:CSV 整串成為 `sh -c` 的單一參數。
- 長度估算(算術,沒在 Linux 實測):單支路徑含快照前綴 `.lumos/lintbase-xxxx/head/` 約 110 到 130 位元組。約 1100 支 `.kt` 檔(大型改名或搬套件)就超過 Linux 單一參數上限 `MAX_ARG_STRLEN=131072`,CI 多半是 Linux。
- 實驗:本機是 Darwin,`ARG_MAX=1048576`,18.5 萬位元組的字串在這裡過得去。
- 程式行為:file: `scripts/lumos:38355` 的 `_lint_run_and_parse` 只接 `TimeoutExpired`,`Popen` 丟出 `OSError`(E2BIG)往上跳。file: `scripts/lumos:67822` 的呼叫端 `except Exception` 把它變成整道新增告警閘 fail-open,所有命令都沒檢查。
- 既有 `{LINT_FILES}` 理論上有同樣問題,但新佔位符是這案新加的路徑,該自己設上限。
- spec 沒有檔數或位元組數的分批、上限或降級規則。⚠ Linux 的 E2BIG 行為我沒有在 Linux 實跑,依據是核心常數與 `Popen` 行為。
- 引句:「用逗號串成一個字串、整串一次加 shell 引號」

**5. 探針被專案設定排除,放行路徑能走,但訊息會誤導**
severity: minor
blocking: 否(spec 已有放行機制,只是訊息要補)
- spec 段落:實務隱患「探針規則被消費專案自己的設定關掉」。
- 實驗:專案設定對 `RedundantSuspendModifier` 加 `excludes: ['**/probe/**']`,探針就不響。`.lumos/` 隱藏目錄本身不影響,探針照響。
- 問題:spec 只提到「關掉那條」,沒提 `excludes` 路徑排除、`active:false` 以外的各形狀。擋下訊息說「型別資訊沒接上」,但這種情況根因是設定,不是型別資訊,會誤導使用者重產型別參數檔。
- 引句:「訊息點名規則並給放行指令;放行綁規則名,關一次就好。」

**6. 冒煙與風險分級遇逗號路徑沒有定義**
severity: minor
blocking: 否(不擋推送,只影響診斷)
- spec 段落:範圍 2 與範圍 4。
- 情境:專案前三支 `.kt` 檔裡有路徑含逗號的檔。
- 實驗:`--input "src/x,y.kt,src/A.kt"` 時 detekt 拒跑,rc=1、不產生 SARIF。
- 程式行為:file: `scripts/lumos:37948` 的 `_lintcheck_smoke_cmd` 取 `git ls-files` 前 3 支,沒有逗號檢查。
- 後果:冒煙會報「命令跑不出可解析 SARIF(task 不存在/工具沒裝?)」,這是假診斷。範圍 2 的 `comma-path` 只寫了新增告警閘。
- 引句:「這條命令這次不跑,記成新的一類「沒跑到」」

**7. 逾時走 env 自動放行,與「擋」衝突**
severity: major
blocking: 是
- spec 段落:實務隱患「探針多花的時間」、範圍 3。
- 問題:帶型別資訊的 detekt 要載入整個 Android classpath(數百個 jar),啟動比無型別慢,而且基準版與現在版各跑一次。
- 程式行為:file: `scripts/lumos:38355` 的 `_lint_run_and_parse` 逾時回 `([], False)`,走 `kind:"env"`,自動放行。
- spec 只寫「整條命令仍受既有的時間預算管」,沒有指出「預算管」的結果是放行而不是擋。
- ⚠ 我沒有量真實 Android 專案的 detekt 耗時,所以只能確定程式路徑,不能確定逾時會多常發生。
- 引句:「整條命令仍受既有的時間預算管。」

**8. 沒有 Android 外掛的純 Kotlin 模組,初始化腳本沒有輸出定義**
severity: major
blocking: 是(合併進 finding 2 的處置也可)
- spec 段落:用詞「初始化腳本」、範圍 5、S11。
- 問題:腳本只取「每個套了 Android 外掛的模組」。多模組專案裡的純 Kotlin/JVM 模組(`kotlin("jvm")`、`java-library`)的 classpath 與編譯輸出不在聯集裡。
- 後果:改到這類模組的檔時,它們依賴的專案內符號解析不到。
- S11 只驗「多模組、有 Compose 與協程」的 Android 專案,沒有驗純 Kotlin 模組。
- 引句:「每個套了 Android 外掛的模組,取指定變體(預設 debug」

**9. 各節核對結果**
- PRIOR-ART、RETIRE-IF、回退、天花板、REVISIT:已讀,無 finding。
- 驗收條款 S1 到 S10:已讀。無獨立 finding,但缺上面 1 到 4 的先紅測試(缺檔、空 classpath、空白路徑、jvm-target 過高、檔數超長),補條款即可。

**實務隱患風險類逐類**
- 並行/多 worktree:有,見 finding 1。`build/` 不進版控,新 worktree 一律沒有型別參數檔。
- 資源上限:有,見 finding 4 與 7。
- 外部工具版本:有,見 finding 3。
- 安全、金流、不可逆:無,spec 已說明,且我查證過沒有新增對外呼叫。

最嚴重 severity:blocker;blocking 共 6 條(finding 1、2、3、4、7、8),另 2 條 minor(5、6)。
