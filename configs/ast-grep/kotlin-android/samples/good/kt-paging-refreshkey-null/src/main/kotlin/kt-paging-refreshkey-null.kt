class S1 : PagingSource<Int, User>() {
    override fun getRefreshKey(state: PagingState<Int, User>): Int? = // GOOD
        state.anchorPosition?.let { state.closestPageToPosition(it)?.prevKey?.plus(1) }
}
class S2 {
    fun getRefreshKey(): Int? { // GOOD 有判斷才回 null
        if (x) return null
        return 1
    }
}
