suspend fun loadHome(api: Api, userId: Long): Home = coroutineScope {
    val user = async { api.user(userId) }
    val feed = async { api.feed(page = 1) } // GOOD:並行
    Home(user.await(), feed.await())
}

// 容易誤報:第二句用到第一句的結果,本來就得串著
suspend fun loadProfile(auth: Auth, api: Api): Profile {
    val token = auth.login()
    val profile = api.profile(token)
    return profile
}
