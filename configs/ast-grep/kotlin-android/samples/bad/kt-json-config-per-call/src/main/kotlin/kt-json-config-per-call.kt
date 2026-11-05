fun a(s: String): User = Json { ignoreUnknownKeys = true }.decodeFromString(s) // BAD
fun b(s: String): User {
    val j = Json(from = base) { isLenient = true } // BAD
    return j.decodeFromString(s)
}
