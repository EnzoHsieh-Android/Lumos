severity: major

## Finding 1
severity: major
blocking: 是

型錄列:TEST-16(正式碼直接讀系統時鐘),``file: `skills/kotlin-idioms/checks-catalog.md:661` ``

主張:壞寫法是 `System.currentTimeMillis()`、`Instant.now()`、`SystemClock.elapsedRealtime()`;標準寫法是「注入 Clock/TimeSource,測試用 testScheduler.timeSource」;來源欄說支持規則本身。

原文網址:https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.time/-clock/

引句:「It is not recommended to use Clock.System directly in the implementation.」

原文網址:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-coroutine-scheduler/time-source.html

引句:「Returns the TimeSource representation of the virtual time of this scheduler.」

問題:
- Clock 頁只點名 `kotlin.time.Clock.System`。型錄列的壞寫法三個 API 一個都不是它:`System.currentTimeMillis()` 是 JDK、`Instant.now()` 是 java.time、`SystemClock.elapsedRealtime()` 是 Android 的單調時鐘。頁面沒說這三個不好。
- 規則實際抓得更廣:`System.nanoTime()`、`LocalDate.now()`、`LocalDateTime.now()`、`ZonedDateTime.now()`、`uptimeMillis()`、`Date()` 都抓。這些型錄列根本沒寫,原文更沒提。``file: `configs/ast-grep/kotlin-android/rules-unwired/testing.yml:9-17` ``
- `timeSource` 頁只說它回傳虛擬時間的 TimeSource。「測試用 testScheduler.timeSource」是 API 存在,頁面沒說該這樣換。
- 「不建議直接用時鐘、改成傳入 Clock」這個原則有權威出處。但規則判定「壞寫法」的對象是另一批 API,出處只涵蓋 `Clock.System`。
- 建議:要嘛把規則和型錄壞寫法收窄到 `Clock.System.now()`,要嘛為 JDK 與 Android 那幾個 API 另找權威出處。

## Finding 2
severity: major
blocking: 是

型錄列:TEST-31(用索引找節點,`kt-compose-test-node-by-index`),``file: `skills/kotlin-idioms/checks-catalog.md:676` ``

主張:`onAllNodes(…)[2]`、`.get(2)` 是壞寫法,後果是「清單順序一變就挑錯節點」。前一手判定為「索引那半直接支持」。

原文網址:https://developer.android.com/codelabs/jetpack-compose-testing

引句:「Composables don't have IDs and you can't use the Node numbers shown in the tree to match them.」

