---
type: project
status: doing
created: 2026-11-08
updated: 2026-11-08
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
  - risk/守衛面
related:
  - "[[Projects/Android現成檢查接上CI與推送前_計劃]]"
  - "[[Projects/Android寫法型錄逐列查證_計劃]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/kotlin規則包
  - Systems/linter精選目錄
---
# Android資安與崩潰靜態檢查補齊_計劃

> 白話:拿業界三份現成清單(Android Lint 內建檢查、Google 另發的 Android 資安 lint 規則包、OWASP 手機 App 資安測試指南 MASTG)對照 Kotlin/Android 寫法型錄,找到 40 條型錄還沒涵蓋、而且光讀程式碼或設定檔就判得出的實務隱患(資安 30 條、會閃退或功能失效 8 條、Compose 2 條);這案做其中 38 條,Compose 那 2 條要等 detekt 升版(見 PRIOR-ART ⑤)。大部分是現成檢查:內建的那批,消費專案照 linter 目錄範本接 CI 後(範本已開 `warningsAsErrors`)本來就會擋,缺的是型錄沒登記、AI 寫碼前查不到;Google 資安規則包範本根本沒裝。MASTG 裡內建檢查沒有的 6 種寫法自己寫成 ast-grep 規則。這案把三件事補上:範本加資安規則包、型錄登記、自寫規則。

