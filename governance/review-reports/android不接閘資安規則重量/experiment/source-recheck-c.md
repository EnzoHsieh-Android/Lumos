三項的結論：第 1 項**部分支持**，第 2 項**找不到**，第 3 項**部分支持**。第 3 項另有一個要注意的地方：你建議的取代寫法本身會被 detekt 一條預設開啟的規則標出來。下面每條原文都是我實際打開頁面讀到的，Sonar 與 CERT 的段落是抓原文頁面或官方原始碼逐字取出。

---

### 第 1 項：直接取現在時間，應改注入 Clock

**判定：部分支持。** `java.time` 的 `now()` 系列和 Kotlin 的 `Clock.System` 有官方原文直接說「該傳入 Clock」。`System.currentTimeMillis()` 和 `Date()` 只有 Sonar 規則的說明文字涵蓋。`System.nanoTime()` 和 Android 的 `SystemClock` 兩個方法完全找不到。

| API | 有沒有原文涵蓋 | 出處 |
|---|---|---|
| `Instant.now()` | 有，直接說 | Oracle Clock javadoc；Sonar S8692 |
| `LocalDate.now()` | 有，直接說 | Oracle Clock javadoc；Sonar S8692 |
| `LocalDateTime.now()` | 有，直接說 | Oracle Clock javadoc；Sonar S8692 |
| `ZonedDateTime.now()` | 有：Oracle 泛指所有 `now()`；Sonar 說明文字沒點名，但它的檢查程式有列 | Oracle Clock javadoc；Sonar 檢查程式 |
| `Date()` | 有：Sonar 說明文字寫「應改成注入時鐘」，檢查程式也會抓 | Sonar S8692 |
| `System.currentTimeMillis()` | 部分：Sonar 說明文字寫要改成注入時鐘，但它的檢查程式其實不抓這個呼叫；Oracle 只說 InstantSource 的毫秒值等同它 | Sonar S8692；Oracle InstantSource |
| `System.nanoTime()` | 沒有 | — |
| `SystemClock.elapsedRealtime()` | 沒有：官方頁只講三種時鐘各用在哪，沒提注入或測試 | — |
| `SystemClock.uptimeMillis()` | 沒有：同上 | — |
| Kotlin `Clock.System`（取代目標那一側） | 有，直接說 | kotlinlang.org 的 kotlin.time.Clock |

**出處與逐字原文：**

1. https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/Clock.html
   &gt; "Best practice for applications is to pass a `Clock` into any method that requires the current instant and time-zone. A dependency injection framework is one way to achieve this"
   &gt; "All key date-time classes also have a `now()` factory method that uses the system clock in the default time zone. ... Applications use an object to obtain the current time rather than a static method. This can simplify testing."

2. https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/InstantSource.html
   &gt; "Best practice for applications is to pass an `InstantSource` into any method that requires the current instant."
   &gt; "This returns the millisecond-based instant ... This is equivalent to the definition of `System.currentTimeMillis()`."（`millis()` 的說明）

3. https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.time/-clock/
   &gt; "It is not recommended to use Clock.System directly in the implementation. Instead, you can pass a Clock explicitly to the necessary functions or classes. This way, tests can be written deterministically by providing custom Clock implementations to the system under test."

4. Sonar 規則 S8692「The system clock should not be used in unit tests」。rules.sonarsource.com 上的頁面回 404，以下是從 Sonar 官方原始碼讀的：`SonarSource/sonar-java` 裡的 `S8692.html` 和 `SystemClockCheck.java`，用 `gh api` 讀取，相關的合併請求是 https://github.com/SonarSource/sonar-java/pull/5611 ，2026-05-21 合併。
   &gt; "Legacy APIs such as `System.currentTimeMillis()`, `new Date()`, and `Calendar.getInstance()` have the same problem and should be replaced with clock injection."
   &gt; "the service uses a static call to `Instant.now()`. This makes it impossible to mock the time without using advanced (and often discouraged) static mocking techniques."
   &gt; "The best practice is to inject a `java.time.Clock` instance into the class or method being tested. In production code, `Clock.systemDefaultZone()` can be used"

   注意兩點：
   - 這條規則只套在測試碼上（設定檔寫 `"scope": "Tests"`）。但它的反例和正解直接改的是正式程式的類別，從 `Instant.now()` 改成建構子傳入 `Clock`，所以算支持「正式程式該注入」這個主張。
   - 它的檢查程式比對的是那些時間類別的 `now()`（無參數或只帶時區）、`Clock.system*`、`Calendar.getInstance`、`new Date()`，**不比對** `System.currentTimeMillis()`，跟說明文字不一致。

5. 測試替身這一側也有官方原文，不過它只說「這個好用」，沒說直接呼叫不好。https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.time/-test-time-source/ ：
   &gt; "A time source that has programmatically updatable readings. It is useful as a predictable source of time in tests."

   `TimeSource` 本身的頁面沒提測試或注入。

