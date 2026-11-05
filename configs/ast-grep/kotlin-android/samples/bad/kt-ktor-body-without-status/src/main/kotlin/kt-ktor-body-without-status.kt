suspend fun a(client: HttpClient): User = client.get("u/1").body<User>() // BAD
suspend fun b(client: HttpClient): User = client.post("u") { setBody(x) }.body() // BAD
