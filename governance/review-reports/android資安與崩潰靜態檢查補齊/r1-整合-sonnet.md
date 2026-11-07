severity: major

我逐節對照了 repo 與官方頁面。下面是我發現的洞,每條都有佐證。我另外下載了 Google 資安包 1.0.4 的 jar 和 MASTG 六個測試頁,用來核對。

## finding 1:新規則放 `rules/` 與規則包自己的規矩互相衝突
spec 段落:PRIOR-ART ④、〈實驗〉、〈範圍〉4。
severity: major
blocking: 是(規則包既有的「新規則先放不接閘,量過再升」被繞過,而且量測方式本身有偏)
問題:
- 規則包「怎麼改」第 1 條要求新規則先放 `rules-review/` 或 `rules-unwired/`,對真專案量過誤報低於一成才升到 `rules/`。同一條還寫,審查點出「形狀分不出對錯」的規則「不再放寬形狀,直接留在覆核級」。
- spec 的「任何一層非 SDK 版本比較的 if 就不報」,正是靠放寬形狀把誤報壓下來,而且代價是放過 4 處真問題。
- 「真專案」只剩五個 App 整份掃。那五個 App 裡,除錯模式 3 處全被排除,其他三條幾乎沒命中,誤報率靠搜尋語料撐起來。
- 搜尋語料撈的是「含目標寫法的檔」,偏向命中。
- 規則形狀是看過同一批語料才改的,所以 0 誤報、2.9%、7.7% 都是樣本內數字。
- 分母很小:舊版 TLS 13 處、除錯模式 11 處。再多一個誤報,舊版 TLS 就從 7.7% 跳到 14%,超過一成門檻。
- spec 自己也承認這兩條「估不準」,卻照樣放進推送前會擋的 `rules/`。
引句:「其他三條幾乎沒命中,誤報率主要是搜尋語料量到的」
佐證:
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:76`:「怎麼改」第 1 條,規則升級的條件與「不再放寬形狀」。
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:21`:REVISIT 2027-02-05 要求「拿兩個以上新的真 Android 專案再量一次」,因為 2026-11-05 只量到 30 處命中。
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md`:RULE 行(誤報超過命中一成就降級或搬 `rules-unwired/`),以及 `cap-retro.json` 對「放寬形狀又帶出新誤報」的結論。

## finding 2:新列的「情境怎麼認」沒定,語意類會讓型錄自檢紅
spec 段落:〈範圍〉2 的新列通電批次、〈範圍〉4 的不接閘規則、S5。
severity: major
blocking: 是(S5 要求自檢 0 個問題,照 spec 寫法可能做不到)
問題:
- spec 規定現成規則列一律寫「告警帶寫法=批四」,卻沒說每列的「情境怎麼認」是形狀還是語意。
- 反序列化那條 spec 自己寫「來源可不可信形狀分不出」,這就是語意類。
- 現有口徑對語意類要求:
  - 接電方式要有「表態對程式」;沒標人裁的還要有「盲判席」。
  - 每一列要被〈情境決策表〉某個 D-n 列收進去,否則報「語意類沒有被任何決策表列收進去」。
- 新列裡明顯要看語意才判得準的還有:
  - 敏感資料寫進 logcat(什麼算敏感)
  - 轉發不可信 Intent
  - 弱亂數(哪些場合算資安)
  - 沒權限就呼叫要權限的 API
- 這些列若標形狀,是對分類說謊;若標語意,spec 沒規劃任何 D-n 列、證據樣式或 `samples/situation/*.kt.txt`。
- 範圍 3 和驗收條款也沒提到這件事。
引句:「來源可不可信形狀分不出」
佐證:
- file: `configs/ast-grep/kotlin-android/check.py:360-389`:形狀類要有告警帶寫法;語意類要有表態對程式、盲判席,且必須被決策表列收進去。
- file: `skills/kotlin-idioms/checks-catalog.md:663`:〈情境決策表〉規則,列編號 D-n 只准往後加。
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:20`:自檢只驗格式,不替你分類。

## finding 3:整包安裝資安包,型錄只登記約 9 個檢查 id,其餘會在 CI 擋人
spec 段落:〈範圍〉1、〈範圍〉2、〈實務隱患〉第一條。
severity: major
blocking: 是(spec 要解決的「CI 會擋但 AI 寫碼前查不到」,對這個包本身又重現一次)
問題:
- `lintChecks("com.android.security.lint:lint:1.0.4")` 會載入整包。我解開 jar 的 `IssueRegistry`,看到的檢查比 spec 登記的多很多。官方 README 的表另有 `DefaultCleartextTraffic`、`InsecureDnsSdkLevel`、`TapjackingVulnerable`、`StrandhoggVulnerable`、`MissingAutoVerifyAttribute`、`InsecureStickyBroadcastsPermission`、`DotPathAttribute`、`SlashPathAttribute`、`HardcodedAbsolutePath` 這些 id。
- jar 內另有 Bluetooth 探索時間、UnintendedExposedUrl、PrivateIpAddress、Permission protection level 這幾個 detector。
- 範本開了 `warningsAsErrors = true`,這些沒登記的檢查在消費專案 CI 上照樣會擋。
- 型錄用 grep 查不到 Tapjack、Strandhogg、AutoVerify、StickyBroadcast。
- spec 的處理只有「誤報由專案自己在 lint 設定關掉那一條」,卻沒告訴專案有哪些 id 可以關。
- 〈用詞〉說資安包要寫成 `資安包:<檢查 id>`,但沒說沒登記的 id 怎麼處理。
- 版本相容也沒寫。既有 Slack 段用整段篇幅講「建置用 lint 版本不高於專案 lint(AGP+23)」,說版本不合時 lint 任務載不進外掛。資安包 jar 的 `IssueRegistry` 看不到 api 或 minApi 宣告,spec 沒查它對應哪個 AGP。⚠ 這點我沒能確定資安包對 AGP 的相容範圍。
引句:「誤報由專案自己在 lint 設定關掉那一條」
佐證:
- file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:181`:Slack 外掛的 AGP 對照段與「版本不合時 lint 任務載不進外掛」。
- file: `skills/kotlin-idioms/checks-catalog.md:171`:API-23 的現成規則欄只認既有 id。
- 官方 README(https://github.com/google/android-security-lints):資安包的 id 清單,即上面列的那些 id。

## finding 4:不接閘的 WebView 一般檔案存取規則沒有對應的型錄列
spec 段落:〈範圍〉2 的 API 清單、〈範圍〉4「不接閘」、S4。
severity: minor
blocking: 否(實作時補一列就能解,不改設計)
問題:
- `allowFileAccess`、`allowContentAccess` 兩條要放 `rules-unwired/`,訊息必須以型錄編號開頭,S4 也這樣要求。
- 但〈範圍〉2 的 API 清單只有「WebView 檔案網址存取(自寫)」,沒有一般檔案、content 存取那一列。
- 若併進檔案網址那一列,該列通電批次同時要寫「批一」(會擋的那條)和「未接」(不接閘那條),自檢與〈統計〉口徑不好判。
- 規則 id 要引用的編號沒有列。
引句:「WebView 開一般檔案或 content 存取」
佐證:
- file: `configs/ast-grep/kotlin-android/check.py:657-684`:`message_problems` 要求訊息編號在型錄主表內。

## finding 5:MASTG 測試頁的判準與 spec 的規則形狀對不上
spec 段落:PRIOR-ART ③、預期值表 S3、〈依據來源〉。
severity: minor
blocking: 否(規則本身可用,只是來源欄與預期值表的引用不準)
問題:
- 檔案網址存取(MASTG-TEST-0252):
  - 判定要「JavaScript 開、`setAllowFileAccess` 為 true(或 minSdk<30 沿用預設)、FileURL 系列為 true」三件同時成立才算失敗。
  - 頁面還寫 `AllowFileAccess` 本身不算漏洞。
  - spec 的規則只看 FileURL 一項,預期值表卻把「報」的來源寫成 0252。
  - 0250 是 Content Provider 存取(`allowContentAccess`),不是 FileURL。
  - 0252/0250 真正講的 `allowFileAccess`、`allowContentAccess` 反而被 spec 放去不接閘。
- 除錯模式(0227):判準是沒檢查 `FLAG_DEBUGGABLE` 就開。spec 的「任何非 SDK 版本比較的 if 都算有開關」(`isBeta`、Xposed 旗標也放過)比這鬆,預期值表仍引 0227 當依據。
- 舊版 TLS(0217):頁面另列 `SSLSocket.setEnabledProtocols(...)`。spec 沒規劃,也沒列進「不做」。
- 反序列化(0337):頁面的重點是 Intent extras、Bundle 這類 Android 平台來源。spec 用的是 Java 的 `ObjectInputStream`,兩者不是同一種寫法。
引句:「WebView 檔案存取 MASTG-TEST-0252/0250」
佐證:
- 官方頁:https://mas.owasp.org/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0252/ 的 Evaluation 段。
- 官方頁:https://mas.owasp.org/MASTG/tests/android/MASVS-RESILIENCE/MASTG-TEST-0227/ 的 Evaluation 段。
- 官方頁:https://mas.owasp.org/MASTG/tests/android/MASVS-NETWORK/MASTG-TEST-0217/ 的 Overview 段。

## finding 6:實測狀態欄寫法與〈統計〉口徑不合,〈統計〉沒有程式也沒有測試守
spec 段落:〈範圍〉2 的通電批次與統計。
severity: minor
blocking: 否
問題:
- 〈輸入與口徑〉規定被規則包守到的列,實測狀態欄寫成「規則 <id>:樣本實測中壞例、好例不報」。
- 〈統計〉的「守到的列數」是看現成規則欄或實測狀態欄有沒有 `rules/` 底下的規則 id。
- spec 要新列的實測狀態欄寫命中與誤報數,沒要求寫規則 id。自寫規則列的現成規則欄是「無」,這四列不會被算進守到的列數。
- spec 還說統計「照程式重算」,但全 repo 沒有算那堆數字的程式或測試。S5 也只驗自檢 0 個問題和未查證 2 列,不管〈統計〉。
- 〈統計〉裡的總列數、各類列數、級的組合、規則包條數(error 30、warning 115,不接閘 8)會被默默改成手算數字。
引句:「實測狀態欄寫〈實驗〉量到的命中與誤報」
佐證:
- file: `skills/kotlin-idioms/checks-catalog.md:882`:守到的列數的口徑。
- file: `skills/kotlin-idioms/checks-catalog.md:15`:被規則包守到的列,實測狀態欄的既有寫法。
- file: `docs/lumos-toolchain-knowledge/Projects/Android寫法型錄逐列查證_計劃.md:38`:同一句「照程式重算」,repo 裡找不到那支程式。

## finding 7:DATA-13 併入 `內建:DataExtractionRules` 後,級、情境與通電批次沒交代
spec 段落:〈範圍〉2。
severity: minor
blocking: 否
問題:
- DATA-13 現在是 D 級、語意、現成規則「無」,通電批次是「表態對程式=批三;盲判席=批三」。
- spec 只說把檢查 id 併進現成規則欄,沒說級要不要改成 A+D、通電批次要不要加批四。
- 自檢只在通電批次含「批四」時才比對標籤,所以不寫也不報。結果是欄位寫了現成規則,通電批次卻看不出它會被 CI 擋,且自檢不會提醒。
- 〈天花板〉第 3 點只講「新列漏寫」,沒涵蓋這個併入列。
引句:「`內建:DataExtractionRules` 併進 DATA-13」
佐證:
- file: `skills/kotlin-idioms/checks-catalog.md:509`:DATA-13 現況。
- file: `configs/ast-grep/kotlin-android/check.py:353`:只判含「批四」的列。

## finding 8:S3 綁的是通用測試,抓不到個別案例;缺 TLSv1.2 邊界好例
spec 段落:驗收條款 S3、預期值表。
severity: minor
blocking: 否
問題:
- `t_kotlin_rulepack_samples` 只驗每條規則壞例命中至少 2 處、好例零命中且至少 2 段。
- S3 列了一堆具體案例:包在 SDK_INT 比較裡的除錯模式要報、包在 `BuildConfig.DEBUG` 裡不報、`src/debug` 排除等。刪掉其中一個樣本,只要剩下的壞例仍有 2 處、好例沒誤報,測試照綠。
- 舊版 TLS 最容易寫壞的邊界,是正規式 `TLSv1` 不小心吃到 `TLSv1.2` 或 `TLSv1.3`。S3 和預期值表都沒有這個好例。
- 除錯模式的早退守衛寫法(`if (!BuildConfig.DEBUG) return` 後面才開)不在任何 if 裡,會被誤報。實驗與好例都沒涵蓋。
- 寫死金鑰只抓字面值。`const val KEY = "..."` 再 `SecretKeySpec(KEY.toByteArray(), ...)` 這種最常見寫法會漏,〈實務隱患〉只寫了 if 判斷的天花板。
引句:「包在 `if (Build.VERSION.SDK_INT < 23)` 裡的除錯模式 應 照報 [test:t_kotlin_rulepack_samples]」
佐證:
- file: `scripts/test_lumos.py:126344`:`t_kotlin_rulepack_samples` 的判準(壞例 ≥2、好例 0、至少兩段)。
- file: `configs/ast-grep/kotlin-android/check.py:826-840`:好例、壞例的判準與報錯。

## finding 9:新列與既有列可能重複 ⚠
spec 段落:〈範圍〉2。
severity: minor
blocking: 否
問題:
- 型錄〈輸入與口徑〉規定「同一個錯誤只留一列」。spec 說併進既有列的只有 DATA-13,但有兩處可能重複。
- 「沒用回傳值(內建 CheckResult)」與既有 PERF-36「忽略回傳值」(現成規則 detekt IgnoredReturnValue)重疊。
- 舊版外部儲存(資安包 `InsecureLegacyExternalStorage`)與 DATA-27 同屬外部儲存。DATA-27 的現成規則欄正好是「待查(Lint SdCardPath 代號待查)」,spec 沒說要不要順手補。
- ⚠ 兩者是否算「同一個錯誤」我判不準,但 spec 沒寫判斷理由。
引句:「沒用回傳值(內建 CheckResult)」
佐證:
- file: `skills/kotlin-idioms/checks-catalog.md:658`:PERF-36。
- file: `skills/kotlin-idioms/checks-catalog.md:523`:DATA-27。

## finding 10:PRIOR-ART ① 的引用說法不準
spec 段落:PRIOR-ART ①、〈依據來源〉。
severity: minor
blocking: 否
問題:
- 官方檢查索引頁(`checks/index.md.html`)只列「id:標題」,沒有等級與提供者;等級在各檢查頁和 `severity.md.html`,提供者在 `vendors.md.html`。
- 另外,spec 要把約 38 個內建檢查標成「批四會擋」,卻沒說有逐條核對它們預設是否啟用。型錄既有口徑會排除「預設關」的規則。
- 我抽看各檢查頁,頁面上沒有明確的預設啟用標記,這點需要有人用 lint 實跑驗。
引句:「Android Lint 官方檢查索引每條有等級與提供者」
佐證:
- https://googlesamples.github.io/android-custom-lint-rules/checks/index.md.html(實際內容只有 id 與標題)。
- file: `configs/ast-grep/kotlin-android/check.py:97-110`:`B4_DEFAULT_OFF` 與 `_B4_SKIP` 的口徑。

## finding 11:新檔 `rules/security.yml` 違反規則包現有的分檔慣例
spec 段落:〈範圍〉4。
severity: minor
blocking: 否
問題:
- 規則包note寫「`rules/`……底下的 yml 依型錄主題分檔」,現有檔名是 `api.yml`、`data.yml` 等九個主題。
- spec 自己說「不新開類別」,但規則檔卻新開一個「資安」主題檔,新規則同時被歸入 API 與 DATA 兩類型錄列。
- 若維持新檔,`kotlin規則包.md` 的「檔案」節要同步改寫。
引句:「新檔 `rules/security.yml`(新增)」
佐證:
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:67`:依型錄主題分檔。
- `ls configs/ast-grep/kotlin-android/rules`:現有檔名是 `api.yml`、`architecture.yml`、`compose.yml`、`coroutines.yml`、`data.yml`、`flow.yml`、`perf.yml`、`state.yml`、`testing.yml`。

## finding 12:已採用範本的專案加資安包時,基準線要重產
spec 段落:〈範圍〉1、〈不做〉。
severity: minor
blocking: 否
問題:
- 範本第 2 步寫「先產基準線、提交,再做第 3 步——反過來 `warningsAsErrors` 會讓舊專案一接就紅」。
- 已在 2026-11-06 後照範本接過 CI 的專案,再加資安包這一行,舊程式的新告警會讓 CI 馬上紅。
- spec 只說「第一次接一樣先產基準線」,沒寫對已接過的專案要刪掉基準線重產。
- 〈不做〉明說不加健檢提醒,所以沒接資安包的專案也沒有任何提示。
引句:「第一次接一樣先產基準線」
佐證:
- file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:184`:基準線先於第 3 步的順序說明。

## 各節與圖譜節點
- 〈用詞〉〈回退〉〈REVISIT〉〈依據來源〉:已讀,無 finding。
- 圖譜節點 `Systems/kotlin規則包`:該節點宣稱的「依型錄主題分檔」(finding 11)與「新規則先放不接閘」(finding 1)會被破壞。節點沒有合約行,其餘 WHY 與 PITFALL 不受影響。
- 圖譜節點 `Systems/linter精選目錄`:第 1 步範本多一行依賴不會破壞既有 KEY。`lumos lint-check` 的 A2 判斷只看 `compose-lint-checks` 與 `io.nlopez.compose.rules`(`scripts/lumos:40564`),資安包不影響它。但 finding 3、12 說的版本相容與基準線順序,要在這一節補。

## 實務隱患鏡頭(這個功能碰到的風險類)
- 金流:無。不碰付款流程。
- 對外送出:無送出資料,但範本讓消費專案 CI 從 Google Maven 拉依賴。供應鏈風險由專案自己承擔,spec 的「由人照抄」說法成立。
- 不可逆:spec 說退提交即回原狀,對本 repo 成立。但已把範本抄走的消費專案、以及針對新規則留下的 `lint-waive` 理由不會跟著退,spec 的〈回退〉沒提。
- 守衛面:有。四條新規則進推送前會擋的集合(finding 1),整包資安包進 CI 會擋的集合(finding 3)。

最嚴重 severity:major,blocking 共 3 條(finding 1、2、3)。
