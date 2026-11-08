**結論**:5 列裡沒有一列被權威原文完整撐住;FLOW-14 最接近,TEST-31 跟 Google 官方 codelab 的建議衝突。以下每段都是我親自打開頁面(WebFetch 或用 `gh api` 抓官方 repo 原始檔)讀到的,不是只看搜尋摘要。

---

**FLOW-14:asFlow() 轉出的迴圈不檢查取消**
- **判定:直接支持**(壞寫法、標準寫法、主要後果都有原文;「寫出過期結果」那半句沒有原文明講)
- 出處 1:kotlinx.coroutines 官方 repo 1.9.0 版的 `docs/topics/flow.md`,〈Flow cancellation checks〉與〈Making busy flow cancellable〉兩節(用 `gh api repos/Kotlin/kotlinx.coroutines/contents/docs/topics/flow.md?ref=1.9.0` 讀的)
  - "However, most other flow operators do not do additional cancellation checks on their own for performance reasons. For example, if you use [IntRange.asFlow] extension to write the same busy loop and don't suspend anywhere, then there are no checks for cancellation"
  - "All numbers from 1 to 5 are collected and cancellation gets detected only before return from `runBlocking`"
  - "In the case where you have a busy loop with coroutines you must explicitly check for cancellation. You can add `.onEach { currentCoroutineContext().ensureActive() }`, but there is a ready-to-use [cancellable] operator provided to do that"
- 出處 2:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/cancellable.html
  - "Returns a flow which checks cancellation status on each emission and throws the corresponding cancellation cause if flow collector was cancelled. Note that flow builder and all implementations of SharedFlow are cancellable by default."
- 說明:原文明講 `asFlow()` 不檢查取消、會跑完整個集合,也給了 `.cancellable()` 或 `ensureActive()` 的寫法。
- **注意**:主線 repo 已經沒有 `docs/topics/flow.md`;目前線上的 kotlinlang.org/docs/coroutines-flow.html 改寫過,我在裡面找不到這兩節。引用時要釘 1.9.0 版的原始檔網址:https://github.com/Kotlin/kotlinx.coroutines/blob/1.9.0/docs/topics/flow.md 。型錄現有的 `flow.html` 連結只寫了 "Emissions from flow builder are cancellable by default — each call to emit also calls ensureActive.",沒提到 `asFlow`。

**STATE-9:WhileSubscribed 沒給停止延遲**
- **判定:部分支持**
  - 有原文的半邊:預設延遲是 0(收集者一走就停),官方範例與 codelab 都寫 5 秒。
  - 缺的半邊:沒有權威原文把「旋轉時上游停掉再重啟、閃載入畫面」直接歸因到延遲是 0。我能找到講 5 秒和 ANR 或旋轉有關係的,只有 Kotlin Slack 的討論,不算出處。
- 出處 1:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-sharing-started/-companion/-while-subscribed.html
  - "stopTimeoutMillis — configures a delay (in milliseconds) between the disappearance of the last subscriber and the stopping of the sharing coroutine. It defaults to zero (stop immediately)."
- 出處 2:https://developer.android.com/topic/architecture/ui-layer/state-production
  - 範例程式寫的是 `started = SharingStarted.WhileSubscribed(5_000)`。正文只說 "Use `SharingStarted.WhileSubscribed` if the pipeline needs to be active only when the UI is visible…",沒解釋為什麼是 5_000。
- 出處 3:https://developer.android.com/codelabs/basic-android-kotlin-compose-update-data-room
  - "To configure a delay (in milliseconds) between the disappearance of the last subscriber and the stopping of the sharing coroutine, pass in the `TIMEOUT_MILLIS` to the `SharingStarted.WhileSubscribed()` method."
  - "Lifecycle events like configuration changes, for example rotating the device, causes the activity to be recreated. This causes recomposition and collecting from your `Flow` all over again."
  - 程式裡是 `private const val TIMEOUT_MILLIS = 5_000L`。
- 說明:官方支持「預設立刻停」和「標準寫法給 5 秒」。codelab 講了旋轉會重新收集,但沒有直接說延遲就是為了這個。

