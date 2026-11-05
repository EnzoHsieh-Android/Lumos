class FeedViewModel(repo: Repo) : ViewModel() {
    val state = repo.stream().stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList()) // GOOD
}

// 容易誤報:輸入放 MutableStateFlow,函式只改輸入,輸出用 flatMapLatest 推導成屬性
class DetailViewModel(private val repo: Repo) : ViewModel() {
    private val selected = MutableStateFlow<Long?>(null)
    val item = selected.filterNotNull().flatMapLatest { repo.item(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null) // GOOD
    fun select(id: Long) {
        selected.value = id
    }
}
