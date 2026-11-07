severity: major

我用作者的抽格程式把第 2 輪修補後的範本全矩陣重跑一遍(T0 到 T5),不符 0 項。T3 另在 Android library 模組(AGP 8.13.2)跑。再加約 20 個我自己寫的變形格,實跑環境是 Gradle 8.13、JDK 17。實驗目錄已用字面絕對路徑刪除,沒有改 repo。

上一輪的修補都真的修好:
- TEST-6 的快照變形斷言紅。
- CO-14 的 try/finally 好寫法綠。
- DATA-72 的 `String? = null` 綠。
- API-21 的並行 401 好寫法綠,而且「加鎖但每次都刷新」「不刷新」兩個壞變形都斷言紅。
- T3 複製 handle 版在 Android 模組跑得動:好寫法綠,STATE-6 與 STATE-26 的壞寫法都斷言紅。viewModelScenario 版在 Android 模組全部例外紅(`Method containsKey in android.os.BaseBundle not mocked`),跟範本文字一致。

審材料引了 `square.github.io/okhttp/recipes/`,我抓不到(404),所以 synchronized 是否合官方建議沒能核對(見 F4)。

**F1 新的 Turbine 讀法對「儲存要掛起」的合法寫法誤紅**
引句:「ProfileViewModel(repo).save("Ada").test {」
severity: major
blocking: 是
- 兩支新寫法(`save_emits_saving_then_saved_once`、`save_blank_name_reports_error`)沒有先推到靜止,就直接 `cancelAndConsumeRemainingEvents()`。範本自己寫著「先把虛擬時間推到靜止」,這兩支卻漏了。
- 重現:正確的 ViewModel 不動,只讓 `FakeProfileRepository.save` 多一行 `delay(100)`(真實的 repo 通常會掛起)。結果兩支都斷言紅,等於對正確程式誤紅。
- 同一份 fake 套上第 1 輪舊寫法(`awaitEvent()` 逐筆等)是綠的,所以是這次修補才引入的退步。
- 建議:取事件前先 `advanceUntilIdle()`。

**F2 API-31 只驗一輪並行,「結果永遠快取、不再重打」的壞變形照綠**
引句:「assertEquals(1, api.calls, "打了 ${api.calls} 次網路")」
severity: major
blocking: 是
- 變形:把好寫法的 `inflight?.takeIf { it.isActive } ?: …` 改成 `inflight ?: …`。這是「合併請求」被過度修正成「永久快取」。
- 重現:`concurrent_refresh_hits_network_once` 綠,整組 T1 全綠。
- 這正是 r1 原則「至少驗兩次狀態變化」沒補到的列。
- 建議:第一批 `awaitAll` 完成後再 `refresh()` 一次,斷言 `api.calls == 2`。

**F3 FLOW-23 放寬成 isNullOrEmpty 後,連「存在的使用者也回空」的壞變形都照綠**
引句:「assertTrue(r.getOrNull().isNullOrEmpty(), "查不到要回 null 或空字串,實際:${r.getOrNull()}")」
severity: minor
blocking: 否
- 重現:`name()` 恆回 `null`(完全不查),`missing_user_returns_null` 綠,T2 全綠。
- 這支測試只查 id 為 "404" 的情況,沒有正向路徑。
- 建議:加 `name("1")` 要回 "Ada"。

**F4 DATA-74 改成 intOrNull 後,quantity 被送成字串也照綠**
引句:「val quantity = Json.parseToJsonElement(body).jsonObject["quantity"]?.jsonPrimitive?.intOrNull」
severity: minor
blocking: 否
- 重現:自訂序列化器把 quantity 送成 `"quantity":"1"`,T5 三支全綠。原因是 `JsonPrimitive.intOrNull` 會把引號字串也解析成 Int。
- 這是罕見變形。
- 另外,API-21 好寫法的 synchronized 說明是「型錄的 mutex.withLock 在這裡用 synchronized」,沒有官方出處。範本把這列標成「出處不全」,但抓不到 OkHttp recipes 頁,所以沒辦法替它背書。
- 順帶:with-timeout 那頁的四句引文(API-32、CO-14)我核對過,逐字吻合。

**F5 其餘驗過、沒問題的格**
引句:「照官方「用測試值建新的 SavedStateHandle」,把第一個 handle 的內容複製成第二個 handle。」
severity: minor
blocking: 否
- 以下變形都得到預期結果:
  - TEST-6 的 `Eagerly`:綠。
  - TEST-9:新 Job 加注入的 dispatcher 的壞變形,斷言紅;`UNDISPATCHED` 的合法寫法,綠。
  - API-1:`awaitAll` 綠,`LAZY` 的壞變形斷言紅。
  - CO-14:取得後不關的壞變形,斷言紅。
  - FLOW-24:`replay=1` 與 `Channel.receiveAsFlow` 綠,`extraBufferCapacity` 的壞變形斷言紅。
  - FLOW-18:Mutex 快取與 `stateIn(Lazily)` 綠。
  - DATA-72:`explicitNulls=false` 的 `String?` 綠;`String?` 沒有預設值的壞變形斷言紅。

總結:最嚴重是 F1(新 Turbine 讀法對掛起的 `save` 誤紅)與 F2(API-31 的永久快取壞變形照綠),兩條都實跑重現,會擋 2 條。

相關路徑:
- /Users/enzo/orca/workspaces/lumos-toolchain/android-test-templates/skills/kotlin-idioms/test-templates.md
- /Users/enzo/orca/workspaces/lumos-toolchain/android-test-templates/governance/review-reports/code-android行為測試範本/r2-repair-範本.patch
