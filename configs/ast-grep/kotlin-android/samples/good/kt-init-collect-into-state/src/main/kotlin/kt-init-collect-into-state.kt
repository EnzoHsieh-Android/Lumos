class FeedViewModel(repo: Repo) : ViewModel() {
    val state = repo.stream().map { FeedState.Ready(it) } // GOOD
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), FeedState.Loading)
}

// 容易誤報:init 裡 collect 但不倒進狀態,只做副作用
class AnalyticsViewModel(repo: Repo, private val analytics: Analytics) : ViewModel() {
    init {
        viewModelScope.launch {
            repo.events().collect { analytics.log(it) }
        }
    }
}
