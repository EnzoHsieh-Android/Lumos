class DetailViewModel(private val repo: Repo) : ViewModel() {
    fun observe(id: Long): StateFlow<Item?> =
        repo.item(id).stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null) // BAD

    fun events(): SharedFlow<Event> {
        return repo.events().shareIn(viewModelScope, SharingStarted.WhileSubscribed()) // BAD
    }
}
