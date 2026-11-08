<!-- 2026-11-08 對照代理原始回報,逐字存檔;編排者沒改內容。條數口徑與下游對應見計劃〈實驗〉〈MobSF 對照〉。 -->

# MobSF Kotlin 規則對照我們的 Kotlin/Android 型錄與規則包

**一句話結論**:這批規則實際是 **50 條,不是 52 條**(6 個檔:android 11、biometric 1、crypto 15、injection 11、network 4、webview 8)。其中 17 條已涵蓋,1 條部分涵蓋,4 條型錄有列但規則還在未接區,5 條型錄登記的現成檢查其實不抓這個形狀,23 條型錄裡完全沒有。這次沒改 repo 任何檔,也沒跑 git 寫入指令。

## 先說兩個最要緊的發現:型錄有兩列登記的檢查,實際抓不到它寫的壞例

這是讀過 Google 偵測器原始碼才確認的。

- **DATA-83(弱雜湊)**:登記的是「資安包:VulnerableCryptoAlgorithm」。它的原始碼只檢查 `javax.crypto.Cipher.getInstance`,雜湊用的 `MessageDigest.getInstance("MD5")` 根本不會經過它。原始碼和測試檔裡 `MessageDigest` 出現 0 次。所以 MD5、SHA-1、MD4 目前沒有任何檢查在抓,這列筆記寫錯了。
- **DATA-79(原始碼寫死秘密)**:登記的是「內建:SecretInSource」。它只檢查 Gemini SDK 的 `GenerativeModel` 建構子,而且只看 `AIza` 開頭、長度超過 30 的金鑰。所以 `const val API_KEY = "…"`、`val password = "…"` 這類一般寫死的秘密都抓不到。AuthLeak 也只抓網址裡的 `user:pass@`。

## 對照表

判定欄的簡寫:**有**=已涵蓋;**部分**;**未接**=型錄有列、自寫規則在 `rules-unwired/`;**錯登**=型錄有列,但登記的現成檢查不抓這個形狀;**無**=型錄完全沒有。

