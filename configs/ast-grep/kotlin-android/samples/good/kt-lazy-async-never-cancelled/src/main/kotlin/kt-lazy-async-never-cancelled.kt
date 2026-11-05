suspend fun a() = coroutineScope {
    val d = async(start = CoroutineStart.LAZY) { load() } // GOOD
    try { if (cond) d.await() } finally { d.cancel() }
}
suspend fun b() = coroutineScope {
    val d = async(start = CoroutineStart.LAZY) { load() } // GOOD
    d.start()
}
suspend fun c() = coroutineScope {
    val d = async(start = CoroutineStart.LAZY) { load() } // GOOD
    prepare()
    val r = d.await()
}
suspend fun e() = coroutineScope {
    val d = async { load() } // GOOD
    if (cond) d.await()
}
