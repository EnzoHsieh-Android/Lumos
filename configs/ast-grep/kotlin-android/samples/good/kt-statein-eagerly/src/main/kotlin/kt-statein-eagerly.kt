class FeedViewModel(repo: Repo) : ViewModel() {
    val state = repo.stream().stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList()) // GOOD
}

// 容易誤報:具名參數寫法,started 給的是 WhileSubscribed
class UserViewModel(repo: Repo) : ViewModel() {
    val user = repo.user().stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),
        initialValue = null,
    ) // GOOD
}
