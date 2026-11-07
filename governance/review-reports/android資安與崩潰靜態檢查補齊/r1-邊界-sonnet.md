severity: major

## 本席說明
實驗目錄:`/tmp/lumos-seat-work/android資安與崩潰靜態檢查補齊/邊界-sonnet/`。草稿規則原樣複製,樣本在 `s/`、`s2/`、`s3/`。
依派工詞,臨時目錄由編排者收貨後刪,本席沒刪。

## Finding 1
severity: major
blocking: 是(會擋的規則漏掉最常見的寫法,S3 表只測單層接收者,測不出來)

- spec 段落:範圍 4「WebView 開檔案網址跨來源存取」、S3 預期值表。
- 引句:「與屬性寫法 `allowUniversalAccessFromFileURLs = true`、`allowFileAccessFromFileURLs = true`。」
- 問題:屬性賦值只在接收者是單一識別字時命中。最常見的 `webView.settings.allowUniversalAccessFromFileURLs = true` 是兩層以上的接收者,整條漏報。
- 佐證:樣本 `s2/app/src/main/B.kt`、`s3/C.kt`。命中的行是 setter 寫法、`apply` 或 `with` 內的裸賦值,以及單層的 `s.allowUniversalAccessFromFileURLs = true`。下面四種都沒命中:
  ```
  s.settings.allowUniversalAccessFromFileURLs = true      // s3/C.kt 第 3 行,漏
  webView.settings.allowUniversalAccessFromFileURLs = true // 漏
  binding.webview.settings.allowFileAccessFromFileURLs = true // 漏
  this.settings.allowFileAccessFromFileURLs = true        // 漏
  ```
  `ast-grep run -p '$X.foo = true' --debug-query=pattern` 顯示 `$X` 掛在 `directly_assignable_expression` 底下,只吃單一節點。
- 另外,S3 唯一的屬性寫法例子是 `settings.allowUniversalAccessFromFileURLs = true`(單層),所以測試會綠、實際卻漏。
- 補充:`s?.allow...`、`value = true` 具名參數、`(true)` 括號、先放進變數 `val t = true` 再傳入,全都漏報。後三種較罕見,放進天花板即可。

## Finding 2
severity: major
blocking: 是(分行的 OkHttp builder 鏈是標準排版,`tlsVersions` 分支整條失效)

- spec 段落:範圍 4「舊版 TLS」。
- 引句:「`tlsVersions(...)` 呼叫裡的 `TlsVersion.TLS_1_0`、`TLS_1_1`、`SSL_3_0`」
- 問題:草稿用 `inside call_expression` 加上 regex `^(\S*\.)?tlsVersions\(`。`\S*` 吃不過空白或換行,所以 `.tlsVersions(` 前面有換行,或 builder 參數裡有 `, ` 時就不命中。
- 佐證:`s2/app/src/main/B.kt`。
  ```
  ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
      .tlsVersions(TlsVersion.TLS_1_0)      // 第 43-44 行,漏報
      .build()
  ConnectionSpec.Builder(true, x)
      .tlsVersions(TlsVersion.TLS_1_1)      // 第 47-48 行,漏報
  ```
  單行 `ConnectionSpec.Builder(true).tlsVersions(TlsVersion.TLS_1_2, TlsVersion.TLS_1_0)` 才命中。
- 反向的誤報:同一個 regex 只看整條鏈的開頭,所以 `...tlsVersions(TLS_1_2).also { println(TlsVersion.TLS_1_0) }` 的第 60 行被誤報,把鏈上任何位置的 `TlsVersion.TLS_1_0` 都算進去。
- 引句:「三種寫法都套跟除錯模式同一個 if 判斷。」
- 建議:改用結構判斷,例如 `kind: navigation_suffix` 的 `.tlsVersions`,或 call_suffix 的 value_arguments,不要靠整串文字的 regex。

## Finding 3
severity: major
blocking: 是(`rules/` 是推送前會擋的規則,把正式版不會開的除錯呼叫誤報成 error)

