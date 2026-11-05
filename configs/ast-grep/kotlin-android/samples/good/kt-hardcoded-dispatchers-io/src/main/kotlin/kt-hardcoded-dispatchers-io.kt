class UserRepository(
    private val api: Api,
    private val io: CoroutineDispatcher = Dispatchers.IO, // GOOD 預設值,測試可換
) {
    suspend fun load() = withContext(io) { api.user() } // GOOD
}
class MainActivity : AppCompatActivity() {
    fun x() = lifecycleScope.launch(Dispatchers.IO) { } // GOOD 不是 Repository
}
