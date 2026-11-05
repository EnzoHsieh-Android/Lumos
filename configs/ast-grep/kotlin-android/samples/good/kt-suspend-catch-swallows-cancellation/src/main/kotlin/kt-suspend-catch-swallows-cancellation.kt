suspend fun a(api: Api): User? {
    return try { api.user() } catch (e: CancellationException) { throw e } catch (e: Exception) { null } // GOOD
}
suspend fun b(api: Api): User? =
    try { api.user() } catch (e: Exception) { coroutineContext.ensureActive(); null } // GOOD
suspend fun c(api: Api): User? =
    try { api.user() } catch (e: Exception) { if (e is CancellationException) throw e; null } // GOOD
fun d(): Int = try { 1 } catch (e: Exception) { 0 } // GOOD 不是 suspend
suspend fun e(api: Api): User? = try { api.user() } catch (e: IOException) { null } // GOOD 窄型別
