suspend fun a(api: Api): List<User> = try { api.users() } catch (e: IOException) { Log.e("t", "x", e); emptyList() } // BAD
fun b(): User? {
    try {
        return load()
    } catch (e: Exception) { // BAD
        Timber.e(e)
        return null
    }
}
