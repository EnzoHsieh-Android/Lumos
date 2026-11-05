fun a() {
    newSingleThreadContext("x").use { d -> run(d) } // GOOD
}
fun b() {
    val pool = Executors.newFixedThreadPool(4).asCoroutineDispatcher() // GOOD
    try { runWith(pool) } finally { pool.close() }
}
object Shared {
    val single = newSingleThreadContext("shared") // GOOD
}
class Worker : Closeable {
    private val single = newSingleThreadContext("worker") // GOOD
    override fun close() { single.close() }
}
val appIo = Dispatchers.IO.limitedParallelism(4) // GOOD
// 容易誤報:包的是 Room 借來的 executor,不是自己建的執行緒,不該由這裡 close
fun c(db: RoomDatabase) {
    val d = db.queryExecutor.asCoroutineDispatcher() // GOOD
    scope.launch(d) { work() }
}
