class UserRepository {
    fun users(): MutableStateFlow<List<User>> = state // BAD
    suspend fun user(id: String): UserDto = api.user(id) // BAD
    val raw: Flow<List<UserDto>> = flow { } // BAD
}
