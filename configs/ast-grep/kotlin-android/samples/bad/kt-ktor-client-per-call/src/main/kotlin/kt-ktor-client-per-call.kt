suspend fun a(): String {
    val client = HttpClient(OkHttp) { install(ContentNegotiation) } // BAD
    return client.get("x").bodyAsText()
}
suspend fun b(): String = HttpClient().get("x").bodyAsText() // BAD

// 代碼審 r2(規則A F4):關的是別的東西,不是這個 client
fun ext(writer: Writer) { val c = HttpClient(CIO); c.get("x"); writer.close() } // BAD
// 代碼審 r3(規則席 Finding 5 的反向對照):use 的是別的資源,不是這個 client
suspend fun useOther(w: Closeable): String { val c = HttpClient(CIO); w.use { }; return c.get("x").bodyAsText() } // BAD
