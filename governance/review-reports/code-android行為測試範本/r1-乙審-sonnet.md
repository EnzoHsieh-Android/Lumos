severity: major

我把 T0、T1 組成純 JVM 專案實跑,另寫了 13 個變形,沒有改 repo。實跑環境是 Gradle 8.13、JDK 17、coroutines 1.10.2。實驗目錄已用字面絕對路徑刪除。

**F1 TEST-6 的測試對「score 只取一次快照、不跟著上游」的變形照綠(假綠)**
severity: major
blocking: 是
引句:「assertEquals(42, vm.score.value)」
- 型錄 `TEST-6` 的壞寫法是「stateIn 沒接上游」。範本只驗「完全沒接」的版本。
- 變形:`val score = flow { emit(repo.scores.first()) }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)`。這是接了上游,但只取第一個值,之後不再跟隨。
- 重現:對 `ProfileViewModelTest` 實跑,`score_follows_repository_while_collected` 是綠的,6 個測試全綠。
- 原因:測試先 `backgroundScope.launch(Unconfined){collect}`,之後才 `repo.scores.value = 42`。stateIn 的上游工作排在 Standard 的 Main 上,要到 `advanceUntilIdle()` 才啟動,所以 `first()` 此時剛好拿到 42。
- 測試名稱叫「follows」,卻沒有收集開始之後再改第二次值,所以測不出「不跟隨」。
- 建議:收集啟動並 `runCurrent()` 之後,先設 42 並斷言,再設 43 並斷言。

**F2 CO-14 的測試把「逾時要回傳 true」寫死,型錄的第二種標準寫法會被誤紅**
severity: major
blocking: 是
引句:「assertEquals(true, r.getOrNull(), "send() 結果:$r")」
- 型錄 `CO-14` 標準寫法有兩種:資源在 `withTimeout` 外取得並 `use`,或「區塊內 `try { … } finally { r.close() }`」。
- 變形(第二種):`withTimeoutOrNull(1_000){ val c = pool.open(); try{ c.write(report); true } finally { c.close() } } ?: false`。
- 重現:`timeout_after_open_still_closes_connection` 紅,訊息是 `send() 結果:Success(false) expected:<true> but was:<false>`。
- 同一個測試裡「連線有沒有關」那條斷言是過的,連線確實關了。誤紅來自第二條斷言,它要求逾時後仍然回傳成功。
- 這等於把唯一的實作形狀(open 放在逾時外)寫進測試,而不是只檢查洩漏。
- 建議:拿掉對 `true` 的斷言,或讓範本說明「逾時時是否仍回成功」要由專案表態。
- 對照:壞變形 `withTimeoutOrNull(1000){pool.open()}` 另包一層函式,測試正確紅(`有連線沒關:[conn1(closed=false)]`)。

**F3 型錄 TEST-18 的標準寫法「結尾 expectNoEvents()」在範本的有限流上會誤紅,範本沒警告**
severity: minor
blocking: 否
引句:「Turbine 自己的檢查(`awaitComplete()`、`awaitError()`、`expectNoEvents()`、區塊結束時的 Unconsumed events)失敗時丟 `app.cash.turbine.TurbineAssertionError`」
- 實跑:對正確的 `save("Ada")` 先 `awaitItem()` 兩次再 `expectNoEvents()`,紅,訊息是 `TurbineAssertionError: Expected no events but found Complete`。
- 有限的冷流會多一個 `Complete` 事件,照型錄抄寫法的人會在正確程式上被誤紅。
- 範本只在 T0 解釋了為什麼用 `awaitEvent()`,沒把「有限流不能用 expectNoEvents」寫成坑。
- 型錄 `TEST-18` 在 `checks-catalog.md:597`;Turbine README 沒提到 `expectNoEvents`,所以也沒有出處可核對。

