suspend fun a(api: Api): User? {
    try { // BAD
        return api.user()
    } catch (e: HttpException) {
        return null
    }
}
suspend fun b(api: Api): User? =
    try { api.user() } catch (e: retrofit2.HttpException) { null } // BAD
