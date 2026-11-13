severity: major

## b1 連帶 import 對「成員／方法／跨套件」的新觸發字會產生不存在的 import,把原本會過的壞法弄成編譯失敗
severity: major
blocking: 是 判準:規則字面會讓現在能判 killed 的情境,上線後變成弱證據、人裁被拒(誤擋回歸)。
- 段落:範圍 1、〈用詞〉連帶替換、〈實務隱患〉「兩個 import…」。
- 引句:「找檔頭有一整行剛好是 `import <套件>.<T_old>`(沒有 `as` 別名)的那一個——剛好一個就用它的套件」
- 問題:spec 假設 T_new 一定是跟 T_old 同套件的頂層可 import 名稱,但觸發字表不是這樣。我用 `_KT_DT_ROWS` 實際列出,同一列裡混著三種東西:
  - 成員名,例如 D-5 的 `WhileSubscribed`、D-7 的 `navigate`、`showSnackbar`。
  - 點號形式,例如 `SharingStarted.Lazily`、`viewModelScope.launch`、`Color(`、`contains(`。
  - 不同套件的名稱,例如 D-7 的 `Channel`(`kotlinx.coroutines.channels`)、`MutableSharedFlow`(`flow`)、`LaunchedEffect`(`androidx.compose.runtime`);D-10 的 `withTimeout`(`kotlinx.coroutines`)、`HttpTimeout`(`io.ktor`)。
- 具體例,D-5 原本能過:
  - 輸入:檔頭 `import kotlinx.coroutines.flow.stateIn` 與 `import kotlinx.coroutines.flow.SharingStarted`;`--old` 是 `stateIn(scope, SharingStarted.Eagerly, x)`,`--new` 是 `stateIn(scope, SharingStarted.WhileSubscribed(5000), x)`。
  - 判法:old 含 {stateIn, SharingStarted.Eagerly},new 含 {stateIn, WhileSubscribed}。T_new 是 `WhileSubscribed`。T_old 候選裡只有 `stateIn` 有逐一 import,所以剛好一個。
  - 預期:不該加任何 import,因為 `SharingStarted` 已經 import。
  - 字面結果:產生 `import kotlinx.coroutines.flow.WhileSubscribed`。這個名稱不存在,出現 Unresolved reference,整個壞法編譯失敗,判成 killed_unattributed,人裁拒絕。
- 跨套件例:`Channel` 換成 `MutableSharedFlow` 時,會補 `import kotlinx.coroutines.channels.MutableSharedFlow`,同樣編譯失敗。
- 後果:S1 只驗 flatMapLatest 換 flatMapConcat 這種同包頂層函式。其餘情況不是補不到,是把原本能過的改壞。
- 修法方向:只在能證明 T_new 是該套件頂層名稱時才產生。例如 T_new 在 `--new` 裡不能是 `X.T_new` 這種限定存取;或查型錄的套件資料。
- 驗證:`scripts/lumos` 的 `_situation_rule_recipe_problem` 現行只比觸發字集合,沒有任何套件或頂層判斷,見 `scripts/lumos:75729`。

## b2 範圍 1 與〈實務隱患〉對「多個 T_old import」的規則互相矛盾,而且規則依賴工具不知道的資訊
severity: major
blocking: 是 判準:同一事件兩節給出相反判法,實作者無法只靠 spec 得出唯一行為。
- 引句:「零個或多個(不同套件)就不產生」
- 引句:「取跟新觸發字在情境決策表同一列、而且套件相同的那一行;找不到就不產生連帶替換」
- 問題:
  - 範圍 1:多個就不產生。
  - 隱患:多個時取「跟新觸發字套件相同」的那一行。但工具不知道 T_new 的套件,觸發字表只有名稱、沒有套件;那句話無法實作。
  - 另外,「多個(不同套件)」沒說同套件多個怎麼辦。具體例:`--old` 同時含 `debounce` 與 `flatMapLatest`,兩者都來自 `kotlinx.coroutines.flow` 且都逐一 import,兩條 import 同套件,那算一個還是多個?
  - 另外,同一個 T_old 重複 import 同一行時,範圍 1 算一個,範圍 2 的「整行比對恰好一行」會判 error。兩處計數口徑不同。
- 要補:寫死「候選以套件去重」的規則,並刪掉或改寫隱患那句。

