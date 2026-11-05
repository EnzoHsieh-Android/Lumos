suspend fun loadUser(): User = coroutineScope {
    async { api.user() }.await() // BAD:立刻 await,沒並行
}

suspend fun loadFeed(scope: CoroutineScope): Feed {
    return scope.async(Dispatchers.IO) { api.feed() }.await() // BAD:只是想換執行緒
}
