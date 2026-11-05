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

// 代碼審 r2(規則A F1):判的是別的回應,或只拿來印 log
suspend fun two(api: Api): Foo {
    val a = api.a()
    if (a.isSuccessful) { log(a) }
    val b = api.b()
    return b.body()!! // BAD:b 完全沒檢查
}
suspend fun logonly(api: Api): Foo {
    val r = api.get()
    Log.d("x", "ok=${r.isSuccessful}") // 只是印出來,沒擋
    return r.body()!! // BAD
}
