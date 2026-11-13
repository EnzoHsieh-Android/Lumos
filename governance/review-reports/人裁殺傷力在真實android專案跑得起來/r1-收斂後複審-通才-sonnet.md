severity: major

我逐節讀完整份 spec,也實際跑過程式驗證。交叉引用都存在且一致:範圍 1–7 對得上、S1–S10 對得上、預期值表剛好 20 列。以下是找到的洞。

## r1 S6 的「頂層 test 任務」判法會永久擋掉純 JVM 模組,而且沒有放行出口
severity: major
blocking: 是——合法的 run_cmd 被 rc 2 拒絕,範圍 4 又寫明「不自動改設定」,使用者沒有辦法繞過。

- spec 段落:〈用詞〉頂層 test 任務、〈範圍〉4、S6 第 2 列。
- 引句:「run_cmd 含頂層 test 任務或含 `YOUR_MODULE` 佔位時,在跑殺傷力之前拒絕(rc 2)」
- 問題:Android 專案裡常有純 Kotlin/JVM 的模組,例如 `:core:domain` 套 `kotlin("jvm")`。這種模組的 `test` 是真正的 Test 任務,收 `--tests`。判法只看任務名是不是 `test`,不看目標模組有沒有 Android 外掛。
- 具體例:輸入 `./gradlew :core:domain:test --tests '*{method}'`,模組是純 JVM、指令完全合法,預期應放行。照 spec 會被判成頂層 test 而 rc 2。
- 查證:`_KT_BUILD_ANDROID` 是整個專案層級的判斷(`scripts/lumos:39308`)。`_android_build_texts` 會讀 `gradle/libs.versions.toml`(`scripts/lumos:40618`),只要版本目錄裡有任何 `com.android.*`,整個 repo 就判成 Android。
- 建議:只拒絕沒有模組前綴的 `test`。或者先看 `--file` 往上最近的建置檔有沒有 Android 外掛。

## r2 印出的「正確格式」沒考慮平台根是子目錄,指令實際上是在 worktree 頂層跑
severity: major
blocking: 是——spec 自己在判 Android 和推模組時都承認平台根可以不是 repo 根,卻給出會在基準階段 abort 的指令。

- spec 段落:〈範圍〉3、〈範圍〉4。
- 引句:「正確格式 `./gradlew :<模組>:test<Variant>UnitTest --tests '*{method}'`」
- 問題:`cmd_guard_kill` 建的隔離工作樹是 repo 頂層,`_kill_run(cmd, wt, …)` 的 cwd 就是工作樹頂層,不是平台根。
- 具體例:Android 專案在 monorepo 的 `android/` 底下,平台 `root` 為 `android`,`gradlew` 在 `android/gradlew`。輸入 `./gradlew :app:testDebugUnitTest --tests …`,預期能跑,實際是 `./gradlew: No such file`,基準 abort。
- init 的單平台與多平台骨架路徑都寫 `"root": "."`(`scripts/lumos:35129`),在 `android/` 子目錄的 repo 裡也是同樣問題。
- 模組候選卻要「相對平台根」算,兩邊的基準點不一致。範圍 3、4 與 S5、S6 都沒提 `cd <平台根> &&`。
- 查證:`scripts/lumos:27909`(`_kill_run(cmd, wt, …)`)、`scripts/lumos:75736`(`_situation_rule_platform` 註解自己就講過平台根是子目錄的情況)。

## r3 插入點「最後一行 import」沒限制在檔頭
severity: minor
blocking: 否——發生時多半被擋成 error 或 killed_unattributed,是失敗而不是誤放行。

- spec 段落:〈範圍〉1 插入點。
- 引句:「HEAD 那支檔最後一行 `import ` 開頭的行之後(逐行比對、取行號,不用子字串)」
- 問題:「逐行比對」只排除子字串,沒排除檔案本體。Kotlin 的 import 只能在檔頭。多行字串(`"""` 內)第 0 欄開頭是 `import ` 的行,例如測試裡的 Gradle 或 Kotlin script 樣板,會被當成「最後一行 import」。
- 具體例:檔頭三行 import,函式裡有一段 raw string 其中一行是 `import foo.Bar`。插入會落在字串內容裡,真正的 import 沒補上,編譯失敗,判 killed_unattributed 被拒;使用者無法指定插入位置。
- 檔頭有 `@file:Suppress(...)` 沒問題,因為 `@file:` 在 `package` 之前,插入點仍在 import 之後。
- 也沒講 CRLF 檔案:`old` 是「那一行加換行」,`\r\n` 下「以換行結尾、只有一行」怎麼算。
- 建議:只在第一個非 import、非 package 宣告之前的連續檔頭區找。

