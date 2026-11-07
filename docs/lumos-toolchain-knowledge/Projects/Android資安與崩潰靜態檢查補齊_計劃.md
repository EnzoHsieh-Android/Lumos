---
type: project
status: done
created: 2026-11-08
updated: 2026-11-08
tags:
  - type/project
  - status/done
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

> 白話:拿業界三份現成清單(Android Lint 內建檢查、Google 另發的 Android 資安 lint 規則包、OWASP 手機 App 資安測試指南 MASTG)對照 Kotlin/Android 寫法型錄,找到型錄還沒涵蓋、而且光讀程式碼或設定檔就判得出的實務隱患。大部分是現成檢查:內建的那批,消費專案照 linter 目錄範本接 CI 後(範本已開 `warningsAsErrors`)本來就會擋,缺的是型錄沒登記、AI 寫碼前查不到;Google 資安規則包(24 條檢查)範本根本沒裝。MASTG 裡現成檢查沒有的 4 種寫法自己寫成 ast-grep 規則,但只有一條在樣本外語料量到誤報低於一成、會擋;其餘三條先放不接閘目錄,量夠了再升。Compose 2 條要等 detekt 升版。

PRIOR-ART: ①內建檢查:Android Lint 官方檢查索引列 id 與標題,每條的等級、提供者與「預設關」字樣在各自的檢查頁(https://googlesamples.github.io/android-custom-lint-rules/checks/index.md.html ,例 https://googlesamples.github.io/android-custom-lint-rules/checks/SetJavaScriptEnabled.md.html );linter 目錄範本已開 `warningsAsErrors = true`,官方 DSL 說明這會讓 warning 級也讓建置失敗(https://developer.android.com/reference/tools/gradle-api/8.7/com/android/build/api/dsl/Lint )。採用:不改範本的等級設定,型錄登記即可;每條檢查頁有「disabled by default」字樣的照既有口徑加進 `B4_DEFAULT_OFF`。②Google 資安規則包:`com.android.security.lint:lint`,官方 README 寫安裝法是 `lintChecks("com.android.security.lint:lint:<version>")`、列 24 條檢查(https://github.com/google/android-security-lints );Google Maven 最新 1.0.4(https://dl.google.com/android/maven2/com/android/security/lint/lint/maven-metadata.xml );建置檔 `build.gradle` 寫 `lintVersion = '31.5.1'`(該檔最後改於 2024-08-07,1.0.4 於 2025-11-13 發版前沒再改)。採用,跟 Slack compose-lints 同一個 `dependencies` 區塊,版本規則照範本既有那條(建置用 lint 版本不高於專案 lint = AGP+23),換算要 AGP 8.5.1 以上。③自寫規則:同類工具 MobSF mobsfscan 的 Kotlin 規則(https://github.com/MobSF/mobsfscan 的 `mobsfscan/rules/semgrep/kotlin/webview.yaml`、`network.yaml`)是「呼叫或屬性賦值加字面 true」的純語法比對,WebView 除錯模式一律報、不看外層判斷;MASTG 測試頁寫明要找的 API(檔案網址存取 MASTG-TEST-0252、WebView 除錯 0227、舊版 TLS 0217、寫死金鑰 0212,網址見〈依據來源〉)。採用同一種形狀規則,在 ast-grep 裡用節點種類比對(ast-grep 的中介變數在賦值左邊只吃單一節點,多層接收者會漏,設計審 r1 實測);除錯開關的判法對齊規則包既有 API-19(只認 `BuildConfig.DEBUG`),再收窄成只認條件恰好是它的那一支。④誤報量測:規則包 RULE「真專案誤報超過命中一成就降級」與操作第 1 條「新規則先放不接閘、量過再升」;資安 API 在 nowinandroid 幾乎不出現,改用 GitHub 程式搜尋撈含目標寫法的真實 repo 檔案,量「命中裡有幾成是誤報」;形狀定案後另撈一批沒看過的 repo 當樣本外語料,以樣本外為準(設計審 r1 整合席:樣本內數字會偏樂觀)。不選:⑤Compose 的 VarsWithoutStateBacking、StaleRememberUpdatedStateInRemember:只在 compose-rules 0.6 以後才有(v0.6.6 起的 docs/rules.md 才有,v0.5.0 沒有),0.5 以後配 detekt 2.x,規則包釘 detekt 1.23.8 加 0.4.28。⑥FLAG_SECURE(MASTG-TEST-0291)與密碼欄鍵盤快取(0258):哪些畫面或欄位算敏感要看業務,形狀判不出。⑦反序列化(MASTG-TEST-0337):測試頁講的是 Intent extras 與 Bundle 這類平台來源,不是 `ObjectInputStream`,寫不成對得上判準的形狀規則。⑧WebView 一般檔案與 content 存取(`allowFileAccess`、`allowContentAccess`):MASTG-TEST-0252 明寫 AllowFileAccess 本身不算漏洞,不寫規則。
RETIRE-IF: 規則包新增的資安規則在樣本外語料量到的誤報超過命中的一成(照規則包 RULE 降級或搬 rules-unwired/);或 Android Lint 內建或 Google 資安規則包補上同一種檢查(那條自寫規則撤掉,型錄改指現成規則)。

## 用詞

- **資安規則包**:Google 發的 `com.android.security.lint:lint`,掛在 Android Lint 上的外掛檢查,不是 AGP 內建。型錄現成規則欄寫成 `資安包:<檢查 id>`(照 `內建:` 的中文前綴先例;提供者原名太長且不是工具名)。官方 README 列 24 條檢查。
- **內建**:隨 AGP 附的 Android Lint 檢查,型錄寫 `內建:<檢查 id>`(既有寫法)。
- **MASTG**:OWASP 手機 App 安全測試指南,每個測試頁有編號(MASTG-TEST-NNNN)。
- **A1、A2**:`lumos lint-check` 與健檢印的 Android 現成檢查提醒代號(A1=CI 設定檔找不到 Android Lint 的跡象、A2=用 Compose 但兩套 Compose 規則都沒接),定義在 [[Systems/linter精選目錄]]。
- **`lint-waive`**:lumos 的新增告警放行指令,對一筆告警的指紋留理由放行,留痕、會被統計。
- **卷證**:審查與實驗的原始紀錄(席報告、判讀表),放 `governance/review-reports/<迴圈編號>/`。
- **實務隱患節的「已排除:<類>」**:`lumos pitfalls --check` 反問的四類風險(金流、對外送出、不可逆、守衛面),每類要答碰不碰。

- **樣本內/樣本外**:樣本內=調規則形狀時看過的語料;樣本外=形狀定案後另撈、排除前面出現過的 repo 的語料,誤報率以樣本外為準。

## 範圍

1. **範本加資安規則包**([[Systems/linter精選目錄]]〈Android Lint 與 Compose lint 標準接法〉第 1 步):`dependencies` 加 `lintChecks("com.android.security.lint:lint:1.0.4")`,附官方 README 與 Maven 網址;寫明:
   - 官方自己說這包「比內建更偏資安、也更實驗性」(README 原文 more security-focused and experimental)。
   - 版本要 AGP 8.5.1 以上(建置用 lint 31.5.1,照同節 Slack 外掛那條規則換算)。
   - 第一次接一樣先產基準線;**已經照範本接過 CI 的專案**加這一行時,要先刪掉 `lint-baseline.xml` 重產再推,不然舊程式的資安告警會讓 CI 立刻紅。
   - 包裡 24 條檢查都登記在型錄(範圍 2),要關哪一條照型錄的檢查 id 在 `lint { disable += "<id>" }` 關。
2. **型錄登記**(`skills/kotlin-idioms/checks-catalog.md`):照既有 12 欄格式,分進現有三類,不新開類別(型錄自檢 `check.py` 的 `_MAIN_ROW_RE` 只認現有九類,lumos 讀型錄也借用同一支檔;下面括號是這次要加進去的內容,不是類別標題)。
   - API(網路與 WebView):WebView 開 JavaScript(內建 SetJavaScriptEnabled)、JavaScript 介面(內建 JavascriptInterface、AddJavascriptInterface)、SSL 錯誤照樣繼續(內建 WebViewClientOnReceivedSslError)、WebView 檔案網址存取(自寫)、WebView 除錯模式(自寫)、Safe Browsing 關掉(資安包 DisabledAllSafeBrowsing)、不安全的 SSL socket(內建 SSLCertificateSocketFactoryGetInsecure、SSLCertificateSocketFactoryCreateSocket)、信任使用者憑證(內建 AcceptsUserCertificates;資安包 DefaultTrustedUserCerts)、舊版 TLS(自寫)、DNS 設定不安全(資安包 InsecureDnsSdkLevel)、寫死內部網址或私有 IP(資安包 UnintendedExposedUrl、UnintendedPrivateIpAddress)。
   - ARCH(元件、Intent 與平台相容):外露 receiver(內建 ExportedReceiver)、外露 content provider(內建 ExportedContentProvider)、PendingIntent 可變又隱式(內建 UnspecifiedImmutableFlag、MutableImplicitPendingIntent)、轉發不可信 Intent(內建 UnsafeIntentLaunch)、沒 action 的隱式 Intent(內建 IntentWithNullActionLaunch、UnsafeImplicitIntentLaunch)、FileProvider 開太寬的路徑(資安包 ExposedRootPath、DotPathAttribute、SlashPathAttribute、HardcodedAbsolutePath;內建 GrantAllUris)、工作被劫持(資安包 StrandhoggVulnerable)、點擊劫持(資安包 TapjackingVulnerable)、App Links 沒驗證(資安包 MissingAutoVerifyAttribute)、黏性廣播(資安包 InsecureStickyBroadcastsMethod、InsecureStickyBroadcastsPermission)、自訂權限保護等級太低(資安包 InsecurePermissionProtectionLevel)、藍牙可被發現時間(資安包 ExtendedBluetoothDiscoveryDuration、ZeroBluetoothDiscoveryDuration)、寫死 debuggable(內建 HardcodedDebugMode)、呼叫超出 minSdk 的 API(內建 NewApi、InlinedApi)、沒權限就呼叫要權限的 API(內建 MissingPermission)、通知權限(內建 NotificationPermission)、manifest 元件無法建立(內建 Instantiatable、MissingClass)、私有 API(內建 SoonBlockedPrivateApi、BlockedPrivateApi)、參數範圍與常數型別(內建 Range、WrongConstant、ResourceType)、Parcelable 缺 CREATOR(內建 ParcelCreator)、通知跳板(內建 NotificationTrampoline)。
   - DATA(秘密、加密、儲存):原始碼裡的秘密(內建 SecretInSource、AuthLeak)、打包私鑰(內建 PackagedPrivateKey)、敏感資料寫進 logcat(資安包 LogInfoDisclosure)、ECB 或沒指定模式的加密(內建 GetInstance;資安包 UnsafeCryptoAlgorithmUsage)、弱雜湊(資安包 VulnerableCryptoAlgorithm)、弱亂數(資安包 WeakPrng;內建 SecureRandom)、全域可讀寫檔(內建 WorldReadableFiles、WorldWriteableFiles、SetWorldReadable)、舊版外部儲存(資安包 InsecureLegacyExternalStorage、SensitiveExternalPath)、寫死金鑰(自寫)。
   - **併進既有列**(型錄規則「同一個錯誤只留一列」):`內建:DataExtractionRules` 併進 DATA-13(那列講的就是 `data_extraction_rules`,級改 `A+D`、通電批次在原有兩段後加「告警帶寫法=批四(CI 範本:Android Lint)」);`資安包:DefaultCleartextTraffic` 併進 API-23(明文 HTTP);`內建:CheckResult` 併進 PERF-36(忽略回傳值,同一個錯誤)。另開不併的:信任使用者憑證跟 API-22(信任所有憑證)後果不同;外露 receiver、content provider 跟 DATA-45(外露 service)各開一列;舊版外部儲存跟 DATA-27(寫死 `/sdcard` 路徑)不是同一個錯誤。
   - **情境怎麼認**:現成規則列寫「形狀:由 Android Lint <檢查 id> 判」(判定是那條檢查做的,型錄只登記);哪些資料算敏感、哪個亂數用在資安場合這類 lint 判不了的語意,不另開情境決策表列(lint 報了就是報了,誤報由專案在 lint 設定關,見範圍 1)。自寫規則列寫「形狀:<規則認的寫法>」。
   - **通電批次**:現成規則列寫「告警帶寫法=批四(CI 範本:Android Lint)」;會擋的自寫規則列寫「告警帶寫法=批一」;放不接閘的寫「告警帶寫法=未接(規則在 rules-unwired/:樣本外誤報超過一成或量不夠)」。
   - **實測狀態**:自寫規則列照型錄既有寫法「規則 <id>:樣本實測中壞例、好例不報」,後面接「真實語料:樣本內 N 處誤報 M、樣本外 N 處誤報 M」;現成規則列寫「未測(lint 規則,CI 跑)」。
   - **來源**:每列帶〔查證 2026-11-08:網址〕,網址是那條檢查的官方說明頁或 MASTG 測試頁;實作時逐一 curl 確認頁面存在、等級與預設開關照頁面寫。〈來源縮寫〉加 `ASL`(資安包 README)、`LINTREF`(lint 檢查索引)、`MASTG`(測試索引)。
   - **統計節**:總列數、各類列數、級的組合、規則包等級條數、會擋規則守到的列數,照型錄既有口徑重算;重算的指令(對主表列與 `rules*/` 的 grep 與計數)寫進實作收貨紀錄,不另寫程式。
3. **第四批口徑認資安包**:型錄自檢 `configs/ast-grep/kotlin-android/check.py` 的 `_B4_LINT` 多認 `資安包:` 前綴,通電批次照樣標「批四(CI 範本:Android Lint)」(資安包掛在 Android Lint 上、同一個 CI 步驟跑);檢查頁寫預設關的,加進 `B4_DEFAULT_OFF`;型錄〈輸入與口徑〉通電批次那條同步寫上。
4. **自寫規則**(`configs/ast-grep/kotlin-android/`,訊息照既有格式「[型錄編號] 錯在哪;改用 <最短修法>」、不超過 120 字,每條附壞例好例樣本;放進按型錄主題分的既有規則檔,API 列的進 `api.yml`、DATA 列的進 `data.yml`):
   - **會擋**(`rules/api.yml`)`kt-webview-file-url-access`:WebView 開檔案網址跨來源存取。認四種寫法:任何接收者的 `.setAllowUniversalAccessFromFileURLs(true)`、`.setAllowFileAccessFromFileURLs(true)`,不帶接收者的同名呼叫(`apply`/`with` 區塊裡),以及左邊整段以 `allowUniversalAccessFromFileURLs` 或 `allowFileAccessFromFileURLs` 結尾、右邊是 `true` 的賦值(節點種類比對,多層接收者、`?.`、`!!` 都認);寫在條件恰好是 `BuildConfig.DEBUG` 的 if 成立那一支或 when 分支裡不報(判法同下一條除錯模式,代碼審 r1 補)。
   - **不接閘**(`rules-unwired/api.yml`)`kt-webview-debugging-enabled`:`WebView.setWebContentsDebuggingEnabled(true)`(含完整套件名、不帶接收者)。不報:寫在條件恰好是 `BuildConfig.DEBUG` 的 if 成立那一支、或條件恰好是 `BuildConfig.DEBUG` 的 when 分支裡;否定、else 分支、`||` 連別的條件、只包在 SDK 版本判斷裡、完全沒包,都報。標準寫法是直接傳 `BuildConfig.DEBUG` 當參數(不報)。放不接閘的理由:樣本外 42 處誤報 16(用 `FLAG_DEBUGGABLE`、別名旗標判除錯版)。
   - **不接閘**(`rules-unwired/api.yml`)`kt-insecure-tls-version`:`SSLContext.getInstance` 第一個參數恰好是 `"SSLv2"`、`"SSLv3"`、`"TLSv1"`、`"TLSv1.1"`(含兩參數版與完整套件名;`"SSL"`、`"TLS"`、`"TLSv1.2"` 不報);`ConnectionSpec.COMPATIBLE_TLS`(含完整套件名,拿來讀 `cipherSuites`、`tlsVersions`、`isTls` 的不報);`tlsVersions(...)` 呼叫參數裡的 `TlsVersion.TLS_1_0`、`TLS_1_1`、`SSL_3_0`(看呼叫的參數節點,分行寫也認);`setEnabledProtocols(arrayOf(...))` 參數裡有上面四個字串。放不接閘的理由:樣本內誤報已達 10.5%。
   - **不接閘**(`rules-unwired/data.yml`)`kt-secretkeyspec-literal-key`:`SecretKeySpec` 第一個參數(含具名參數 `key =`)是不含插值的字串字面值接 `.toByteArray(...)` 或 `.encodeToByteArray(...)`、或參數全是整數字面值的 `byteArrayOf(...)`;變數、插值字串、`byteArrayOf(變數)`、展開、空陣列不報。放不接閘的理由:樣本外只撈到 3 處,量不夠。
   - **升級條件**(不接閘 → `rules/`):樣本外語料(排除這次出現過的 repo)至少 20 處命中、誤報不超過一成;升級時改型錄那列的通電批次與實測狀態。
   - 路徑排除:四條都用規則包 `rules/state.yml` 那份七項清單(`**/src/test*/**`、`**/src/androidTest*/**`、`**/src/testFixtures/**`、`**/src/*Test/**`、`**/src/sharedTest/**`、`**/*-test/src/**`、`**/*testing/src/**`),另加 `**/src/debug*/**`(debug 變體目錄只進除錯版;樣本外語料有一筆誤報就落在這種目錄)。

**不做**:不改 `warningsAsErrors` 等範本既有設定;不在推送前跑 Android Lint(上一案已決定只在 CI 跑);不接 compose-rules 0.6 的兩條(PRIOR-ART ⑤);不寫 FLAG_SECURE、密碼欄鍵盤、反序列化、WebView 一般檔案存取的規則(PRIOR-ART ⑥⑦⑧);不新開型錄類別;不加健檢提醒(資安包沒裝的專案,A1/A2 那種字面提醒另案)。代碼審 r2 架構對齊席指出同一包裡出現兩套除錯判法,改成共用判斷 `configs/ast-grep/kotlin-android/utils/debug-only.yml`(新增),既有 API-19、DATA-16 一起改用(原本把 `!BuildConfig.DEBUG` 與 else 分支也當成有開關,改後照報),見〈審計修正紀錄〉。

REVISIT:2027-05-08 看 detekt 有沒有升 2.x;升了就把 compose-rules 換 0.6 以後的版本,型錄補 VarsWithoutStateBacking、StaleRememberUpdatedStateInRemember 兩列
REVISIT:2027-02-08 看資安包有沒有新版(Google Maven metadata),範本版本與型錄檢查清單照新版改;看 FLAG_SECURE 與密碼欄要不要進情境決策表;再撈一批樣本外語料,看三條不接閘規則能不能照升級條件升

## 實驗

### 第一輪(設計審前,樣本內)

2026-11-08,ast-grep 0.51.1,草稿規則放 scratchpad 跑(未進 repo)。語料:①五個開源 App 淺複製整份(duckduckgo/Android、thunderbird-android、nextcloud/android、AntennaPod、Tusky,共 11,618 支 kt 檔);②GitHub 程式搜尋八個目標寫法、撈回 186 支 kt 檔(保留原路徑,路徑排除才量得到);③寫死金鑰另撈 74 支。②裡三個 repo 是靜態分析工具的規則樣本與 OWASP 示範檔(federicodotta/semgrep-rules、j3ssie/curated-semgrep-rules、OWASP/mastg),是刻意寫壞的教材、不是 App 程式,從語料移出。每處命中由代理打開命中行前後 15 行判真假,編排者看過判讀表、抽看上下文。

| 規則 | 第一版 | 改形狀 | 最後命中 | 誤報 |
|---|---|---|---|---|
| WebView 檔案網址跨來源存取 | 84 處,誤報 13 全是分析工具樣本 | 不改 | 71 | 0 |
| 舊版 TLS | 18 處,誤報 2、判不準 1 | 拿掉 `"SSL"`(Android 上回傳的仍是 TLS 1.2 以上,判不準那筆);包在條件不是單純比 `Build.VERSION.SDK_INT` 的 if 裡不報(誤報那筆包在命令列除錯旗標裡) | 13 | 1(建好沒用的死程式),7.7% |
| WebView 除錯模式 | 第一版只排除條件含 debug 的 if:五個 App 整份 3 處全被排除(都包在 `BuildConfig.DEBUG` 或 `isDebuggable` 裡);語料②17 處,誤報 2(包在熱重載旗標、開發版套件名判斷裡) | 同舊版 TLS 的結構判斷:只有單純比 SDK 版本的 if 照報,其他 if 一律當成有開關 | 11 | 0(代價:4 處真問題被放過,三處是 Xposed 模組刻意開、一處包在別的判斷) |
| 寫死金鑰 | 五個 App 6 處全誤報(比到演算法名稱字串 `"AES"`) | 只看第一個參數是字串字面值轉位元組或 `byteArrayOf(...)`;字串有插值(`"$secret&"`,執行時才組出來)不報 | 語料②8 處、③60 處 | 2(Telegram WebApp 的 `"WebAppData"`、BIP32 的 `"Bitcoin seed"`,協定規定的公開常數),2.9% |

- 第一輪結論已被第二輪推翻(四條都放 `rules/` 那個結論):形狀是看同一批語料調的,設計審 r1 指出樣本內偏樂觀,而且多層接收者、分行呼叫鏈、反向除錯判斷三類寫法沒在語料裡被量到。

### 第二輪(設計審 r1 之後,樣本外)

- 第二版規則照 PRIOR-ART ③ 改成節點種類比對,先拿審查席留下的樣本與編排者寫的逐例樣本實跑(卷證 experiment/v2-key-cases.kt.txt、v2-debug-cases.kt.txt:該報的全報、不該報的全不報);實跑時發現第二版寫死金鑰規則整條零命中(限制掛錯節點),改成看第一個參數節點後才對。
- 樣本外語料:GitHub 程式搜尋另撈 250 支(檔案網址與除錯模式)加 419 支(寫死金鑰,按路徑分批查)kt 檔,排除前兩批出現過的 repo。每處命中由代理打開前後 20 行判真假(卷證 experiment/oos-judge.tsv)。

| 規則 | 樣本外命中 | 誤報 | 放哪 |
|---|---|---|---|
| WebView 檔案網址跨來源存取 | 80 | 0 | `rules/`(會擋) |
| WebView 除錯模式 | 42 | 16(38%):別名除錯旗標 8、直接判 `FLAG_DEBUGGABLE` 6、BuildType 比對 1、debug 變體目錄 1 | `rules-unwired/` |
| 寫死金鑰 | 3 | 0 | `rules-unwired/`(量不夠) |
| 舊版 TLS | 沒另撈(樣本內第二版 19 處誤報 2,已達 10.5%) | — | `rules-unwired/` |

- 量不到的:漏報(語料偏向命中);寫死金鑰的樣本外分母太小。
- 卷證:`governance/review-reports/android資安與崩潰靜態檢查補齊/experiment/`(兩版規則、判讀表、語料清單;語料本身不進 repo,清單附 repo 與路徑可重抓)。

## 實務隱患

- **資安包是實驗性**:官方自己說比內建更實驗,可能誤報;範本照樣先產基準線,新告警才擋,誤報由專案自己在 lint 設定關掉那一條(型錄有全部 24 條的 id)。
- **已接過範本的專案加資安包會立刻紅**:範圍 1 寫明要先刪基準線重產。
- **內建檢查要等 CI**:型錄登記後 AI 寫碼前查得到,但機器真的擋要消費專案照範本接 CI;推送前沒有。
- **會擋的那條只認字面 true**:`val enable = true` 再傳進去、別名 import 會漏;只是漏報,不會誤擋。
- **三條自寫規則不擋**:不接閘目錄只在規則包自檢跑樣本,消費專案推送前不報;型錄那列照實寫「未接」。
- **GitHub 程式搜尋的語料偏向命中**:只量得出命中裡的誤報比例,量不出漏報。
- 已排除:金流:不碰付款
- 已排除:對外送出:規則與型錄都是本機讀檔;範本的依賴由人照抄,依賴從 Google Maven 拉是消費專案自己的供應鏈
- 已排除:不可逆:新增規則、型錄列與範本文字,退提交即回原狀;已抄走範本的消費專案與留下的 `lint-waive` 理由不跟著退(見〈回退〉)
- 守衛面:新增一條會擋的推送前規則(擋得更多)、範本讓消費專案 CI 多跑 24 條資安檢查,走完整設計審

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 要比對業界清單、出處要官方 | 使用者要求 | 使用者 2026-11-05「你的標準、最佳寫法來源要有依據，不要你自己寫」;2026-11-07「Android的規則也一樣，來源、依據」 |
| 內建檢查的等級、提供者、預設開關 | Android Lint 官方各檢查頁 | https://googlesamples.github.io/android-custom-lint-rules/checks/index.md.html |
| 資安規則包安裝法、檢查清單、版本 | 官方 README、Google Maven、建置檔 | https://github.com/google/android-security-lints 、https://dl.google.com/android/maven2/com/android/security/lint/lint/maven-metadata.xml |
| 自寫規則用呼叫與賦值形狀 | MobSF mobsfscan 的 Kotlin 規則 | https://github.com/MobSF/mobsfscan |
| WebView 檔案網址存取 | MASTG-TEST-0252(FileURL 設定是失敗的必要條件之一) | https://mas.owasp.org/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0252/ |
| WebView 除錯模式 | MASTG-TEST-0227 | https://mas.owasp.org/MASTG/tests/android/MASVS-RESILIENCE/MASTG-TEST-0227/ |
| 舊版 TLS | MASTG-TEST-0217 | https://mas.owasp.org/MASTG/tests/android/MASVS-NETWORK/MASTG-TEST-0217/ |
| 寫死金鑰 | MASTG-TEST-0212 | https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0212/ |
| 誤報超過一成要降級、新規則先不接閘 | 規則包 RULE 與操作第 1 條(Google Tricorder 門檻) | [[Systems/kotlin規則包]] |

## 驗收條款

- [S1] 當讀 linter 目錄〈Android Lint 與 Compose lint 標準接法〉第 1 步的 kotlin 圍欄時,`dependencies` 區塊 應 有 `lintChecks("com.android.security.lint:lint:1.0.4")` 這一行,而且同一步的文字 應 寫出「AGP 8.5.1」與「刪掉」基準線重產的說明 [test:t_linter_catalog_android_security_lint]
- [S2] 當型錄某列現成規則欄有一段寫 `資安包:<大寫開頭的檢查 id>`、不含待查等四個字樣,而且通電批次寫了批四時,型錄自檢 應 要求標的是「批四(CI 範本:Android Lint)」,標成別的批四值 應 報問題;`batch4_expected_tags` 對同一欄拿掉 `資安包:` 前綴後 應 回空清單 [test:t_kt_catalog_batch4_wiring]
- [S3] 當新寫的逐例測試對預期值表每一列 S3 的寫法各跑一次規則包時,該報的 應 恰好被那條規則報一次、不該報的 應 不被它報 [test:t_kotlin_rulepack_security_rules]
- [S4] 當列舉規則包時,`kt-webview-file-url-access` 應 在 `rules/api.yml`,`kt-webview-debugging-enabled`、`kt-insecure-tls-version` 應 在 `rules-unwired/api.yml`,`kt-secretkeyspec-literal-key` 應 在 `rules-unwired/data.yml`,每條訊息 應 以這次新增的型錄列編號開頭、不超過 120 字 [test:t_kotlin_rulepack_security_rules]
- [S5] 當跑型錄自檢時,真實型錄 應 是 0 個問題、還沒逐列查證 應 是 0 列(新增的列都帶查證紀錄;原本的 2 列 API-14、TEST-31 在 2026-11-08 使用者裁定後標出處不全),型錄裡 應 找得到資安包 README 列的 24 個檢查 id [test:t_kt_catalog_security_lint_ids]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | linter 目錄第 1 步的 kotlin 圍欄 | 有 `lintChecks("com.android.security.lint:lint:1.0.4")` | 官方 README 安裝法與 Google Maven 最新版 1.0.4 |
| S2 | 現成規則欄 `資安包:LogInfoDisclosure`、通電批次標「批四(現成規則)」 | 型錄自檢報這列不一致 | 本計劃範圍 3;資安包掛在 Android Lint 上同一步跑(官方 README 第 2 步 `./gradlew lint`) |
| S3 | `webView.settings.allowUniversalAccessFromFileURLs = true` | 報 | MASTG-TEST-0252;設計審 r1 通才、邊界兩席實測多層接收者 |
| S3 | `settings.apply { allowFileAccessFromFileURLs = true }` | 報 | MASTG-TEST-0252 |
| S3 | `s?.setAllowUniversalAccessFromFileURLs(true)` | 報 | MASTG-TEST-0252 |
| S3 | `webView.settings.allowFileAccessFromFileURLs = false` | 不報 | MASTG-TEST-0252:設成 false 是建議寫法 |
| S3 | `if (BuildConfig.DEBUG) { WebView.setWebContentsDebuggingEnabled(true) }` | 不報 | MASTG-TEST-0227:只在除錯版開 |
| S3 | `if (!BuildConfig.DEBUG) { WebView.setWebContentsDebuggingEnabled(true) }` | 報 | MASTG-TEST-0227;設計審 r1 通才席實測 |
| S3 | `if (BuildConfig.DEBUG) { } else { WebView.setWebContentsDebuggingEnabled(true) }` | 報 | MASTG-TEST-0227;設計審 r1 通才席實測 |
| S3 | `if (Build.VERSION.SDK_INT >= 19) { WebView.setWebContentsDebuggingEnabled(true) }` | 報 | MASTG-TEST-0227;版本判斷不是除錯開關 |
| S3 | `WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)` | 不報 | 官方建議寫法:直接傳除錯旗標 |
| S3 | `SSLContext.getInstance("TLSv1")` | 報 | MASTG-TEST-0217 列的舊版 TLS 寫法 |
| S3 | `SSLContext.getInstance("TLSv1.2")` | 不報 | MASTG-TEST-0217 只點名舊版本;設計審 r1 整合席點名的邊界 |
| S3 | `SSLContext.getInstance("TLS")` | 不報 | MASTG-TEST-0217 只點名指定舊版本的寫法 |
| S3 | 分兩行的 `ConnectionSpec.Builder(x)` 接下一行 `.tlsVersions(TlsVersion.TLS_1_0)` | 報 | MASTG-TEST-0217;設計審 r1 邊界席實測分行寫法 |
| S3 | `ConnectionSpec.COMPATIBLE_TLS.cipherSuites` | 不報 | 實驗語料 okhttp tlssurvey:只讀屬性沒啟用 |
| S3 | `SecretKeySpec("0123456789abcdef".toByteArray(), "AES")` | 報 | MASTG-TEST-0212 寫死金鑰 |
| S3 | `SecretKeySpec(byteArrayOf(0x48, 0x65), "AES")` | 報 | MASTG-TEST-0212;樣本外語料的真實寫法 |
| S3 | `SecretKeySpec("$secret&".toByteArray(), "HmacSHA1")` | 不報 | 實驗語料 OAuth 簽章金鑰:執行時組出來的,不是寫死 |
| S3 | `SecretKeySpec(byteArrayOf(x, y), "AES")` | 不報 | 設計審 r1 邊界席:變數組出來的不是寫死 |
| S3 | 放在 `src/debug/kotlin/` 底下的 `webView.settings.allowFileAccessFromFileURLs = true` | 不報 | debug 變體目錄只進除錯版(樣本外語料一筆誤報在這種目錄) |
| S3 | `with(webView.settings) { setAllowUniversalAccessFromFileURLs(true) }` | 報 | MASTG-TEST-0252;代碼審 r1 審查席:不帶接收者的呼叫原本沒有案例守 |
| S3 | `socket.setEnabledProtocols(arrayOf("TLSv1", "TLSv1.2"))` | 報 | MASTG-TEST-0217 列的 `setEnabledProtocols` 寫法 |
| S3 | `if (BuildConfig.DEBUG) { webView.settings.allowFileAccessFromFileURLs = true }` | 不報 | 只在除錯版開;判法同除錯模式那條(代碼審 r1 審查席) |
| S3 | `if (!BuildConfig.DEBUG) { webView.settings.allowFileAccessFromFileURLs = true }` | 報 | 否定是正式版才開 |
| S4 | 列舉規則包 | 一條在 `rules/api.yml`、兩條在 `rules-unwired/api.yml`、一條在 `rules-unwired/data.yml`,訊息以新列編號開頭且不超過 120 字 | 規則包 WHY:訊息格式與 120 字上限;本計劃〈實驗〉第二輪的放置 |
| S5 | 真實型錄跑型錄自檢、對資安包 README 的 24 個 id 逐一找 | 0 個問題、還沒逐列查證 0 列、24 個 id 都找得到 | 型錄逐列查證計劃:新增列要同提交帶查證紀錄;官方 README 檢查清單 |

## 回退

退回本計劃的提交:範本那一行依賴與說明、型錄新增列與 DATA-13、API-23、PERF-36 補的檢查 id、〈統計〉節數字、`_B4_LINT` 的 `資安包` 前綴與 `B4_DEFAULT_OFF` 新增項、自寫規則與樣本、新測試拿掉。已照範本加了資安包的消費專案與已留下的 `lint-waive` 理由不會跟著退,要另外通知。

## 天花板

1. 誤報只量了命中裡的比例,漏報沒量。
2. 內建與資安包的檢查要消費專案 CI 跑才擋;lumos 判不到 CI 有沒有真的跑(既有 A1 只看字面)。
3. 型錄自檢只核對通電批次已寫批四的列:新列漏寫批四那一段,自檢不會報(既有口徑的盲點,這案不改)。
4. 這次只有一條自寫規則會擋;另外三條要等樣本外語料夠才升。

## 審計修正紀錄

- r1(2026-11-08,4 席):27 條/blocking 9/規則形狀用中介變數配整串、自創除錯判法、樣本內量測三組根因;改用節點種類比對、對齊 API-19 再收窄、另撈樣本外語料定放置(只留一條會擋),資安包 24 條全登記並寫版本與基準線重產,條款改綁逐例測試;卷證 governance/review-reports/android資安與崩潰靜態檢查補齊/。
- 例:輸入 `webView.settings.allowUniversalAccessFromFileURLs = true` → 第一版不報、修後報;輸入 `if (!BuildConfig.DEBUG) { WebView.setWebContentsDebuggingEnabled(true) }` → 第一版不報、修後報。
- 2026-11-08 實作:型錄新增 41 列(API-37–47、ARCH-68–88、DATA-79–87),DataExtractionRules、DefaultCleartextTraffic、CheckResult 併進 DATA-13、API-23、PERF-36;API-23 原寫的 `內建:DefaultCleartextTraffic` 照檢查頁提供者改成資安包;63 個檢查頁逐頁查過都沒有「disabled by default」,`B4_DEFAULT_OFF` 不加;舊版 TLS 規則照範圍 4 補 `setEnabledProtocols`(草稿沒有);統計重算腳本存卷證 experiment/catalog-stats.py.txt。
- 2026-11-08 代碼審 r1(2 席):6 條/blocking 1/規則讀法收進 load_rules、訊息上限讀 MSG_MAX、會擋那條也認 BuildConfig.DEBUG 成立那一支、補 with 區塊與 setEnabledProtocols 案例;測試找檔路徑的寫法照鄰居兩種並存放行;卷證 governance/review-reports/code-android資安與崩潰靜態檢查補齊/。
- 2026-11-08 代碼審 r2(2 席新席):5 條/blocking 2/同一包兩套除錯判法 → 抽成 utils/debug-only.yml、四份 sgconfig 掛 utilDirs,API-40、API-41、API-19、DATA-16 四條共用(條件是 BuildConfig.DEBUG 或只用「且」接別的條件的 if 成立那一支、或 when 的 DEBUG 分支);else、when、且、或四個子條件各補案例;舊版 TLS 補 `?.` 與屬性賦值寫法;load_rules 讀多行 ignores。例:`if (BuildConfig.DEBUG) Level.NONE else Level.BODY` → 改前 API-19 不報、改後報。
- 2026-11-08 代碼審 r3(2 席新席):7 條/blocking 2/共用除錯判斷用字面正規式判條件(排除驚嘆號把 `!=`、`!x && DEBUG` 也當正式版)、「X 且 DEBUG」那支沒案例守;同一判讀第二次被打穿,換形狀改看語法節點種類(條件本身是除錯旗標、或「且」的直接一項是它;!DEBUG 的 else;when 主詞的 true 分支;可帶套件名),不再用字面;共用判斷 id 改短名 in-debug-only-branch、規則包節點補目錄說明;舊版 TLS 的屬性賦值改節點種類比對。r3 是代碼審上限,修補由審查三列的全部寫法加 12 筆新案例與 6 個改壞驗證把關,沒有再派新席。例:`if (x != null && BuildConfig.DEBUG) Level.BODY else Level.NONE` → r2 版 API-19 報、r3 版不報;`if (a && (b || BuildConfig.DEBUG))` → 報。
