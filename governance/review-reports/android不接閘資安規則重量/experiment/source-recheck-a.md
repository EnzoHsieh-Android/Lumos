五列查完：直接支持 1 列（CO-37），部分支持 3 列（API-14、ARCH-3、UI-103），找不到 1 列（API-36），跟權威原文矛盾的 0 列。其中 API-14 雖算部分支持，但標準寫法有一半跟維護者說法衝突，要改列內容。以下逐列。

---

**API-36 錯誤對應依賴例外訊息字串**
- **判定：找不到**。權威來源裡沒有一句話說「不要比對例外訊息、要比對型別」，也沒找到 Sonar、PMD、Error Prone、IntelliJ 的對應規則頁。
- 最接近的是 Throwable 的官方參考頁（打開讀到）：https://developer.android.com/reference/java/lang/Throwable
  - getMessage：「the detail message string of this `Throwable` instance (which may be `null`).」
  - getLocalizedMessage：「Subclasses may override this method in order to produce a locale-specific message. For subclasses that do not override this method, the default implementation returns the same result as `getMessage()`.」
- 說明：官方只說訊息可能是 null、可以另外做在地化版本，間接說明訊息字串不是穩定的判斷依據。但它沒有講這個壞寫法或後果。而且依原文，跟語系有關的是 getLocalizedMessage，不是 getMessage，所以「換語系就失效」這個後果對 `e.message` 並沒有直接根據。「升版後失效」也沒有權威原文。

**API-14 async 立刻 await 等於沒並行**
- **判定：部分支持**。這是公認的壞寫法這一半有支持；標準寫法有一半跟維護者的說法衝突。
- 出處一，IntelliJ 內建檢查。我是從 IntelliJ 原始碼的訊息檔讀到的（Inspectopedia 上沒有這條的規則頁，網址會回 404）：https://github.com/JetBrains/intellij-community/blob/master/plugins/kotlin/base/resources/resources-en/messages/KotlinBundle.properties
  - 「inspection.redundant.async.display.name=Redundant 'async' call」
  - 「redundant.async.call.may.be.reduced.to.0=Redundant ''async'' call may be reduced to ''{0}''」
- 出處二，kotlinx.coroutines 議題 #1493。用 gh api 讀全文，留言者是當時協程庫的主要維護者 elizarov：https://github.com/Kotlin/kotlinx.coroutines/issues/1493
  - 「Indeed, they are not equivalent. Yes, usually `async { ... }.await()` is an error anyway.」
  - 同一串另一位留言者說：「Async invocation suggests, that there is some concurrency in this code, but there is none.」
- 說明：
  - **支持的部分**：IntelliJ 把它當冗餘寫法、建議改成 withContext，維護者也說這通常是錯的。
  - **衝突的部分**：壞寫法第二例 `scope.async(ctx){…}.await()` 用的是另一個 scope，維護者明說它跟 withContext「not equivalent」（取消行為不同），所以那一例的標準寫法不能無條件寫成改 withContext。
  - **其他**：議題留言不在你列的權威來源範圍內，只能算「近權威」。列裡寫的「detekt SequentialAsyncAwait」，我在 detekt repo 原始碼搜不到這個名字，也沒找到規則頁（之後 GitHub 額度用完，沒能再搜第二次）。

**ARCH-3 導航點擊沒擋生命週期，連點兩下崩潰**
- **判定：部分支持**。Compose 的標準寫法和崩潰的例外都有原文；連點兩下會造成這兩個後果，以及 View 的寫法，沒有原文。
- 出處一，dropUnlessResumed 的 KDoc（打開讀到）：https://developer.android.com/reference/kotlin/androidx/lifecycle/compose/dropUnlessResumed.composable
  - 「For Navigation users, it's recommended to safeguard navigate methods when using them while a composable is in transition as a result of navigation.」