| MobSF id | 判定 | 型錄列 | 接法 | 官方出處 | 一句原文 |
|---|---|---|---|---|---|
| android_kotlin_hiddenui | 無 | 無 | 不做(只是可疑,低) | https://mas.owasp.org/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0008/ | "Search for any traces of sensitive information and evaluate if it should be masked or completely removed." |
| android_kotlin_logging | 有 | DATA-81(資安包 LogInfoDisclosure) | — | — | MobSF 每個 Log 都報(INFO 級);我們只報帶 password、token、key 等字的,比較準 |
| android_kotlin_hardcoded | 錯登 | DATA-79 | 自寫形狀規則(提示級:變數名稱配字串字面值;是不是真秘密要看語意) | https://developer.android.com/privacy-and-security/risks/hardcoded-cryptographic-secrets | "it's common to find them hardcoded into the application as a string or byte array in the code" |
| android_kotlin_world_writable | 有 | DATA-85(內建 WorldWriteableFiles) | — | — | Lint 只認識常數名稱;直接寫數字 2 的抓不到(API 24 以上本來就會丟例外,可忽略) |
| android_kotlin_world_readable | 有 | DATA-85(內建 WorldReadableFiles) | — | — | 同上 |
| android_kotlin_world_read_write | 有 | DATA-85 | — | — | 只寫數字 3 的抓不到,同上可忽略 |
| android_kotlin_sensitive_input_keyboard_cache | 無 | 無 | 只能語意(表態)。內建 TextFields 只管「沒寫 inputType」,屬易用性檢查,不管快取 | https://mas.owasp.org/MASTG/tests/android/MASVS-STORAGE/MASTG-TEST-0006/ | "If the XML attribute android:inputType is given the value textNoSuggestions , the keyboard cache will not be shown" |
| android_kotlin_sensitive_notification | 無 | 無 | 只能語意(表態) | https://mas.owasp.org/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0315/ | "Notifications can be created using the setContentTitle and setContentText methods of Notification.Builder" |
| android_kotlin_pending_intent_not_immutable | 有 | ARCH-70(內建 UnspecifiedImmutableFlag、MutableImplicitPendingIntent) | — | — | — |
| android_kotlin_db_on_external_storage | 部分 | DATA-27(`getExternalStorageDirectory` 那一支有抓) | 自寫形狀規則:補「`getExternalFilesDir` 當資料庫路徑」那一支 | https://developer.android.com/privacy-and-security/risks/sensitive-data-external-storage | "any data stored on the external storage can be accessed by any other application with the READ_EXTERNAL_STORAGE permission." |
| android_kotlin_oauth_custom_scheme_redirect | 無 | 無 | 自寫形狀規則(提示級,低~中)。RFC 允許自訂 scheme 搭 PKCE,MobSF 講得太重 | https://datatracker.ietf.org/doc/html/rfc8252 | "App-claimed "https" scheme redirects are less susceptible to URI interception due to the presence of the URI authority" |
| android_kotlin_biometric_without_crypto | 無 | 無 | 只能語意(表態)。形狀抓得到「沒碰 cryptoObject」,但要不要綁加密看保護的是什麼 | https://mas.owasp.org/MASTG/tests/android/MASVS-AUTH/MASTG-TEST-0327/ | "When used without a CryptoObject the app relies on the onAuthenticationSucceeded callback to determine if authentication was successful (event-bound)." |
| android_kotlin_insecure_random | 有 | DATA-84(資安包 WeakPrng、內建 SecureRandom) | — | — | — |
| android_kotlin_aes_ecb | 有 | DATA-82(內建 GetInstance) | — | — | — |
| android_kotlin_aes_ecb_default | 有 | DATA-82(內建 GetInstance,認得 "AES"、"DES"、"DESede") | — | — | — |
| cbc_kotlin_padding_oracle | 有 | DATA-82(資安包 UnsafeCryptoAlgorithmUsage;原始碼確認 CBC 都會報) | — | — | — |
| android_kotlin_rsa_no_oaep | 錯登 | DATA-82 | 自寫形狀規則。GetInstance 跳過 `RSA/` 開頭;UnsafeCrypto 只報 RSA 配 PKCS1Padding 和 CBC,`RSA/ECB/NoPadding` 兩支都不報 | https://developer.android.com/privacy-and-security/risks/broken-cryptographic-algorithm | "Asymmetric encryption: RSA-2048 / RSA-4096 with OAEP padding" |
| android_kotlin_weak_hash(MD4) | 錯登 | DATA-83 | 自寫形狀規則(提示級:拿來做檢查碼是合理用途) | 同上 | "The use of weak or broken cryptographic hash functions (such as MD5 or SHA1 ) poses a significant risk" |
| android_kotlin_weak_ciphers | 有 | DATA-83(資安包 VulnerableCryptoAlgorithm:DES、RC2、RC5、Blowfish、RC4,只認大寫) | — | — | — |
| android_kotlin_md5 | 錯登 | DATA-83 | 自寫形狀規則(提示級) | 同上 | 同上 |
| android_kotlin_sha1 | 錯登 | DATA-83 | 自寫形狀規則(提示級) | 同上 | 同上 |
| android_kotlin_weak_iv | 無 | 無 | 自寫形狀規則(全是整數字面值的 IV) | https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0309/ | "NIST SP 800 38A states that CBC requires a fresh or unpredictable IV for every encryption." |
| android_kotlin_custom_xor_crypto | 無 | 無 | 只能語意(低) | https://mas.owasp.org/MASTG/0x04g-Testing-Cryptography/ | "Always investigate further when you find bit manipulation operators like XOR (exclusive OR)." |
| android_kotlin_aes_hardcoded_key | 未接 | DATA-87(kt-secretkeyspec-literal-key) | 量完誤報後搬進 `rules/` | https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0212/ | "we need to focus on the cryptographic implementations of hardcoded keys." |
| android_kotlin_cbc_static_iv | 無 | 無 | 自寫形狀規則(`IvParameterSpec` 吃字面值) | 同 MASTG-TEST-0309 | 同上 |
| android_kotlin_insecure_sslv3 | 未接 | API-45(kt-insecure-tls-version 已含 SSLv3) | 量完誤報後搬進 `rules/` | https://mas.owasp.org/MASTG/tests/android/MASVS-NETWORK/MASTG-TEST-0217/ | "An app can obtain an SSLContext using an insecure TLS protocol by calling SSLContext.getInstance("TLSv1.1")" |
| android_kotlin_weak_key_size | 無 | 無 | 自寫形狀規則(RSA 小於 2048、AES 小於 128 的字面值) | https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0208/ | "The key size can be specified using the initialize(int keysize) method." |
| android_kotlin_sql_raw_query | 有 | DATA-24(自寫 kt-sql-string-concat,已上線;只報串接,比 MobSF 準) | — | — | — |
| android_kotlin_jackson_deserialize | 無 | 無 | 自寫形狀規則(低:Android 少用 Jackson) | https://mas.owasp.org/MASTG/tests/android/MASVS-CODE/MASTG-TEST-0337/ | "If the app deserializes data from these sources without restricting the allowed classes … can introduce unintended application behavior" |
| android_kotlin_command_injection | 無 | 無 | 只能語意(資料從哪來) | https://cwe.mitre.org/data/definitions/78.html | "The product constructs all or part of an OS command using externally-influenced input from an upstream component" |
| android_kotlin_command_injection_warning | 無 | 無 | 自寫形狀規則(提示級:串接或 `sh -c`)。另見文末:可登記 UnsafeDynamicallyLoadedCode | 同上 | 同上 |
| android_kotlin_object_deserialization | 無 | 無(DATA-78 SerializableUsage 只管類別實作 Serializable) | 自寫形狀規則(提示級:`ObjectInputStream(`) | https://developer.android.com/privacy-and-security/risks/unsafe-deserialization | "A feasible solution could be to implement the look-ahead pattern for the java.io.ObjectInputStream library ." |
| android_kotlin_xmlinputfactory_xxe | 無 | 無 | 不做:Android SDK 沒有這個 API(官方參考頁回 404) | https://developer.android.com/reference/javax/xml/stream/XMLInputFactory | 404 |
| android_kotlin_xmlinputfactory_xxe_enabled | 無 | 無 | 不做(同上) | 同上 | 404 |
| android_kotlin_xml_decoder_xxe | 無 | 無 | 不做:`java.beans.XMLDecoder` 不在 Android SDK | https://developer.android.com/reference/java/beans/XMLDecoder | 404 |
| android_kotlin_provider_path_traversal | 無 | 無 | 自寫形狀規則(近似:provider 的 `openFile` 用路徑做 File,同一函式裡沒有 canonicalPath 比對)。中~高 | https://developer.android.com/privacy-and-security/risks/path-traversal | "an attacker might use special characters such as ../ to unexpectedly change the resource target" |
| android_kotlin_zip_slip | 無 | 無 | 自寫形狀規則(近似:`File(dir, entry.name)` 同一函式沒有 canonicalPath)。高 | https://developer.android.com/privacy-and-security/risks/zip-path-traversal | "The Zip Path Traversal vulnerability, also known as ZipSlip, is related to handling compressed archives." |
| android_kotlin_intent_redirection | 有 | ARCH-71(內建 UnsafeIntentLaunch) | — | — | — |
| android_kotlin_insecure_ssl | 有 | API-22(TrustAllX509TrustManager、AllowAllHostnameVerifier、BadHostnameVerifier)+ API-43 | — | — | — |
| android_kotlin_insecure_tls_version | 未接 | API-45 | 量完誤報後搬進 `rules/` | 同 MASTG-TEST-0217 | 同上 |
| android_kotlin_weak_tls_cipher_suite | 無 | 無(API-45 只管 TLS 版本) | 自寫形狀規則(`setEnabledCipherSuites` 或 OkHttp `cipherSuites` 帶弱套件名) | https://developer.android.com/reference/javax/net/ssl/SSLSocket | "This group is set using the setEnabledCipherSuites method" |
| android_kotlin_local_server_socket | 無 | 無 | 只能語意(有沒有驗證握手) | https://developer.android.com/reference/android/net/LocalServerSocket | "Non-standard class for creating an inbound UNIX-domain socket in the Linux abstract namespace." |
| android_kotlin_webview | 有 | API-38(內建 AddJavascriptInterface、JavascriptInterface) | — | — | — |
| android_kotlin_webview_allow_file_from_url | 有 | API-40(自寫 kt-webview-file-url-access,已上線) | — | — | — |
| android_kotlin_webview_debug | 未接 | API-41(kt-webview-debugging-enabled;樣本外 42 處誤報 16) | 先修誤報再搬 | https://mas.owasp.org/MASTG/tests/android/MASVS-RESILIENCE/MASTG-TEST-0227/ | "All locations where WebView.setWebContentsDebuggingEnabled is called with true at runtime." |
| android_kotlin_webview_ignore_ssl | 有 | API-39(內建 WebViewClientOnReceivedSslError) | — | — | — |
| android_kotlin_webview_mixed_content | 無 | 無(Lint 索引裡沒有對應檢查) | 自寫形狀規則(`MIXED_CONTENT_ALWAYS_ALLOW`)。中 | https://developer.android.com/reference/android/webkit/WebSettings | "For highest security, apps are recommended to use MIXED_CONTENT_NEVER_ALLOW ." |
| android_kotlin_webview_external | 有(連帶抓到) | DATA-27 會報 `Environment.getExternalStorageDirectory()`,但告警理由是分區儲存,不是 WebView 風險 | — | — | — |
| android_kotlin_webview_set_allow_file_access | 無 | 無(API-40 的規則只管 …FromFileURLs 那兩個) | 自寫形狀規則:擴充 kt-webview-file-url-access。中 | https://developer.android.com/privacy-and-security/risks/webview-unsafe-file-inclusion | "Enabling setAllowFileAccess , setAllowFileAccessFromFileURLs , and setAllowUniversalAccessFromFileURLs can allow malicious intents … to access arbitrary local files" |
| android_kotlin_deeplink_to_webview | 無 | 無 | 只能語意(資料流);最直接的 `loadUrl(intent.data…)` 形狀可以補提示級。高 | https://developer.android.com/privacy-and-security/risks/unsafe-uri-loading | "An unsafe URI Loading occurs when an Android application fails to correctly evaluate the validity of a URI before loading it into a WebView." |

