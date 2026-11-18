// 第二批選擇點樣本([[Projects/選擇點表第二批常見誤用寫法_計劃]] 範圍 2):不插進既有樣本檔(行指紋含前後各兩行,插進去會改到既有行的指紋)。
// HIT 標在節點開始的那一行(樣本核對只看節點起始行)。
package sample

fun nul(name: String?, a: String?, b: String?, c: String) {
    val n = name ?: "guest" // HIT C-32
    val m = name // HIT C-32
        ?: "guest"
    val k = a ?: b ?: c // HIT C-32
    val s = user?.profile?.name // HIT C-33
    val t = repo.user()
        ?.name // HIT C-33
    val u = repo.user() // 取使用者
        ?.name // MISS C-33
    val v = repo.user() /* 註 */ ?.name // MISS C-33
    val w = repo.user().name // MISS C-33 C-32
}

fun scope(x: Int?, list: List<Int?>, c: Boolean) {
    val y = x.let { it + 1 } // HIT C-34
    val xs = list.map { it?.let { g(it) } } // HIT C-34 C-33
    x?.let { show(it) } // MISS C-34
    if (c) x.let { show(it) } // MISS C-34
    for (i in list) x.let { show(it) } // MISS C-34
    while (c) x.let { show(it) } // MISS C-34
    if (c) go() else x.let { show(it) } // MISS C-34
    when (c) { true -> x.let { show(it) }; else -> go() } // MISS C-34
    val z = if (c) x.let { it + 1 } else 0 // HIT C-34
    if (c) { go() } else if (d) { x.let { show(it) } } // MISS C-34
    if (c) go() else if (d) x.let { show(it) } // MISS C-34
    if (c) if (d) x.let { show(it) } // MISS C-34
    for (i in list) if (c) x.let { show(it) } // MISS C-34
    if (c) when (d) { true -> x.let { show(it) }; else -> go() } // MISS C-34
    if (c) try { x.let { show(it) } } catch (e: Exception) { go() } // MISS C-34
    val q = if (c) 1 else if (d) x.let { it + 1 } else 0 // MISS C-34(巢狀在分支裡的 if 當值用,語法判不完,不收)
    fun h() = if (c) x.let { it + 1 } else 2 // HIT C-34
    // 值位置的每一種外層各一行 HIT、catch 區塊當陳述一行 MISS:規則每個子句拿掉都要有一行翻紅(代碼審 r3 c1 g1)
    val u = when (c) { true -> x.let { it + 1 }; else -> 0 } // HIT C-34
    val v = if (c) { go(); x.let { it + 1 } } else 0 // HIT C-34
    val w = when (c) { true -> { go(); x.let { it + 1 } }; else -> 0 } // HIT C-34
    val t = try { go(); x.let { it + 1 } } catch (e: Exception) { 0 } // HIT C-34
    val t2 = try { go() } catch (e: Exception) { x.let { it + 1 } } // HIT C-34
    if (c) try { go() } catch (e: Exception) { x.let { show(it) } } // MISS C-34
    // 第四輪補齊:規則每一行、行內每個選項拿掉都要有一行翻紅(註解排除、最後一個陳述、when 掛在 if 底下、方法名比對;代碼審 r4 c1)
    val lc = list.map {
        x.let { it + 1 } // HIT C-34
    }
    val mc = list.map {
        x.let { it + 1 } /* 註 */ // HIT C-34
    }
    val ys = list.map { x.let { go(it) }; 1 } // MISS C-34
    val v2 = if (c) { x.let { go(it) }; 5 } else 0 // MISS C-34
    if (c) when (d) { true -> { go(); x.let { show(it) } }; else -> go() } // MISS C-34
    val al = x.also { it + 1 } // MISS C-34
    // 第五輪補齊:if 區塊最後一個陳述後接註解、finally 不是值、方法名頭尾、點號前後空白、沒有呼叫(代碼審 r5 b1 c1 c2)
    val v3 = if (c) {
        go(); x.let { it + 1 } // HIT C-34
    } else 0
    val t3 = try { go() } finally { x.let { it + 1 } } // MISS C-34
    val lx = x.letX { it } // MISS C-34
    val sp = x . let { it + 1 } // HIT C-34
    run { x.let } // MISS C-34
    done()
}

