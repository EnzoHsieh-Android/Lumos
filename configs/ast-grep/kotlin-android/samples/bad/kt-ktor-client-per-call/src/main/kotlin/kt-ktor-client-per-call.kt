suspend fun a(): String {
    val client = HttpClient(OkHttp) { install(ContentNegotiation) } // BAD
    return client.get("x").bodyAsText()
}
suspend fun b(): String = HttpClient().get("x").bodyAsText() // BAD

// 代碼審 r2(規則A F4):關的是別的東西,不是這個 client
fun ext(writer: Writer) { val c = HttpClient(CIO); c.get("x"); writer.close() } // BAD
