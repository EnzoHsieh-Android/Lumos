class VM(private val repo: UserRepository) : ViewModel() {
    val flow = Pager(PagingConfig(20), pagingSourceFactory = { UserSource(repo) }).flow.cachedIn(viewModelScope) // GOOD
    val flow2 = Pager(PagingConfig(20)) { repo.pagingSource() }.flow.cachedIn(viewModelScope) // GOOD
}

// 容易誤報:factory 是 lambda 裡呼叫 Repository 產生新的 PagingSource,不是回傳同一個變數
class OrderViewModel(private val repo: OrderRepository) : ViewModel() {
    val orders = Pager(PagingConfig(pageSize = 20)) { repo.pagingSource() }.flow.cachedIn(viewModelScope) // GOOD
}
