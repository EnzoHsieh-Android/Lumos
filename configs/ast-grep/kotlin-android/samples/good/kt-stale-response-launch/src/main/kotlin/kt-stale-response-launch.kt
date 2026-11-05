class SearchViewModel(private val repo: Repo) : ViewModel() {
    private val query = MutableStateFlow("")
    val results = query.flatMapLatest { repo.search(it) } // GOOD:只留最新一次
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    fun onQuery(text: String) {
        query.value = text
    }
}

// 容易誤報:同樣每次呼叫都 launch,但先取消前一個 Job
class DetailViewModel(private val repo: Repo) : ViewModel() {
    private var job: Job? = null
    fun load(id: Long) {
        job?.cancel()
        job = viewModelScope.launch {
            _state.update { it.copy(item = repo.get(id)) } // GOOD
        }
    }
}
