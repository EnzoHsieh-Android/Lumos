package bad

// case: lazily
class J1ViewModel(repo: Repo) : ViewModel() {
    val uiState = repo.stream().stateIn(viewModelScope, SharingStarted.Lazily, UiState())
}
// case: whileSubscribed-no-timeout
class J2ViewModel(repo: Repo) : ViewModel() {
    val uiState = repo.stream().stateIn(viewModelScope, SharingStarted.WhileSubscribed(), UiState())
}
// case: bare-whileSubscribed
class J3ViewModel(repo: Repo) : ViewModel() {
    val uiState = repo.stream().stateIn(viewModelScope, WhileSubscribed(), UiState())
}
