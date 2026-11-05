suspend fun a(client: HttpClient): User? {
    val r = client.get("u/1") // GOOD 先看狀態
    return if (r.status.isSuccess()) r.body<User>() else null
}
suspend fun b(api: Api): User? = api.getUser().body() // GOOD Retrofit 不是 Ktor
fun c(resp: Response<User>) = resp.body() // GOOD