PRIOR-ART: ①內建檢查:Android Lint 官方檢查索引每條有等級與提供者(https://googlesamples.github.io/android-custom-lint-rules/checks/index.md.html );linter 目錄範本已開 `warningsAsErrors = true`,官方 DSL 說明這會讓 warning 級也讓建置失敗(https://developer.android.com/reference/tools/gradle-api/8.7/com/android/build/api/dsl/Lint )。採用:不改範本的等級設定,型錄登記即可。②Google 資安規則包:`com.android.security.lint:lint`,官方 README 寫安裝法是 `lintChecks("com.android.security.lint:lint:<version>")`(https://github.com/google/android-security-lints );Google Maven 最新 1.0.4(2025-12-12,https://dl.google.com/android/maven2/com/android/security/lint/lint/maven-metadata.xml )。採用,跟 Slack compose-lints 同一個 `dependencies` 區塊。③自寫規則:MASTG 每個測試頁寫明要找的 API 與參數(WebView 檔案存取 MASTG-TEST-0252/0250、WebView 除錯 0227、舊版 TLS 0217、寫死金鑰 0212、反序列化 0337,網址見〈依據來源〉);同類工具的做法:MobSF 的 mobsfscan 與 semgrep 社群規則(例 https://github.com/federicodotta/semgrep-rules 的 android-webview 規則)都是「呼叫形狀加字面參數」的純語法比對。採用同一種形狀規則,沿用規則包既有的 ast-grep 寫法、路徑排除與訊息格式。④誤報量測:規則包 RULE「真專案誤報超過命中一成就降級」;既有做法是拿 nowinandroid 整份掃(資安 API 在那裡幾乎不出現,量不到),這次另用 GitHub 程式搜尋撈含目標寫法的真實檔案(偏向命中,量的是「命中裡有幾成是誤報」,正是那條 RULE 的口徑)。不選:⑤Compose 的 VarsWithoutStateBacking、StaleRememberUpdatedStateInRemember:只在 compose-rules 0.6 以後才有(v0.6.6 起的 docs/rules.md 才有這兩條,v0.5.0 沒有),0.5 以後配 detekt 2.x,規則包釘的是 detekt 1.23.8 加 0.4.28,升 detekt 是另一案。⑥FLAG_SECURE(MASTG-TEST-0291)與密碼欄鍵盤快取(0258):哪些畫面或欄位算敏感要看業務,形狀判不出,不寫規則。
RETIRE-IF: 規則包新增的資安規則在真專案量到的誤報超過命中的一成(照規則包 RULE 降級或搬 rules-unwired/);或 Android Lint 內建或 Google 資安規則包補上同一種檢查(那條自寫規則撤掉,型錄改指現成規則)。

## 用詞

- **資安規則包**:Google 發的 `com.android.security.lint:lint`,掛在 Android Lint 上的外掛檢查,不是 AGP 內建。型錄現成規則欄寫成 `資安包:<檢查 id>`。
- **內建**:隨 AGP 附的 Android Lint 檢查,型錄寫 `內建:<檢查 id>`(既有寫法)。
- **MASTG**:OWASP 手機 App 安全測試指南,每個測試頁有編號(MASTG-TEST-NNNN)。
- **A1、A2**:`lumos lint-check` 與健檢印的 Android 現成檢查提醒代號(A1=CI 設定檔找不到 Android Lint 的跡象、A2=用 Compose 但兩套 Compose 規則都沒接),定義在 [[Systems/linter精選目錄]]。
- **`lint-waive`**:lumos 的新增告警放行指令,對一筆告警的指紋留理由放行,留痕、會被統計。
- **卷證**:審查與實驗的原始紀錄(席報告、判讀表),放 `governance/review-reports/<迴圈編號>/`。
- **實務隱患節的「已排除:<類>」**:`lumos pitfalls --check` 反問的四類風險(金流、對外送出、不可逆、守衛面),每類要答碰不碰。

## 範圍

1. **範本加資安規則包**([[Systems/linter精選目錄]]〈Android Lint 與 Compose lint 標準接法〉第 1 步):`dependencies` 加 `lintChecks("com.android.security.lint:lint:1.0.4")`,附官方 README 與 Maven 網址;寫明這個包的檢查官方說是「比內建更偏資安、也更實驗性」(README 原文 more security-focused and experimental),第一次接一樣先產基準線。
2. **型錄登記**(`skills/kotlin-idioms/checks-catalog.md`):照既有 12 欄格式,分進現有三類,不新開類別(型錄自檢 `check.py` 的 `_MAIN_ROW_RE` 只認現有九類,lumos 讀型錄也借用同一支檔;下面括號是這次要加進去的內容,不是類別標題):
   - API(網路與 WebView):WebView 開 JavaScript(內建 SetJavaScriptEnabled)、JavaScript 介面(內建 JavascriptInterface、AddJavascriptInterface)、SSL 錯誤照樣繼續(內建 WebViewClientOnReceivedSslError)、WebView 檔案網址存取(自寫)、WebView 除錯模式(自寫)、Safe Browsing 關掉(資安包 DisabledAllSafeBrowsing)、不安全的 SSL socket(內建 SSLCertificateSocketFactoryGetInsecure、SSLCertificateSocketFactoryCreateSocket)、信任使用者憑證(內建 AcceptsUserCertificates;資安包 DefaultTrustedUserCerts)、舊版 TLS(自寫)。
   - ARCH(元件、Intent 與平台相容):外露 receiver(內建 ExportedReceiver)、外露 content provider(內建 ExportedContentProvider)、PendingIntent 可變又隱式(內建 UnspecifiedImmutableFlag、MutableImplicitPendingIntent)、轉發不可信 Intent(內建 UnsafeIntentLaunch)、沒 action 的隱式 Intent(內建 IntentWithNullActionLaunch、UnsafeImplicitIntentLaunch)、FileProvider 開根目錄(資安包 ExposedRootPath;內建 GrantAllUris)、寫死 debuggable(內建 HardcodedDebugMode)、呼叫超出 minSdk 的 API(內建 NewApi、InlinedApi)、沒權限就呼叫要權限的 API(內建 MissingPermission)、通知權限(內建 NotificationPermission)、manifest 元件無法建立(內建 Instantiatable、MissingClass)、私有 API(內建 SoonBlockedPrivateApi、BlockedPrivateApi)、參數範圍與常數型別(內建 Range、WrongConstant、ResourceType)、沒用回傳值(內建 CheckResult)、Parcelable 缺 CREATOR(內建 ParcelCreator)、通知跳板(內建 NotificationTrampoline)。
   - DATA(秘密、加密、儲存與序列化):原始碼裡的秘密(內建 SecretInSource、AuthLeak)、打包私鑰(內建 PackagedPrivateKey)、敏感資料寫進 logcat(資安包 LogInfoDisclosure)、備份規則(內建 DataExtractionRules,已有 DATA-13 的併進去)、ECB 或沒指定模式的加密(內建 GetInstance;資安包 UnsafeCryptoAlgorithmUsage)、弱雜湊(資安包 VulnerableCryptoAlgorithm)、弱亂數(資安包 WeakPrng;內建 SecureRandom)、全域可讀寫檔(內建 WorldReadableFiles、WorldWriteableFiles、SetWorldReadable)、舊版外部儲存(資安包 InsecureLegacyExternalStorage、SensitiveExternalPath)、寫死金鑰(自寫)、反序列化不可信資料(自寫)。
   - 每列來源欄帶〔查證 2026-11-08:網址〕,網址是那條檢查的官方說明頁或 MASTG 測試頁。併進既有列的只有一個:`內建:DataExtractionRules` 併進 DATA-13(那列講的就是 `data_extraction_rules`);信任使用者憑證跟 API-22(信任所有憑證)後果不同,另開新列;外露 receiver 與 content provider 跟 DATA-45(外露 service)各開一列,不併。
   - 新列的通電批次:現成規則列寫「告警帶寫法=批四(CI 範本:Android Lint)」;自寫規則列寫「告警帶寫法=批一」;實測狀態欄寫〈實驗〉量到的命中與誤報(規則包操作第 4 條要求寫回)。
   - 型錄〈統計〉節(總列數、各類列數、規則包等級條數、會擋規則守到的列數)照程式重算。
3. **第四批口徑認資安包**:型錄自檢 `configs/ast-grep/kotlin-android/check.py` 的 `_B4_LINT` 多認 `資安包:` 前綴,通電批次照樣標「批四(CI 範本:Android Lint)」(資安包掛在 Android Lint 上、同一個 CI 步驟跑);型錄〈輸入與口徑〉通電批次那條同步寫上。
4. **自寫規則**(`configs/ast-grep/kotlin-android/`,訊息照既有格式「[型錄編號] 錯在哪;改用 <最短修法>」、不超過 120 字,每條附壞例好例樣本):
   - 會擋(`rules/`,新檔 `rules/security.yml`(新增)):
     - WebView 開檔案網址跨來源存取:`setAllowUniversalAccessFromFileURLs(true)`、`setAllowFileAccessFromFileURLs(true)` 與屬性寫法 `allowUniversalAccessFromFileURLs = true`、`allowFileAccessFromFileURLs = true`。
     - WebView 除錯模式:`setWebContentsDebuggingEnabled(true)`,往外找到的任何一層 if,條件只要不是單純比 `Build.VERSION.SDK_INT` 就不報(結構判斷,不看旗標名);不在任何 if 裡、或只包在 SDK 版本比較裡才報。
     - 舊版 TLS:`SSLContext.getInstance` 的字串參數是 SSLv2、SSLv3、TLSv1、TLSv1.1(`"SSL"`、`"TLS"` 不報);`ConnectionSpec.COMPATIBLE_TLS`,但拿來讀 `cipherSuites`、`tlsVersions`、`isTls` 屬性的不報;`tlsVersions(...)` 呼叫裡的 `TlsVersion.TLS_1_0`、`TLS_1_1`、`SSL_3_0`;三種寫法都套跟除錯模式同一個 if 判斷。
     - 寫死金鑰:`SecretKeySpec` 第一個參數是字串字面值接 `.toByteArray(...)` 或 `.encodeToByteArray(...)`、或 `byteArrayOf(...)`;字串裡有 `$` 插值的不報。
   - 不接閘(`rules-unwired/`):WebView 開一般檔案或 content 存取(`allowFileAccess`、`allowContentAccess` 設 true;離線網頁常是刻意的)、`ObjectInputStream(...)`(來源可不可信形狀分不出)。兩條都沒逐筆量誤報,照規則包 WHY「還沒量過誤報的新規則放 rules-unwired/」,型錄通電批次寫「未接」。
   - 路徑排除:四條會擋的規則都用規則包 `rules/state.yml` 那份七項清單(`**/src/test*/**`、`**/src/androidTest*/**`、`**/src/testFixtures/**`、`**/src/*Test/**`、`**/src/sharedTest/**`、`**/*-test/src/**`、`**/*testing/src/**`),另加 `**/src/debug*/**`(debug 變體的程式只進 debug 版)。

**不做**:不改 `warningsAsErrors` 等範本既有設定;不在推送前跑 Android Lint(上一案已決定只在 CI 跑);不接 compose-rules 0.6 的兩條(見 PRIOR-ART ⑤);不寫 FLAG_SECURE 與密碼欄鍵盤規則(見 PRIOR-ART ⑥);不新開型錄類別;不加健檢提醒(資安包沒裝的專案,A1/A2 那種字面提醒另案)。

REVISIT:2027-05-08 看 detekt 有沒有升 2.x;升了就把 compose-rules 換 0.6 以後的版本,型錄補 VarsWithoutStateBacking、StaleRememberUpdatedStateInRemember 兩列
REVISIT:2027-02-08 看資安包有沒有新版(Google Maven metadata),範本版本照新版改;看 FLAG_SECURE 與密碼欄要不要進情境決策表

## 實驗

2026-11-08,ast-grep 0.51.1,草稿規則放 scratchpad 跑(未進 repo)。語料:①五個開源 App 淺複製整份(duckduckgo/Android、thunderbird-android、nextcloud/android、AntennaPod、Tusky,共 11,618 支 kt 檔);②GitHub 程式搜尋八個目標寫法、撈回 186 支 kt 檔(保留原路徑,路徑排除才量得到);③寫死金鑰另撈 74 支。②裡三個 repo 是靜態分析工具的規則樣本與 OWASP 示範檔(federicodotta/semgrep-rules、j3ssie/curated-semgrep-rules、OWASP/mastg),是刻意寫壞的教材、不是 App 程式,從語料移出。每處命中由代理打開命中行前後 15 行判真假,編排者看過判讀表、抽看上下文。

| 規則 | 第一版 | 改形狀 | 最後命中 | 誤報 |
|---|---|---|---|---|
| WebView 檔案網址跨來源存取 | 84 處,誤報 13 全是分析工具樣本 | 不改 | 71 | 0 |
| 舊版 TLS | 18 處,誤報 2、判不準 1 | 拿掉 `"SSL"`(Android 上回傳的仍是 TLS 1.2 以上,判不準那筆);包在條件不是單純比 `Build.VERSION.SDK_INT` 的 if 裡不報(誤報那筆包在命令列除錯旗標裡) | 13 | 1(建好沒用的死程式),7.7% |
| WebView 除錯模式 | 第一版只排除條件含 debug 的 if:五個 App 整份 3 處全被排除(都包在 `BuildConfig.DEBUG` 或 `isDebuggable` 裡);語料②17 處,誤報 2(包在熱重載旗標、開發版套件名判斷裡) | 同舊版 TLS 的結構判斷:只有單純比 SDK 版本的 if 照報,其他 if 一律當成有開關 | 11 | 0(代價:4 處真問題被放過,三處是 Xposed 模組刻意開、一處包在別的判斷) |
| 寫死金鑰 | 五個 App 6 處全誤報(比到演算法名稱字串 `"AES"`) | 只看第一個參數是字串字面值轉位元組或 `byteArrayOf(...)`;字串有插值(`"$secret&"`,執行時才組出來)不報 | 語料②8 處、③60 處 | 2(Telegram WebApp 的 `"WebAppData"`、BIP32 的 `"Bitcoin seed"`,協定規定的公開常數),2.9% |

- 結論:四條都在一成以下,放 `rules/` 會擋;協定常數那種誤報用 `lint-waive` 附理由。
- 規則包 RULE 說的「真專案」這次包含 GitHub 程式搜尋撈的真實 repo 檔案:五個 App 整份掃,除錯模式 3 處全被排除、其他三條幾乎沒命中,誤報率主要是搜尋語料量到的。
- WebView 一般檔案存取 94 處、`ObjectInputStream` 25 處,沒逐筆判,所以放 `rules-unwired/`(見範圍 4)。
- 量不到的:漏報(語料偏向命中);命中數小的規則誤報率估不準(舊版 TLS 13 處、除錯模式 11 處)。
- 卷證:命中與判讀表存 `governance/review-reports/android資安與崩潰靜態檢查補齊/experiment/`(judge.tsv 與三份命中摘要;語料本身不進 repo,清單附 repo 與路徑可重抓)。

## 實務隱患

- **資安包是實驗性**:官方自己說比內建更實驗,可能誤報;範本照樣先產基準線,新告警才擋,誤報由專案自己在 lint 設定關掉那一條。
- **內建檢查要等 CI**:型錄登記後 AI 寫碼前查得到,但機器真的擋要消費專案照範本接 CI;推送前沒有。
- **自寫規則的 if 判斷會放過真問題**:除錯模式與舊版 TLS 只要包在任何不是 SDK 版本比較的 if 裡就不報,條件是 `isBeta`、`isXposedHooked` 這種正式版也會成立的旗標也放過(實驗放過 4 處真問題);換來誤報降到一成以下,天花板照實寫。
- **GitHub 程式搜尋的語料偏向命中**:只量得出命中裡的誤報比例,量不出漏報。
- 已排除:金流:不碰付款
- 已排除:對外送出:規則與型錄都是本機讀檔;範本的依賴由人照抄
- 已排除:不可逆:新增規則、型錄列與範本文字,退提交即回原狀
- 守衛面:新增四條會擋的推送前規則(擋得更多),走完整設計審

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 要比對業界清單、出處要官方 | 使用者要求 | 使用者 2026-11-05「你的標準、最佳寫法來源要有依據，不要你自己寫」;2026-11-07「Android的規則也一樣，來源、依據」 |
| 內建檢查的等級與提供者 | Android Lint 官方檢查頁 | https://googlesamples.github.io/android-custom-lint-rules/checks/index.md.html |
| 資安規則包安裝法與版本 | 官方 README、Google Maven | https://github.com/google/android-security-lints 、https://dl.google.com/android/maven2/com/android/security/lint/lint/maven-metadata.xml |
| WebView 檔案網址存取 | MASTG-TEST-0252、0250 | https://mas.owasp.org/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0252/ |
| WebView 除錯模式 | MASTG-TEST-0227 | https://mas.owasp.org/MASTG/tests/android/MASVS-RESILIENCE/MASTG-TEST-0227/ |
| 舊版 TLS | MASTG-TEST-0217 | https://mas.owasp.org/MASTG/tests/android/MASVS-NETWORK/MASTG-TEST-0217/ |
| 寫死金鑰 | MASTG-TEST-0212 | https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0212/ |
| 反序列化 | MASTG-TEST-0337 | https://mas.owasp.org/MASTG/tests/android/MASVS-CODE/MASTG-TEST-0337/ |
| 誤報超過一成要降級 | 規則包 RULE(Google Tricorder 門檻) | [[Systems/kotlin規則包]] |

## 驗收條款

- [S1] 當讀 linter 目錄〈Android Lint 與 Compose lint 標準接法〉第 1 步的 kotlin 圍欄時,`dependencies` 區塊 應 有 `lintChecks("com.android.security.lint:lint:1.0.4")` 這一行 [test:t_linter_catalog_android_security_lint]
- [S2] 當型錄某列現成規則欄有一段寫 `資安包:<大寫開頭的檢查 id>`、不含待查等四個字樣,而且通電批次寫了批四時,型錄自檢 應 要求標的是「批四(CI 範本:Android Lint)」,標成別的批四值 應 報問題;`batch4_expected_tags` 對同一欄拿掉 `資安包:` 前綴後 應 回空清單 [test:t_kt_catalog_batch4_wiring]
- [S3] 當規則包樣本跑四條會擋的新規則時,壞例 應 各自命中;好例 應 不報:除錯模式包在 `if (BuildConfig.DEBUG)` 或任何非 SDK 版本比較的 if 裡、TLS 規則碰到 `ConnectionSpec.COMPATIBLE_TLS.cipherSuites` 或 `SSLContext.getInstance("TLS")`、金鑰是插值字串或變數、檔案放在 `src/test`、`src/debug` 底下;包在 `if (Build.VERSION.SDK_INT < 23)` 裡的除錯模式 應 照報 [test:t_kotlin_rulepack_samples]
- [S4] 當列舉規則包時,四條會擋的新規則 應 在 `rules/security.yml`、兩條不接閘的 應 在 `rules-unwired/`,每條訊息 應 以這次新增或併入的型錄列編號開頭、不超過 120 字 [test:t_kotlin_rulepack_security_rules_placement]
- [S5] 當跑型錄自檢時,真實型錄 應 是 0 個問題、還沒逐列查證 應 維持 2 列(新增的列都帶查證紀錄) [manual:跑 python3.14 configs/ast-grep/kotlin-android/check.py --catalog-only 看最後兩行]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | linter 目錄第 1 步的 kotlin 圍欄 | 有 `lintChecks("com.android.security.lint:lint:1.0.4")` | 官方 README 安裝法與 Google Maven 最新版 1.0.4 |
| S2 | 現成規則欄 `資安包:LogInfoDisclosure`、通電批次標「批四(現成規則)」 | 型錄自檢報這列不一致 | 本計劃範圍 3;資安包掛在 Android Lint 上同一步跑(官方 README 第 2 步 `./gradlew lint`) |
| S3 | `if (BuildConfig.DEBUG) { WebView.setWebContentsDebuggingEnabled(true) }` | 不報 | MASTG-TEST-0227:只在正式版開著才是問題 |
| S3 | `if (Build.VERSION.SDK_INT >= 19) { WebView.setWebContentsDebuggingEnabled(true) }` | 報 | MASTG-TEST-0227;版本判斷不是除錯開關(實驗語料 DoKit、MetaCam 判真問題) |
| S3 | `SSLContext.getInstance("TLSv1")` | 報 | MASTG-TEST-0217 列的舊版 TLS 寫法 |
| S3 | `SSLContext.getInstance("TLS")` | 不報 | MASTG-TEST-0217 只點名指定舊版本的寫法 |
| S3 | `ConnectionSpec.COMPATIBLE_TLS.cipherSuites` | 不報 | 實驗語料 okhttp tlssurvey:只讀屬性沒啟用 |
| S3 | `SecretKeySpec("0123456789abcdef".toByteArray(), "AES")` | 報 | MASTG-TEST-0212 寫死金鑰 |
| S3 | `SecretKeySpec("$secret&".toByteArray(), "HmacSHA1")` | 不報 | 實驗語料 OAuth 簽章金鑰:執行時組出來的,不是寫死 |
| S3 | `settings.allowUniversalAccessFromFileURLs = true` | 報 | MASTG-TEST-0252 |
| S5 | 真實型錄跑型錄自檢 | 0 個問題、還沒逐列查證 2 列 | 型錄逐列查證計劃:新增列要同提交帶查證紀錄,剩 API-14、TEST-31 待人裁 |
| S4 | 列舉規則包 | 四條新會擋規則在 `rules/security.yml`、兩條在 `rules-unwired/`,訊息以新列編號開頭且不超過 120 字 | 規則包 WHY:訊息格式與 120 字上限(新增告警閘截在 120 字) |

## 回退

退回本計劃的提交:範本那一行依賴、型錄新增列與 DATA-13 補的檢查 id、〈統計〉節數字、`_B4_LINT` 的 `資安包` 前綴、自寫規則與樣本拿掉。

## 天花板

1. 誤報只量了命中裡的比例,漏報沒量。
2. 內建與資安包的檢查要消費專案 CI 跑才擋;lumos 判不到 CI 有沒有真的跑(既有 A1 只看字面)。
3. 型錄自檢只核對通電批次已寫批四的列:新列漏寫批四那一段,自檢不會報(既有口徑的盲點,這案不改)。

## 審計修正紀錄
