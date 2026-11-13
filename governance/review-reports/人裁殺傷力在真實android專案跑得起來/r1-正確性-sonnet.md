severity: major

## c1 逐一 import 有兩個舊觸發字時規則互相矛盾,真實 D-4 寫法會落進「不產生」
severity: major
blocking: 是——照字面實作會讓型錄自己的典型寫法(`debounce(300).flatMapLatest`)不產生 also,缺口 1 沒補到;實作者還得在兩條互相矛盾的規則裡自己挑一條。

- 位置:〈範圍〉1 與〈實務隱患〉第 2 條。
- 問題 1:〈範圍〉1 說 T_old 要從「`--old` 含的該列觸發字」裡找,而 D-4 一列的觸發字有 `debounce`、`flatMapLatest`、`collectLatest`、`flatMapConcat` 等。
  - 型錄 D-4 的示範寫法是 `query.debounce(300).flatMapLatest { … }`。
  - 輸入:檔頭有 `import kotlinx.coroutines.flow.debounce` 和 `import kotlinx.coroutines.flow.flatMapLatest`,`--old` 是 `.debounce(300).flatMapLatest {…}`,`--new` 是 `.debounce(300).flatMapConcat {…}`。
  - T_new 只有 `flatMapConcat`。`--old` 含的觸發字是 `debounce` 與 `flatMapLatest`,兩個都有逐一 import,而且是同一套件。
  - 字面「剛好一個就用…零個或多個…就不產生」,所以兩個 import 都在就不產生。
  - 正確做法應該只看「`--old` 有、`--new` 沒有」的觸發字(這裡只有 `flatMapLatest`),但規格沒這樣寫。
- 問題 2:〈實務隱患〉說「取…套件相同的那一行」,這跟〈範圍〉1 的「多個就不產生」矛盾。
  - 它也循環:新觸發字要先有套件才能比對,但套件正是從 T_old 那行 import 推出來的。
  - 它沒說兩個 import 同套件時取哪個。
- 預期值表沒有「`--old` 同時含兩個觸發字」的列,S1 也沒有對應案例。

引句:「剛好一個就用它的套件;零個或多個(不同套件)就不產生。」
引句:「取跟新觸發字在情境決策表同一列、而且套件相同的那一行;找不到就不產生連帶替換」

file: `/Users/enzo/harness/lumos-srl-android/skills/kotlin-idioms/checks-catalog.md:743`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:75732`

## c2 沒限定 T_new 是「同套件、可 import 的頂層名」,會產生假 import 或讓本來能編的壞法編不過
severity: major
blocking: 是——規則會把能編譯的壞法改成編譯失敗,又判成弱證據被拒,等於製造現在要修的那個症狀。

- 位置:〈範圍〉1 的產生規則;〈範圍〉2 的格式檢查只看 `^import [\w.]+$`。
- 問題:T_new 是「觸發字」,不保證是 `kotlinx.coroutines.flow` 底下的頂層函式。D-4 與 D-16 的觸發字裡有:
  - 點號寫法 `viewModelScope.launch`。
  - 成員函式 `trySend`。
  - 常數 `UNLIMITED`。
  - 在 `kotlinx.coroutines.channels` 的 `Channel`。
- 例 1:T_old=`flatMapLatest`(從 flow 套件逐一 import),`--new` 用 D-4 的命令式寫法 `searchJob = viewModelScope.launch {…}`。
  - 規則產生 `import kotlinx.coroutines.flow.viewModelScope.launch`。
  - 它符合 `^import [\w.]+$`,通過格式檢查。
  - 結果是 Unresolved import,編譯失敗。
- 例 2:T_old=`conflate`,`--new` 含 `trySend`。
  - `trySend` 是 `ProducerScope` 的成員,不用 import,原本能編。
  - 規則加了 `import kotlinx.coroutines.flow.trySend`,反而編不過。
- 例 3:T_new=`Channel` 的 import 套件會錯成 flow。
- 規格要求「同一套件」,卻沒有任何機制確認 T_new 真的在那個套件。
- 第二個缺口是別名:「已有 `import <套件>.T_new`」沒說 `import pkg.T_new as x` 算不算已有,實作者會做出不同結果。

引句:「對 `--new` 含、`--old` 不含的每個該列觸發字 T_new」
引句:「每筆 `also` 的 `old` 要在套完主替換之後的檔裡**整行比對**恰好一行」

file: `/Users/enzo/harness/lumos-srl-android/skills/kotlin-idioms/checks-catalog.md:743`

## c3 S8 的 400 字與最後 5 行,在 Gradle 編譯失敗時抓不到編譯錯誤
severity: major
blocking: 是——這是缺口 4「看不出失敗原因」的修法,但在真實 Gradle 輸出上沒修到,規格卻寫「含編譯錯誤」。

- 位置:〈範圍〉6 與預期值表 S8。
- 問題:Gradle 編譯失敗的輸出順序是:
  1. `e: file:///…/X.kt:57:12 Unresolved reference …`
  2. 空行
  3. `FAILURE: Build failed…`
  4. `* What went wrong:` 加上幾行
  5. `* Try:` 加上四行 `> Run with --stacktrace…`
  6. `BUILD FAILED in 14s`
