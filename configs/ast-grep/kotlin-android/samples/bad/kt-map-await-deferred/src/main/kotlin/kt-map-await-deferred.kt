package bad

suspend fun loadAll(ids: List<String>) = coroutineScope {
    ids.map { async { api.get(it) } }.map { it.await() }  // BAD
}

suspend fun collect(ds: List<Deferred<Int>>) = ds.map { d -> d.await() }  // BAD
