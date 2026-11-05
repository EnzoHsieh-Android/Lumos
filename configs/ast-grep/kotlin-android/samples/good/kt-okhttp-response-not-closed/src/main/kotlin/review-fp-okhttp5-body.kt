// 語意覆核級已知誤報(代碼審 r3 規則席 Finding 1):OkHttp 5 的 body 是不可為 null 的屬性,
// 不寫 ?. / !!;讀完或 use 掉 body 會把連線還回去,形狀上分不清是不是同一個 Response
fun ok5a(client: OkHttpClient, req: Request): String {
    val r = client.newCall(req).execute()
    return r.body.string()
}
fun ok5b(client: OkHttpClient, req: Request): String {
    val r = client.newCall(req).execute()
    return r.body.use { it.string() }
}
fun ok5c(client: OkHttpClient, req: Request): String? {
    val r = client.newCall(req).execute()
    return r.body?.use { it.string() }
}
fun ok5d(client: OkHttpClient, req: Request): String {
    val r = client.newCall(req).execute()
    return r.body!!.use { it.string() }
}
// 席位原片段:在 use 區塊裡直接 return
fun o7(c: OkHttpClient, req: Request): String { val r = c.newCall(req).execute(); r.body.use { return it.string() } }