**F4 TEST-9 對「自建 scope 但用 Dispatchers.Main」的變形照綠**
severity: minor
blocking: 否
引句:「class Uploader(scope: CoroutineScope, private val api: UploadApi) {」
- 變形:`CoroutineScope(SupervisorJob() + Dispatchers.Main)`。測試規則已把 Main 換成共用排程器,所以 `upload_runs_in_injected_scope` 綠。
- 這是不採用注入 scope 的程式,測試抓不到。型錄壞例寫的是「用真 dispatcher」,Main 在正式環境確實是真的,但在測試裡被替換了,所以算罕見變形。
- 對照:`GlobalScope.launch(Dispatchers.IO)` 的變形有被抓到,斷言紅是 `expected:<[a.jpg]> but was:<[]>`。

**F5 API-4 依據的摘句在原頁找不到**
severity: minor
blocking: 否
引句:「A failure of a child does not cause the supervisor job to fail and does not affect its other children」
- 我抓了 https://kotlinlang.org/docs/exception-handling.html,頁面沒有這句逐字。
- 最接近的是「a failure or cancellation of a child does not propagate to the supervisor job or its other children」。意思相同,但引號內不是原文。

**F6 API-32 與 CO-14 的依據摘句無法複驗,且是兩條摘句併在同一個網址上**
severity: minor
blocking: 否
引句:「原文無法再開頁複驗,以本組實跑當實證」
- 我抓 https://kotlinlang.org/docs/cancellation-and-timeouts.html 兩次,內容都是空的,和作者一樣核不到。
- 這兩句帶引號的摘句至今沒有任何人核對過原文。

**F7 其餘依據核對與無問題的變形**
severity: minor
blocking: 否
引句:「Concurrent invocations of resume methods lead to a IllegalStateException」
- 已核對且摘句逐字吻合:
  - android coroutines/test 頁的 `advanceUntilIdle`、「doesn't mean that it'll run them to completion eagerly」、「replace real dispatchers with instances of TestDispatchers」、「automatically skip any delays」、「only be one scheduler instance」。
  - android flow/test 頁的 backgroundScope、「at least one collector」、「treating StateFlow as a data holder」。
  - Turbine README 的 Unconsumed events 句。
  - produce 頁的 lifecycle 句。
  - cancellable-continuation 頁的 Concurrent 句。
  - API-34 備註已寫明頁面沒有依序 resume 兩次的說法,這點作者自己承認了。
- 範本的協程寫法與官方一致:`MainDispatcherRule` 先宣告並明傳 Standard、`backgroundScope` 配 `UnconfinedTestDispatcher(testScheduler)`、`runCurrent()` 推背景工作。官方頁面同樣要求「先建立 MainDispatcherRule 屬性」。我沒看到不穩的時序。
- 其餘 9 個變形的實跑結果(沒有列為發現):
  - API-1 的 `async{}.await()` 依序變形,紅 `expected:<1000> but was:<2000>`。
  - API-31 的 mutex 串行變形,紅 `打了 3 次網路`。
  - API-32 的重拋 `CancellationException` 變形,紅 `but was:<Loading>`。
  - TEST-19 的吞錯並發 `Saved` 變形,紅 `實際:Item(Saved)`。
  - FLOW-29 的 `receiveCatching` 變形和 `for` 加 `break` 變形,都紅 `firstPage() 沒結束`。
  - API-32 的 catch `TimeoutCancellationException` 好寫法、API-10 的 `submitting` 旗標好寫法、FLOW-29 的 `receive()` 加 `cancel()` 好寫法,都正確綠。
- 消費專案編譯風險:`awaitEvent()`、`backgroundScope`、`runTest(timeout=)` 需要 Turbine 1.x 與 coroutines 1.7 以上,範本開頭已要求版本對齊。`data object` 需要 Kotlin 1.9 以上,在舊專案會編不過,範本沒寫這個前提(未實跑,僅判讀)。

總結:最嚴重是 F1(TEST-6 對「只取一次快照」假綠)與 F2(CO-14 把「逾時要回 true」寫死,誤紅型錄的第二種標準寫法),兩條實跑重現,會擋 2 條。
