severity: major

審查範圍:coroutines.yml、data.yml、flow.yml、perf.yml 的 ast-grep 規則。我用規則包原樣的 sgconfig 掃一份自寫的 Kotlin 片段,下列問題都實跑重現。臨時目錄已刪。

重現指令(下列每條共用):
`/Users/enzo/lumos-scratch/android-checks/venv/bin/ast-grep scan --config /Users/enzo/orca/workspaces/lumos-toolchain/shearwater/configs/ast-grep/kotlin-android/sgconfig.yml --json=stream <檔>`

**1. kt-withcontext-in-flow 把正確寫法擋成 error**

引句:「pattern: withContext($$$)」
severity: major
blocking: 是

規則只要 `flow { }` 裡出現 `withContext` 就報。真正違規的是「emit 在 withContext 裡面」。型錄 FLOW-4 的壞例是 `flow { withContext(IO) { emit(load()) } }`。`flow { emit(withContext(IO) { load() }) }` 或 `val x = withContext(IO){…}; emit(x)` 是合法的:emit 在 flow 自己的協程裡,不會觸發 invariant 例外。

- 片段:`fun g() = flow { emit(withContext(Dispatchers.IO) { load() }) }`
- 輸出:`A.kt 3 kt-withcontext-in-flow error`
- 修法:規則要求 `emit(...)` 在 `withContext` 的 lambda 內才報。
- 另一個漏報:`flow<Int> { … }` 帶型別參數的長相抓不到(第 2 行沒報,minor)。

**2. 測試程式碼沒排除,官方測試寫法被 error 擋下**

引句:「pattern: $B.allowMainThreadQueries()」
severity: major
blocking: 是

Room 官方測試寫法 `Room.inMemoryDatabaseBuilder(...).allowMainThreadQueries().build()` 被 error 擋。DataStore 官方測試寫法 `PreferenceDataStoreFactory.create(scope = testScope) { tmp.newFile(...) }` 在測試類別裡也被 error 擋。這兩條規則都沒有 `ignores`。同一份 diff 裡別的規則(PERF-4、DATA-71)已經排除測試路徑,所以這是漏掉,不是刻意。

- 片段:`src/test/k/B.kt`
- 輸出:`src/test/k/B.kt 4 kt-room-main-thread-queries error`、`src/test/k/B.kt 5 kt-datastore-not-singleton error`
- 修法:兩條都加 `ignores: ['**/src/test*/**', '**/src/androidTest*/**']`。

**3. kt-datastore-not-singleton 擋 Hilt 的 DataStore 提供者**

引句:「pattern: PreferenceDataStoreFactory.create { $$$ }」
severity: major
blocking: 是

`@Module` 的 `companion object` 裡的 `@Provides @Singleton` 提供者是標準 DI 寫法,也是這條規則的 message 自己建議的做法(「注入單例」)。規則只排除 `object_declaration`,而 `companion_object` 是另一種節點,所以被擋。`@Module class` 裡的 `@Provides @Singleton` 函式同樣被擋。

- 片段:`interface DsModule { companion object { @Provides @Singleton fun provideDs(...) = PreferenceDataStoreFactory.create {…} } }`
- 輸出:`C.kt 8 kt-datastore-not-singleton error`、`C.kt 16 kt-datastore-not-singleton error`
- 修法:`not` 補上 `companion_object` 與 `@Provides`/`@Singleton` 函式。

**4. kt-sql-string-concat 擋掉無法綁參數的 SQL**

引句:「message: '[DATA-24]SQL 字串直接串接或內插變數,有注入風險;改用 ? 綁定參數」
severity: major
blocking: 是

- `db.execSQL("PRAGMA user_version = $version")`、`db.execSQL("DROP TABLE IF EXISTS $tableName")` 被 error 擋。這兩種語句 SQLite 不能用 `?` 綁定,message 教的修法做不到。
- `apollo.query("search $term")` 也被擋。`$D.query($$$)` 對任何有 `query` 方法的物件都成立(GraphQL、搜尋客戶端等),不限 SQLiteDatabase。
- 輸出:`D.kt 18 / 19 / 20 kt-sql-string-concat error`
- 修法:`query` 的接收者要限縮到 DB 類(或拿掉 `query`),並排除 PRAGMA 與 DDL。

**5. kt-vm-channel-event 的 constraints 沒套到 Channel**

引句:「regex: (Event|Effect|Command|Navigation|Nav|Message|Toast|Snackbar)」
severity: major
blocking: 是

constraints 只約束 `$T`(`MutableSharedFlow<$T>`)。`Channel<$CT>`、`Channel($$$)`、`$C.receiveAsFlow()` 都沒有約束,所以 ViewModel 裡任何 Channel 都報,包括拿來當工作佇列的 `Channel<Int>`。另外 `Message` 這個字太寬:`MutableSharedFlow<ChatMessage>` 是資料流,不是一次性事件,也被報。

- 輸出:`D.kt 3`(`Channel<Int>`)、`D.kt 4`(`MutableSharedFlow<ChatMessage>`)都是 `kt-vm-channel-event warning`
- 修法:把 constraint 一併套到 `$CT`,並收窄「Message」。

**6. kt-worker-retry-unbounded 不認「先擋後回」的寫法**

引句:「Result.retry() 沒看 runAttemptCount,永久錯誤也一直重試」
severity: major
blocking: 是

規則只認 `Result.retry()` 在含 `runAttemptCount` 的 if/when 之內。下面這種早退寫法完全符合型錄 DATA-36 的標準寫法,也被報:

```
if (runAttemptCount >= 3) return Result.failure()
return try { sync(); Result.success() } catch (e: IOException) { Result.retry() }
```

