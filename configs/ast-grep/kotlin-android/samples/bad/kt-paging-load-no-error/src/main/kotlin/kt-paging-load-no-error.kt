class S1(private val api: Api) : PagingSource<Int, User>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, User> { // BAD
        val page = api.page(params.key ?: 1)
        return LoadResult.Page(page.items, null, page.next)
    }
}
class S2(private val api: Api) : PagingSource<Int, User>() {
    override suspend fun load(params: LoadParams<Int>) = // BAD
        LoadResult.Page(api.page(1).items, null, null)
}
