suspend fun a(api: Api): User? {
    return try { api.user() } catch (e: Exception) { null } // BAD
}
suspend fun b(api: Api) {
    try {
        api.sync()
    } catch (t: Throwable) { // BAD
        Log.e("t", "fail", t)
    }
}
