val client = HttpClient(OkHttp) { install(ContentNegotiation) } // GOOD 頂層單例
suspend fun a(): String = HttpClient().use { it.get("x").bodyAsText() } // GOOD use 會關
@Provides @Singleton
fun provide(): HttpClient = HttpClient(OkHttp) // GOOD DI