- spec 段落:範圍 4「WebView 除錯模式」、〈實務隱患〉第 3 條。
- 引句:「不在任何 if 裡、或只包在 SDK 版本比較裡才報。」
- 問題:規則只認「祖先有 `if_expression`」才當作有開關。其他開關寫法都被當成沒開關而誤報,實驗語料沒量到這些形狀。
- 佐證:`s2/app/src/main/B.kt`,下面各行都被 `d-webview-debugging`(severity error)報出:
  ```
  if (!BuildConfig.DEBUG) return
  WebView.setWebContentsDebuggingEnabled(true)         // 第 15 行誤報
  (大括號形式的 early return,第 21 行同樣誤報)
  when { BuildConfig.DEBUG -> WebView.setWebContentsDebuggingEnabled(true) }   // 第 24 行
  when (BuildConfig.BUILD_TYPE) { "debug" -> ... }                              // 第 25 行
  BuildConfig.DEBUG.let { WebView.setWebContentsDebuggingEnabled(true) }        // 第 26 行
  takeIf { BuildConfig.DEBUG }?.let { ... }                                     // 第 27 行
  ```
- 這些寫法都不是 if 包住,卻和 `if (BuildConfig.DEBUG)` 同義。early return 守衛是很常見的慣例。
- 引句:「條件是 `isBeta`、`isXposedHooked` 這種正式版也會成立的旗標也放過(實驗放過 4 處真問題)」
- 這句只承認漏報。誤報這邊(when、let、early return)spec 沒提,也沒有對應的好例。
- 建議:S3 補上 early return、`when`、`.let` 的好例;或把 `when` 分支和 early return 一併當成有開關。

## Finding 4
severity: minor
blocking: 否(漏報,屬已承認的天花板類,但 spec 對 SDK 版本比較的承諾比實際窄)

- spec 段落:範圍 4「WebView 除錯模式」、S3。
- 問題:regex 只認 `(android.os.)?Build.VERSION.SDK_INT <比較符> 單一詞`。下面這些純 SDK 版本比較,都被當成「別的條件」而不報,和「只包在 SDK 版本比較裡才報」及 S3 的「應照報」不一致。
- 佐證:
  ```
  if (SDK_INT >= 19) {...}                                  // 靜態 import,第 42 行
  if (VERSION.SDK_INT >= VERSION_CODES.KITKAT) {...}        // 第 43 行
  if (Build.VERSION.SDK_INT >= 19 && Build.VERSION.SDK_INT < 30) ...   // 第 29 行
  if (19 <= Build.VERSION.SDK_INT) ...                      // 第 30 行
  if (Build.VERSION.SDK_INT in 19..30) ...                  // 第 41 行
  ```
  以上都未命中。會報的只有 `Build.VERSION.SDK_INT >= 19`、`>= Build.VERSION_CODES.KITKAT`、`android.os.Build...`。
- 同一個 regex 也用在舊版 TLS 規則上。

## Finding 5
severity: minor
blocking: 否(漏報,常見但不致誤擋)

- spec 段落:範圍 4「舊版 TLS」「寫死金鑰」、「WebView 除錯模式」。
- 問題:完整套件名、別名 import、具名參數、兩參數 provider 版本都漏報。
- 佐證:
  - `javax.net.ssl.SSLContext.getInstance("TLSv1")` 漏。
  - `SSLContext.getInstance("TLSv1", "AndroidOpenSSL")` 漏,原因是 pattern 只有 `$V` 一個參數。
  - `okhttp3.ConnectionSpec.COMPATIBLE_TLS` 漏。
  - `javax.crypto.spec.SecretKeySpec("abc".toByteArray(), "AES")` 漏。
  - `import ... SecretKeySpec as SKS` 之後的 `SKS("abc".toByteArray(), "AES")` 漏。
  - `SecretKeySpec(key = "abc".toByteArray(), algorithm = "AES")` 漏。
  - `android.webkit.WebView.setWebContentsDebuggingEnabled(true)` 漏。
  - `import ... WebView as WV` 之後的 `WV.setWebContentsDebuggingEnabled(true)` 漏。
- 這些都是等價寫法,建議至少在天花板節寫明,或用 `any` 補上帶完整套件名的 pattern。

## Finding 6
severity: minor
blocking: 否(誤報可用 `lint-waive`,但實驗只量了字串形狀)

