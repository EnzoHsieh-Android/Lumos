class UserRepository {
    private val state = MutableStateFlow(emptyList<User>()) // GOOD 私有
    fun users(): StateFlow<List<User>> = state // GOOD
    private fun fetch(): UserDto = api.user("1") // GOOD 私有
    suspend fun user(id: String): User = api.user(id).toDomain() // GOOD
}
class UserMapper { fun map(d: UserDto): User = d.toDomain() } // GOOD 不是 Repository