## b3 init 與人裁檢查用「唯一 application 模組」當測試模組,常見版面下給出跑不到測試的指令,範圍 4 還會硬擋並印這個錯誤寫法
severity: major
blocking: 是 判準:修補指向的指令在最常見的多模組 Android 版面下本身就是錯的,而且人裁被它擋死。
- 段落:範圍 3、範圍 4、〈實務隱患〉「多模組專案的模組名」。
- 引句:「`lumos init` 偵測到**恰好一個** Android application 模組時,kotlin-junit 與 java-junit 兩個 profile 的 run_cmd 都給 `./gradlew <模組>:testDebugUnitTest --tests '*{method}'`」
- 具體例,Now in Android 式版面:
  - 輸入:`:app` 是 application,`SearchViewModel` 與它的測試在 `:feature:search`(library)。
  - spec 給出:`./gradlew :app:testDebugUnitTest --tests '*onlyLatestQueryShown'`。
  - 實際:`:app` 沒有這支測試,Gradle 對 `--tests` 零命中判失敗,基準非綠,abort。
  - 範圍 4 又會對舊 `test --tests` 設定 rc 2,並建議這個寫法,等於人裁在這種專案被兩頭擋死。
- 其他版面的同類風險:
  - 有 `productFlavors` 的專案,AGP 只產生 `testFreeDebugUnitTest` 這類任務,沒有 `testDebugUnitTest`,指令直接 Task not found。
  - Android app 加一個 JVM 後端模組的 monorepo,後端測試跑不到。
- 〈實務隱患〉只提「測試在別的模組要人手改」,但範圍 4 是拒絕而不是提示。〈天花板〉也沒列 flavor 與「測試所在模組不是 app」。
- 修法方向:範圍 4 的模組應從人裁的 `--file` 或測試所在路徑推,而不是取 application 模組。init 骨架則只能當起點並標示。

## b4 Gradle 偵測的解析規則只寫了「結果」,沒寫字面怎麼讀,極端寫法會判錯
severity: major
blocking: 是 判準:範圍 3、4 的觸發條件是否成立,全看一套 spec 沒定義的解析;不同實作對下列輸入會給出相反結果,且判錯會直接誤擋或給錯模組。
- 段落:〈用詞〉「Android application 模組」、範圍 3、〈天花板〉3。
- 引句:「寫法是外掛 id `com.android.application`,或 version catalog 別名(`alias(libs.plugins.<名>)` 的 `<名>` 去掉點與連字號、轉小寫後等於 `androidapplication`)」
- 逐一走過:
  - **註解**:`// id 'com.android.application'` 或 `/* apply plugin: 'com.android.application' */` 沒說要不要剝除。不剝就把 library 模組判成 application,於是「恰好一個」變兩個而放棄(漏給),或反過來把非 app 當 app(給錯模組)。
  - **apply false**:`id("com.android.application") version "8.5.0" apply false` 與 `alias(libs.plugins.android.application) apply false` 只是宣告、並未套用。字面「套用了」要排除,但沒寫。根專案 build 常這樣寫,若根被當成模組,會誤算。
  - **apply 舊寫法**:`apply plugin: 'com.android.application'`、`apply(plugin = "com.android.application")`、`id "com.android.application"`(雙引號)、`id("...") version "x"`,spec 的「外掛 id」沒說哪些算。
  - **catalog 別名**:別名只是字串啟發式,沒讀 `libs.versions.toml`。`libs.plugins.androidApplication` 可以,但 `libs.plugins.agp.app` 之類不認;這類別名反而可能有人指到 library。別名正規化也沒定義 camelCase。
  - **settings include**:Groovy `include ':app', ':wear'`、`include(":app", ":wear")`、單雙引號、一行多個、多行續行、`include` 在註解裡、`includeBuild`、動態 `file('modules').eachDir { include … }`,spec 都沒定義。
  - **projectDir 重導**:`project(':app').projectDir = file('../real-app')` 時,「`<模組路徑>/build.gradle`」指到不存在或別的目錄。
  - **雙檔並存**:`settings.gradle` 與 `settings.gradle.kts` 同時存在、`build.gradle` 與 `.kts` 同時存在,取哪個。
  - **CRLF/BOM**:BOM 在檔首會讓以行首為錨的 `include` 比對落空,CRLF 會讓以 `$` 結尾的比對落空。
  - **根專案即 app**:單模組舊專案(沒有 include、根 build.gradle 就套 application)偵測不到,維持壞的舊指令。〈天花板〉沒列。
