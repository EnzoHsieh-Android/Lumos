// 第三批選擇點樣本([[Projects/選擇點表第三批業務情境寫法_計劃]] 範圍 2、S5):不插進既有樣本檔(行指紋含前後各兩行,插進去會改到既有行的指紋)。
// HIT 標在節點開始的那一行(樣本核對只看節點起始行):作用域兩列是識別字那一行,retry 兩列是接收者開頭那一行。
package sample

fun scopes(ids: List<Int>, list: List<Int>, c: Boolean) {
    supervisorScope { // HIT C-38
        val a = async { f() }
        val b = async { g() }
    }
    coroutineScope { // HIT C-39
        launch { f() }
        launch { g() }
    }
    // 同一個陳述裡兩個、for/while 本體與迴圈呼叫裡一個(會開出很多個)都算兩個以上
    coroutineScope { awaitAll(async { a() }, async { b() }) } // HIT C-39
    supervisorScope { for (id in ids) { launch { load(id) } } } // HIT C-38
    supervisorScope { while (c) { launch { f() } } } // HIT C-38
    supervisorScope { repeat(3) { launch { f() } } } // HIT C-38
    coroutineScope { ids.map { async { load(it) } }.awaitAll() } // HIT C-39
    coroutineScope { ids.forEach { launch { load(it) } } } // HIT C-39
    supervisorScope { launch { a() }; launch { b() } } // HIT C-38
    // 只有一個子協程、夾了別的 lambda、帶接收者的,都不算這個作用域的兩個子協程(計劃〈用詞〉子協程、最近一層 lambda)
    supervisorScope { val a = async { f() }; a.await() } // MISS C-38
    coroutineScope { load { async { x() } } } // MISS C-39
    list.map { coroutineScope { async { x() } } } // MISS C-39
    supervisorScope { val x = coroutineScope { async { 1 }.await() }; val y = coroutineScope { async { 2 }.await() } } // MISS C-38 C-39
    coroutineScope { scope.launch { a() }; scope.launch { b() } } // MISS C-39
    supervisorScope { this.async { a() }; async { b() } } // MISS C-38
    supervisorScope { list.map { ids.forEach { launch { f() } } } } // MISS C-38
    supervisorScope { withContext(io) { launch { a() }; launch { b() } } } // MISS C-38
    mySupervisorScope { launch { a() }; launch { b() } } // MISS C-38
    x.supervisorScope { launch { a() }; launch { b() } } // MISS C-38
    // 建立後立刻 .await()/.join() 的照樣算子協程:每支都立刻等的換寫法必然等價、落成等價放行(計劃〈天花板〉第 3 條);
    // 不看先後的排除會把同時跑的兄弟一起排掉(代碼審 r2 正確性、邊界、通才三席實跑),所以不收這條排除
    supervisorScope { // HIT C-38
        val a = async { f() }.await()
        val b = async { g() }.await()
    }
    coroutineScope { launch { a() }.join(); launch { b() }.join() } // HIT C-39
    supervisorScope { val a = async { f() }.await(); launch { g() } } // HIT C-38
    // 先開一支不等、再開一支立刻等:兩支同時在跑,一定要命中
    supervisorScope { launch { g() }; async { f() }.await() } // HIT C-38
    supervisorScope { val a = async { f() }; val b = async { g() }.await(); a.await() } // HIT C-38
    coroutineScope { launch { a() }; val r = async { b() }.await() } // HIT C-39
    // 都沒有立刻等的、包在別的呼叫引數裡才等的,照常算
    supervisorScope { // HIT C-38
        val a = async { f() }
        val b = async { g() }
        a.await() + b.await()
    }
    coroutineScope { foo(async { a() }).await(); foo(async { b() }).await() } // HIT C-39
}

fun picks(users: List<U>, s: String, q: Flow<String>, id: Int) {
    val u = users.singleOrNull { it.id == id } // HIT C-40
    val u1 = users.single { it.id == id } // HIT C-41
    val u2 = users.firstOrNull { it.ok } // HIT C-42
    val n = s.toIntOrNull() ?: 0 // HIT C-43
    val n2 = s.toLongOrNull() // HIT C-44
    val n3 = s?.toDoubleOrNull() // HIT C-45
    val r = q.mapLatest { search(it) } // HIT C-46
    val r2 = q.transformLatest { emit(it) } // HIT C-47
    // 沒有呼叫的屬性存取、名字頭尾不同的不收
    val p = users.single // MISS C-41
    val sx = users.singleX { it.ok } // MISS C-41
    val fx = users.firstOrNullX { it.ok } // MISS C-42
    val ix = s.toIntOrNullSafe() // MISS C-43
    val mx = q.mapLatestBy { it } // MISS C-46
}

