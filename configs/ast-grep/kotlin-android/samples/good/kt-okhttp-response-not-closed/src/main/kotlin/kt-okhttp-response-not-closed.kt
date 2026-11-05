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
