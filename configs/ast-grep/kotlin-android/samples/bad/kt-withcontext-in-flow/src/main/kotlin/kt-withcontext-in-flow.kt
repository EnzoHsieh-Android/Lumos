fun users(api: Api): Flow<List<User>> = flow {
    withContext(Dispatchers.IO) { emit(api.users()) } // BAD
}

fun feed(api: Api, io: CoroutineDispatcher): Flow<Feed> = flow {
    val feed = withContext(io) { api.feed() } // BAD
    emit(feed)
}
