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

// 代碼審 r2(規則B Finding 4):鄰行別人的理由註解、或 reasonable 這種字,不是這一行的理由
class NeighborViewModel(f: Flow<Int>) : ViewModel() {
    val a = f.stateIn(viewModelScope, SharingStarted.Eagerly, 0) // 理由: 初始就要
    val b = f.stateIn(viewModelScope, SharingStarted.Eagerly, 0) // BAD
    val c = f.stateIn(viewModelScope, SharingStarted.Eagerly, 0) // BAD
    // 理由: 要
    val d = f.stateIn(viewModelScope, SharingStarted.Eagerly, 0)
    // TODO fix reasonable thing
    val e = f.stateIn(viewModelScope, SharingStarted.Eagerly, 0) // BAD
}
