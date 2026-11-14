// 乾節點規則樣本:行尾 `// HIT <列號…>` = 那條規則有節點從這一行開始;`// MISS <列號…>` = 沒有節點從這一行開始。
// 型錄〈乾節點規則〉每一列至少一個 HIT 與一個 MISS(論文 3.1、附錄 A)。
package sample

fun logs(q: List<Int>, e: Exception) {
    Timber.tag(TAG).d("q=${q.size > 0}") // HIT A-1
    Log.d(TAG, "x") // HIT A-1
    println(q) // HIT A-1
    e.printStackTrace() // HIT A-1
    catalog.d("x") // MISS A-1
    logic.run(q) // MISS A-1
}

fun asserts(x: Int) {
    require(x > 0) // HIT A-2
    check(x < 9) { "x" } // HIT A-2
    error("boom") // HIT A-2
    validator.require(x > 0) // MISS A-2
}

fun debug(x: Int) {
    if (BuildConfig.DEBUG) { show(x) } // HIT A-3
    if (BuildConfig.DEBUG && x > 1) show(x) // HIT A-3
    if (Config.DEBUG) show(x) // MISS A-3
}

suspend fun time(retry: Long) {
    delay(retry * 1000L) // HIT A-4
    withTimeout(500) { work() } // HIT A-4
    delayed(retry) // MISS A-4
}

fun monitor() {
    Trace.beginSection("x") // HIT A-5
    analytics.logEvent("open") // HIT A-5
    analyticsStore.save("x") // MISS A-5
}

fun capacity(n: Int) {
    val a = ArrayList<Int>(n * 2) // HIT A-6
    val b = StringBuilder(16) // HIT A-6
    val c = ArrayList(other) // MISS A-6
}

class Point(val x: Int) {
    override fun toString() = "a" + x // HIT A-7
    override fun hashCode(): Int { // HIT A-7
        return x * 31
    }
    fun describe() = "a" + x // MISS A-7
}

fun nulls(user: User?) {
    if (user != null) show(user.name) // HIT A-8
    if (user == other) show(user) // MISS A-8
}

fun sizes(items: List<Int>, s: String) {
    if (items.size == 0) return // HIT A-9
    if (s.length > 0) show(s) // HIT A-9
    if (items.size > 1) show(s) // MISS A-9
}

fun early(xs: List<Int>, token: String): List<Int> {
    if (xs.isEmpty()) return emptyList() // HIT A-10
    if (token.isEmpty()) return AuthError.Missing // MISS A-10
    return xs
}

fun bounds(x: Int, lo: Int) {
    val a = x.coerceIn(lo, lo + 10) // HIT A-11
    val b = maxOf(x, lo + 1) // HIT A-11
    val c = combine(x, lo + 1) // MISS A-11
}

fun floats(f: Float) {
    if (f > 1.5f) show(f) // HIT A-12
    if (f > limit) show(f) // MISS A-12
}

fun streams(out: Writer) {
    out.flush() // HIT A-13
    out.close() // HIT A-13
    out.write("x") // MISS A-13
}

@Module
class AppModule { // HIT A-14
    @Provides
    fun repo(api: Api) = RepoImpl(api) // HIT A-14
}

class Plain {
    fun repo(api: Api) = RepoImpl(api) // MISS A-14
}
