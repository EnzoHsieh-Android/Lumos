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
  - "[[Projects/Android資安與崩潰靜態檢查補齊_計劃]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/kotlin規則包
---
# Android資安靜態檢查補齊第二批_計劃

> 白話:第一批(#174)拿三份業界清單補了資安與閃退檢查。使用者要「靜態能先掃描的實務隱患都先處理過」,於是再拿第四份獨立清單——資安掃描工具 MobSF 的 Kotlin 規則集(50 條)——逐條對照:已涵蓋 17、部分涵蓋 1、型錄有列但規則不接閘 4、型錄登記的現成檢查其實抓不到 5、型錄完全沒有 23(對照表在卷證 `experiment/mobsf-compare.md`)。抓不到的 5 條落在兩列錯登:DATA-83 登記的 Google 資安包 VulnerableCryptoAlgorithm 其實只看 `Cipher.getInstance`、抓不到 `MessageDigest.getInstance("MD5")`;DATA-79 登記的內建 SecretInSource 其實只看 Gemini SDK 的金鑰;另外 DATA-82 登記的兩條檢查都不報 `RSA/ECB/NoPadding`。這批把錯登那幾列縮回現成檢查真正管得到的範圍、管不到的另開新列,登記 Android Lint 內建有但型錄漏的 4 條,把形狀判得出的 16 種寫法寫成規則(量誤報後只有一條會擋),剩下只能看語意或沒有權威出處的寫進〈不做〉並各附回頭條件。

PRIOR-ART: ①第四份清單:MobSF mobsfscan 的 Kotlin 規則集(https://github.com/MobSF/mobsfscan 的 `mobsfscan/rules/semgrep/kotlin/`),跟第一批用的 Android Lint、Google 資安包、MASTG 是不同來源;逐條對照由代理做、再派一個沒看過結論的乾淨代理用原始問題獨立複核(專案 CLAUDE.md「說沒有之前先派乾淨 agent 對一次」),對照代理原始回報存卷證 `experiment/mobsf-compare.md`。②錯登的依據:Google 資安包原始碼 `BadCryptographyUsageDetector.kt` 先判呼叫的是不是 `javax.crypto.Cipher`,弱演算法以前綴比對 Blowfish、DES、RC2、RC5、RC4、ARCFOUR(所以 DESede 也會報),RSA 只在配 PKCS1Padding 時報(摘錄存卷證 `experiment/lint-badcrypto-excerpt.md`);`SecretDetector.kt` 只看 `GenerativeModel` 建構子。③自寫規則的寫法沿用第一批:節點種類比對、八項路徑排除、共用除錯判斷 `utils/debug-only.yml`、樣本外語料量誤報(樣本外命中 ≥20、誤報 ≤10% 才放 `rules/`)。④生物辨識那條借 OWASP 的示範(MASTG-DEMO-0090 用 Semgrep 認「authenticate 沒帶 CryptoObject」);指令執行那條參考 Semgrep 的 Kotlin 規則 `kotlin.lang.security.command-injection-formatted-runtime-call`(只認串接與 String.format,官方標低信心)。⑤官方出處:各規則與型錄列的出處見〈依據來源〉,以 OWASP MASTG 測試頁與 Android 官方安全風險指南(https://developer.android.com/privacy-and-security/risks)為主。
RETIRE-IF: 放 `rules-unwired/` 的 15 條,到 2027-05-08 換語料重量仍沒有一條達到升級條件 → 檢討是不是該整類改成表態題而不是規則;或 Android Lint、Google 資安包補上同一種檢查 → 那條自寫規則撤掉、型錄改指現成檢查。

## 用詞

- **樣本內/樣本外**:同第一批([[Projects/Android資安與崩潰靜態檢查補齊_計劃]]):樣本內=調規則形狀時看過的語料;樣本外=形狀凍結後另撈、排除前面出現過的 repo 的語料,誤報率以樣本外為準。
- **錯登**:型錄某列的現成規則欄登記了某個檢查,但那個檢查實際抓不到這列寫的壞寫法。
- **判不準**:判讀表的 `UNSURE`;算誤報比例時留在分母。
- **外部協定強制**:寫法是外部格式或對方伺服器規定的(例:ADB 簽章用 RSA 無填充、模仿舊版 TLS 指紋),開發者改不了;這次判讀一律算誤報。
- **產品需求**:App 的功能本身就要這種寫法(例:閱讀 App 讓使用者加自訂 http 書源、App 內建瀏覽器);開發者改得動、只是改了功能就沒了,判讀照真問題算,另外計數。
- **fork 去重**:同一份程式被 fork 成多個 repo 時(同檔名、同內容),判讀只算一次。

## 範圍

1. **錯登那幾列縮回現成檢查真正管的範圍**(`skills/kotlin-idioms/checks-catalog.md`;管不到的那半另開新列,不併進同一列——同一列的通電批次只能寫一種值,型錄自檢 `check.py` 的批四口徑看到現成規則欄有 `內建:`、`資安包:` 規則碼就要求整列寫批四,併進去型錄又會說「整列都擋」):
   - DATA-83:名稱改「加密用弱演算法」;壞寫法換成 `Cipher.getInstance("DES/CBC/PKCS5Padding")`、`"RC4"`、`"Blowfish"`;現成規則欄寫成 `資安包:VulnerableCryptoAlgorithm(只看 Cipher.getInstance,前綴比對 DES、RC2、RC5、Blowfish、RC4、ARCFOUR,DESede 也會報)`;情境欄照新範圍寫。雜湊那半移到新列 DATA-96。
   - DATA-79:名稱改「寫死 Gemini API 金鑰或網址帶帳密」;壞寫法換成 `GenerativeModel(modelName = "…", apiKey = "AIza…")`、`https://user:pass@host`;現成規則欄寫成 `內建:SecretInSource(只看 Gemini SDK 的 GenerativeModel 金鑰,AGP 8.3.0 以上才有)、AuthLeak(只看網址裡的 user:pass@)`。一般寫死秘密移到新列 DATA-97。
   - DATA-82:壞寫法欄尾加一句「RSA 不帶 OAEP 填充(`RSA/ECB/NoPadding`)這列登記的兩條檢查都不報,見 DATA-98」。
   - 三列的實測狀態欄在原記之前加一句:2026-11-08 讀 Google 原始碼確認範圍、原登記多算的那半移到哪一列。
2. **登記 Android Lint 內建漏登的 4 條**(都是 Android Open Source Project 提供、Warning、預設開;各檢查頁的 Since 版本:SdCardPath 最早、SetWorldWritable 1.5.0、UnsafeDynamicallyLoadedCode 2.0.0、UnsanitizedFilenameFromContentProvider **8.8.0**):
   - `SdCardPath` 進 DATA-27 的現成規則欄(原寫「待查(Lint SdCardPath 代號待查)」),通電批次改「告警帶寫法=批一、批四(CI 範本:Android Lint)」;標準寫法欄加一句「別照 Lint 訊息改用 `Environment.getExternalStorageDirectory().getPath()`,那個寫法會被同列的自寫規則 kt-external-storage-hardcoded 擋;改用 `getExternalFilesDir` 或 MediaStore」。
   - `SetWorldWritable` 併進 DATA-85(同列都是 Lint,通電批次不變)。
   - `UnsafeDynamicallyLoadedCode`(從非程式庫目錄動態載入程式碼)另開 ARCH-89。
   - `UnsanitizedFilenameFromContentProvider`(信任別人 provider 給的檔名)另開 DATA-95,名稱尾標「(AGP 8.8.0 以上才有)」,實測狀態寫明範本下限 AGP 8.5.1 的專案在 8.8.0 以前照接 CI 也不會有這條檢查。
3. **型錄新列**(編號照型錄現有最大號往下:API 到 47、ARCH 到 88、DATA 到 87;規則訊息開頭用下列編號):

   | 型錄列 | 內容 | 管它的 |
   |---|---|---|
   | API-48 | WebView 允許混合內容 | `kt-webview-mixed-content-always` |
   | API-49 | 外部傳進來的網址直接丟進 WebView | `kt-loadurl-external` |
   | API-50 | TLS 開弱加密套件 | `kt-weak-cipher-suite` |
   | API-51 | WebView 開啟本機檔案存取 | `kt-webview-file-access` |
   | ARCH-89 | 從非程式庫目錄動態載入程式碼 | 內建 UnsafeDynamicallyLoadedCode |
   | ARCH-90 | 用非字面值組外部指令 | `kt-command-exec-nonliteral` |
   | ARCH-91 | 生物辨識沒綁加密物件 | `kt-biometric-no-crypto` |
   | DATA-88 | 解壓縮沒擋路徑穿越(Zip Slip) | `kt-zip-slip` |
   | DATA-89 | ContentProvider 開檔沒擋路徑穿越 | `kt-provider-openfile-traversal` |
   | DATA-90 | 加密用固定 IV | `kt-static-iv` |
   | DATA-91 | 金鑰長度太短 | `kt-weak-key-size` |
   | DATA-92 | ObjectInputStream 反序列化 | `kt-object-input-stream` |
   | DATA-93 | 資料庫放外部儲存 | `kt-db-on-external-files` |
   | DATA-94 | XML 解析沒關外部實體(XXE) | `kt-xxe-documentbuilder` |
   | DATA-95 | 信任別人 provider 給的檔名 | 內建 UnsanitizedFilenameFromContentProvider |
   | DATA-96 | 用弱雜湊(MD5、SHA-1、MD4) | `kt-weak-message-digest` |
   | DATA-97 | 原始碼裡寫死一般秘密 | `kt-hardcoded-secret-name` |
   | DATA-98 | RSA 不帶 OAEP 填充 | `kt-rsa-no-oaep` |

   來源欄帶〔查證 2026-11-08:網址〕(〈依據來源〉那幾頁,實作時逐一 curl 確認);實測狀態寫樣本內外的命中與誤報。DATA-92 跟 DATA-78 不同一件事(DATA-78 管的是類別實作 Serializable)。
4. **自寫規則 16 條**(`configs/ast-grep/kotlin-android/`,形狀照卷證 `experiment/draft-rules.yml.txt`,混合內容那條照 `experiment/mixed-rejudge-rule.yml.txt`,新三條照〈實驗〉):
   - **會擋**(`rules/api.yml`)`kt-webview-mixed-content-always`:`mixedContentMode = …MIXED_CONTENT_ALWAYS_ALLOW`、`setMixedContentMode(…ALWAYS_ALLOW)`,以及寫整數字面值 `0`(這個常數的值)。setter 只看 `setMixedContentMode` 自己的直接參數(往下逐層寫到 value_argument,不用 `stopBy: end`:ast-grep 的 has 帶 `stopBy: end` 會一路找到葉節點,參數裡任何內層呼叫帶 0 都會報);賦值的 `0` 只在左邊接收者鏈有一段名字以 `settings` 或 `Settings` 結尾(`settings`、`webSettings`、`getSettings()`,容許 `?.`、`!!.`)時才報,`cfg.mixedContentMode = 0` 不報。
   - **不接閘**(`rules-unwired/`)其餘 15 條;放哪支檔:`rules-unwired/api.yml` 放 `kt-loadurl-external`、`kt-weak-cipher-suite`、`kt-webview-file-access`;`rules-unwired/architecture.yml` 放 `kt-command-exec-nonliteral`、`kt-biometric-no-crypto`;`rules-unwired/data.yml` 放其餘 10 條。理由分兩型:誤報超過一成、或樣本外命中不到 20 處(各條數字見〈實驗〉)。
   - **路徑排除**:每條都恰好是規則包既有的八項清單(同第一批,測試 `_KTSEC_IGNORES` 照比)。實驗時 Zip Slip 與 XXE 多排除了建置腳本(`buildSrc`、`build-logic`、`*.gradle.kts`),進 repo 不帶這三項,所以那兩條在建置腳本裡的命中會比〈實驗〉量到的多;兩條都不接閘,不影響推送。
   - **訊息**:照規則包 WHY「[型錄編號] 錯在哪;改用 <最短修法>」,連前綴不超過 120 字(`check.py` 的 MSG_MAX;初稿有 8 條超過,實作時縮修法說明,XXE 只留「改成 setFeature 關掉 DOCTYPE」一句,完整修法寫在型錄那列的標準寫法欄)。
   - **樣本**:每條 `samples/bad/<id>/` 至少兩處命中、`samples/good/<id>/` 至少兩段,照規則包既有硬要求(`check.py` 樣本檢查)。
   - 升級條件同第一批:樣本外命中 ≥20、誤報 ≤10%。
5. **規則包節點**([[Systems/kotlin規則包]]):把「資安四條自寫規則放哪一級、升級條件」那行 WHY 改寫成涵蓋兩批(第二批:混合內容放 `rules/api.yml`、其餘 15 條放哪支檔與理由),不另開新行,升級條件只寫一處。
6. **型錄的手寫節跟著改**(〈待查證〉〈統計〉〈輸入與口徑〉都是人手寫的,沒有程式產生;型錄〈輸入與口徑〉那句「〈待查證〉一節由程式從這兩欄撈出」跟程式對不上,改寫成「手寫,改主表時一起改」):
   - 〈待查證〉刪主表已解決的列:DATA-27(主表現成規則欄已不含待查、來源欄已有〔查證〕),以及 2026-11-05 逐列查證後主表已解決、這一節沒跟著刪的 83 列(實作時用 S4 的判準機械挑出;刪完剩 51 列)。
   - 〈統計〉用程式重數:總列數、各主題、各級、情境、待查證、規則包條數(含不接閘條數)、被會擋的規則守到的列數、逐列查證列數。
   - 〈輸入與口徑〉的「未接」定義補「量過誤報但超過一成或樣本外命中不到 20 處」。
   - 判準放進型錄自檢 `configs/ast-grep/kotlin-android/check.py`(接在 catalog_problems,推送前的規則包自檢會跑):〈統計〉每個手寫的數(總列數、各主題、各級、級的組合、情境、出處不全與人裁、規則包各等級與不接閘、被會擋的規則守到的列數、逐列查證、待查證)要等於重數的值;〈待查證〉跟主表雙向一致(該列的都列、已解決的不列、兩格寫不寫內容跟主表一致、編號不重複)。情境決策表那行另見下面 REVISIT。測試只驗自檢真型錄乾淨、寫死的改壞各被抓到(〈驗收條款〉S4;代碼審 r2 改,原本判準寫在測試檔)。

**不做**:
- 通知放敏感資料、密碼欄鍵盤快取:要看內容敏不敏感;鍵盤快取的設定在版面 XML 的 `android:inputType`,不在 Kotlin 原始碼裡,規則包掃不到。
- LocalServerSocket 沒驗證連線方:Android 參考頁只寫它是什麼、沒寫風險,找不到權威出處支持「出現就是錯」;MobSF 那條也沒附出處。
- 自寫 XOR 加密:XOR 在雜湊、校驗、圖形運算都常見,形狀分不出是不是拿來加密,MASTG 也只寫「看到 XOR 要再查」。
- 深層連結資料跨函式流進 WebView:要追資料流;同一函式內直接 `loadUrl(intent…)` 的那段由 `kt-loadurl-external` 管。
- Jackson default typing:Android 少用 Jackson,語料撈不到。
- MobSF 的 XMLInputFactory、XMLDecoder 三種 XXE:Android SDK 沒有這兩個 API(官方參考頁 404)。
- MobSF 的 hidden UI:只是可疑,不是隱患。
- OAuth 自訂 scheme:RFC 8252 允許自訂 scheme 搭 PKCE,MobSF 講得太重。
- 不改第一批已上線的規則形狀(`kt-webview-file-url-access` 只管 …FromFileURLs 兩個開關,`setAllowFileAccess` 另開新規則)。

REVISIT:2027-05-08 換一批語料(至少三個不是這次出現過的 Kotlin 為主開源 App)重量第二批 15 條不接閘規則,照升級條件升;外部網址丟進 WebView 那條(樣本外誤報 7%、只差命中數)優先
REVISIT:2027-05-08 看 Android Lint 或 Google 資安包有沒有補上 MessageDigest 弱雜湊、一般寫死秘密、RSA 無填充的檢查,有就把 DATA-96、DATA-97、DATA-98 改指現成檢查、自寫規則撤掉
REVISIT:2027-05-08 查 MASTG 與 Android 官方安全指南有沒有出 LocalServerSocket、自寫 XOR 加密、通知敏感資料的測試頁;有權威出處且寫得出形狀的,開型錄列與不接閘規則
REVISIT:2026-11-22 型錄〈統計〉的情境決策表那行(證據樣式主寫、例外、兩段都寫(無)的列數 8、31、5)重數對不上,查清口徑後改成程式數得出的值
REVISIT:2026-12-08 型錄自檢的批四口徑只判「已寫批四的列標籤對不對」,不判「現成規則欄登了 Android Lint 檢查的列一定要寫批四」;2026-11-08 量過全型錄有 11 列會被新判法點到(API-9、STATE-5、UI-1、UI-3、UI-10、UI-16、ARCH-16、ARCH-17、ARCH-44、TEST-23、PERF-2,多半註記只部分涵蓋,疑似第四批刻意只標批一),查第四批計劃的理由後決定改 check.py 還是在口徑寫明例外
REVISIT:2027-05-08 查規則包有沒有開始掃版面 XML;有就把密碼欄 `inputType` 沒帶 textNoSuggestions 寫成規則
REVISIT:2027-05-08 再用 GitHub 程式搜尋撈 Jackson `enableDefaultTyping`、`activateDefaultTyping` 的 Kotlin 檔;正式碼命中 ≥5 處就開型錄列與不接閘規則

## 實驗

2026-11-08,ast-grep 0.51.1,規則初稿放 scratchpad 跑(未進 repo),卷證 `governance/review-reports/android資安靜態檢查補齊第二批/experiment/`。語料:①五個開源 App 整份加 Now in Android;②GitHub 程式搜尋按規則關鍵字撈約 1,560 個 repo、2,067 支檔(排除資安教材與規則樣本 repo);③形狀凍結後另撈 2,952 個 repo 當樣本外(與①②不重疊)。每處命中由判讀代理打開前後 20 行判,單條超過 40 處以種子 20261109 抽 40 處;誤報比例=誤報÷抽判數(判不準留在分母)。判準:正式碼、開發者改得動才算真問題;外部協定強制、測試碼、範例碼算誤報。

**MobSF 對照**(50 條):23 條型錄沒有的,13 條寫成規則(弱 IV 與固定 IV 兩條併成 `kt-static-iv`,命令注入兩條併成 `kt-command-exec-nonliteral`,深層連結進 WebView 由 `kt-loadurl-external` 管同函式那段)、5 條不做(hidden UI、OAuth、三種 Android 沒有的 XXE)、5 條寫進〈不做〉加回頭條件(鍵盤快取、通知、XOR、LocalServerSocket、Jackson);5 條錯登由 3 條規則管(MD4、MD5、SHA-1 併成 `kt-weak-message-digest`);部分涵蓋 1 條由 `kt-db-on-external-files` 補。16 條規則裡 `kt-xxe-documentbuilder` 不是 MobSF 來的(MobSF 的 XXE 用的都是 Android 沒有的 API,Android 真正的入口 DocumentBuilderFactory 是對照代理順帶指出的),4 條內建漏登也是順帶發現。

| 規則 | 樣本外命中/抽判/誤報 | 誤報比例 | 放哪 |
|---|---|---|---|
| kt-webview-mixed-content-always | 273(fork 去重 244)/120/2 | 1.7%(95% 上界 5.9%) | `rules/` |
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
| kt-webview-file-access | 59/40/16 | 40.0% | `rules-unwired/` |
| kt-biometric-no-crypto | 46/40/2 | 5.0%(95% 上界 16.5%) | `rules-unwired/`(判真問題要看保護的是什麼) |
| kt-command-exec-nonliteral | 55/40/28 | 70.0%(收窄前) | `rules-unwired/`(收窄後未重量) |

- **新三條**(設計審 r1 後補,語料另撈:6 個單詞查詢、排除前面出現過的 repo 與資安教材,871 個 repo;repo 名雜湊奇偶分樣本內外,形狀在樣本內調完凍結,雜湊 `experiment/new3-frozen.sha.txt`;判讀表 `experiment/new3-judge.tsv`):
  - WebView 本機檔案存取:誤報大宗是只載自家 `file:///android_asset` 的 WebView、範例碼;判不準 7 處多是 EPUB 閱讀器這類要讀本機檔的功能。
  - 生物辨識:判讀另加一條準則「成功回呼放行的是錢包、密碼、金鑰、帳號、登入、App 鎖這類敏感資產才算真問題」;真問題 32 處多數是 App 鎖畫面。MASTG-TEST-0327 寫的是「每個值得保護的敏感操作」,要不要綁加密物件看保護的是什麼,形狀定不了,所以點估計 5% 也不升 `rules/`。規則靠接收者或參數名稱含 prompt、biometric、info 這類字樣擋自家包裝,`bp.authenticate(pi)` 會漏。
  - 指令執行:量到的形狀(任何非字面參數)誤報 70%,大宗是桌面或 CLI 工具、內部常數與 pid、執行使用者指令本來就是功能的工具;真問題 3 處都是外部資料組進 `su -c`。進 repo 時收窄成 Semgrep `command-injection-formatted-runtime-call` 的形狀:`exec` 的單一字串參數是串接、`String.format` 或帶插值的字串樣板,或 `ProcessBuilder` / `exec` 的參數有 `"-c"` 而後面接非字面值;收窄後沒重量(事後分類:`-c` 型 10 處裡真問題 2、單一字串 21 處裡 0)。路徑排除照八項,不帶實驗時多加的建置腳本三項。
- **混合內容那條重判**(設計審 r1 後):修 setter 與 `= 0` 兩處形狀,語料③命中數不變(273,兩處修法只對人造例子有效);同一份程式 fork 成多個 repo 的只留一處(244 處),以種子 20261110 抽 120 處:真問題 118、誤報 2(都是函式庫附帶的示範 App)。真問題裡 25 處是產品需求(自訂書源 8、App 內建瀏覽器 7、自架區網主機 3、預覽使用者自寫 HTML 2、開第三方文章網址 5)。判讀表 `experiment/mixed-rejudge-judge.tsv`、去重表 `experiment/mixed-rejudge-dedup-groups.tsv`;第一次 40 處抽判(誤報 2)保留在 `judge-oos.tsv`。
- 誤報最大宗:外部協定強制(ADB 簽章、模仿舊版 TLS 指紋、護照晶片、第三方 API 格式)集中在 RSA、靜態 IV、弱雜湊、弱套件四條;資料來自可信來源(自己的私有檔、自己的設定)集中在反序列化與 XXE。
- 量不到的:漏報(語料偏向命中);外部網址那條的命中都沒看 AndroidManifest,不確定那些畫面有沒有 exported。
- XXE 的修法照 Android 官方 XXE 指引(https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection);Android 的 DOM 解析器預設會不會解析外部實體,沒實測。

## 實務隱患

- **只有一條會擋**:其餘 15 條只登記、不擋,消費專案推送前不會被這些寫法擋;型錄那幾列照實寫「未接」。
- **混合內容那條會擋人**:被擋的多半是真問題,但裡面約兩成是產品需求(自訂書源、內建瀏覽器),那種用 `lint-waive` 附理由放行;誤報是函式庫附帶的示範 App。
- **混合內容那條的已知漏報**:值藏在 if、elvis、括號、轉型裡(`= if (b) ALWAYS_ALLOW else NEVER_ALLOW`)、先存進變數或常數再給、`settings.apply { mixedContentMode = 0 }` 這種不帶接收者的 `0`、`0x0` 這類寫法都不報;規則只認「直接把這個常數或 0 給它」。
- **錯登修正讓型錄看起來「少防」**:DATA-83、DATA-79、DATA-82 原本看起來整列有現成檢查,修正後縮回現成檢查真正管的範圍,管不到的那半另開新列寫「未接」;這是讓型錄說實話,不是放寬。
- **DATA-95 在舊 AGP 上不存在**:範本下限 AGP 8.5.1,這條 8.8.0 才有;8.8.0 以前的專案照範本接 CI 也不會擋,型錄那列名稱標版本。
- **SdCardPath 的建議跟自家規則打架**:Lint 訊息建議改用 `Environment.getExternalStorageDirectory().getPath()`,同列的 kt-external-storage-hardcoded 會擋這個寫法;型錄 DATA-27 標準寫法寫明改用 `getExternalFilesDir` 或 MediaStore。
- 已排除:金流:不碰付款
- 已排除:對外送出:規則與型錄都是本機讀檔;實驗語料由 GitHub 公開檔下載,只讀
- 已排除:不可逆:新增規則、型錄列與文字,退提交即回原狀
- 守衛面:新增一條會擋的推送前規則(擋得更多),走完整設計審

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 要把靜態能掃描的隱患都先處理 | 使用者要求 | 使用者 2026-11-07:「目標是把Android靜態能先掃描的實務隱患都先處理過」 |
| 第四份對照清單 | MobSF mobsfscan Kotlin 規則集 | https://github.com/MobSF/mobsfscan |
| DATA-83、DATA-82 錯登 | Google 資安包原始碼與檢查頁 | https://github.com/google/android-security-lints 、https://googlesamples.github.io/android-custom-lint-rules/checks/VulnerableCryptoAlgorithm.md.html |
| DATA-79 錯登 | Android Lint 檢查頁 | https://googlesamples.github.io/android-custom-lint-rules/checks/SecretInSource.md.html |
| 四條漏登的內建檢查與 Since 版本 | Android Lint 檢查頁(2026-11-08 curl 確認 200、Warning、預設開) | https://googlesamples.github.io/android-custom-lint-rules/checks/UnsanitizedFilenameFromContentProvider.md.html |
| Zip Slip | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/zip-path-traversal |
| provider 路徑穿越 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/path-traversal |
| 混合內容 | Android WebSettings 參考頁 | https://developer.android.com/reference/android/webkit/WebSettings |
| setter 只看直接參數 | ast-grep 關係規則文件:has 預設只看下一層,stopBy: end 一路找到底 | https://ast-grep.github.io/guide/rule-config/relational-rule.html |
| WebView 本機檔案存取 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/webview-unsafe-file-inclusion |
| RSA 無填充、弱雜湊 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/broken-cryptographic-algorithm |
| 固定 IV | MASTG-TEST-0309 | https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0309/ |
| 金鑰太短 | MASTG-TEST-0208 | https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0208/ |
| 反序列化 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/unsafe-deserialization |
| 弱加密套件 | Android 官方安全風險指南(DES、RC4 列為弱加密) | https://developer.android.com/privacy-and-security/risks/broken-cryptographic-algorithm |
| 外部網址丟進 WebView | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/unsafe-uri-loading |
| 外部儲存資料庫 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/sensitive-data-external-storage |
| XXE | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection |
| 寫死秘密 | Android 官方安全風險指南 | https://developer.android.com/privacy-and-security/risks/hardcoded-cryptographic-secrets |
| 生物辨識沒綁加密物件 | MASTG-TEST-0327 與示範 MASTG-DEMO-0090 | https://mas.owasp.org/MASTG/tests/android/MASVS-AUTH/MASTG-TEST-0327/ |
| 用非字面值組外部指令 | CWE-78;Semgrep Kotlin 規則 | https://cwe.mitre.org/data/definitions/78.html 、https://github.com/semgrep/semgrep-rules/blob/develop/kotlin/lang/security/command-injection-formatted-runtime-call.yaml |
| 誤報一成門檻、新規則先不接閘 | 規則包 RULE 與操作第 1 條 | [[Systems/kotlin規則包]] |

## 驗收條款

- [S1] 當逐例測試對預期值表每一列 S1 的寫法各跑一次規則包時,該報的 應 恰好被那條規則報一次、不該報的 應 不被它報 [test:t_kotlin_rulepack_security_rules]
- [S2] 當列舉規則包時,16 條新規則 應 各在範圍 4 寫的那支檔(會擋的 `rules/api.yml` 一條,其餘照 `rules-unwired/` 的三支檔),每條訊息 應 以範圍 3 那張表的型錄列編號開頭、連前綴不超過 120 字,路徑排除 應 恰好是規則包既有八項 [test:t_kotlin_rulepack_security_rules]
- [S3] 當讀型錄時,DATA-83 的現成規則欄 應 寫明 VulnerableCryptoAlgorithm 只看 Cipher、DATA-79 應 寫明 SecretInSource 只看 Gemini 金鑰,兩列與 DATA-82 的壞寫法 應 不再含移到新列的那半;範圍 3 那張表的 18 列 應 各在型錄出現;SdCardPath、SetWorldWritable、UnsafeDynamicallyLoadedCode、UnsanitizedFilenameFromContentProvider 應 各在型錄出現,DATA-95 名稱 應 帶 AGP 8.8.0;型錄自檢 應 是 0 個問題、還沒逐列查證 0 列 [test:t_kt_catalog_security_lint_batch2]
- [S4] 當讀型錄〈統計〉與〈待查證〉時,總列數、各主題列數、規則包條數、不接閘條數 應 等於程式從表格與規則檔數出的值,〈待查證〉應 不列主表現成規則欄已不含待查、來源欄已不含未核對字樣的列 [test:t_kt_catalog_stats_consistent]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `webView.settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW` | 報 | Android WebSettings 參考頁:建議 MIXED_CONTENT_NEVER_ALLOW |
| S1 | `webView.settings.mixedContentMode = 0` | 報 | Android WebSettings 參考頁:MIXED_CONTENT_ALWAYS_ALLOW 的常數值是 0 |
| S1 | `webSettings.mixedContentMode = 0` | 報 | 同上;接收者名字以 Settings 結尾 |
| S1 | `webView.settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW` | 不報 | 同上:建議值 |
| S1 | `cfg.mixedContentMode = 0` | 不報 | 設計審 r1 通才席:接收者不是 WebView 設定 |
| S1 | `webView.settings.setMixedContentMode(resolve(0, 1))` | 不報 | 設計審 r1 邊界席:0 是內層呼叫的參數,不是這個 setter 的 |
| S1 | `webView.settings.setMixedContentMode(0)` | 報 | Android WebSettings 參考頁 |
| S1 | 放在 `src/test/kotlin/` 底下的混合內容寫法 | 不報 | 規則包既有路徑排除八項 |
| S1 | `fun unzip(zis: ZipInputStream, destDir: File) { var entry = zis.nextEntry; while (entry != null) { val f = File(destDir, entry.name); f.outputStream().use { zis.copyTo(it) }; entry = zis.nextEntry } }` | 報(不接閘那條) | Android 官方 Zip Path Traversal 頁 |
| S1 | 同上一列,`val f = …` 之後加 `if (!f.canonicalPath.startsWith(destDir.canonicalPath + File.separator)) throw SecurityException()` | 不報 | 同上:官方建議的檢查 |
| S1 | `Cipher.getInstance("RSA/ECB/NoPadding")` | 報(不接閘那條) | Android 官方 broken-cryptographic-algorithm 頁:RSA 要 OAEP |
| S1 | `Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding")` | 不報 | Android 官方 broken-cryptographic-algorithm 頁 |
| S1 | `IvParameterSpec(byteArrayOf(0, 0, 0, 0))` | 報(不接閘那條) | MASTG-TEST-0309:CBC 要每次新的 IV |
| S1 | `MessageDigest.getInstance("MD5")` | 報(不接閘那條) | Android 官方 broken-cryptographic-algorithm 頁 |
| S1 | `MessageDigest.getInstance("SHA-256")` | 不報 | Android 官方 broken-cryptographic-algorithm 頁 |
| S1 | `webView.loadUrl(intent.getStringExtra("url")!!)` | 報(不接閘那條) | Android 官方 unsafe-uri-loading 頁 |
| S1 | `val password = "Abc12345xyz"` | 報(不接閘那條) | Android 官方 hardcoded-cryptographic-secrets 頁 |
| S1 | `val passwordKey = "pref_password"` | 不報 | 實驗語料:鍵名型名稱不是秘密 |
| S1 | `webView.settings.allowFileAccess = true` | 報(不接閘那條) | Android 官方 webview-unsafe-file-inclusion 頁 |
| S1 | `webView.settings.allowFileAccess = false` | 不報 | 同上:建議值 |
| S1 | `biometricPrompt.authenticate(promptInfo)` | 報(不接閘那條) | MASTG-TEST-0327:沒帶 CryptoObject 只靠回呼判成功 |
| S1 | `biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))` | 不報 | MASTG-TEST-0327 |
| S1 | `Runtime.getRuntime().exec("ping -c 1 " + host)` | 報(不接閘那條) | CWE-78:外部輸入組進指令 |
| S1 | `Runtime.getRuntime().exec("ls")` | 不報 | 同上:純字面值沒有外部輸入 |
| S2 | 列舉規則包 | 一條在 `rules/api.yml`、15 條照範圍 4 的三支 `rules-unwired/` 檔,訊息都 ≤120 字、以型錄編號開頭,路徑排除都是八項 | 本計劃〈實驗〉的放置與規則包既有格式 |
| S3 | 真實型錄跑型錄自檢、讀 DATA-79、DATA-82、DATA-83、DATA-95 與範圍 3 的 18 列 | 0 個問題、還沒逐列查證 0 列、三列只寫現成檢查管得到的範圍、18 列都在、DATA-95 帶 AGP 8.8.0 | Google 檢查原始碼與 Android Lint 檢查頁 |
| S4 | 真實型錄 | 〈統計〉總列數等於表格列數加總、規則包與不接閘條數等於規則檔裡的 id 數;〈待查證〉沒有 DATA-27 | 本計劃範圍 6:〈統計〉的數要等於重數的值 |

## 回退

退回本計劃的提交:16 條規則與樣本、型錄新列與 DATA-27、DATA-79、DATA-82、DATA-83、DATA-85 的改動、〈待查證〉〈統計〉〈輸入與口徑〉的改動、測試擴充與新測試、規則包節點那行改回第一批版本。卷證留著。

## 天花板

1. 誤報只量了命中裡的比例,漏報沒量;四條規則的樣本外命中不到 10 處。
2. 只能看語意或沒有權威出處的 5 種隱患這批不處理(〈不做〉,各附回頭條件)。
3. 判讀把外部協定強制算誤報、把產品需求算真問題;換個算法幾條規則的誤報率會變,混合內容那條若把產品需求也算誤報是 27/120(22.5%)。
4. 指令執行那條進 repo 的是收窄後的形狀,誤報沒重量;生物辨識那條靠名稱字樣擋自家包裝,換了名字的寫法會漏。
5. 混合內容那條的 fork 去重只認逐字相同,換了路徑或套件名的近親重複還在(合併兩對後是 2/118,結論不變)。

## 審計修正紀錄

- r1(2026-11-08,4 席:通才、邊界、整合、架構對齊):19 條/blocking 6/錯登修正會讓型錄自檢逼整列寫批四、〈待查證〉〈統計〉其實手寫、DATA-95 要 AGP 8.8、Zip Slip 預期值照字面測不到、語意 7 種判得太快、混合內容 setter 帶 stopBy: end 誤報;全數折入,混合內容那條擴大抽判到 120 處重判仍留 `rules/`,新增 3 條形狀規則。
- 席報告:`governance/review-reports/android資安靜態檢查補齊第二批/r1-*.md`;處置與先查世界見 `r1-intake.md`。
- 實作時更正(2026-11-08):S4 的〈待查證〉判準在真型錄上挑出 DATA-27 以外還有 83 列過期,範圍 6 照條款原意擴成一起刪;Semgrep registry 網址回 404,改用 GitHub 規則原始檔;補弱加密套件的依據列。
