class FeedViewModel(repo: Repo) : ViewModel() {
    val state = repo.stream().stateIn(viewModelScope, SharingStarted.Eagerly, emptyList()) // BAD
}

class UserViewModel(repo: Repo) : ViewModel() {
    val user = repo.user().stateIn(scope = viewModelScope, started = SharingStarted.Eagerly, initialValue = null) // BAD
}

// 上一行的註解不是理由
class OtherViewModel(repo: Repo) : ViewModel() {
    // cache
    val c = repo.stream().stateIn(viewModelScope, SharingStarted.Eagerly, 0) // BAD
}
