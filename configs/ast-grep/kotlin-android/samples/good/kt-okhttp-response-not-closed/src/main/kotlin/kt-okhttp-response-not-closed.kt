fun a(client: OkHttpClient, req: Request): String =
    client.newCall(req).execute().use { it.body!!.string() } // GOOD
fun b(client: OkHttpClient, req: Request): Int {
    val r = client.newCall(req).execute() // GOOD 之後有 use
    return r.use { it.code }
}
fun c(client: OkHttpClient, req: Request): Int {
    val r = client.newCall(req).execute() // GOOD finally close
    try { return r.code } finally { r.close() }
}
fun d(client: OkHttpClient, req: Request) {
    client.newCall(req).enqueue(callback) // GOOD 非同步不在此規則
}

// 容易誤報(代碼審 r1 M10):讀完 string() 會關 body,連線就還回去了
fun e(c: OkHttpClient, r: Request): String? = c.newCall(r).execute().body?.string() // GOOD
fun f(client: OkHttpClient, req: Request): String {
    val response = client.newCall(req).execute() // GOOD
    return response.body!!.string()
}