問題:
- 這句講的是語意樹印出來的 Node 編號(Node #1 這類除錯輸出),意思是不能拿那個編號當比對條件。它沒有談 `onAllNodes(...)[i]` 這種對 `SemanticsNodeInteractionCollection` 取索引的寫法。
- codelab 全文我找不到 `onAllNodes`、`[0]`、`get(index)`、`onFirst` 任何一個。型錄列和規則訊息寫的「清單順序一變就挑錯」是推論,原文沒講。``file: `configs/ast-grep/kotlin-android/rules-unwired/testing.yml:42` ``
- 我另外打開了 Compose 測試的 common-patterns 頁和 cheatsheet 頁,沒找到把索引寫法判為壞的句子。cheatsheet 只是圖片,我讀不到內容。
- 原文真正支持的是標準寫法那半:先用語意屬性,對不上時 testTag 是 last resort(「as a last resort」)。
- 這條規則是以「索引=壞」為判定依據,出處卻沒有這句。要保留就得補一個真有談索引的權威出處,否則按現有出處該降為只有標準寫法的建議。

## Finding 3
severity: minor
blocking: 否

型錄列:STATE-9(WhileSubscribed 沒給停止延遲),``file: `skills/kotlin-idioms/checks-catalog.md:254` ``

主張:後果是「旋轉螢幕重建畫面會重新收集,上游跟著停掉又重啟」;標準寫法是 `WhileSubscribed(5_000)`。

原文網址:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-sharing-started/-companion/-while-subscribed.html

引句:「It defaults to zero (stop immediately).」

原文網址:https://developer.android.com/codelabs/basic-android-kotlin-compose-update-data-room

引句:「Lifecycle events like configuration changes, for example rotating the device, causes the activity to be recreated.」

問題:
- 兩句各自成立。預設 0 和旋轉重建合在一起,可以推出「上游停掉又重啟」,但推論要靠人接起來,沒有一句原文直接寫。
- codelab 只出現 `TIMEOUT_MILLIS = 5_000L` 這個常數,沒說 5 秒是為了擋旋轉。
- state-production 頁(我重新打開讀過)只示範 `WhileSubscribed(5_000)`,同樣沒解釋 5 秒的用途。
- 「5_000 就是對的值」是官方範例的慣例,不是官方規定。型錄的標準寫法寫成唯一解,語氣比原文強。
- 建議把後果改成原文兩句的並列,標準寫法註明「官方範例用 5 秒」。

## Finding 4
severity: minor
blocking: 否

型錄列:ARCH-3(Compose 導航點擊沒擋生命週期),``file: `skills/kotlin-idioms/checks-catalog.md:447` ``

主張:後果是「重複導航;用 action id 導航時,目前所在頁找不到目的地會丟 IllegalArgumentException」;形狀判準含「或 currentDestination 判斷」。

原文網址:https://developer.android.com/reference/kotlin/androidx/lifecycle/compose/dropUnlessResumed.composable

引句:「For Navigation users, it's recommended to safeguard navigate methods when using them while a composable is in transition as a result of navigation.」

原文網址:https://developer.android.com/reference/androidx/navigation/NavController

引句:「if the desired destination cannot be found from the current destination」

問題:
- 「轉場期間建議用 dropUnlessResumed 包 navigate」有直接原文,Compose 那半成立。
- 把「重複點擊」接到「IllegalArgumentException」是推論。NavController 的 Throws 只說「找不到目的地」,沒說這是轉場期間重複點擊造成的。
- 「重複導航」這個字面也不在 KDoc 裡。
- 形狀判準裡「currentDestination 判斷」是社群慣例,兩頁都沒提。
- 影響不大,規則是 hint。建議後果只寫原文有的部分,再把例外那句掛上「官方 API 參考:找不到目的地時」。

## Finding 5
severity: minor
blocking: 否

型錄列:FLOW-14(asFlow() 轉出的迴圈不檢查取消),``file: `skills/kotlin-idioms/checks-catalog.md:222` ``

主張:壞例 `(1..1_000_000).asFlow().collect { heavy(it) }`,後果「收集端取消後仍跑完整個集合」。

原文網址:https://github.com/Kotlin/kotlinx.coroutines/blob/1.9.0/docs/topics/flow.md

引句:「However, most other flow operators do not do additional cancellation checks on their own for performance reasons.」

引句:「In the case where you have a busy loop with coroutines you must explicitly check for cancellation.」

問題:
- 原文的範例是 `IntRange.asFlow` 配一個從不暫停的 collect(busy loop),取消要等到結束才被發現。
- 型錄後果寫得比原文寬。如果 `heavy(it)` 是會暫停的函式,collect 裡本來就會檢查取消,不會「跑完整個集合」。原文只保證不暫停的迴圈。
- 「為了效能」那句講的是「大多數其他 flow 運算子」,不是單講 `asFlow`。
- 型錄已用「(誤報多)」自承,規則只是 hint。建議把壞例註明 `heavy` 為不暫停的運算。

## 圖譜鏡頭(固定席 Systems/kotlin規則包)
判「不影響」。這份設計只動 `rules-unwired/` 不接閘目錄、型錄文字和出處補查的紀錄,沒有改任何會擋的規則。該節點計劃連結資料也顯示掛 0 條合約、0 行 KEY,沒有可被破壞的合約。

## 逐列核對結果

- FLOW-14:問題見 Finding 5。1.9.0 `flow.md` 找得到取消檢查那段,來源可靠。
- CO-37:Mutex KDoc 原文為「It is non-reentrant, that is invoking lock even from the same thread/coroutine that currently holds the lock still suspends the invoker.」,「不可重入、同協程再鎖會一直暫停」直接成立。「鎖在自己手上、沒人能解開」是合理的白話推論。「拆成不加鎖的內部函式」是慣用法,原文沒講,型錄只放在標準寫法欄,沒寫成官方要求。這列沒問題。
- TEST-16:問題見 Finding 1。
- STATE-9:問題見 Finding 3。KDoc 預設 0 與官方範例給 5 秒都屬實。
- TEST-33:LooperMode.Mode javadoc 原文為「Deprecated. use LooperMode.PAUSED. LEGACY mode is not supported on Android SDKs &gt; Baklava」,另有「The default UNPAUSED state will execute tasks posted to a Looper inline synchronously.」與 PAUSED 的「must be explicitly executed via ShadowLooper APIs」。「LEGACY 已棄用、新 SDK 不支援、PAUSED 要明確排空」都有直接原文,規則訊息的「會立即執行主執行緒工作、跟真機不同」也對得上。一點小保留:`ActivityController.setup()` 等 API 會自動 idle,「明確 idle()」不是每個情境都需要,原文沒說「預設」二字,這列的來源欄也沒補這一點。這列沒有出處不支持的主張。
- ARCH-3:問題見 Finding 4。
- API-14:IntelliJ 的字串表(`KotlinBundle.properties`)確有 `redundant.async.call.may.be.reduced.to.0=Redundant ''async'' call may be reduced to ''{0}''`,同 scope 那半有 IDE 內建檢查支持。我只讀到訊息字串,沒讀到該檢查的說明頁,檢查的觸發條件(是否涵蓋 `async(ctx){}`)沒親眼驗證。議題 #1493 我讀到 elizarov 的話:「Indeed, they are not equivalent. Yes, usually `async { ... }.await()` is an error anyway.」這是官方 repo 的議題留言,維護者的話,當佐證用。型錄列已把「別的 scope 的 async」排除在外,與維護者所說「不等價」一致。後果「讀者以為有並行」原文沒寫,只是口語化敘述,不是判定依據。這列保留站得住。
- TEST-31 索引那半:問題見 Finding 2。
- TEST-31 用顯示文字找那半(已移除):移除站得住。codelab 同一段把「用語意屬性比對」列為首選,testTag 才是 last resort,等於反對規則的方向。型錄 ``file: `skills/kotlin-idioms/checks-catalog.md:676` `` 的形狀欄仍寫著 `onNodeWithText("中文字面")`,與「該規則已移出」不一致,是型錄的殘留字樣。
- UI-103(已移除):移除站得住。我讀了官方 previews 頁全文,沒有一句要求預覽包主題。範例有包的(`MaterialTheme { Surface { … } }`)和沒包的(`Text("Hello World")`)並存。我沒另外打開 `PreviewWrapper` 頁,那頁前一手說只是統一包裝的 API。
- API-36(已移除):我沒有再做額外搜尋,沒親自找到任何權威來源。移除是「前一手與我都沒找到」,不是「確定不存在」。要補強的話應該先搜 Sonar 規則庫與 detekt 規則,再下定論。

建過的路徑:無(沒有在 `/tmp/lumos-seat-work/android不接閘資安規則重量/出處二-sonnet/` 底下建任何東西,也沒改 repo 任何檔案)。

最高等級 major;blocking 2 條