- 部分失效是安全方向(退回舊骨架),但混合情況會變成「看起來剛好一個」而給錯。例如一個靜態 include 的 `:app`,加一個靠迴圈動態 include 的第二個 application。
- 修法方向:spec 要明寫剝註解、排除 `apply false`、動態 include 一律放棄,並為每種各給一列預期值。

## b5 範圍 4 沒說偵測用 repo 根還是平台根,與同一檔案裡「平台根可為子目錄」不一致
severity: minor
blocking: 否 判準:歧義會讓範圍 4 在子目錄 Gradle 專案不觸發(退回舊行為,不更糟),不造成誤擋。
- 引句:「`settings.gradle` 不在 repo 根(Gradle 根在子目錄)時不猜」
- 範圍 3 說 settings 不在 repo 根就不猜。範圍 4 說「範圍 3 的偵測算得出模組」,但設定檔裡預設平台的 `root` 可以是 `android/`。`_situation_rule_platform` 明確處理平台根在子目錄(`scripts/lumos:75868` 附近)。
- 結果:用 platforms 設定、`root: "android"` 的專案,run_cmd 是壞的 `test --tests`,但範圍 4 因 repo 根沒有 settings.gradle 而不擋,人裁照舊跑壞指令。範圍 4 應以平台根當偵測起點。
- init 多平台路徑本來就寫 `"root": "."` 當佔位(`scripts/lumos:35129`),這裡也猜不到真實根,spec 要寫清楚。

## b6 範圍 5 把使用者明給的 `--diff` 靜默丟掉,且範例本身不可執行
severity: minor
blocking: 否 判準:行為與現行共用函式一致,只是 UX 與範例缺陷,不影響判定正確性。
- 引句:「分支找得到主線分岔點時一律用分岔點、`--diff` 不生效」
- 問題:使用者帶了 `--diff` 卻被忽略,沒有任何提示。這跟 `code-loop check` 同規則沒錯,但在人裁這種「人明講範圍」的指令上會讓人以為範圍生效。至少要印一行「`--diff` 因找得到分岔點而未採用」。
- 預期值表 S7 第一列:「沒有主線分岔點的 repo,帶 `--diff main..HEAD`」。`_mainline_ref` 只認 `main`/`master`(含 upstream),見 `scripts/lumos:69340`。沒有這兩個 ref 時 `main..HEAD` 在 git 就是非法範圍,範例無法執行。要用 `develop..HEAD` 之類舉例。
- 還有:`--diff A..B` 的終點若不是 HEAD,段是從 A..B 切、檔卻從 HEAD 讀(`_situation_rule_recipe_problem` 讀 HEAD 版),spec 沒說終點必須等於 HEAD。

## b7 範圍 6 的「最後 400 字」在 Gradle 輸出下可能抓不到編譯錯誤,預期值表宣稱「含編譯錯誤」沒有查證
severity: minor
blocking: 否 判準:屬可診斷性不足,不影響判定與帳本正確性。
- 段落:範圍 6、預期值表 S8。
- 引句:「kill-log 那筆 tail 是壞法那次輸出最後 400 字(含編譯錯誤)」
- Gradle 失敗的結尾是固定的 What went wrong、Try、`--stacktrace`、`--info`、`--scan`、help.gradle.org 這一長串。編譯器的 `e: …Unresolved reference` 行出現在更前面。依我對 Gradle 輸出格式的了解(這份 spec 與程式裡都沒有實測輸出),400 字大約只涵蓋 footer,人裁拒絕訊息再取最後 5 行,幾乎只剩 `BUILD FAILED`。
- `_kill_run` 現在保留全文(`scripts/lumos:27995` 的註解),實作可以改取含 `e:` 或 `error:` 的行。S8 要用真 Gradle 輸出驗,不要只用假輸出。
- 附帶:tail 原樣寫入 `.kill-log.jsonl`。該檔不進版控,「不含祕密」的說法偏樂觀,但風險低(本機檔)。

