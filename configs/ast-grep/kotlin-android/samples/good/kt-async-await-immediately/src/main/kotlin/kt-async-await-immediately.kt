suspend fun loadFeed(): Feed = withContext(io) { api.feed() } // GOOD:換執行緒用 withContext

suspend fun loadUser(): User = api.user() // GOOD:直接呼叫

// 容易誤報:async 先全部開出去、最後才 await,真的有並行
suspend fun loadHome(): Home = coroutineScope {
    val user = async { api.user() }
    val feed = async { api.feed() }
    Home(user.await(), feed.await())
}
