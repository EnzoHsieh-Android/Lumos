severity: major

審查摘要:T2 到 T5 的原始矩陣我用作者的抽格程式重跑了一次,25 格全部與矩陣相符,沒有不一致。另外我寫了 30 多個變形格(壞寫法變形、合法好寫法變形),並在 Android library 模組(AGP 8.13.2、compileSdk 36)實測了 T3。重現檔都在 `/tmp/lumos-seat-work/code-android行為測試範本/丙審-sonnet/`,純 JVM 變形在 `lab/v_*`,Android 模組在 `droid/`。

### F1 T3 主測試照抄到 Android 模組就跑不過,好壞寫法一律例外紅
引句:「這份檔替其中在電腦 JVM 上就跑得動的列放測試範本」
severity: major
blocking: 是

- 範本只在純 JVM 專案驗過,但 T3 的消費對象是 Android 專案。
- 我把 T3〈測試〉(`viewModelScenario` 版)與〈好寫法〉原樣放進 Android library 模組,跑 `testDebugUnitTest`,兩支測試都紅,而且是例外紅:
  - `RuntimeException: Method containsKey in android.os.BaseBundle not mocked`。
  - 原因是 Android 變體的 `SavedState` 就是 `android.os.Bundle`,JVM 單元測試只有 stub。
- 再開 `isReturnDefaultValues = true`,改成 `NullPointerException: ... android.os.Bundle.keySet() ... is null`,仍然不通過。
- 所以〈怎麼用〉第 5 步的「翻成斷言紅」,在 Android 專案根本走不到。
- 〈測試:複製 handle 版〉在同一個 Android 模組是正常的:好寫法綠,STATE-6 壞寫法斷言紅 `ComparisonFailure`。
- 範本完全沒提 Robolectric 或這個限制,也沒說「Android 專案預設用複製 handle 版」。
- 重現:`droid/`,依賴為 `lifecycle-viewmodel-testing:2.9.4` 加 `lifecycle-viewmodel-savedstate:2.9.4`。

### F2 API-21 只測上限,沒測「加鎖」;範本的好寫法本身就沒鎖,不加鎖的版本照綠
引句:「型錄列:API-21、API-26。真的 OkHttp/Retrofit 打本機 MockWebServer。」
severity: major
blocking: 是

- 型錄 API-21 的標準寫法含 `mutex.withLock { if (token 已被別人刷新) 用新的 else refresh() }`,後果欄寫「刷新風暴、權杖互相覆蓋」。
- 範本好寫法(`TokenAuthenticator`,只數 `priorResponse`)沒有任何鎖。
- 我在好寫法上追加一支測試:5 個執行緒並行打 401,期望 `refreshes == 1`。結果紅:`5 個並行 401 刷新了 4 次 expected:<1> but was:<4>`(`lab/v_t4_storm`)。
- 也就是照這個範本的好寫法寫的 Authenticator,正是型錄列點名的壞寫法,卻通過 `refresh_gives_up_after_three_tries`。
- 範本沒聲明這一半沒測,但矩陣把整列 API-21 掛在 T4 底下。

另一個相關變形:Authenticator 恆回 `null`、完全不刷新(`lab/v_t4_norefresh`),`refresh_gives_up_after_three_tries` 全綠。
引句:「assertEquals(401, r.getOrNull())」
這部分是 minor:測試沒有「401 之後刷新成功」的正向路徑。

### F3 DATA-72 型錄標準寫法 `String? = null` 被誤判紅
引句:「assertEquals(listOf("", ""), r.getOrThrow().map { it.name })」
severity: major
blocking: 是

- 型錄 DATA-72 的標準寫法第一個就是 `val name: String? = null`,第二個才是 `= ""`。
- 我把 `UserDto` 改成 `val name: String? = null`,解碼完全正常。
- 測試卻紅:`expected:<[, ]> but was:<[null, null]>`(`lab/v_t5_nullable`)。
- 原因是斷言把「預設值是空字串」寫死。這比「解碼不丟 MissingFieldException」多釘了一層。
- 用標準寫法一的專案照抄就誤紅。
- 建議:改成只斷言 `r.isSuccess` 與 `size == 2`,或提示兩種預設值二選一。

### F4 Turbine:「漏事件」會被 TurbineAssertionError 蓋掉,收證不算抓到
引句:「assertEquals(listOf("ab:1"), awaitItem())」
severity: minor
blocking: 否

- 「多出事件」抓得到。flatMapMerge 變形,以及會多吐一筆的變形,都在 `cancelAndConsumeRemainingEvents()` 的斷言紅(`v_a8_merge`:`expected:<[]> but was:<[Item([a:1])]>`;`v_a8_dup`:`expected:<[ab:1]> but was:<[ab:1, extra]>`)。
- 「漏事件」不算抓到。我寫了一個永遠不更新結果的 ViewModel(`v_a8_never`):
  - `awaitItem()` 等 3 秒後丟 `TurbineAssertionError: No value produced in 3s`,`assertion_failure` 判為非斷言。
  - 這與範本自己寫的「Turbine 自己的檢查…不算成斷言失敗」矛盾。
- 第 107 行 `awaitItem()` 也有同樣問題。
- 建議全程改用 `awaitEvent()` 加 `assertEquals`/`assertIs`。

### F5 T3「複製 handle 版」對 `setSavedStateProvider` 的合法寫法誤紅
引句:「private fun SavedStateHandle.afterProcessDeath() = SavedStateHandle(keys().associateWith { get<Any?>(it) })」
severity: minor
blocking: 否

