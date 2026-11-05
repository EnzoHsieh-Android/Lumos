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
