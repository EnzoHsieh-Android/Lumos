class S1 : PagingSource<Int, User>() {
    override fun getRefreshKey(state: PagingState<Int, User>): Int? = null // BAD
}
class S2 : PagingSource<Int, User>() {
    override fun getRefreshKey(state: PagingState<Int, User>): Int? { // BAD
        return null
    }
}
