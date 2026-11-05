suspend fun a(ids: List<Int>) = coroutineScope {
    ids.map { id -> async(Dispatchers.IO) { blockingCall(id) } }.awaitAll() // BAD
}
fun b(ids: List<Int>) {
    for (id in ids) {
        scope.launch {
            launch(Dispatchers.IO) { upload(id) } // BAD
        }
    }
}
