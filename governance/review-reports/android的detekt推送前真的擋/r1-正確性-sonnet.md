severity: blocker

## 審查報告:android的detekt推送前真的擋 r1(正確性席)

本席在 detekt 1.23.8 實測,用 `/tmp` 底下的最小專案跑。實驗目錄已刪。

### 1. 參數檔不存在時,detekt 沒有 SARIF,整條命令被自動放行,探針永遠判不到

severity: blocker
blocking: 是——該擋沒擋,而且正好是 spec 標題「不再安靜放行」要解的情境。

- spec 段落:〈範圍〉第 3 條、〈用詞〉探針的最後一點、〈範圍〉第 6 條的參數檔提醒。
- 引句:「探針那次 detekt 沒產出可解析的結果時,沿用既有判定:整條命令記成「跑不出結果」;這種情況不再判探針」
- 重現:宣告命令寫 `detekt @build/lumos/detekt-typeinfo.args --input {LINT_FILES_CSV} ...`。參數檔放在 `build/`,通常被 git 忽略。全新 clone、第二個 worktree、跑過 `./gradlew clean` 之後,這個檔都不存在。
- 實測 `detekt @build/lumos/nonexistent.args --input X.kt --report sarif:out`:印出 `Could not read file ...`,rc=1,沒有產出 SARIF。
- file: `scripts/lumos:38353`(`_lint_run_and_parse` 讀不到暫存檔就回 `([], False)`)。
- file: `scripts/lumos:39147`(`_lint_new_verdict` 把 `not ok` 記成 `kind: "env"`)。
- file: `scripts/lumos:39003`(`_lint_new_classify` 對 env 類設 `autopass=True`,狀態變 `env-unavailable`,不擋)。
- 結果:型別資訊「根本沒接上」這個最常見狀態走不到 `probe-missing`,推送被放行,只記一筆 fail-open。
- spec 補的「參數檔不存在」提醒只在 `lumos lint-check` 與健檢印(〈範圍〉第 6 條),推送閘不看,所以沒有擋。

### 2. 參數檔的路徑含空白時,detekt 同樣沒有 SARIF,同樣被自動放行

severity: major
blocking: 是——真實環境常見的輸入下,該擋沒擋。

- spec 段落:〈用詞〉型別參數檔、初始化腳本。
- 引句:「內容是 detekt 指令列參數,一行一個:`--classpath`、組好的 classpath、`--jdk-home`、JDK 路徑、`--jvm-target`、目標版本。」
- 重現:參數檔內容 `--classpath` 換行 `/…/dir with space/x/cc.jar`,再跑 `detekt @該檔 --input P.kt`。
- 實測:detekt 的參數解析器(JCommander)把一行裡的空白當分隔,印出 `Was passed main parameter 'with' but no main parameter was defined`,rc=1,沒有 SARIF。
- 加雙引號(`"…"`)或反斜線跳脫(`\ `)都一樣失敗,沒有任何寫法能救。
- 常見會含空白的路徑:`--jdk-home` 指到 Android Studio 內建 JDK(`/Applications/Android Studio.app/Contents/jbr/...`)、使用者家目錄含空白、Windows 的 `Program Files`。spec 說「JDK 用跑 Gradle 的那個 JDK」,所以由 Android Studio 啟動 Gradle 時就會中。
- 後果同第 1 條:走 env 類、自動放行,探針不判。
- 同一份參數檔去掉空白後(`nospace/cc.jar`)正常出 SARIF,所以原因只在空白。
- spec 的 2026-11-04 實測只涵蓋沒有空白的路徑。
- 初始化腳本沒有被要求偵測或拒寫含空白的路徑。

### 3. 路徑含分號時,detekt 也拆路徑,逗號護欄擋不到

severity: minor
blocking: 否——只有檔名含分號才中,極罕見,但誤判方向是放行。

- spec 段落:〈範圍〉第 2 條「含逗號的路徑」。
- 引句:「某支要檢查的檔的相對路徑含逗號時,detekt 會把它拆成兩個不存在的路徑而整條拒跑」
- 重現:`detekt --input "semi/a;b.kt"` 印出 `ParameterException: Provided path 'semi/a' does not exist!`,沒有 SARIF。
- 結果:`comma-path` 只判逗號。含分號的檔走 env 類自動放行,不會擋。
- 護欄應判 detekt 實際的分隔字元集(逗號與分號)。

### 4. 同一條命令同時有兩種佔位符時,探針加到哪個佔位符沒寫

severity: minor
blocking: 否——⚠ 判不準。spec 沒寫這個輸入怎麼處理,我沒有走到會判錯的程式路徑。

