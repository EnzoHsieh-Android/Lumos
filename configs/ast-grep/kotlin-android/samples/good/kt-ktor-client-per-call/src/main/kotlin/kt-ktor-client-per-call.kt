val client = HttpClient(OkHttp) { install(ContentNegotiation) } // GOOD 頂層單例
suspend fun a(): String = HttpClient().use { it.get("x").bodyAsText() } // GOOD use 會關
@Provides @Singleton
fun provide(): HttpClient = HttpClient(OkHttp) // GOOD DI

// 容易誤報(代碼審 r1 M14):同函式裡 finally close()
suspend fun ktorClose(): String {
    val client = HttpClient(CIO)
    try { return client.get("x").bodyAsText() } finally { client.close() } // GOOD
}
// 容易誤報(代碼審 r3 規則席 Finding 5):先存進變數,再對同一個變數 use { } 關掉
suspend fun ktorUseVar(): String {
    val client = HttpClient(CIO)
    return client.use { it.get("x").bodyAsText() } // GOOD
}
