package good

suspend fun loadAll(ids: List<String>) = coroutineScope {
    ids.map { async { api.get(it) } }.awaitAll()
}

suspend fun joinAll(jobs: List<Job>) {
    jobs.joinAll()
}

// 容易誤報:forEach 逐一 await 出處(awaitAll KDoc、IntelliJ 檢查)沒講到,這條不報
suspend fun drain(ds: List<Deferred<Int>>) {
    ds.forEach { it.await() }
}
