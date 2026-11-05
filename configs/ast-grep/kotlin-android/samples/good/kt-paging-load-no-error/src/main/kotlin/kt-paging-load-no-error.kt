class S1(private val api: Api) : PagingSource<Int, User>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, User> = try { // GOOD
        val page = api.page(params.key ?: 1)
        LoadResult.Page(page.items, null, page.next)
    } catch (e: IOException) {
        LoadResult.Error(e)
    }
}
class Loader { suspend fun load() = api.page(1) } // GOOD 不是 PagingSource
