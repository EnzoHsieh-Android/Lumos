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

// 容易誤報:真要 Eagerly 而且附了一行理由(型錄 STATE-4 的標準寫法)
class CacheRepository(scope: CoroutineScope, source: Flow<Int>) {
    // 理由: app-scope cache must warm up before first screen
    val cache = source.stateIn(scope, SharingStarted.Eagerly, 0)
    val warm = source.stateIn(
        scope,
        SharingStarted.Eagerly, // 理由: 開機就要預熱
        0,
    )
}
