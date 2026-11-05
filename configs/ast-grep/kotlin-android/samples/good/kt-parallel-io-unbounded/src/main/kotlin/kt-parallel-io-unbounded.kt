suspend fun a(ids: List<Int>) = coroutineScope {
    val io = Dispatchers.IO.limitedParallelism(8)
    ids.map { id -> async(io) { blockingCall(id) } }.awaitAll() // GOOD
}
suspend fun b(ids: List<Int>) = coroutineScope {
    ids.map { id -> async(Dispatchers.IO) { sem.withPermit { blockingCall(id) } } }.awaitAll() // GOOD
}
suspend fun c() = coroutineScope {
    val d = async(Dispatchers.IO) { load() } // GOOD
}
