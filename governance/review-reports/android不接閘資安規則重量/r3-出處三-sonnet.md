severity: major

## Finding 1
severity: major
blocking: 是

TEST-16 的 kt-prod-reads-system-clock 有兩個樣式,查到的出處沒有直接講到:`System.currentTimeMillis()` 和 `Date()`。

計劃對這兩個寫法的說法是:
引句:「保留的 java.time `now()`、`Date()`、`System.currentTimeMillis()` 各有 Oracle Clock javadoc 或 Sonar S8692 的原文」

我重新打開出處後的結果如下。
- Oracle Clock javadoc 只講 Clock 注入和 `now()` 工廠方法。內文沒有出現 `currentTimeMillis` 或 `Date`。
- Sonar S8692 是這兩個寫法唯一的出處,但它是「測試」規則。
  - 規則 json 的 scope 是 `Tests`,標題是 "The system clock should not be used in unit tests"。
  - 檢查原始碼的訊息是 "Do not use the system clock in tests."。
  - 說明裡這兩個寫法的句子是:`System.currentTimeMillis()`, `new Date()`, and `Calendar.getInstance()` "have the same problem and should be replaced with clock injection"。這句的語境是「測試不該依賴系統時鐘」,沒有說正式碼讀這兩個 API 是缺陷。
  - 型錄引的 "Legacy APIs such as System.currentTimeMillis(), new Date() …" 在我讀到的 PR 與規則頁都沒有逐字出現。
- 規則的 `ignores` 排除了測試目錄,只報正式碼。Sonar 的 scope 正好相反(Tests)。
- 要接上正式碼,得靠推論:測試怕時鐘,所以正式碼要注入 Clock。依判法,這不算直接涵蓋。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/configs/ast-grep/kotlin-android/rules-unwired/testing.yml`(kt-prod-reads-system-clock,pattern `System.currentTimeMillis()`、`Date()`)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/skills/kotlin-idioms/checks-catalog.md:661`(TEST-16 來源欄)
- 網頁:https://raw.githubusercontent.com/SonarSource/sonar-java/master/sonar-java-plugin/src/main/resources/org/sonar/l10n/java/rules/java/S8692.json 逐字原文:`"scope": "Tests"`、`"title": "The system clock should not be used in unit tests"`
- 網頁:https://raw.githubusercontent.com/SonarSource/sonar-java/master/java-checks/src/main/java/org/sonar/java/checks/tests/SystemClockCheck.java 逐字原文:"Do not use the system clock in tests."
- 網頁:https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/Clock.html 逐字原文:"Best practice for applications is to pass a `Clock` into any method that requires the current instant and time-zone."

建議二選一:把這兩個樣式拿掉(收窄到 `Instant/LocalDate/LocalDateTime/ZonedDateTime.now()` 加 `Clock.System.now()`),或找到直接講正式碼的出處。

## Finding 2
severity: major
blocking: 是

API-14 的 kt-async-await-immediately 兩個樣式是 `async { $$$ }.await()` 和 `async($$$) { $$$ }.await()`。它們沒有一份「講到這個寫法」的主要出處。