fun flows(q: Flow<Int>, scope: CoroutineScope, n: Int) {
    val f1 = MutableSharedFlow<Int>(replay = 1) // HIT C-48
    val f2 = MutableSharedFlow<Int>(replay = 0) // HIT C-49
    val f9 = q.shareIn(scope, SharingStarted.Eagerly, replay = 1) // HIT C-48
    val fa = q.shareIn(scope, SharingStarted.Eagerly, replay = 0) // HIT C-49
    val f3 = MutableSharedFlow<Int>(replay = 2) // MISS C-48 C-49
    // replay = 1 換 0 會在建構時丟例外的(帶 onBufferOverflow、沒有值不是 0 的 extraBufferCapacity)不收;DROP_OLDEST 照常命中
    val f4 = MutableSharedFlow<Int>(replay = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST) // MISS C-48
    val f5 = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = 0, onBufferOverflow = BufferOverflow.DROP_OLDEST) // MISS C-48
    // 同一個呼叫拆兩行:replay 那一列不命中、DROP_OLDEST 那一列照常命中(一行只能標一種,所以拆開標)
    val f4b = MutableSharedFlow<Int>(replay = 1, // MISS C-48
        onBufferOverflow = BufferOverflow.DROP_OLDEST) // HIT C-51
    val f6 = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST) // HIT C-48 C-51
    // 顯式寫預設的 SUSPEND:換 0 照樣合法,照常命中(代碼審 r1 b2 c1);零寫成十六進位、二進位、帶正負號或 Long 也認得是 0,照樣排除
    val fe = MutableSharedFlow<Int>(replay = 1, onBufferOverflow = BufferOverflow.SUSPEND) // HIT C-48
    val ff = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = 0x0, onBufferOverflow = BufferOverflow.DROP_OLDEST) // MISS C-48
    val fg = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = 0X00, onBufferOverflow = BufferOverflow.DROP_OLDEST) // MISS C-48
    val fh = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = 0b0, onBufferOverflow = BufferOverflow.DROP_OLDEST) // MISS C-48
    val fi = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = -0, onBufferOverflow = BufferOverflow.DROP_OLDEST) // MISS C-48
    val fj = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = +0, onBufferOverflow = BufferOverflow.DROP_OLDEST) // MISS C-48
    val fk = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = 0L, onBufferOverflow = BufferOverflow.DROP_OLDEST) // MISS C-48
    val fl = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = -0x0, onBufferOverflow = BufferOverflow.DROP_OLDEST) // MISS C-48
    val fb = MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = n, onBufferOverflow = BufferOverflow.DROP_LATEST) // HIT C-48 C-52
    val f7 = Foo(replay = 1) // MISS C-48
    val f8 = MutableSharedFlow<Int>(1) // MISS C-48
    val fc = MutableSharedFlow<Int>(extraBufferCapacity = 1) // MISS C-48 C-49
    val f10 = MutableSharedFlow<Int>(extraBufferCapacity = 8, onBufferOverflow = BufferOverflow.DROP_LATEST) // HIT C-52
    val fd = Channel<Int>(8, MyOverflow.DROP_OLDEST) // MISS C-51
}

fun starts(scope: CoroutineScope) {
    val j = async(start = CoroutineStart.LAZY) { f() } // HIT C-50
    // 建立後立刻 .await()/.join() 的必然等價不收;只看直接接在後面那一層,包在別的呼叫引數裡的照收
    val j2 = async(start = CoroutineStart.LAZY) { f() }.await() // MISS C-50
    val j3 = launch(start = CoroutineStart.LAZY) { f() }.join() // MISS C-50
    val j5 = scope.async(start = CoroutineStart.LAZY) { f() }.await() // MISS C-50
    val j4 = foo(async(start = CoroutineStart.LAZY) { f() }).await() // HIT C-50
    val j6 = async(start = CoroutineStart.LAZY) { f() }.start() // HIT C-50
    val j7 = MyStart.LAZY // MISS C-50
}

suspend fun saves() {
    withContext(NonCancellable) { save() } // HIT C-53
    // finally 裡一定要用(型錄 CO-15),換掉只會造出已知錯誤寫法;不是唯一引數的不收
    try { work() } finally { withContext(NonCancellable) { close() } } // MISS C-53
    withContext(NonCancellable + io) { save() } // MISS C-53
    withContext(io, NonCancellable) { save() } // MISS C-53
    launch(NonCancellable) { save() } // MISS C-53
}

fun retries(flow: Flow<Int>, repo: Repo) {
    val w = flow.retry(3).map { it } // HIT C-54
    val w2 = repo.items().retry(3) { it is IOException } // HIT C-54
    val w3 = repo.items().retry { it is IOException } // HIT C-54
    val w4 = repo.items()?.retry(3) // HIT C-54
    val z = repo.items( // HIT C-55
    )
        .retryWhen { c, n -> n < 2 }
    val z2 = repo.items().retryWhen { c, n -> n < 2 } // HIT C-55
    val myRes = myResult.retry() // HIT C-54
    // WorkManager 的 Result.retry() 拿掉呼叫編不過,不收
    val r1 = Result.retry() // MISS C-54
    val r2 = ListenableWorker.Result.retry() // MISS C-54
    val r3 = androidx.work.ListenableWorker.Result.retry() // MISS C-54
    val r4 = flow.retryX(3) // MISS C-54
}