fun flows(a: Flow<Int>, b: Flow<Int>) {
    val f = a.combine(b) { x, y -> x + y } // HIT C-35
    val g = combine(a, b) { x, y -> x + y } // MISS C-35
    val h = kotlinx.coroutines.flow.combine(a, b) { x, y -> x + y } // MISS C-35
    val z = a.zip(b) { x, y -> x + y } // MISS C-35
    // 沒有呼叫的屬性存取不收(代碼審 r4)
    val p = a.combine // MISS C-35
    // 安全呼叫、點號前後空白、名字頭尾、完整套件名只認整串(代碼審 r5 c1 c4)
    val f1 = a?.combine(b) { x, y -> x + y } // HIT C-35
    val f3 = a.combineLatest(b) { x, y -> x + y } // MISS C-35
    val f5 = a . combine(b) { x, y -> x + y } // HIT C-35
    val f7 = kotlinx.coroutines
        .flow.combine(a, b) { x, y -> x + y } // MISS C-35
    val f8 = my.kotlinx.coroutines.flow.combine(a, b) { x, y -> x + y } // HIT C-35
}

@Composable
fun effects(userId: String, id: Int, k: Int, items: List<Int>) {
    LaunchedEffect(userId, id) { load(userId, id) } // HIT C-36
    LaunchedEffect("user_$id") { load() } // HIT C-36
    LaunchedEffect(Unit) { load() } // MISS C-36
    LaunchedEffect("init") { load() } // MISS C-36
    LaunchedEffect(key1 = Unit) { load() } // MISS C-36
    LaunchedEffect() { load() } // MISS C-36
    LaunchedEffect(k, block = { load() }) // MISS C-36
    LaunchedEffect(-1) { load() } // MISS C-36
    LaunchedEffect('c') { load() } // MISS C-36
    LaunchedEffect(+2.5) { load() } // MISS C-36
    LaunchedEffect(-1.coerceAtLeast(k)) { load() } // HIT C-36
    LaunchedEffect(-k) { load() } // HIT C-36
    // 每一種字面值各一行 MISS:字面值清單漏抄一種就有一行翻紅(代碼審 r3 c2)
    LaunchedEffect(true) { load() } // MISS C-36
    LaunchedEffect(null) { load() } // MISS C-36
    LaunchedEffect(1) { load() } // MISS C-36
    LaunchedEffect(1.5) { load() } // MISS C-36
    LaunchedEffect(1L) { load() } // MISS C-36
    LaunchedEffect(0x1F) { load() } // MISS C-36
    LaunchedEffect(0b1) { load() } // MISS C-36
    LaunchedEffect(1u) { load() } // MISS C-36
    LaunchedEffect(-1L) { load() } // MISS C-36
    LaunchedEffect(-0x1F) { load() } // MISS C-36
    LaunchedEffect(-0b1) { load() } // MISS C-36
    LaunchedEffect(-1u) { load() } // MISS C-36
    // 字串插值兩種寫法與方法名比對各一行(代碼審 r4 c2)
    LaunchedEffect("k${id}") { load() } // HIT C-36
    LaunchedEffectCompat(k) { load() } // MISS C-36
    LaunchedEffect(k + 1) { load() } // HIT C-36
    run(k) { load() } // MISS C-36 C-37
    // 名字頭尾錨點、Unit 只認整個名字、帶號的是運算式不是常數、標註加常數仍是常數(代碼審 r5 c1 c3)
    MyLaunchedEffect(k) { load() } // MISS C-36
    LaunchedEffect(distanceUnit) { load() } // HIT C-36
    LaunchedEffect(UnitX) { load() } // HIT C-36
    LaunchedEffect(-k + 1) { load() } // HIT C-36
    LaunchedEffect(@Suppress("x") 1) { load() } // MISS C-36
    val r1 = remember(k) { items.sorted() } // HIT C-37
    val r2 = remember<Int>(k) { 3 } // HIT C-37
    val r3 = remember() { 3 } // MISS C-37
    val r4 = remember(Unit) { 3 } // MISS C-37
    val r7 = remember(-1) { 3 } // MISS C-37
    val r8 = remember(-1.0.coerceAtLeast(k)) { 3 } // HIT C-37
    val r5 = remember(k) // MISS C-37
    val r9 = remember("k${id}") { 3 } // HIT C-37
    val r10 = rememberSaveable(k) { 3 } // MISS C-37
    val r11 = myremember(k) { 3 } // MISS C-37
    val r12 = remember(distanceUnit) { 3 } // HIT C-37
    val r6 = remember( // HIT C-37
        items,
        k,
    ) { items.size + k }
}
