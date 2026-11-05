package good

// case: whileSubscribed-5000
class J4ViewModel(repo: Repo) : ViewModel() {
    val uiState = repo.stream().stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState())
}
// case: named-timeout
class J5ViewModel(repo: Repo) : ViewModel() {
    val uiState = repo.stream().stateIn(viewModelScope, SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000), UiState())
}
// case: repository-lazily-cache
class CacheRepository(scope: CoroutineScope, api: Api) {
    val data = api.stream().shareIn(scope, SharingStarted.Lazily, 1)
}
