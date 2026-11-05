suspend fun a(): String {
    val client = HttpClient(OkHttp) { install(ContentNegotiation) } // BAD
    return client.get("x").bodyAsText()
}
suspend fun b(): String = HttpClient().get("x").bodyAsText() // BAD
