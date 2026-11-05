package good

// case: property-initializer
class K3ViewModel(private val repo: Repo) : ViewModel() {
    val uiState = repo.stream().stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState())
}
// case: getter-returns-backing
class K4ViewModel : ViewModel() {
    private val _s = MutableStateFlow(0)
    val s: StateFlow<Int> get() = _s.asStateFlow()
}
// case: by-lazy
class K5ViewModel(private val repo: Repo) : ViewModel() {
    val uiState by lazy { repo.stream().stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState()) }
}