- 出處二，Lifecycle 2.8.0-alpha02 版本說明（打開讀到）：https://developer.android.com/jetpack/androidx/releases/lifecycle
  - 「this can be used with Navigation Compose to avoid handling click events after a transition to another screen has already begun: `onClick: () -&gt; Unit = dropUnlessResumed { navController.navigate(NEW_SCREEN) }`」
- 出處三，NavController 參考頁（打開讀到）：https://developer.android.com/reference/androidx/navigation/NavController
  - navigate(resId) 的例外說明：「IllegalArgumentException — if the desired destination cannot be found from the current destination」
- 說明：
  - **支持的部分**：Compose 用 `dropUnlessResumed` 包 navigate 是官方建議；用 action id 導航時，目前所在頁找不到目的地會丟 IllegalArgumentException 有原文。
  - **缺的部分**：沒有官方原文把「連點兩下」直接連到這兩個後果，「堆疊重複頁」也沒有原文。View 寫法「先比對 `currentDestination?.id`」只出現在社群文章，官方沒寫。
  - **補一點**：IllegalArgumentException 是 action id 的寫法才會發生；Compose 用路由導航時，連點比較可能是推兩次同一頁。這一列把兩種情況混在一起寫。

**UI-103 預覽沒包主題**
- **判定：部分支持**。標準寫法（預覽外層包主題）有官方範例與 API 支持；「預覽外觀與實際不符」這個後果沒有原文。
- 出處一，PreviewWrapperProvider 參考頁（打開讀到）：https://developer.android.com/reference/kotlin/androidx/compose/ui/tooling/preview/PreviewWrapperProvider
  - 「Implementations of this interface allow developers to wrap the content of a `Preview` to provide specific environments, themes, or containers (such as a Remote Compose) without requiring repetitive code in every preview function.」
- 出處二，PreviewWrapper 參考頁（打開讀到）：https://developer.android.com/reference/kotlin/androidx/compose/ui/tooling/preview/PreviewWrapper
  - 「Android Studio looks for this annotation to determine if the preview content should be wrapped in a custom container (e.g., for Remote Compose or custom theming).」
- 出處三，Compose Basics 官方 codelab（打開讀到）：https://developer.android.com/codelabs/jetpack-compose-basics
  - 「Because `BasicsCodelabTheme` wraps `MaterialTheme` internally, `MyApp` is styled with the properties defined in the theme.」
- 說明：官方範例確實在預覽外包主題，這組 API 註明從 Compose UI 1.11.0 起提供，也就是把「每個預覽包主題」改成一個註解統一套用。預覽工具主頁（https://developer.android.com/develop/ui/compose/tooling/previews ）只在範例裡用了 `MaterialTheme { … }`，沒有任何一句叫你一定要包。建議在列裡補上 PreviewWrapper 這個新寫法。

**CO-37 Mutex 重入**
- **判定：直接支持**（只限「不可重入 → 同一協程第二次 lock 會一直等」這個核心主張）。
- 出處，Mutex 的 KDoc（打開讀到）：https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-mutex/
  - 「It is non-reentrant, that is invoking lock even from the same thread/coroutine that currently holds the lock still suspends the invoker.」
- 說明：原文明講同一協程再次 lock 會被暫停；鎖在自己手上，沒有別人能解開，所以就是死鎖（「deadlock」這個詞是推論，原文沒寫）。標準寫法「拆成不加鎖的 `helperLocked()`」官方沒寫，是社群慣用做法。

---

我沒有建任何臨時目錄或檔案，也沒動任何 repo。另外 GitHub API 額度在查 API-14 時用完了，之後沒再呼叫。

**各判定列數**：直接支持 1（CO-37）／部分支持 3（API-14、ARCH-3、UI-103）／找不到 1（API-36）／跟權威原文矛盾 0。API-14 的 `scope.async(ctx){…}.await()` 改成 withContext 這一半跟維護者說法衝突，算部分矛盾。
