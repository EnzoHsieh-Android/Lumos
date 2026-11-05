package bad

// case: suspend-get-model
class ModelRepository { suspend fun getModel(): Model = api.fetch() }
// case: interface-load-list
interface NewsRepo { suspend fun loadNews(page: Int): List<News> }