## r4 fail_excerpt 的「FAILED 開頭」挑不到 Gradle 真正的測試失敗行
severity: minor
blocking: 否——退化成較沒用的摘錄,不會誤判。

- spec 段落:〈範圍〉6。
- 引句:「以 `e: `、`error:`、`FAILED` 開頭,或 `* What went wrong:` 之後到下一個空行」
- 問題:真 Gradle 的測試失敗行是 `SearchViewModelTest > onlyLatestQueryShown() FAILED`,FAILED 在行尾。`FAILED` 開頭只會對到 pytest 摘要的 `FAILED tests/x.py::t - …`,對到的不是 Gradle 那行。
- 具體例:killed_unattributed 的情境是紅燈來自別支測試。Gradle 輸出只有 `* What went wrong:\nExecution failed for task ':app:testDebugUnitTest'.\n> There were failing tests…`。規則 3 有命中,所以不會退回取結尾。摘錄裡沒有「哪支測試紅」,而這正是歸因最需要的資訊。
- pytest 的 `E   assert …` 行以 `E ` 開頭,也沒挑到,只靠摘要行那一句。
- 查證:`scripts/lumos:27955` 附近 `m_tail` 是全文,規則可以改,只是目前規則不夠。

## r5 摘錄的「先截 600 字、後換路徑」順序與 macOS 路徑形式有洞
severity: minor
blocking: 否。

- spec 段落:〈範圍〉6、S8 預期值表。
- 引句:「依原順序取到 600 字;一行都挑不到才退回取結尾 600 字。存之前把隔離工作樹的絕對路徑換成 `<worktree>`」
- 問題一:順序沒講清楚。先截 600 字再換,會把半截路徑留在帳裡;先換再截,`<worktree>` 較短,多出的位置又沒說。
- 問題二:macOS 的 `tempfile` 路徑是 `/var/folders/…`,Gradle 或 realpath 印的是 `/private/var/folders/…`。`wt` 與 `wt_real` 不同(`scripts/lumos:27880` 一帶),要兩種都換,spec 只說「絕對路徑」。S8 的「工作樹路徑換成 `<worktree>`」在 macOS 可能只換掉一種。
- 問題三:多個 `e:` 行每行約 190 字(含 `file:///private/var/…`),三行就吃滿 600 字,`What went wrong` 區塊被截掉,與 S8 預期「含 e: 行與 What went wrong 區塊」衝突。
- 補充:`_kill_run` 回的「全文」其實有 256KB 上限,超過會砍中段(`scripts/lumos:27708`)。多數情況不影響,但 spec 該寫明。

## r6 `--import` 的名稱判法:判什麼、怎麼比沒講清楚,而且 D-5 這類列的合法 import 仍會被拒
severity: minor
blocking: 否——是能力邊界,而且會編譯失敗被拒,不會誤放行。

- spec 段落:〈範圍〉1、〈天花板〉1。
- 引句:「`<名稱>` 要是 `--new` 含、`--old` 不含的該列觸發字之一(用 `_kt_trigger_re` 判,點號寫法的觸發字不能當 `<名稱>`)」
- 問題一:`_kt_trigger_re` 只回正規式字串(`scripts/lumos:39178`),沒說是拿名稱 `fullmatch` 還是拿整行 `search`。我跑過:`fullmatch(_kt_trigger_re("flatMapConcat"), "flatMapConcat")` 為真,`search(_kt_trigger_re("viewModelScope.launch"), "launch")` 為假。若拿整行 `search`,`import kotlinx.coroutines.sync.Mutex` 的包名段 `sync` 會撞到 D-59 的觸發字 `sync`。
- 問題二:D-5 的觸發字是 `SharingStarted.Lazily`、`SharingStarted.Eagerly`、`WhileSubscribed`。把 `WhileSubscribed(…)` 換成 `SharingStarted.Lazily` 時,真正要補的是 `import kotlinx.coroutines.flow.SharingStarted`,名稱 `SharingStarted` 不是觸發字,S2 會拒。這是 r1 設計審說的「成員名/跨套件名」問題換個形式還在。〈天花板〉1 沒列這個限制。
- 問題三:`<套件>` 與「識別字」沒定義是 ASCII 還是 Unicode `\w`,也沒定義 Kotlin 關鍵字、反引號。形狀檢查若用 `$` 而不是 `fullmatch`,尾隨換行會漏過。

