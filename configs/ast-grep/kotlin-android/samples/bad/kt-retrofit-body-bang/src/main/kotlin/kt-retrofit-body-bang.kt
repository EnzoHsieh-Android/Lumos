suspend fun loadUser(api: Api): User {
    val response = api.user()
    return response.body()!! // BAD:沒看 isSuccessful
}

suspend fun loadFeed(api: Api): Feed {
    val response = api.feed()
    if (response.code() >= 0) {
        return response.body()!! // BAD:看的不是 isSuccessful
    }
    error("unreachable")
}
