severity: major

整體判斷:會擋的混合內容規則本身站得住。我拿 ast-grep 0.51.1 對真實寫法跑過,抓得到 `mixedContentMode = ALWAYS_ALLOW`、`setMixedContentMode(…)`、多層接收者和整數 `0`,`BuildConfig.DEBUG` 分支也正確排除;`0` 是常數值已對照 Android WebSettings 參考頁,10 萬行檔掃描 0.3 秒。有問題的是「錯登修正」只改了半列、型錄統計與待查證節沒人更新,以及〈不做〉的整批丟棄。

## 實務隱患鏡頭逐類答

- 金流:不碰,同意。
- 對外送出:只讀本機檔,同意。
- 不可逆:退提交即可,同意。
- 守衛面:新增一條 `error` 級擋推送的規則。f1 和 f2 說的是它的證據和誤擋面。
- 資料正確性(型錄說實話):f3 說的是兩列只修一半。
- 效能與記憶體:混合內容那條不會慢,同意。
- 相容(AGP 版本):f5。
- 漂移(統計與待查證節):f4。

## Findings

### F1
severity: minor
blocking: 否
引句:「誤報 5% 來自刻意開放混合內容的瀏覽器類 App;用 `lint-waive` 附理由放行。」
- 這條會擋的規則,5% 的誤報率抽樣太小。`judge-oos.tsv` 抽判 40 處、誤報 2 處,Wilson 95% 區間上界約 16.5%,過 10% 門檻的證據很薄。
- 樣本內同一條規則是 5/40 = 12.5% 誤報,計劃書沒提。
- 40 處裡約 7 處是 legado 系列 fork,同一支 `WebViewPool.kt` 第 145 行在 `readdai` 和 `legado-jingshiro` 各出現一次。抽樣有重複。
- legado 是讀書 App,要抓使用者自訂的 http 書源,混合內容放行是產品需求,開發者改不了。判讀代理全判成 TP,和〈用詞〉裡「外部協定強制算誤報」的準則不一致。
- 實測還有這些誤擋與漏擋:
  - 誤擋:`cfg.mixedContentMode = 0` 這種非 WebView 屬性會報;`setMixedContentMode(modeFor(0))` 因為 `has` 帶 `stopBy: end` 會報;`BuildConfig.FLAVOR == "dev"` 分支會報。
  - 漏擋:`mixedContentMode = if (x) ALWAYS_ALLOW else …`、先存進變數再指派、`0x0` 都漏。
- 建議:誤擋面在天花板節寫明;或抽樣擴大、fork 去重後再放進 `rules/`。

