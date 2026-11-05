suspend fun a(ids: List<Int>) = coroutineScope {
    val list = ids.map { async(Dispatchers.Default) { f(it) } }.awaitAll() // GOOD
}
suspend fun b(ids: List<Int>) = coroutineScope {
    val list = mutableListOf<X>()
    ids.map { async(Dispatchers.Default) { val x = f(it); mutex.withLock { list.add(x) } } } // GOOD
}
suspend fun c(ids: List<Int>) = coroutineScope {
    ids.map { async(Dispatchers.Default) { val out = mutableListOf<X>(); out.add(f(it)); out } } // GOOD
}
fun d() {
    viewModelScope.launch { items.add(load()) } // GOOD
}