- 官方 savedstate 頁(WebFetch 核對過)的非 parcelable 做法,就是 `setSavedStateProvider`。
- 我用該寫法做合法實作:`recreate()` 版全綠,複製版紅 `expected:<[kotlin]> but was:<[]>`(`v_t3_provider`、`v_t3_provider_copy`)。
- 因為複製只複製 `keys()` 裡的值,不會呼叫 provider。
- 這個版本是給舊專案的退路,範本應註明它不涵蓋 provider。

### F6 T3 在 JVM 上不驗 Bundle 型別,存不能序列化的物件照綠
引句:「斷言輸入與待處理的 id 還在」
severity: minor
blocking: 否

- 我寫了 `handle["q"] = Query(q)`,其中 `Query` 不是 Parcelable 也不是 Serializable。官方頁寫明這類值在 Android 上不能直接存。
- 兩個版本都全綠(`v_t3_nonbundle`、`v_t3_nonbundle_copy`)。
- `recreate()` 在 JVM 上並沒有真的經過 Bundle 型別檢查,只模擬了「存下來、清掉 ViewModelStore、重建」。
- 範本把它說成「程序被殺」,應補一句「不驗 Bundle 可存型別」。
- 另外官方頁還提醒 Compose 下寫入 handle 要等 Activity stop 才存,範本沒提。

### F7 FLOW-18 的假上游永不掛起,沒同步的快取版照綠
引句:「override suspend fun fetch(): Int { calls++; return 100 }」
severity: minor
blocking: 否

- 變形壞寫法:`flow { if (cached == null) cached = api.fetch(); emit(cached!!) }`,沒有同步、並行時會重複打(`v_f18_cache`)。
- `two_collectors_share_one_fetch` 全綠,因為 `fetch()` 不掛起,兩個收集者其實是依序執行。
- 型錄的壞寫法(冷流各自收)仍然紅,所以只是罕見變形。
- 建議假 API 在 `fetch()` 裡加 `delay`。

### F8 FLOW-23 與 DATA-74 的斷言過窄(罕見變形)
引句:「assertNull(r.getOrNull())」
severity: minor
blocking: 否

- FLOW-23:`firstOrNull() ?: ""` 是合理的好寫法,但被 `assertNull` 誤紅(`v_f23_goodDefault`)。
- 該測試對 `first()`、`single()`、`toList().first()` 都能抓到。

引句:「assertTrue("\"quantity\":1" in body, 」
- DATA-74:這是子字串比對。預設值 10 的 `"quantity":10` 也會讓它通過(`v_t5_q10`)。
- 建議改成比對 `"quantity":1}` 或解回物件再比。

### F9 API-21 依據網址 404
引句:「(https://square.github.io/okhttp/5.x/okhttp/okhttp3/-authenticator/)」
severity: minor
blocking: 否

- 這個網址與 4.x、`index.html` 兩個變體都回 404(WebFetch 與 curl)。
- 摘句本身是真的,在 OkHttp 原始碼 `okhttp/src/commonJvmAndroid/kotlin/okhttp3/Authenticator.kt`(`Give up, we've already failed to authenticate.`、`priorResponse`、`Returns null if the challenge cannot be satisfied`)。
- 依據網址應換成能開的連結。

### 已核對、沒發現問題的項目

- **WebFetch 抽查(5 列)**:
  - STATE-6/26 的 savedstate 頁:兩句原文都在。
  - lifecycle 2.9.0 發行說明:`recreate()` 與「KMP compatible」都在。
  - FLOW-23 的 `first()`:`Throws NoSuchElementException if the flow was empty`。
  - FLOW-24 的 SharedFlow:`the emitted value is immediately lost`,但出處是 `tryEmit` 的句子,不是 emit 的普通說明(輕微)。
  - DATA-72/73/74 的 kotlinx 設定頁:兩段引文都在。
  - API-21:摘句在,網址壞(見 F9)。
- **T4 依賴挑法**:Maven Central 的 `mockwebserver3` 只有 5.0.0-alpha.x 與 5.x,沒有 4.12.0。所以「OkHttp 4 要配 `mockwebserver` 而不是 `mockwebserver3`」成立。OkHttp 4 與 5 兩套各 3 格我實跑,結果與矩陣相同。
- **T5 版本相容**:kotlinx-serialization 1.9.0 配 Kotlin 2.2.21 在 JVM 專案編得過。1.12.0 是 Maven Central 現行版,與作者說的「編不過」方向一致,我沒另外重驗。
- **其他變形**:
  - API-8 的 flatMapMerge 與漏事件變形會紅;job 取消版、`mapLatest` 版的合法變形綠。
  - FLOW-3 的 `distinctUntilChanged` 變形會紅;`stateIn` 預設值版綠。
  - FLOW-18 的「每次存取都新建 shareIn」變形會紅;`stateIn(Lazily)` 版綠。
  - FLOW-20 的 `toList` 變形會紅;`takeWhile` 版綠。
  - FLOW-23 的 `single()` 變形、`toList().first()` 變形都紅。
  - FLOW-24 的 `tryEmit` 變形會紅;Channel 版綠。
  - STATE-10 的 `id = text` 變形會紅。
  - API-26 的「Unit 回傳」好寫法綠;try/catch 吞例外回 false 變形紅。
  - DATA-74 的 `encodeDefaults = true` 好寫法綠。
  - DATA-72 的「可空但無預設值」變形紅;DATA-73 的關掉 `coerceInputValues` 變形兩支皆紅。

總結:最嚴重是 T3 主測試在 Android 模組跑不過、API-21 的鎖沒測、DATA-72 標準寫法被誤紅,會擋 3 條。
