// 容易誤報:測試假實作
class FakeNewsRepository {
    val news = MutableStateFlow<List<News>>(emptyList())
    suspend fun fetch(): NewsDto = NewsDto()
}