## r7 S9 假平台腳本的條件寫成無條件,基準階段就會 abort
severity: minor
blocking: 否——是測試設計寫法的歧義。

- spec 段落:預期值表 S9。
- 引句:「被改檔沒有 `import …flatMapConcat` 就印 `e: Unresolved reference` 並回 1,有就跑測試」
- 問題:基準跑的是 HEAD,HEAD 用 `flatMapLatest`、沒有 `import …flatMapConcat`。照字面,基準就回 1,判 abort,永遠到不了「不帶 `--import` → killed_unattributed」。
- 修正:條件要寫成「檔案用到了 `flatMapConcat` 卻沒有該 import 才失敗」。

## r8 〈天花板〉3 說「用自訂約定外掛的專案判不到」,與程式現況不符
severity: minor
blocking: 否——只是自述的局限與實際行為不符,實際是偵測更常成立。

- spec 段落:〈天花板〉3。
- 引句:「用自訂約定外掛(build-logic 的 convention plugin)套 Android 外掛、建置檔深過三層的專案判不到」
- 查證:我造了一個專案,`app/build.gradle.kts` 只寫 `alias(libs.plugins.myapp.android.application)`,另有 `gradle/libs.versions.toml` 含 `id = "com.android.application"`。`_android_build_texts` 回兩份文字,`_KT_BUILD_ANDROID` 的比對結果是 `[False, True]`,整體判成 Android。
- 實況:約定外掛專案只要版本目錄有宣告 AGP,多半判得到。反過來,伺服器端 Kotlin 專案若版本目錄列了 AGP,也會判成 Android,再加上 r1 就會被誤擋。
- 另外,〈用詞〉說「跟既有 Android 現成檢查提醒同一套判法」。`_lint_android_ci_advisories` 傳的是 repo 根(`scripts/lumos:40747`),spec 改成平台根,根不同。

## r9 `--diff` 的細節:「沒採用」的判斷方式與 S7 條款涵蓋範圍
severity: minor
blocking: 否。

- spec 段落:〈範圍〉5、S7。
- 引句:「分支找得到主線分岔點時一律用分岔點、`--diff` 不生效」
- 查證:我核對過 `_codeloop_disp_range`(`scripts/lumos:75138`)與 `_kt_bj_segments`(`scripts/lumos:75379`),spec 描述的 fallback 行為(找不到主線才用 `--diff`)與現況一致。
- 問題一:spec 沒說怎麼判斷「沒採用」。比較回傳的 `rng` 與使用者給的字串,會在 `--diff main..HEAD` 這種語意相同的情況誤報「沒採用」,因為 `rng` 是 `<mb>..<sha>` 形式。
- 問題二:`tip_on_ml` 為真(HEAD 已在主線)時 `--diff` 也被靜默忽略,spec 沒講要不要印。
- 問題三:`..` 右端解析成 HEAD 只提右端。`A...B` 三點寫法、左端不存在的提交,都沒定義。
- 問題四:S7 條款文字只涵蓋「算不出分岔點」那種情形,預期值表另外兩列(沒採用的提示、rc 2)沒有對應條款。

## r10 `also` 的資料形狀與檢查函式的描述前後不一
severity: minor
blocking: 否。

- spec 段落:〈用詞〉連帶替換、〈範圍〉1、〈範圍〉2。
- 引句:「每筆 `also` 的 `old` 要是一整行(以換行結尾、只有一行)」
- 問題:範圍 1 說「產生一筆 `also`」,範圍 2 說「每筆」,〈用詞〉說「額外做的替換」,到底是單一物件還是清單沒定。`_kill_also_issue` 要檢查「多出來的每一行」,用 `splitlines()` 會把 `\u2028`、`\x0b` 當換行,與 Kotlin 的換行定義(`\n`、`\r`)不同。
- `also` 的 `old` 是整行加換行,若該行恰好也出現在 raw string 裡,spec 要求的「恰好一行」會失敗,只能判 error,使用者無從修。

