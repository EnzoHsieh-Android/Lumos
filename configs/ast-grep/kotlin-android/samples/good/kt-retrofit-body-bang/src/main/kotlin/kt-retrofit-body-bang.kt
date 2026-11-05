suspend fun loadUser(api: Api): User {
    val response = api.user()
    return if (response.isSuccessful) response.body() ?: error("empty") else throw HttpException(response) // GOOD
}

// 容易誤報:介面直接回傳 T,讓 Retrofit 自己丟 HttpException,沒有 body()!!
interface UserApi {
    @GET("user")
    suspend fun user(): User
}

suspend fun loadFeed(api: Api): Feed? {
    val response = api.feed()
    return response.body() // GOOD:沒有 !!,呼叫端處理 null
}

// 容易誤報(代碼審 r1 M1):先擋掉失敗再 body()!!
suspend fun loadGuard(api: Api): User {
    val response = api.user()
    if (!response.isSuccessful) throw HttpException(response)
    return response.body()!! // GOOD
}

suspend fun loadAnd(api: Api): User {
    val response = api.user()
    if (response.isSuccessful && response.body() != null) { return response.body()!! } // GOOD
    throw HttpException(response)
}

suspend fun loadCheck(api: Api): User {
    val response = api.user()
    check(response.isSuccessful)
    return response.body()!! // GOOD
}
