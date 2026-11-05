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
