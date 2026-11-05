val json = Json { ignoreUnknownKeys = true }
fun a(s: String): User = json.decodeFromString(s) // GOOD 共用實例
fun b(u: User) = Json.encodeToString(u) // GOOD 編碼不受影響