## r11 S6 的「gradlew 之後的任務清單」沒定義怎麼切詞,四個具體例結果不明
severity: minor
blocking: 否。

- spec 段落:〈用詞〉頂層 test 任務、S6。
- 引句:「run_cmd 裡 gradlew 之後的任務清單中,有一個任務名(去掉 `:模組:` 前綴後)剛好是 `test`」
- 逐例走一遍:
  - `./gradlew test`:拒絕,正確。
  - `./gradlew :app:test`:拒絕,對 Android 模組正確;純 JVM 模組見 r1。
  - `gradle test`(沒有 w):「gradlew 之後」對不到,放行,與 S6 意圖不符。
  - `./gradlew testDebug`:不是 `test`,放行。Gradle 的駝峰縮寫會解到 `testDebugUnitTest`,所以其實可跑,但 spec 沒講是有意放行。
- 另外,`./gradlew :app:testDebugUnitTest -x test --tests …` 的 `-x test` 是排除任務,不該算,選項的值怎麼跳過沒定義。
- `./gradlew testDebugUnitTest --tests …`(沒模組前綴)會放行,但多模組專案每個模組的 Test 任務都套這個過濾,沒有匹配的模組會因 `No tests found for given includes` 失敗,可能要跑十幾分鐘才 abort。這是 r1 的反面:該擋的反而不擋。

## r12 實務隱患:fail_excerpt 進版控帳的風險面
severity: minor
blocking: 否——spec 已承認並說明,與單人自用的威脅模型相容;只補一個具體例。

- spec 段落:〈實務隱患〉。
- 引句:「不宣稱不含祕密,600 字上限與只在弱證據判定時存讓量很少」
- 具體例:abort 的典型原因是找不到 SDK,Gradle 訊息會帶 `/Users/<帳號>/Library/Android/sdk` 這類家目錄路徑。`<worktree>` 遮罩只處理工作樹路徑,家目錄路徑會原樣進入進版控的 kill-log。

## 已讀、無 finding 的節

- 〈白話〉:無 finding。
- 〈舊否決比對〉:無 finding。
- 範圍 1 的確認畫面與治理帳 `imports` 欄、範圍 2 套用與還原的描述:無 finding。我核對過 `cmd_guard_kill` 的寫檔與 `git checkout` 還原流程,可以接上 `also`,`error` 判法的位置在寫檔之前也合理。
- 範圍 3 的 `YOUR_MODULE` 佔位:無 finding。用佔位不用角括號的理由成立。
- 範圍 7、〈不做〉、〈回退〉、〈審計修正紀錄〉:無 finding。
- 〈依據來源〉:無 finding,但有兩點。「AGP 9 起」那列的來源是 Slack 聊天室存檔,「頂層 test 不收 `--tests`」的來源是 2023 年的 StackOverflow kiwix 鏡像,證據力偏弱。這兩條都不是載重宣稱,因為工具不猜任務名。
- 驗收條款 S1–S10 與預期值表:對得上,不一致處已在 r7、r9 列出。

## 實務隱患鏡頭

- 金流:無,spec 不碰付款與金額。
- 對外送出:無,只在本機隔離工作樹改檔、寫本機帳。
- 不可逆:無,連帶替換只在隔離工作樹、跑完用 `git checkout` 還原。
- 資安:`--import` 的值只寫進工作樹檔案內容,不進 shell。但 `fail_excerpt` 進版控的 kill-log,見 r12。
- 併發與資源:同一台機器上 Gradle daemon 閒置駐留(spec 已列);基準逾時上限 `max(600, floor)`,大型專案冷建構可能直接 abort,要靠 `LUMOS_KILL_TIMEOUT_FLOOR` 調。
- 相容性:舊版讀帳略過新欄位(spec 已述);我只確認治理帳投影用固定欄位清單(`scripts/lumos:18293`),沒發現會因多欄而失敗。

最嚴重:major;blocking 共 2 條