**TEST-16:正式碼直接讀系統時鐘**
- **判定:部分支持**
  - 有原文的半邊:不要直接用系統時鐘、改成注入 Clock;測試端的 `testScheduler.timeSource` 也有。
  - 缺的半邊:沒點名 `System.currentTimeMillis()`、`Instant.now()`、`SystemClock.elapsedRealtime()`;後果只講到「測試才能寫成確定的」,沒講「跨日、跨時區才出錯」。
- 出處 1:https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.time/-clock/
  - "It is not recommended to use [Clock.System] directly in the implementation. Instead, you can pass a [Clock] explicitly to the necessary functions or classes. This way, tests can be written deterministically by providing custom [Clock] implementations to the system under test."
- 出處 2:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-coroutine-scheduler/time-source.html
  - "Returns the TimeSource representation of the virtual time of this scheduler."
- 說明:Kotlin 標準庫官方明講「實作裡不要直接用系統時鐘、要從外面傳 Clock 進來,測試才能寫成確定的」。
- 補充:kotlinx-datetime 的 Clock 頁我試了兩個網址都是 404,沒讀到。

**TEST-33:Robolectric 測試依賴未設定的 SDK 或 looper 模式**
- **判定:部分支持**
  - looper 這半邊有原文:舊的 LEGACY 模式已棄用、要用 PAUSED,也要手動 `idle()`。
  - SDK 這半邊沒有原文支持:官方說預設照模組的 `targetSdk` 跑,沒有建議固定 `@Config(sdk=…)`。「升級 Robolectric 就壞」也找不到原文。
- 出處 1:https://robolectric.org/blog/2019/06/04/paused-looper/
  - "Tasks posted to the main Looper are not automatically executed inline."
  - "you may need to insert shadowOf(getMainLooper()).idle() calls to your test to drain the main Looper."
  - "Robolectric will warn users if a test fails with unexecuted tasks in the main Looper queue."
- 出處 2:https://robolectric.org/javadoc/latest/org/robolectric/annotation/LooperMode.Mode.html
  - LEGACY 標為 "Deprecated.",並寫 "use LooperMode.PAUSED. LEGACY mode is not supported on Android SDKs &gt; Baklava"
- 出處 3:https://robolectric.org/configuring/
  - "By default, Robolectric will run your code against the `targetSdk` specified in your module's…"
  - "If you want to test your code under a different SDK, you can specify the desired SDK(s)"
- 說明:「主執行緒排的工作沒跑、要 idle」和「LEGACY 已棄用」有原文。官方把「指定 SDK」寫成想測別的版本時才用,不是必設,所以這列的 SDK 部分建議刪掉或改寫。

**TEST-31:用顯示文字或索引找節點**
- **判定:跟權威原文矛盾**(只有「不要靠位置或編號」那半邊算部分支持)
- 出處 1:https://developer.android.com/codelabs/jetpack-compose-testing
  - "Warning: Composables don't have IDs and you can't use the Node numbers shown in the tree to match them. If matching a node with its semantics properties is impractical or impossible, you can use the testTag modifier with the hasTestTag matcher as a last resort."
  - "it's a good idea to avoid using broad finders alone (such as `hasText`) which might fail in larger tests (when other instances of the text might be found)."
- 出處 2:https://developer.android.com/develop/ui/compose/testing
  - 官方的典型測試範例直接寫 `composeTestRule.onNodeWithText("Continue").performClick()`。
- 出處 3:https://developer.android.com/develop/ui/compose/testing/apis
  - 把 `onNodeWithText`、`onNodeWithContentDescription` 列為 "convenience finders for the most common searches",沒有說要避免。
- 說明:
  - 官方的優先順序是:先用文字、內容描述這類語意屬性,真的做不到才用 testTag(原文說是 "last resort",最後手段)。這跟本列「testTag 是標準寫法、用文字找是壞寫法」相反。
  - 支持的只有兩點:不能靠節點編號找,單用 `hasText` 這種寬鬆比對可能撞到別的同字節點。
  - 「改文案或語系就壞」這個後果沒有官方原文。
  - 建議把這列改成「別用索引或寬鬆的單一條件找節點」,不要寫「用文字找是錯的」。

---

**判定統計**:直接支持 1(FLOW-14)/ 部分支持 3(STATE-9、TEST-16、TEST-33)/ 找不到 0 / 跟權威原文矛盾 1(TEST-31)

我只讀資料,沒改任何檔案,沒動 git,也沒建任何臨時目錄。