- spec 段落:〈範圍〉第 3 條「在現在版那次把探針檔加進輸入」,以及 S1。
- S1 只驗替換結果。
- 輸入:命令同時帶 `{LINT_FILES_CSV}` 與 `{LINT_FILES}`,例如 `detekt --input {LINT_FILES_CSV} ... ; other {LINT_FILES}`。
- spec 沒寫探針併進哪個佔位符,也沒寫「這條命令有逗號路徑」的判定是否讓整條不跑,包括只靠 `{LINT_FILES}` 的那一半。
- file: `scripts/lumos:39135` 現行 `_lint_cmd_with_files` 單一呼叫,沒有探針注入點可對照。

### 5. 初始化腳本只涵蓋套了 Android 外掛的模組,純 Kotlin/JVM 模組的型別資訊與協程探針可能對不上

severity: minor
blocking: 否——⚠ 沒有可跑的 Android 專案,只靠 spec 文字推論。

- spec 段落:〈用詞〉初始化腳本。
- 引句:「每個套了 Android 外掛的模組,取指定變體(預設 debug,可用 `-PlumosDetektVariant=<變體>` 換)的編譯 classpath」
- 輸入:乾淨架構常見的 `:domain` 純 Kotlin 模組,協程依賴用 `implementation` 只宣告在它自己身上,改動檔在 `:domain`。
- 疑慮:classpath 聯集可能不含協程 jar 或該模組的依賴,那支檔含 `kotlinx.coroutines` 字樣就要求協程探針,結果缺規則而被判 `probe-missing`。補法(重跑初始化腳本)修不了,只能放行。
- S11 只驗「真的 Android 專案」,沒涵蓋這個形狀。

### 已逐項核對、查無 finding 的重點

- **探針結果怎麼認出來再拿掉**:detekt 回報 `file:///` 絕對路徑加百分號編碼,不帶 `originalUriBaseIds`。
  - `_lint_run_and_parse` 會剝掉 `file://`、解碼、相對化,macOS 的 `/tmp` 與 `/private/tmp` 也處理了。
  - 探針放 `.lumos/lintbase-x/probe/`,不在 `.../head/` 底下,所以 `path_prefix` 剝不掉它,可以靠留下的 `probe/` 前綴認出。
  - 實測探針檔還會被 `MagicNumber`、`FunctionOnlyReturningConstant` 等規則命中,所以「探針檔的所有結果都拿掉」這句是必要的。
  - spec 對這點寫得對。
- **探針只加在現在版**:差集 `_lint_new_diff_claims` 只比指紋次數。探針結果先拿掉就不進差集,基準版少的探針結果不會影響別的指紋。
- **共用設定下四條探針規則會響**:用 `configs/detekt/android.yml` 加協程 jar,`InjectDispatcher`、`RedundantSuspendModifier`、`SuspendFunWithFlowReturnType` 都響。
- **`{LINT_FILES_CSV}` 與既有 `{LINT_FILES}` 的子字串關係**:前者不含後者作為子字串,所以 `_lint_run_and_parse` 的「佔位符沒換掉就不跑」守衛(`scripts/lumos:38382`)不會誤擋。spec 的 S2 已要求改兩種都認。
- **放行鍵 `detekt-probe:<規則名>`**:`cmd_lint_waive` 接受任意字串鍵,放行檔又是每個專案各一份(`.lumos/lint-waivers.json`),所以不會跨專案。只比規則名時,自訂規則集若撞名會一起放行,這個機率低,沒有給出實例,不標。
- **`@參數檔` 讓缺型別提醒失效**:判定函式把任何 `@` 開頭的詞當「看不到完整參數」而不印缺型別提醒(`scripts/lumos:37874`)。spec 的新提醒補上「檔不存在」這一條。
- **detekt 官方文件說「`--input` 逗號分隔」**:實測 `--input "a b.kt,a b.kt"` 在含空白的檔名下沒問題,檔案路徑含空白不是問題;問題只在參數檔。
- **Windows 路徑與引號**:本工具以 `subprocess.Popen(shell=True)` 加 `shlex.quote`,既有 `{LINT_FILES}` 同一做法。逗號佔位符沿用同一個慣例,沒有新增風險類別。

### 附上的固定席節點

- [[Issues/推送閘對Android的detekt只記錄不擋]]:本案就是它的修法,不影響其宣稱。
- 其餘附的節點(`pitfalls-lint-adapter`、`linter精選目錄`、`android-e2e-acceptance`、`lint-declaration-health`)都是文件落點或舊否決。我只對照了節點名稱與 spec 引用,沒有逐篇讀全文,不影響判斷。

### 實務隱患風險類

- **推送閘 fail-open**:有,見 finding 1、2、3。三條都落在同一條既有的「跑不出結果=環境類」路徑上,這條路徑把本案新增的錯誤也吞掉了。
- **差集/基準版比錯**:無。探針只加在現在版,結果先剔除再比差集,基準與現在用同一份參數檔,所以兩邊對稱。
- **資安/金流/對外**:無,與 spec 所述一致。
- **效能/記憶體**:無新發現。探針只多分析兩個小檔。

最嚴重 severity:blocker;blocking 共 2 條(finding 1、2)。
