class SearchViewModel(private val repo: Repo) : ViewModel() {
    fun search(query: String) {
        viewModelScope.launch { _results.value = repo.search(query) } // BAD:舊查詢晚到會蓋掉新的
    }
}

class DetailViewModel(private val repo: Repo) : ViewModel() {
    fun load(id: Long) {
        viewModelScope.launch {
            _state.update { it.copy(item = repo.get(id)) } // BAD
        }
    }
}
