suspend fun a(api: Api): Result<User> =
    try { // GOOD
        Result.success(api.user())
    } catch (e: HttpException) {
        Result.failure(ServerError(e.code(), e))
    } catch (e: IOException) {
        Result.failure(NetworkError(e))
    }
suspend fun b(api: Api): User? =
    try { api.user() } catch (e: java.io.IOException) { null } // GOOD 只接 IOException 不在此規則
fun c() = try { parse() } catch (e: HttpExceptionWrapper) { null } // GOOD 名字相似的別的型別
