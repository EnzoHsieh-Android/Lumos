package bad

// case: getter-expression
class K1ViewModel(private val repo: Repo) : ViewModel() {
    val uiState get() = repo.stream().stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState())
}
// case: getter-typed-block
class K2ViewModel(private val repo: Repo) : ViewModel() {
    val events: SharedFlow<Int>
        get() { return repo.ticks().shareIn(viewModelScope, SharingStarted.WhileSubscribed(5_000)) }
}