- spec 段落:範圍 4「寫死金鑰」、S3。
- 引句:「或 `byteArrayOf(...)`;字串裡有 `$` 插值的不報。」
- 問題:`$K` 的限制(字串字面值、無插值)只掛在前兩個 pattern 上,`byteArrayOf($$$)` 這支完全沒限制,參數是變數也會報。
- 佐證:
  ```
  SecretKeySpec(byteArrayOf(x, y), "AES")        // 第 119 行,誤報
  SecretKeySpec(byteArrayOf(*other), "AES")      // 第 118 行,誤報
  SecretKeySpec(byteArrayOf(), "AES")            // 第 103 行,空陣列也報
  ```
- 引句:「金鑰是插值字串或變數、檔案放在 `src/test`、`src/debug` 底下」
- 這句好例只涵蓋 `.toByteArray()` 的變數(實測 `KEY.toByteArray()` 不報),涵蓋不到 `byteArrayOf` 的變數。
- 建議:`byteArrayOf` 的參數限制為全是整數字面值(`integer_literal`、`hex_literal`)。
- 補充:`"""多行""".trimIndent().toByteArray()` 與 `("ab"+"cd").toByteArray()` 漏報,屬已知形狀限制。

## Finding 7
severity: minor
blocking: 否(誤報面極小,記入規則註解即可)

- spec 段落:範圍 4「舊版 TLS」。
- 問題:`SSLContext.getInstance($V)` 搭配 `has stopBy end string_content` 只要引數裡任何位置有符合的字串就報。
- 佐證:
  ```
  SSLContext.getInstance("TLSv1.2".replace("x","TLSv1"))    // 第 71 行,命中
  SSLContext.getInstance(if (a()) "TLSv1.2" else "TLSv1")   // 第 68 行,命中(這個算真問題)
  SSLContext.getInstance("TLSv1$x")                         // 第 74 行,命中
  ConnectionSpec.COMPATIBLE_TLS.let { it.cipherSuites }     // 第 80 行,命中
  ```
  最後一行是讀屬性,但 `inside` 只看直接父節點,所以沒被「讀屬性不報」排除。
- 後果:少見,但會有 `lint-waive` 的雜訊。

## 逐節
- 範圍 1(範本加資安規則包):已讀,無 finding。
- 範圍 2(型錄登記):已讀,無 finding。
- 範圍 3(`_B4_LINT` 認資安包):已讀,無 finding。
  - `check.py:107` 的 regex 是 `(?:...|內建|slack|Android Lint):\s*([A-Z]...)`,加上 `資安包` 前綴可行。
  - `check.py:114-122` 以 `;`、`、` 切段,每段只要一個前綴加大寫開頭 id 就算,spec 列的 `資安包:A;內建:B` 形式沒問題。
  - ⚠ 資安包裡若有預設關的檢查,要加進 `B4_DEFAULT_OFF`(`check.py:104`)。我無法離線驗證,spec 沒提。
- 範圍 4 路徑排除:已讀,無 finding。
  - 實測 `src/debug/kotlin`、`src/test`、`src/debugFoo`、`src/testDebug` 都被排除。
  - 在 module 目錄內用相對路徑 `src` 掃也一樣被排除。
  - 不誤傷 `src/main/java/x/debug/` 和 `m-debug/src/main`,這兩處仍會掃。
  - 路徑排除的範圍沒有疑慮。
- 範圍 4 不接閘(`rules-unwired/`):已讀,無 finding。
- S1、S2、S4、S5:已讀,無 finding。
- S3:見 Finding 1、3。

## 實務隱患鏡頭
- 金流:無,spec 已寫明不碰付款。
- 對外送出:無,規則與型錄都是本機讀檔。
- 不可逆:無,退提交即回原狀。
- 守衛面:有,即 Finding 1 到 7。四條新規則進推送前的 `rules/`,漏報等於假安全,誤報等於擋住正常提交。

## 圖譜節點
- `Systems/kotlin規則包`:看了派工附的摘要,沒讀全文。新增的規則檔與樣本不改既有合約行為(該節點目前 0 條合約、0 行 KEY),所以判不影響。⚠ 如果規則包有「樣本必須覆蓋所有等價寫法」之類的未列入摘要的約定,Finding 1、2 會直接違反它。
- `Systems/linter精選目錄`:只加範本一行依賴,不動 12 行 KEY 的行為。我沒逐條比對,判不影響但沒驗。

最嚴重 severity:major,blocking 共 3 條(Finding 1、2、3)。
