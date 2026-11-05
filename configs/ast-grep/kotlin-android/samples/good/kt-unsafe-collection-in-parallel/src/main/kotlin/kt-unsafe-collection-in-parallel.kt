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
// 容易誤報:執行緒安全的集合;協程內自己宣告的本地集合
fun e(ids: List<Int>) {
    val cache = ConcurrentHashMap<Int, X>()
    ids.forEach { id -> scope.launch(Dispatchers.IO) { cache.put(id, load(id)) } } // GOOD
}
suspend fun g(ids: List<Int>) = coroutineScope {
    ids.map { id ->
        async(Dispatchers.IO) {
            val local = mutableListOf<X>()
            local.add(load(id)) // GOOD
            local
        }
    }.awaitAll()
}
