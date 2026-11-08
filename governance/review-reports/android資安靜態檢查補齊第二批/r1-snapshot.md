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
  - "[[Projects/Android資安與崩潰靜態檢查補齊_計劃]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/kotlin規則包
---
# Android資安靜態檢查補齊第二批_計劃

> 白話:第一批(#174)拿三份業界清單補了資安與閃退檢查。使用者要「靜態能先掃描的實務隱患都先處理過」,於是再拿第四份獨立清單——資安掃描工具 MobSF 的 Kotlin 規則集(50 條)——逐條對照,找到 22 條型錄沒涵蓋、1 條只涵蓋一部分,另外發現第一批登記錯了兩列:DATA-83 登記的 Google 資安包 VulnerableCryptoAlgorithm 其實只看 `Cipher.getInstance`、抓不到 `MessageDigest.getInstance("MD5")`;DATA-79 登記的內建 SecretInSource 其實只看 Gemini SDK 的金鑰。這批修正那兩列、登記 Android Lint 內建有但型錄漏的 4 條、把形狀判得出的 13 種寫法寫成規則(量誤報後只有一條會擋),只能看語意的 7 條寫進〈不做〉。

PRIOR-ART: ①第四份清單:MobSF mobsfscan 的 Kotlin 規則集(https://github.com/MobSF/mobsfscan 的 `mobsfscan/rules/semgrep/kotlin/`),跟第一批用的 Android Lint、Google 資安包、MASTG 是不同來源;逐條對照由代理做、再派一個沒看過結論的乾淨代理用原始問題獨立複核(專案 CLAUDE.md「說沒有之前先派乾淨 agent 對一次」),兩次都判 22 條沒涵蓋、1 條部分涵蓋(卷證 experiment/ 與本計劃〈實驗〉)。②錯登那兩列的依據:Google 檢查原始碼 `BadCryptographyUsageDetector.kt` 先判呼叫的是不是 `javax.crypto.Cipher`、`SecretDetector.kt` 只看 `GenerativeModel` 建構子(兩次對照都讀了原始碼)。③自寫規則的寫法沿用第一批:節點種類比對、八項路徑排除、共用除錯判斷 `utils/debug-only.yml`、樣本外語料量誤報(樣本外命中 ≥20、誤報 ≤10% 才放 `rules/`)。④官方出處:各規則與型錄列的出處見〈依據來源〉,以 OWASP MASTG 測試頁與 Android 官方安全風險指南(https://developer.android.com/privacy-and-security/risks)為主。
RETIRE-IF: 放 `rules-unwired/` 的 12 條,到 2027-05-08 換語料重量仍沒有一條達到升級條件 → 檢討是不是該整類改成表態題而不是規則;或 Android Lint、Google 資安包補上同一種檢查 → 那條自寫規則撤掉、型錄改指現成檢查。

## 用詞

- **樣本內/樣本外**:同第一批([[Projects/Android資安與崩潰靜態檢查補齊_計劃]]):樣本內=調規則形狀時看過的語料;樣本外=形狀凍結後另撈、排除前面出現過的 repo 的語料,誤報率以樣本外為準。
- **錯登**:型錄某列的現成規則欄登記了某個檢查,但那個檢查實際抓不到這列的壞寫法。
- **判不準**:判讀表 `judge-oos.tsv` 的 `UNSURE`;算誤報比例時留在分母(反序列化 5、RSA 1、弱雜湊 4)。
- **外部協定強制**:寫法是外部格式或對方伺服器規定的(例:ADB 簽章用 RSA 無填充、模仿舊版 TLS 指紋),開發者改不了;這次判讀一律算誤報。

## 範圍

1. **修正錯登**(`skills/kotlin-idioms/checks-catalog.md`):
   - DATA-83:現成規則欄把 `資安包:VulnerableCryptoAlgorithm` 寫明「只抓 `Cipher.getInstance` 的弱加密演算法(DES、RC2、RC4、Blowfish),不抓 MessageDigest」,雜湊那半改指自寫規則 `kt-weak-message-digest`(不接閘);名稱拆清楚「弱加密演算法與弱雜湊」。
   - DATA-79:現成規則欄把 `內建:SecretInSource` 寫明「只抓 Gemini SDK 的 GenerativeModel 金鑰」、`內建:AuthLeak` 寫明「只抓網址裡的 user:pass@」,一般寫死秘密改指自寫規則 `kt-hardcoded-secret-name`(不接閘)。
   - 兩列實測狀態照實寫錯登的經過與日期。
2. **登記 Android Lint 內建漏登的 4 條**(都是 Android Open Source Project 提供、Warning、預設開,範本 `warningsAsErrors` 下接 CI 就擋):`SdCardPath` 併進 DATA-27(那列原寫「代號待查」;〈待查證〉節那一行由程式從主表撈,主表改了自然跟著變);`SetWorldWritable` 併進 DATA-85;`UnsafeDynamicallyLoadedCode`(從非程式庫目錄動態載入程式碼)另開 ARCH 列;`UnsanitizedFilenameFromContentProvider`(信任別人 provider 給的檔名)另開 DATA 列。
3. **型錄新列**(編號照型錄現有最大號往下:API 到 47、ARCH 到 88、DATA 到 87;規則訊息開頭用下列編號,初稿裡暫用的 `[SEC-xx]` 實作時換掉):`kt-webview-mixed-content-always`→API-48、`kt-loadurl-external`→API-49、`kt-weak-cipher-suite`→API-50、`kt-zip-slip`→DATA-88、`kt-provider-openfile-traversal`→DATA-89、`kt-rsa-no-oaep`→併進 DATA-82(ECB 與沒指定模式的加密,同一列講 Cipher 參數)、`kt-static-iv`→DATA-90、`kt-weak-key-size`→DATA-91、`kt-weak-message-digest`→併進 DATA-83、`kt-object-input-stream`→DATA-92(DATA-78 管的是類別實作 Serializable,不同一件事)、`kt-db-on-external-files`→DATA-93、`kt-xxe-documentbuilder`→DATA-94、`kt-hardcoded-secret-name`→併進 DATA-79;內建 `UnsafeDynamicallyLoadedCode`→ARCH-89、`UnsanitizedFilenameFromContentProvider`→DATA-95。來源欄帶〔查證 2026-11-08:網址〕(MASTG 或 Android 官方安全風險頁,實作時逐一 curl 確認);實測狀態寫樣本內外的命中與誤報。
4. **自寫規則**(`configs/ast-grep/kotlin-android/`,定案形狀照卷證 experiment/draft-rules.yml.txt,改名改訊息照既有格式):
   - **會擋**(`rules/api.yml`)`kt-webview-mixed-content-always`:`mixedContentMode = MIXED_CONTENT_ALWAYS_ALLOW`、`setMixedContentMode(…ALWAYS_ALLOW)`,以及直接寫整數字面值 `0`(這個常數的值),多層接收者都認。樣本外 273 處、抽判 40 處誤報 2(5%)。
   - **不接閘**(`rules-unwired/`)其餘 12 條,各自的樣本外數字見〈實驗〉;理由分兩型:誤報超過一成(RSA 79.5%、靜態 IV 53.3%、金鑰 66.7%、弱雜湊 80.0%、反序列化 75.0%、XXE 62.5%、寫死秘密 25.0%、Zip Slip 41.7%)、命中不到 20 處(provider 6、弱套件 6(樣本內誤報 82%)、外部儲存資料庫 1、外部網址 14)。
   - 路徑排除:八項清單(同第一批),Zip Slip 與 XXE 另排除建置腳本(`buildSrc`、`build-logic`、`*.gradle.kts`)。
   - 升級條件同第一批:樣本外命中 ≥20、誤報 ≤10%。
5. **規則包節點**([[Systems/kotlin規則包]]):補一行 WHY 寫第二批放哪一級與理由;不接閘目錄的條數說明跟著改。

**不做**:
- 只能看語意、形狀判不出的 7 種(密碼欄鍵盤快取、通知放敏感資料、生物辨識沒帶 CryptoObject、指令注入的資料來源、LocalServerSocket 驗證、自寫 XOR 加密、深層連結資料進 WebView 的跨函式資料流):要看資料從哪來、保護的是什麼,不屬於「靜態能先掃描」;不寫規則,也不在這批開情境決策表列。
- MobSF 的 XMLInputFactory、XMLDecoder 兩種 XXE:Android SDK 沒有這兩個 API(官方參考頁 404)。
- MobSF 的 hidden UI:只是可疑,不是隱患。
- OAuth 自訂 scheme:RFC 8252 允許自訂 scheme 搭 PKCE,MobSF 講得太重。
- Jackson default typing:Android 少用 Jackson,樣本撈不到;留給之後。
- 不改第一批已上線的規則形狀。

REVISIT:2027-05-08 換一批語料(至少三個不是這次出現過的 Kotlin 為主開源 App)重量第二批 12 條不接閘規則,照升級條件升;外部網址丟進 WebView 那條(樣本外誤報 7%、只差命中數)優先
REVISIT:2027-05-08 看 Android Lint 或 Google 資安包有沒有補上 MessageDigest 弱雜湊、一般寫死秘密的檢查,有就把 DATA-83、DATA-79 改回指現成檢查

## 實驗

2026-11-08,ast-grep 0.51.1,規則初稿放 scratchpad 跑(未進 repo),卷證 `governance/review-reports/android資安靜態檢查補齊第二批/experiment/`。語料:①五個開源 App 整份加 Now in Android;②GitHub 程式搜尋按規則關鍵字撈約 1,560 個 repo、2,067 支檔(排除資安教材與規則樣本 repo);③形狀凍結後另撈 2,952 個 repo 當樣本外(與①②不重疊)。每處命中由判讀代理打開前後 20 行判,單條超過 40 處以種子 20261109 抽 40 處;誤報比例=誤報÷抽判數(判不準留在分母)。判準:正式碼、開發者改得動才算真問題;外部協定強制、測試碼、範例碼算誤報。

| 規則 | 樣本外命中/抽判/誤報 | 誤報比例 | 放哪 |
|---|---|---|---|
| kt-webview-mixed-content-always | 273/40/2 | 5.0% | `rules/` |
| kt-loadurl-external | 14/14/1 | 7.1% | `rules-unwired/`(命中不到 20) |
| kt-provider-openfile-traversal | 6/6/0 | 0% | `rules-unwired/`(命中太少) |
| kt-weak-cipher-suite | 6/6/0 | 0%(樣本內 82%) | `rules-unwired/` |
| kt-db-on-external-files | 1/1/0 | — | `rules-unwired/` |
| kt-hardcoded-secret-name | 36/36/9 | 25.0% | `rules-unwired/` |
| kt-zip-slip | 24/24/10 | 41.7% | `rules-unwired/` |
| kt-static-iv | 30/30/16 | 53.3% | `rules-unwired/` |
| kt-xxe-documentbuilder | 66/40/25 | 62.5% | `rules-unwired/` |
| kt-weak-key-size | 6/6/4 | 66.7% | `rules-unwired/` |
| kt-object-input-stream | 194/40/30 | 75.0% | `rules-unwired/` |
| kt-rsa-no-oaep | 39/39/31 | 79.5% | `rules-unwired/` |
| kt-weak-message-digest | 143/40/32 | 80.0% | `rules-unwired/` |

- 誤報最大宗:外部協定強制(ADB 簽章、模仿舊版 TLS 指紋、護照晶片、第三方 API 格式)集中在 RSA、靜態 IV、弱雜湊、弱套件四條;資料來自可信來源(自己的私有檔、自己的設定)集中在反序列化與 XXE。
- 量不到的:漏報(語料偏向命中);外部網址那條的命中都沒看 AndroidManifest,不確定那些畫面有沒有 exported。
- XXE 的修法照 Android 官方 XXE 指引(https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection);Android 的 DOM 解析器預設會不會解析外部實體,沒實測。

## 實務隱患

- **只有一條會擋**:其餘 12 條只登記、不擋,消費專案推送前不會被這些寫法擋;型錄那幾列照實寫「未接」。
- **混合內容那條會擋人**:誤報 5% 來自刻意開放混合內容的瀏覽器類 App;用 `lint-waive` 附理由放行。
- **錯登修正讓型錄看起來「少防」**:DATA-83、DATA-79 原本看起來有現成檢查,修正後照實寫現成檢查管不到、改指不接閘的規則;這是讓型錄說實話,不是放寬。
- 已排除:金流:不碰付款
- 已排除:對外送出:規則與型錄都是本機讀檔;實驗語料由 GitHub 公開檔下載,只讀
- 已排除:不可逆:新增規則、型錄列與文字,退提交即回原狀
- 守衛面:新增一條會擋的推送前規則(擋得更多),走完整設計審

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 要把靜態能掃描的隱患都先處理 | 使用者要求 | 使用者 2026-11-07:「目標是把Android靜態能先掃描的實務隱患都先處理過」 |
| 第四份對照清單 | MobSF mobsfscan Kotlin 規則集 | https://github.com/MobSF/mobsfscan |
| DATA-83、DATA-79 錯登 | Google 檢查原始碼與檢查頁 | https://googlesamples.github.io/android-custom-lint-rules/checks/VulnerableCryptoAlgorithm.md.html 、https://googlesamples.github.io/android-custom-lint-rules/checks/SecretInSource.md.html |
| 四條漏登的內建檢查 | Android Lint 檢查頁(2026-11-08 curl 確認 200、Warning、預設開) | https://googlesamples.github.io/android-custom-lint-rules/checks/SdCardPath.md.html |
| Zip Slip | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/zip-path-traversal |
| provider 路徑穿越 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/path-traversal |
| 混合內容 | Android WebSettings 參考頁 | https://developer.android.com/reference/android/webkit/WebSettings |
| RSA 無填充、弱雜湊 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/broken-cryptographic-algorithm |
| 固定 IV | MASTG-TEST-0309 | https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0309/ |
| 金鑰太短 | MASTG-TEST-0208 | https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0208/ |
| 反序列化 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/unsafe-deserialization |
| 外部網址丟進 WebView | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/unsafe-uri-loading |
| 外部儲存資料庫 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/sensitive-data-external-storage |
| XXE | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection |
| 寫死秘密 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/hardcoded-cryptographic-secrets |
| 誤報一成門檻、新規則先不接閘 | 規則包 RULE 與操作第 1 條 | [[Systems/kotlin規則包]] |

## 驗收條款

- [S1] 當逐例測試對預期值表每一列 S1 的寫法各跑一次規則包時,該報的 應 恰好被那條規則報一次、不該報的 應 不被它報 [test:t_kotlin_rulepack_security_rules_batch2]
- [S2] 當列舉規則包時,`kt-webview-mixed-content-always` 應 在 `rules/api.yml`,其餘 12 條 應 在 `rules-unwired/`,每條訊息 應 以這次新增或併入的型錄列編號開頭、不超過 120 字、路徑排除照範圍 4 [test:t_kotlin_rulepack_security_rules_batch2]
- [S3] 當讀型錄時,DATA-83 的現成規則欄 應 寫明 VulnerableCryptoAlgorithm 只抓 Cipher、DATA-79 應 寫明 SecretInSource 只抓 Gemini 金鑰,兩列 應 改指自寫規則;SdCardPath、SetWorldWritable、UnsafeDynamicallyLoadedCode、UnsanitizedFilenameFromContentProvider 應 各在型錄出現;型錄自檢 應 是 0 個問題、還沒逐列查證 0 列 [test:t_kt_catalog_security_lint_batch2]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `webView.settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW` | 報 | Android WebSettings 參考頁:建議 MIXED_CONTENT_NEVER_ALLOW |
| S1 | `webView.settings.mixedContentMode = 0` | 報 | Android WebSettings 參考頁:MIXED_CONTENT_ALWAYS_ALLOW 的常數值是 0 |
| S1 | `webView.settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW` | 不報 | 同上:建議值 |
| S1 | `File(destDir, entry.name)` 同函式沒有 canonicalPath 檢查 | 報(不接閘那條) | Android 官方 Zip Path Traversal 頁 |
| S1 | `File(destDir, entry.name)` 之後比對 `canonicalPath.startsWith(destDir.canonicalPath)` | 不報 | 同上:官方建議的檢查 |
| S1 | `Cipher.getInstance("RSA/ECB/NoPadding")` | 報(不接閘那條) | Android 官方 broken-cryptographic-algorithm 頁:RSA 要 OAEP |
| S1 | `Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding")` | 不報 | Android 官方 broken-cryptographic-algorithm 頁 |
| S1 | `IvParameterSpec(byteArrayOf(0, 0, 0, 0))` | 報(不接閘那條) | MASTG-TEST-0309:CBC 要每次新的 IV |
| S1 | `MessageDigest.getInstance("MD5")` | 報(不接閘那條) | Android 官方 broken-cryptographic-algorithm 頁 |
| S1 | `MessageDigest.getInstance("SHA-256")` | 不報 | Android 官方 broken-cryptographic-algorithm 頁 |
| S1 | `webView.loadUrl(intent.getStringExtra("url")!!)` | 報(不接閘那條) | Android 官方 unsafe-uri-loading 頁 |
| S1 | `val password = "Abc12345xyz"` | 報(不接閘那條) | Android 官方 hardcoded-cryptographic-secrets 頁 |
| S1 | `val passwordKey = "pref_password"` | 不報 | 實驗語料:鍵名型名稱不是秘密 |
| S1 | 放在 `src/test/kotlin/` 底下的混合內容寫法 | 不報 | 規則包既有路徑排除八項 |
| S2 | 列舉規則包 | 一條在 `rules/api.yml`、12 條在 `rules-unwired/` | 本計劃〈實驗〉的放置 |
| S3 | 真實型錄跑型錄自檢、讀 DATA-83、DATA-79 與四個內建檢查 id | 0 個問題、還沒逐列查證 0 列、兩列寫明錯登、四個 id 都找得到 | Google 檢查原始碼與 Android Lint 檢查頁 |

## 回退

退回本計劃的提交:13 條規則與樣本、型錄新列與 DATA-27、DATA-79、DATA-83、DATA-85 的改動、新測試、規則包節點那行拿掉。卷證留著。

## 天花板

1. 誤報只量了命中裡的比例,漏報沒量;四條規則的樣本外命中不到 10 處。
2. 只能看語意的 7 種隱患這批不處理(〈不做〉)。
3. 判讀把外部協定強制算誤報;改算真問題的話幾條規則的誤報率會下降,但開發者改不了,擋了也只能放行。

## 審計修正紀錄
