class VM(private val remote: UserRemote) : ViewModel() {
    val users = Pager(PagingConfig(20)) { UserSource(remote) }.flow.cachedIn(viewModelScope) // GOOD
}
class UserRepository(private val api: Api) {
    fun users() = Pager(PagingConfig(20)) { UserSource(api) }.flow // GOOD 快取交給 ViewModel
}