## b8 範圍 2 的 `error` 與既有「old 命中數不符」的 `drifted` 判法不一致,且 `old` 以子字串替換
severity: minor
blocking: 否 判準:在 rc 優先序合約下都不放行,錯的只是判類與實作細節風險。
- 引句:「不合就判 `error`、不套用壞法、不跑壞法那一次(基準在這之前可能已跑過——跟 old 不合的既有判法同一處)」
- 問題 1:既有 old 命中數不符是 `drifted`(`scripts/lumos:27938`),不是 `error`。spec 兩句話對同一處說兩種判類。
- 問題 2:套用走 `src.replace(r["old"], r["new"], 1)`(`scripts/lumos:27948`),是子字串替換。規則寫「整行恰好一行」,但實作若只用現有的 `src.count` 加 `replace`,`import a.b.flatMapLatest` 會同時命中 `import a.b.flatMapLatestX` 的前綴,替換落在第一個出現處而不是被驗證的那一行。要用逐行比對加行號定位。
- 問題 3:多個 T_new 會產生多筆 `also`,spec 沒說驗證是對「主替換後」還是「逐筆累積後」的檔,也沒說同一 old 行被多筆 also 套用時的順序。
- 已讀並確認的合約:Systems/guard-kill 的 rc 優先序(error 屬 rc2)與 `--json` 純度不被破壞。

## b9 驗收條款覆蓋缺口
severity: minor
blocking: 否 判準:屬測試覆蓋不足,先紅測試可補。
- 引句:「[S5] 當 repo 恰好有一個 Android application 模組,lumos init 應給那個模組的 testDebugUnitTest 跑單支測試指令」
- 一條 S5 要擔下預期值表的五列,包含別名寫法、多個、無模組、單平台與多平台兩條骨架路徑、java-junit。範圍 4 的「看 profile 名不看平台鍵」、範圍 5 的「分岔點存在時 `--diff` 不生效」只在預期值表有列、條款沒有單獨綁測試。範圍 7 文件無條款。
- 每個極端寫法(b4 清單)都需要各自的先紅案例,否則偵測規則只由兩個正常寫法守著。

## 逐節確認
- 〈白話〉、PRIOR-ART、RETIRE-IF:已讀,無 finding(RETIRE-IF 兩個條件可機械觀察)。
- 〈舊否決比對〉:已讀。三條否決都已逐條處理,「概念上擦邊」已交設計審,無 finding。
- 〈不做〉:已讀,無 finding。別名 import 與 Java 不處理,與範圍 1 一致。
- 〈回退〉:已讀,無 finding。
- 交叉引用:Issues、三個 Projects 與三個 Systems 節點皆存在;範圍 N 與 S1-S9 與預期值表各列對得上。已核對審材快照與 9eccaaa 的計劃節點全文相同。

## 圖譜鏡頭(固定席)
- 該節點宣稱:人裁循環、殺傷力的 rc 優先序、`recipes_override` 路徑只對臨時配方生效。
- 判「不影響合約」:兩條 ★INVARIANT★(guard kill rc 優先序、`--json` 純度)不受影響,因為 `also` 不合走既有 error 與 rc2,且不新增 stdout JSON 輸出。
- 判「會破壞行為宣稱」:b1 會讓原本能判 killed 的人裁情境變成被拒,與計劃自己的目標「讓人裁在真實 Android 專案用得起來」相反。
- 無其他 ★INVARIANT★ 或 ★IRREVERSIBLE★ 被碰到。

## 實務隱患類別
- 金流:無。不碰付款與金額。
- 對外送出:無。只在本機隔離工作樹與本機帳。
- 不可逆:無。工作樹整支還原,寫回條款行為不變。
- 資安:低。`tail` 原樣入本機未進版控的帳(見 b7)。`also` 只能由工具依固定規則產生,使用者不能自帶,攻擊面沒有增加。
- 效能與資源:低。`also` 與 Gradle 檔解析都只讀單一檔與 settings;大檔另有 `_KT_SIT_READ_MAX` 上限擋(`_kt_sit_read_many`)。
- 相容性(新舊版混用、舊帳):spec 已寫,已讀,無 finding。
- 極端輸入(替使用者發聲):空輸入已被既有檢查擋;重點缺口都在 b1、b2、b4。CRLF 的 import 比對沒問題,因為 `_kt_sit_read_many` 先把 `\r\n` 轉成 `\n`(`scripts/lumos:39979`)。

最嚴重:major;blocking 共 4 條
