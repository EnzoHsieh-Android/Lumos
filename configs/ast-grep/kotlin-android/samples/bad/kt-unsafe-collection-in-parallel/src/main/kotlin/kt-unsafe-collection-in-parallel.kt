suspend fun a(ids: List<Int>) = coroutineScope {
    val list = mutableListOf<X>()
    ids.map { async(Dispatchers.Default) { list.add(f(it)) } }.awaitAll() // BAD
}
fun b(ids: List<Int>) {
    val map = HashMap<Int, X>()
    ids.forEach { id ->
        scope.launch(Dispatchers.IO) {
            map[id] = load(id) // BAD
        }
    }
}
