fun users(api: Api, io: CoroutineDispatcher): Flow<List<User>> = flow {
    emit(api.users())
}.flowOn(io) // GOOD

// 容易誤報:withContext 寫在 flow 會呼叫的 suspend 函式裡,不在 flow { } 本體
suspend fun loadFeed(api: Api, io: CoroutineDispatcher): Feed = withContext(io) { api.feed() }

fun feed(api: Api, io: CoroutineDispatcher): Flow<Feed> = flow { emit(loadFeed(api, io)) }

// 容易誤報:emit 在 flow 自己的協程裡,withContext 只包取值
fun g(): Flow<Int> = flow { emit(withContext(Dispatchers.IO) { load() }) }

fun h(io: CoroutineDispatcher): Flow<Feed> = flow<Feed> {
    val x = withContext(io) { loadFeed() }
    emit(x)
}
