class VM(private val source: UserSource) : ViewModel() {
    val flow = Pager(PagingConfig(20), pagingSourceFactory = { source }).flow // BAD
    val flow2 = Pager(PagingConfig(20)) { source }.flow // BAD
}