### F2
severity: minor
blocking: 否
引句:「`SdCardPath` 併進 DATA-27(那列原寫「代號待查」」
- SdCardPath 的官方頁寫的修法是「改用 `Environment.getExternalStorageDirectory().getPath()`」。
- `configs/ast-grep/kotlin-android/rules/data.yml:230` 的 `kt-external-storage-hardcoded` 是會擋的規則,它正好把 `Environment.getExternalStorageDirectory()` 當壞寫法。
- 具體情境:開發者照 Lint 的訊息改,推送時被自家規則擋下。
- 該檢查在官方頁的分類是 Correctness,也不是 Security。
- DATA-27 併入時要註明「別照 Lint 建議改,改用 `getExternalFilesDir` 或 MediaStore」。

### F3
severity: major
blocking: 是
引句:「現成規則欄把 `資安包:VulnerableCryptoAlgorithm` 寫明「只抓 `Cipher.getInstance` 的弱加密演算法」
- 錯登本身是對的:`BadCryptographyUsageDetector.kt` 只處理 `javax.crypto.Cipher`,`SecretDetector.kt` 只有 `GenerativeModel` 建構子。
- 但同一列有三個欄位在講「Lint 管這件事」,範圍 1 只改其中一個:
  - 「情境怎麼認」:`checks-catalog.md:615` 的 DATA-83 是「形狀:由 Android Lint VulnerableCryptoAlgorithm 判」;DATA-79 同理(`checks-catalog.md:611`)。
  - 「通電批次」:兩列都是「告警帶寫法=批四(CI 範本:Android Lint)」。
  - 「實測狀態」:「未測(lint 規則,CI 跑)」;範圍 1 的第三點有提到要改這一欄。
- `check.py` 的 `catalog_problems` 會依「現成規則」欄是否帶 `內建:`、`資安包:` 前綴,強制「通電批次」寫「批四(CI 範本:Android Lint)」。
- 只要「現成規則」欄還留著 `內建:SecretInSource(只抓 Gemini)` 這種字樣,通電批次就必須維持批四,型錄仍然宣稱整列被 CI 擋。
- DATA-79 這類半接半未接的列,規格沒有寫「通電批次」該怎麼寫,後果是二選一:
  - 寫「未接」,自檢變紅。
  - 維持批四,型錄還是在說謊。
- 〈實務隱患〉聲稱的「讓型錄說實話」做不到。
- 同樣的混列問題也出現在併進 DATA-82 的 `kt-rsa-no-oaep`、DATA-85 的 `SetWorldWritable`。DATA-82 的 Lint 半邊是批四,RSA 那半是未接。
- 建議:規格要明寫混列的「通電批次」格式,例如「批四(CI 範本:Android Lint);雜湊半未接」,並把「情境怎麼認」欄一併列進範圍 1;或把自寫規則拆成獨立新列,不要併進 Lint 列。

### F4
severity: minor
blocking: 否
引句:「〈待查證〉節那一行由程式從主表撈,主表改了自然跟著變」
- 這個說法對不上程式:全 repo 沒有任何程式產生〈待查證〉節或〈統計〉節。
- `configs/ast-grep/kotlin-android/check.py:344` 把〈待查證〉節排除在檢查之外;`scripts/test_lumos.py` 的 `t_kt_catalog_unverified_rows` 說明也寫「待查證節不在檢查範圍」。
- `checks-catalog.md:865` 的 `DATA-27 | 待查(Lint SdCardPath 代號待查)` 是手寫列,改完主表後會變成過期的待查證列。
- `checks-catalog.md:915-925` 的統計也是手寫:總列數 514、DATA 87、API 47、ARCH 88、規則包條數 211、「14 條在不接閘」、被會擋的規則守到 127 列、逐列查證 501 列。加 12 列新列和 13 條規則後全部變舊,沒有測試會抓。
- 範圍只提規則包節點補一行,沒列這幾處。
- S3 只驗型錄自檢 0 問題,這些漂移測試不會紅。

### F5
severity: minor
blocking: 否
引句:「(都是 Android Open Source Project 提供、Warning、預設開,範本 `warningsAsErrors` 下接 CI 就擋)」
- 四條檢查的 Since 版本不同:官方頁寫 `UnsanitizedFilenameFromContentProvider` 是 8.8.0(2025-01)才有。
- 範本鎖的 AGP 下限是 8.5.1(`t_linter_catalog_android_security_lint` 釘的是 `AGP 8.5.1`)。
- 具體情境:專案在 AGP 8.5 到 8.7,照範本接了 CI,DATA-95 看起來有防,實際上 lint 根本沒這條檢查,靜默沒擋。
- 同理 `SecretInSource` 是 8.3.0 才有。
- 建議:DATA-95 的型錄列註明最低 AGP 版本。
- 連帶一個小錯:DATA-83 寫的弱演算法清單「DES、RC2、RC4、Blowfish」少了原始碼裡的 `RC5` 和 `ARCFOUR`,而且是 `startsWith` 比對,所以 3DES(`DESede`)也會被抓。

### F6
severity: major
blocking: 是
引句:「不屬於「靜態能先掃描」;不寫規則,也不在這批開情境決策表列。」
- 使用者的目標是「靜態能先掃描的都先處理過」,這 7 種被判成不屬於靜態可掃描,理由站不住。
- 其中有幾種的核心是純形狀:
  - 生物辨識沒帶 CryptoObject:`BiometricPrompt.authenticate(info)` 單參數對上 `authenticate(info, cryptoObject)`,是呼叫參數個數。
  - LocalServerSocket 驗證:`LocalServerSocket(` 的出現位置就是形狀。
  - 指令注入的資料來源:`Runtime.getRuntime().exec(` 帶非字面值是經典形狀;資料從哪來才是語意,但接收端形狀可以先掃。
- 這個專案本來就有「語意類」的處理法:型錄有 106 列語意列,配情境決策表與「表態對程式」。「不寫規則」不等於「不登記」。
- `checks-catalog.md` 搜 Biometric、CryptoObject、LocalServerSocket、ProcessBuilder、`Runtime.exec` 都是 0 筆。
- 這 7 種和另列的 Jackson default typing(「留給之後」)沒有任何痕跡,規則包也不會提醒。
- 專案 CLAUDE.md 鐵則 4 要求承認的缺口要附回頭條件,這裡只有〈不做〉,沒有 `REVISIT:`。
- 建議:至少用「語意類」列加決策表列登記;或為這 7 種與 Jackson 各寫一行 `REVISIT:`。

## 查證過、沒問題的部分
- `kt-webview-mixed-content-always` 的預期值表三列(`ALWAYS_ALLOW`、`0`、`NEVER_ALLOW`)在 0.51.1 下行為符合。
- 型錄編號起點 API 47、ARCH 88、DATA 87 與 `checks-catalog.md` 實際最大號一致。
- 12 個官方與 MASTG 網址 curl 全部 200。
- 草稿 13 條規則裡 9 條訊息長度是 135–236 字(超過 120)。範圍 4 已寫「改訊息」,`message_problems` 會在實作時擋住,不算洞。
- `kt-zip-slip` 草稿會誤報 `File(destDir, File(e.name).name)`(只取檔名的安全寫法)。這條不接閘,只影響升級量測。

## 附加:圖譜節點對照
附的 [[Systems/kotlin規則包]] 只是計劃落點:不影響其現有合約,因為它沒有 KEY 行也沒掛合約。但範圍 5 只寫「補一行 WHY」,漏了 F4 的條數說明與統計。