- 從 `e:` 那行到結尾已經超過 400 字,所以尾 400 字不含錯誤本身。最後 5 行只會是 `Get more help…`、空行、`BUILD FAILED`、`N actionable tasks`。
- 用合成輸出寫的 t_kill_log_tail_on_weak 會綠,真實專案仍然看不出原因。
- 修法方向:規格應改成保留 `e: ` 或 `error:` 行(類似 `_kill_cap` 的 keep_re),或取第一個錯誤附近的行。
- 附帶:同一個 `tail` 欄現在對 survived/abort 是基準輸出尾 200 字,對弱證據是壞法輸出尾 400 字,語意混用,規格沒標示。
- 查證:現行程式只有 survived 存 `b_tail[-200:]`,弱證據不存任何輸出。`_kill_attribute` 要求測試名出現在輸出裡,所以編譯錯誤必然判成 unattributed。

引句:「kill-log 那筆 tail 是壞法那次輸出最後 400 字(含編譯錯誤)」
引句:「人裁被拒時,訊息另印摘錄最後 5 行」

file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:27995`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:27739`

## c4 also 驗證的判法、位置與驗證函式:表與條文不一致,「同一支格式檢查」不存在
severity: minor
blocking: 否——實作者能自己補齊,但測試與判定值會寫得不一致。

- 位置:〈範圍〉1 末句、〈範圍〉2、預期值表 S3。
- 問題 1:S3 列寫「不跑測試」,但〈範圍〉2 自己說基準可能已跑過。也就是 baseline 會跑,只有壞法那次不跑。測試案例會被這句誤導成「完全不跑」。
- 問題 2:`old` 不合的既有判法是 `drifted`(`old 命中 N 次`),規格卻說 also 不合判 `error`,又說「跟 old 不合的既有判法同一處」。位置同、判定值不同,沒說明為什麼。
- 問題 3:〈範圍〉1 說人裁先用範圍 2「同一支格式檢查」驗 also,但程式裡沒有這支函式,檢查目前只能內嵌在 `cmd_guard_kill` 的迴圈裡。
  - 規格沒寫要抽出來,也沒說抽出來是否牴觸「不另抽」的舊否決。
  - 它還需要「主替換後的檔」,而 `_situation_rule_recipe_problem` 讀完的 `src` 沒有往外回傳。
- 問題 4:規格說「套完主替換之後」整行比對,但沒寫必須是記憶體內字串。若實作成先寫檔再驗,「不套用壞法」就不成立。

引句:「判 error、檔不動、不跑測試」
引句:「人裁在跑殺傷力之前先用範圍 2 的同一支格式檢查驗一次產生的 `also`」

file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:27937`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:75711`

## c5 S7 的第一列輸入前後矛盾,`--diff` 被無聲忽略,而且沒擋 `-` 開頭的值
severity: minor
blocking: 否——都是補條文就能解決的小洞,不補會讓測試寫歪或留一個參數注入口。

- 位置:〈範圍〉5 與預期值表 S7。
- 問題 1:S7 第一列「沒有主線分岔點的 repo,帶 `--diff main..HEAD`」自相矛盾。
  - `_mainline_ref` 會直接用本地 `main`。有 `main` 且有共同祖先就有分岔點,`--diff` 不生效。
  - 想讓 `--diff` 生效只有兩種情況:repo 沒有 main/master,或 main 與 HEAD 是無關歷史(orphan)。
  - 規格沒寫測試要怎麼造這個 repo。
- 問題 2:`--diff` 被忽略時,規格沒要求印一句「你給的 `--diff` 沒生效、改用分岔點」。使用者會以為範圍被採用。
- 問題 3:`--diff` 的值直接進 `git diff … <範圍> -- *.kt`。
  - 其他指令(`impact`、`pitfalls`、`cochange-check`)都有「`-` 開頭就 rc2」的檢查。
  - blind-judge 和 situation-rule 的路徑沒有。
  - `--diff=--output=/some/file` 會被 git 當選項,寫出檔案。
  - 〈範圍〉5 說「不改共用函式」,但這個檢查必須加在新旗標入口。
  - 在單人自用的威脅模型下嚴重度低,但〈實務隱患〉沒列。
- 事實核對:〈範圍〉5 描述 `_codeloop_disp_range` 的行為正確,分岔點存在時一律用分岔點。

引句:「沒有主線分岔點的 repo,帶 `--diff main..HEAD`」
引句:「不改那支共用函式。」

file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:75138`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:69334`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:39931`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:63322`

## c6 Android 模組偵測與 Scope 4 的字串比對定義不足,會漏掉常見寫法
severity: minor
blocking: 否——退路是「不猜、照舊」,但實作者會各自猜一套解析法。

- 位置:〈用詞〉Android application 模組、〈範圍〉3、〈範圍〉4、〈天花板〉3。
- 問題 1:`settings.gradle` 的 `include` 寫法規格沒給解析規則,實務上有:
  - `include ':app', ':core'`
  - `include(":app",\n ":wear")`
  - 多行
  - `project(':app').projectDir = file('x')` 改目錄
  - 規格寫「`<模組路徑>/build.gradle`」,沒處理 projectDir 改寫。