## 統計(共 50 條)

- **已涵蓋:17 條**(含 webview_external 連帶抓到的 1 條)。**部分涵蓋:1 條**(db_on_external)。
- **要登記現成檢查:0 條**。上表每個缺口都查過 Lint 索引的 851 個檢查 id,沒有一個能直接接的。
- **把未接的自寫規則接通:4 條**(API-41、API-45 兩條、DATA-87)。
- **可自寫形狀規則:18 條**,其中 hardcoded、MD4、MD5、SHA-1、oauth、command_injection_warning、object_deserialization 這 7 條只適合當提示級。
- **只能語意(表態):7 條**(鍵盤快取、通知、生物辨識、命令注入、LocalServerSocket、deeplink 進 WebView、XOR)。
- **不做:4 條**(hiddenui,加上 3 條 XXE:用的 API Android 上根本沒有)。

**實務上最該先補的**:
1. zip_slip、provider 路徑穿越:可以被利用,任意讀寫檔案。
2. deeplink 進 WebView:配上 JavaScript 橋接就變成遠端注入。
3. DATA-83 和 DATA-79 修正登記並補規則:現在等於完全沒防。
4. RSA 不帶填充、寫死的 IV、`MIXED_CONTENT_ALWAYS_ALLOW`、`setAllowFileAccess(true)`。

