suspend fun a() = coroutineScope {
    val d = async(start = CoroutineStart.LAZY) { load() } // BAD
    if (cond) d.await()
}
suspend fun b() = coroutineScope {
    val extra = scope.async(Dispatchers.IO, CoroutineStart.LAZY) { more() } // BAD
    when (mode) { 1 -> extra.await() else -> Unit }
}
