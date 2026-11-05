fun users(api: Api): Flow<List<User>> = flow {
    withContext(Dispatchers.IO) { emit(api.users()) } // BAD
}

fun feed(api: Api, io: CoroutineDispatcher): Flow<Feed> = flow<Feed> {
    withContext(io) { // BAD 帶型別參數的 flow<T> 也要抓
        api.feed().items.forEach { emit(it) }
    }
}