## 順帶發現(不在 MobSF 裡,但是內建有、型錄沒登記)

- **DATA-27** 寫著「Lint SdCardPath 代號待查」。這個檢查確實存在,而且檢查頁就叫 SdCardPath,可以直接登記成 `內建:SdCardPath`。
- **DATA-85** 登記了 SetWorldReadable,但漏了成對的 **SetWorldWritable**。這個檢查存在,原始碼裡 `setWritable(true, false)` 和 setReadable 走同一段邏輯。
- **UnsafeDynamicallyLoadedCode**(用 `System.load` 從非程式庫目錄載入程式碼)型錄沒有,可以接 command_injection_warning 裡 loadLibrary 那一支的鄰近風險。另一個鄰近檢查 **UnsanitizedFilenameFromContentProvider** 管的是「信任別人 provider 給的檔名」,方向和 MobSF 那條相反,但同屬路徑穿越這一類。
- Android 上真正的 XXE 入口是 `DocumentBuilderFactory`、`XmlPullParser`,MobSF 和我們都沒管。官方頁:https://developer.android.com/privacy-and-security/risks/xml-external-entities-injection
- MobSF 自己附的參考有 3 條指錯頁:鍵盤快取指到 0005(其實是通知)、通知指到 0010(其實是截圖)、provider 路徑穿越指到 0022(其實是憑證釘選)。上表已換成正確的頁。

## 備註

- 所有網址都用 curl 實際打開確認過:XMLInputFactory 和 XMLDecoder 兩頁回 404,用來佐證「Android 沒有這個 API」;其餘都回 200。
- 上面 23 條「無」是用關鍵字掃整份型錄、再打開相關列讀過才判的。照專案規則,如果要據此動手做規則,建議先派一個乾淨 agent 用原始問題獨立對一次。
- DATA-83 和 DATA-79 這兩句筆記錯了;照專案規則應該各立一篇 Issue,並在 catalog-rulings 那個工作樹修正登記。這次是只讀任務,所以沒動。
- 這次在 scratchpad 建的網頁快取和小工具目錄已刪;MobSF 原始資料沒動。