計劃的立場是:
引句:「別的 scope 那例沒有原文說能換成 withContext(維護者在議題 #1493 說兩者不等價」

我讀到的兩份出處各自的內容:
- IntelliJ `KotlinBundle.properties` 只有一行,逐字是 `redundant.async.call.may.be.reduced.to.0=Redundant ''async'' call may be reduced to ''{0}''`。
  - 它只有名字和一個佔位符 `{0}`。
  - 沒有說什麼樣的 `async` 呼叫算冗餘。
  - 沒有說接 `.await()`。
  - 沒有說要改成什麼,更沒有說「直接呼叫 `f()`」。
  - 我試了推測的 inspection 原始碼與說明檔路徑,都是 404,沒讀到判定邏輯。
- kotlinx.coroutines #1493 只是議題留言,依判法只算佐證。
  - 議題標題是 "Redundant 'async' call may be reduced to 'kotlinx.coroutines.withContext'"。
  - 這說明 IntelliJ 實際報的是帶明確接收者的 `X.async(ctx){…}.await()`,建議改 withContext,而規則剛好排除這個形狀。
  - 維護者 elizarov 的逐字原文是 "Indeed, they are not equivalent. Yes, usually `async { ... }.await()` is an error anyway." 這是留言,不是官方文件。
- 所以規則抓的「同一個 scope、省略接收者」形狀,沒有任何官方文件、KDoc 或規則頁直接講到。
- 規則訊息「改成直接呼叫 f(),要換執行緒就改用 withContext(io) { f() }」在兩份出處裡也都沒有。
- 型錄來源欄還引了 "detekt SequentialAsyncAwait"。r2 前的查證報告 a 已寫過在 detekt 原始碼搜不到,型錄沒有更正。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/configs/ast-grep/kotlin-android/rules-unwired/api.yml`(kt-async-await-immediately)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/skills/kotlin-idioms/checks-catalog.md:166`
- 網頁:https://raw.githubusercontent.com/JetBrains/intellij-community/master/plugins/kotlin/base/resources/resources-en/messages/KotlinBundle.properties 逐字原文:`redundant.async.call.may.be.reduced.to.0=Redundant ''async'' call may be reduced to ''{0}''`
- 網頁:https://github.com/Kotlin/kotlinx.coroutines/issues/1493(議題,只算佐證)

## Finding 3
severity: minor
blocking: 否

FLOW-14 的 kt-asflow-not-cancellable 樣式是 `$X.asFlow()`,接收者什麼都收。型錄來源 flow.md 的 Flow cancellation checks 只用 `IntRange.asFlow` 當例子。

- 原文只在例子裡提到 `IntRange.asFlow`。
- 其他接收者我另外讀了官方 `Builders.kt`(1.9.0)。Iterable、Iterator、Sequence、Array、IntArray、LongArray、LongRange 的 `asFlow` 都用同一個不做取消檢查的 `unsafeFlow` 寫法。事實上成立,但這份原始碼不在型錄的來源欄。
- 這不是主張錯誤,是來源欄缺一個網址。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/configs/ast-grep/kotlin-android/rules-unwired/flow.yml`(kt-asflow-not-cancellable)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/skills/kotlin-idioms/checks-catalog.md:222`
- 網頁:https://raw.githubusercontent.com/Kotlin/kotlinx.coroutines/1.9.0/kotlinx-coroutines-core/common/src/flow/Builders.kt 逐字原文:`public fun &lt;T&gt; Iterable&lt;T&gt;.asFlow(): Flow&lt;T&gt; = flow { forEach { value -&gt; emit(value) } }`(該檔把 `flow` 匯入成 `unsafeFlow`)

## Finding 4
severity: minor
blocking: 否

ARCH-3 的 kt-click-navigate-unguarded 抓得比 KDoc 寬。

- `dropUnlessResumed` KDoc 的範例只有 `Button(onClick = dropUnlessResumed { … })`。
- 文字只說 "it's recommended to safeguard navigate methods when using them while a composable is in transition"。
- 規則的 `Modifier.clickable { … }` 是同類點擊處理器,合理。
- 但規則的 `$N.navigate($$$)` 不限定接收者。ViewModel 或其他物件的 `.navigate()` 也會被抓,KDoc 只講 `navController.navigate`。
- 型錄後果欄第二句(NavController 的 `IllegalArgumentException`)是 `navigate(resId)` 的 Throws 表。頁面沒有把它和點擊重入連起來,這是型錄自己串的,規則訊息沒用到。
- 核心(Compose 點擊內 `navigate` 要用 `dropUnlessResumed` 包)有 KDoc 直接支持。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/configs/ast-grep/kotlin-android/rules-unwired/architecture.yml`(kt-click-navigate-unguarded)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/skills/kotlin-idioms/checks-catalog.md:447`
- 網頁:https://developer.android.com/reference/kotlin/androidx/lifecycle/compose/dropUnlessResumed.composable 逐字原文:"it's recommended to safeguard navigate methods when using them while a composable is in transition as a result of navigation."

## Finding 5
severity: minor
blocking: 否

CO-37 的 kt-mutex-reentrant 的 `has` 帶 `stopBy: end`,會穿過子協程的 lambda 邊界。

- Mutex KDoc 只說「同一個 thread/coroutine 再次 lock 會暫停」。
- `m.withLock { scope.launch { m.withLock {…} } }` 這種外層沒等子協程的寫法,不是同一個協程重入。原文沒涵蓋,訊息的「會一直暫停、等不到」也不一定成立。
- 規則的主要寫法(同一協程內巢狀 `withLock` 或 `lock()`)有 KDoc 逐字支持。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/configs/ast-grep/kotlin-android/rules-unwired/coroutines.yml`(kt-mutex-reentrant)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/skills/kotlin-idioms/checks-catalog.md:315`
- 網頁:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-mutex/ 逐字原文:"It is non-reentrant, that is invoking lock even from the same thread/coroutine that currently holds the lock still suspends the invoker."

## Finding 6
severity: minor
blocking: 否

STATE-9 和 TEST-33 的型錄有幾處寫得比原文多,或來源欄的網址對不上主張。規則判定依據都沒問題。

- STATE-9:
  - 規則訊息「停止延遲預設 0,最後一個收集者一走就停」有 KDoc 逐字支持。「改用 `WhileSubscribed(5_000)`」有官方範例支持。
  - 型錄後果欄的「旋轉螢幕會重建畫面、重新收集(codelab)」是把兩段話接在一起。codelab 只說 config change 會重建 Activity,以及要設 `TIMEOUT_MILLIS` 來延遲停止。它沒有說「預設 0 所以旋轉會重啟」,這是推論。
  - KDoc 沒把 0 稱為缺陷。
- TEST-33:
  - `@LooperMode(LEGACY)`:`LooperMode.Mode` javadoc 有 Deprecated、"use LooperMode.PAUSED"、"not supported on Android SDKs &gt; Baklava"、"execute tasks posted to a Looper inline synchronously"。
  - 型錄寫「PAUSED looper(預設)」,出處是 `LooperMode.html` 的 "Robolectric will default to LooperMode.Mode.PAUSED behavior"。型錄 2026-11-07 列的 `robolectric.org/configuring/` 我讀過,頁面完全沒提 LooperMode,所以「預設」那句的來源網址沒列在型錄裡。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/configs/ast-grep/kotlin-android/rules-unwired/state.yml`(kt-whilesubscribed-no-timeout)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/configs/ast-grep/kotlin-android/rules-unwired/testing.yml`(kt-robolectric-legacy-looper)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/skills/kotlin-idioms/checks-catalog.md:254`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure/skills/kotlin-idioms/checks-catalog.md:678`
- 網頁:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-sharing-started/-companion/-while-subscribed.html 逐字原文:"It defaults to zero (stop immediately)."
- 網頁:https://robolectric.org/javadoc/latest/org/robolectric/annotation/LooperMode.html 逐字原文:"Currently Robolectric will default to LooperMode.Mode.PAUSED behavior."

## 逐列核對結果

我每個來源都重新打開。`gh` 在這個席位被擋,GitHub 檔改用 raw 網址讀。API-14 的 IntelliJ 檢查原始碼我試了幾個路徑都是 404,沒讀到,所以那列的判定只依 `KotlinBundle.properties` 一行與議題內容。

保留的七列:
- API-14:同 scope 形狀沒有官方文件或規則頁直接涵蓋,是 Finding 2(阻擋)。
- ARCH-3:核心有 KDoc 直接支持,receiver 不限定與 `clickable` 是範圍略寬,不阻擋。
- CO-37:核心有 KDoc 直接支持,穿過子協程邊界是邊緣,不阻擋。
- FLOW-14:事實成立,只是 `Builders.kt` 該補進來源欄,不阻擋。
- STATE-9:規則依據有 KDoc 與官方範例,後果欄的旋轉那句是推論,不阻擋。
- TEST-16:java.time 的 `now()` 與 `Clock.System.now()` 有 Oracle 與 Kotlin 文件支持。`Date()` 和 `System.currentTimeMillis()` 兩個樣式的唯一出處是測試範圍的 Sonar 規則,見 Finding 1(阻擋)。
- TEST-33:`@LooperMode(LEGACY)` 有 javadoc 直接支持,「預設 PAUSED」要補 `LooperMode.html` 當來源,不阻擋。

已移除的三列,移除站得住:
- API-36:我另外搜了 detekt、Sonar、PMD、Error Prone 的規則庫,沒找到「用 `message` 字串比對判斷錯誤類型」的規則,只找到相近但不同的規則。沒有符合判法的出處。
- UI-103:官方 previews 頁我通讀。沒有一句說預覽不包主題是錯的,只有寫法範例,而且基本範例 `SimpleComposablePreview` 自己就沒包主題。移除站得住。
- TEST-31:官方 codelab 把 `testTag` 放在最後手段,和「用文字找是錯的」相反。索引取節點沒有警告。官方範例自己用 `onFirst()`。移除站得住。

圖譜鏡頭(固定席節點 `Systems/kotlin規則包`):這份設計不影響該節點宣稱的行為與合約。該節點掛 0 條合約和 0 行 KEY,所有改動都在只登記不擋的目錄,不改會擋的規則。但上面兩條阻擋項若修正(拿掉樣式或改寫),型錄與規則包的樣本、測試期望(`t_kotlin_rulepack_samples` 與統計寫死值)要跟著改。

我在 `/tmp/lumos-seat-work/android不接閘資安規則重量/出處三-sonnet/` 建了一個空目錄,沒寫任何檔案。

最高等級 major;blocking 2 條
