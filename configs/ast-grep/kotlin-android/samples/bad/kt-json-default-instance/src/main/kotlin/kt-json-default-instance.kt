fun a(s: String): User = Json.decodeFromString(s) // BAD
fun b(s: String) = Json.decodeFromString<User>(s) // BAD
fun c(e: JsonElement) = Json.Default.decodeFromString<User>(e.toString()) // BAD