- 輸出:`D.kt 9 kt-worker-retry-unbounded warning`
- 修法:判定改成「函式內有 runAttemptCount 就放行」。

**7. kt-volatile-compound-update 沒看鎖**

引句:「message: '[CO-35]@Volatile 只保證看得到最新值」
severity: major
blocking: 是

`@Volatile var n` 的 `n++` 放在 `synchronized(lock) { }` 內,或 `mutex.withLock { }` 內,是正確的。規則照樣報 error。

- 輸出:`D.kt 15 kt-volatile-compound-update error`
- 修法:加 `not: inside: synchronized / withLock`。

**8. kt-nested-collect 沒排除內層另開協程**

引句:「message: '[FLOW-1]collect 裡又 collect,內層永不結束」
severity: minor
blocking: 否

`outer.collect { id -> launch { inner(id).collect { … } } }` 內層在新協程,不卡外層,卻被報。輸出:`D.kt 22 kt-nested-collect warning`。修法是 `inside` 的 stopBy 遇到 `launch`/`async` 就停。

**9. kt-unsafe-collection-in-parallel 對執行緒安全集合與本地集合誤報**

引句:「message: '[CO-39]多個 Default/IO 協程同時改一般集合或變數」
severity: minor
blocking: 否

`ConcurrentHashMap.put` 被報。協程內自己宣告的本地 `mutableListOf` 的 `add` 也被報:規則末段那個「本地變數就放行」的 not 看起來沒生效。輸出:`D.kt 23 kt-unsafe-collection-in-parallel warning`。

**10. kt-bg-dispatcher-touches-view 不認 Main 切回**

引句:「message: '[CO-44]在 Dispatchers.IO/Default 上直接改 View 會丟 CalledFromWrongThreadException」
severity: minor
blocking: 否

`withContext(mainDispatcher)`(注入的 Main,正是 CO-1 鼓勵的寫法)和 `launch(Dispatchers.Main) { … }` 都沒被當成切回 Main,仍被報。規則只認 `withContext(Dispatchers.Main`。輸出:`D.kt 24`、`D.kt 25` 都是 warning。

**11. kt-dispatcher-not-closed 對借來的 executor 誤報**

引句:「- pattern: $E.asCoroutineDispatcher()」
severity: minor
blocking: 否

`db.queryExecutor.asCoroutineDispatcher()` 包的是 Room 的 executor,不是自己建的執行緒。要它 `close()` 反而會關掉別人的 executor,message 的修法不適用。輸出:`D.kt 26 kt-dispatcher-not-closed warning`。

**12. kt-datastore-read-no-catch 不認 runCatching**

引句:「- pattern: $D.data.firstOrNull()」
severity: minor
blocking: 否

`runCatching { dataStore.data.first() }` 已經處理了例外,仍被報。`not` 只認 try_expression 和 `.catch`。輸出:`D.kt 27 kt-datastore-read-no-catch warning`。

**13. kt-gson-nonnull-field 不看「全部有預設值」**

引句:「message: '[DATA-75]Gson 不認 Kotlin 的非空與預設值」
severity: minor
blocking: 否

Kotlin 的類別所有參數都有預設值時會產生無參建構子,Gson 會用它,預設值有效。`class GModel(@SerializedName("n") val n: String = "", …)` 被報兩次,message 的前提不成立。輸出:`D.kt 28 kt-gson-nonnull-field warning`。

**14. kt-long-lived-scope-plain-job 看不出 job 變數就是 SupervisorJob**

引句:「regex: ^(SupervisorJob|coroutineContext)$」
severity: minor
blocking: 否

`private val job = SupervisorJob(); private val scope = CoroutineScope(Dispatchers.Main + job)` 被報,但這個 scope 本來就是 SupervisorJob。輸出:`D.kt 29 kt-long-lived-scope-plain-job warning`。

**15. kt-data-class-mutable-field 對 Room Entity 的 var 一律報**

引句:「message: '[PERF-30]data class 帶 var 或可變集合」
severity: minor
blocking: 否

`@Entity data class User(@PrimaryKey(autoGenerate = true) var id: Long = 0, …)` 被報。輸出:`D.kt 30 kt-data-class-mutable-field warning`。建議放行帶 `@Entity` 的類別,或這條降成提示級。

**其他沒實跑的觀察(minor,未重現)**

- kt-flow-catch-before-oneach 與 kt-catch-before-operator 都是 FLOW-11,同一段會重複報。kt-onreceive-async-without-goasync 與 kt-receiver-long-work 都是 DATA-52,也會重複報。
- kt-catch-before-operator 把 `catch{ emit(default) }.map{ 安全轉換 }` 這種刻意的放法也當壞寫法。
- kt-try-emit-in-flow 是 error。型錄也承認 `catch (e: IOException)` 只攔上游型別時不會出執行期例外,建議降成 warning。我沒實跑。

**severity 總評**

- 該維持 error 的:CO-35、DATA-3、DATA-1、FLOW-4、DATA-24。前提是先修上面 1 到 7 的誤報。
- error 的 kt-sql-string-concat 要限縮接收者並放行 PRAGMA 與 DDL,否則 error 太重。
- 目前的 warning 都會擋推送。12 到 15 這類啟發式的規則,誤報率沒量過就擋推送太重,建議先放 hints。

**總結:** 7 條 major,都已實跑重現,且都會擋推送,主因是規則漏排測試路徑、漏認 `companion object`、鎖和 `runAttemptCount` 早退等常見正確寫法,以及 SQL 規則的 message 教了做不到的修法。另有 8 條 minor。
