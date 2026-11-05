fun users(api: Api, io: CoroutineDispatcher): Flow<List<User>> = flow {
    emit(api.users())
}.flowOn(io) // GOOD

// 容易誤報:withContext 寫在 flow 會呼叫的 suspend 函式裡,不在 flow { } 本體
suspend fun loadFeed(api: Api, io: CoroutineDispatcher): Feed = withContext(io) { api.feed() }

fun feed(api: Api, io: CoroutineDispatcher): Flow<Feed> = flow { emit(loadFeed(api, io)) }
