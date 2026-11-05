class UserRepository(private val api: Api) {
    suspend fun load() = withContext(Dispatchers.IO) { api.user() } // BAD
}
class UserLocalDataSource {
    private val io = Dispatchers.IO // BAD
}
