class VM(private val api: Api) : ViewModel() {
    val users = Pager(PagingConfig(20)) { UserSource(api) }.flow // BAD
    val items get() = Pager(PagingConfig(20), pagingSourceFactory = { ItemSource(api) }).flow // BAD
}
@Composable
fun List(api: Api) {
    val items = Pager(PagingConfig(20)) { ItemSource(api) }.flow.collectAsLazyPagingItems() // BAD
}