**一句說明：** `java.time` 的 `now()` 和 Kotlin 的 `Clock.System` 有官方文件直接背書；`System.currentTimeMillis()` 和 `Date()` 靠的是 Sonar 一條測試範圍規則的說明文字；`System.nanoTime()` 與 Android `SystemClock` 兩個方法沒有任何權威原文。

另外查到但不構成支持的：Error Prone 的 JavaTimeDefaultTimeZone 只要求明確指定時區，沒提 Clock；detekt 沒有這類內建規則。

---

### 第 2 項：Compose 測試用索引挑節點

**判定：找不到。** 也談不上矛盾。

**出處與逐字原文：**

1. https://developer.android.com/reference/kotlin/androidx/compose/ui/test/SemanticsNodeInteractionCollection ，`get(index)` 的說明只有：
   &gt; "Retrieve node at the given index of this collection."

   沒有任何關於順序穩不穩定的警告。

2. https://developer.android.com/develop/ui/compose/testing/apis ，官方範例自己就用位置挑節點，不過是先過濾、再斷言數量之後才挑：
   ```
   composeTestRule.onNode(hasTestTag("Players"))
       .onChildren()
       .filter(hasClickAction())
       .assertCountEquals(4)
       .onFirst()
       .assert(hasText("John"))
   ```

3. 其他查過的：測試語意那一頁沒講節點唯一性。detekt、compose-rules、Slack compose-lints 都沒有針對測試索引的規則。Sonar 和 Android Lint 也都沒找到。

**一句說明：** 官方只有說明這個方法做什麼，自己的範例還在用 `onFirst()`，沒有任何權威原文說靠位置挑節點不好。這條主張目前只能算經驗法則。

---

### 第 3 項：靠例外訊息字串判斷錯誤

**判定：部分支持。** 你列的那些工具規則庫（Sonar、detekt、PMD、Error Prone、Android Lint）都沒有「別比對例外訊息」的規則。直接講這件事的原文只找到一篇，來自 CERT 程式寫作標準，它不在你列的權威清單裡。官方 javadoc 只撐得住「訊息可能因語系而變」這半句。

**出處與逐字原文：**

1. CERT Java 程式寫作標準 ERR51-J「Prefer user-defined exceptions over more general exception types」：https://cmu-sei.github.io/secure-coding-standards/sei-cert-oracle-coding-standard-for-java/recommendations/exceptional-behavior-err/err51-j （抓原文頁面讀的）
   &gt; "This noncompliant code example attempts to distinguish between different exceptional behaviors by looking at the exception's message"
   &gt; "However, any change to the exception message literals involved will break the code."
   &gt; "This compliant solution uses specific exception types and defines new special-purpose exception types where required."

   這篇把整個主張講完整了：比對訊息會壞，應改用型別。但它是卡內基美隆大學軟體工程研究所（SEI）的安全程式寫作標準，不是官方文件，也不是工具規則頁，要不要採計請你裁。

2. https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Throwable.html ，`getLocalizedMessage()` 的說明：
   &gt; "Subclasses may override this method in order to produce a locale-specific message."

   只能間接撐「訊息不是穩定介面」，而且它講的是 `getLocalizedMessage()`，不是 `getMessage()`。

3. 第 3 項的「取代寫法」本身會被抓。https://detekt.dev/docs/rules/exceptions/ 的 InstanceOfCheckForException 規則，官方標示預設開啟（Active by default: Yes）：
   &gt; "This rule reports catch blocks which check for the type of exception via is checks or casts. Instead of catching generic exception types and then checking for specific exception types the code should use multiple catch blocks."

   換句話說，你建議的改法若寫成在 catch 區塊裡判斷 `if (e is SocketTimeoutException)`，會被這條規則抓到。它支持「靠型別區分」，但要的形狀是另寫一個 `catch (e: SocketTimeoutException)`，不是在 catch 裡用 `is` 判斷。

4. 其他查過的：PMD 的議題 #1747 裡雖然出現 `getMessage().contains(...)`，但那是另一條規則的誤報，不是規則本身。Sonar Java 規則說明裡提到 `getMessage` 的幾條（S8714、S3658、S5779、S1166）都跟這件事無關。

**一句說明：** 「改用型別」只有 CERT 這份不在清單裡的標準完整講到；官方 javadoc 只撐得住「訊息可能隨語系變」；取代寫法建議寫成另一個 catch 子句，不要寫成 `is` 判斷，才不會被 detekt 預設開啟的規則抓到。

---

全程只讀，沒有改任何檔案，沒有動 git，也沒有建任何臨時目錄。

**三項判定：第 1 項部分支持（java.time 的 now() 系列與 Kotlin Clock.System 直接支持；currentTimeMillis 與 Date() 只有 Sonar 測試範圍規則的說明文字；nanoTime 與 SystemClock 兩個方法找不到）／第 2 項找不到／第 3 項部分支持（只有不在清單的 CERT ERR51-J 直接講；取代寫法若用 `is` 判斷會被 detekt 預設規則抓到）。**