- 問題 2:`testDebugUnitTest` 在有 productFlavors 時不存在(變成 `testFreeDebugUnitTest`),規格沒提。用有 flavor 的專案,骨架會寫出一條跑不了的指令,而且 Scope 4 會要求使用者改成它。
- 問題 3:唯一的 application 模組是 `:app`,但測試在 library 模組 `:core` 時,Scope 4 會誤導成 `:app:testDebugUnitTest`,實際會 `No tests found`。規格只在〈實務隱患〉提到要人手改。
- 問題 4:Scope 4 判斷「空白正規化後含 `gradlew test --tests`」。
  - `./gradlew clean test --tests …`、`./gradlew --no-daemon test --tests …`、`./gradlew -q test …` 都不命中,但同樣會失敗。
  - 〈範圍〉3 說「`settings.gradle` 不在 repo 根就不猜」,但 `_situation_rule_platform` 明確支援平台根是子目錄(例 `android/`)。
  - 規格沒說 Scope 4 的偵測從 repo 根還是平台根找。
- 問題 5:`com.android.application` 以 `apply false` 出現在根 build 檔(沒有 include 的根專案)時,是否誤判,規格沒寫。

引句:「只認外掛 id 與 `alias(libs.plugins.<名>)` 這兩種寫法」
引句:「空白正規化後含 `gradlew test --tests`」

file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:34890`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:75736`

## c7 隔離工作樹裡跑真實 Gradle 的環境隱患,〈實務隱患〉沒列
severity: minor
blocking: 否——不影響設計正確性,但會讓「真實專案跑得起來」在別人的專案上失敗而且原因不明。

- 位置:〈實務隱患〉與已排除項「對外送出」;對照 `_isolated_worktree`、`_kill_run`。
- 問題 1:殺傷力在 `git worktree add` 的新工作樹裡跑,不含 gitignored 檔:
  - `local.properties`(`sdk.dir`)
  - `google-services.json`
  - `keystore.properties`
  - 沒設 `ANDROID_HOME` 時,基準第一次就是 abort,規格沒寫這個前置條件。
- 問題 2:每次都是冷建構。基準上限 600 秒;每次的 `build/` 與 `.gradle` 留在 `/tmp` 工作樹裡。規格只在輸出提示「可能十幾分鐘」,沒講磁碟用量,也沒講清理一定發生。
- 問題 3:`_kill_run` 用 `killpg` 收子程序群組,但 Gradle daemon 自己 setsid。
  - Ctrl-C 或逾時後 daemon 仍活著,工作目錄已被刪。
  - 這是資源類隱患,應該寫成「無害因為 idle 逾時」或要求處理,規格都沒寫。
- 查證:`_isolated_worktree` 是 context manager,新加的 also 錯誤路徑只 `continue`,不會漏清工作樹,這一點沒問題。

引句:「只在本機隔離工作樹改檔跑測試、寫本機帳」

file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:27881`
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:27636`

## c8 「輸出不含祕密」的宣稱不成立,而 kill-log 是進版控的檔
severity: minor
blocking: 否——單人自用框架下風險低,但宣稱本身不能當事實用。

- 位置:〈實務隱患〉第 5 條。
- 問題:`docs/.kill-log.jsonl` 在 git 追蹤清單裡(`git ls-files` 有它),消費專案會把壞法那次的輸出摘錄提交進自己的 repo。
  - 測試輸出可能印出環境變數、BuildConfig 值或內部 URL。
  - 「只跑專案自己的測試」不等於輸出沒有祕密。
- 規格只該說「含路徑,可能含 stdout」,並考慮對 tail 做長度之外的處理。
- 〈回退〉說舊版讀新帳不受影響,這點成立:`tail` 欄原本就在帳上。

引句:「輸出可能含路徑與測試名,不含祕密(殺傷力只跑專案自己的測試)」

file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:28038`

## 其他節
- 〈白話〉〈舊否決比對〉〈用詞〉〈不做〉〈依據來源〉〈回退〉〈天花板〉1、2:已讀,無 finding。
- 交叉引用:S1 到 S9 在驗收條款與預期值表一一對得上,〈範圍〉N 指向都存在。
- 預期值表缺三列:兩個觸發字都有 import、T_new 不可 import、別名 import(見 c1、c2)。

## 圖譜鏡頭(固定席)
- 該節點宣稱的行為與合約:這份設計不會破壞它們。
  - 筆記配方格式不變:只有 `recipes_override` 路徑認 `also`。
  - `kill-log` 的 `tail` 欄本來就存在。
  - 不另抽共用殺傷力函式:照字面成立,但 c4 的「同一支格式檢查」需要抽函式,要在設計裡講清楚。
  - 「壞法人宣告、不生成變異」:擦邊但可接受,前提是 c2 修好。現在這條規則會自己加一行錯的 import,實際上在生成壞法的一部分。
- 與其他計劃衝突:未見衝突。

最嚴重:major;blocking 共 3 條
