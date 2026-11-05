class FeedViewModel(repo: Repo) : ViewModel() {
    private val _state = MutableStateFlow<FeedState>(FeedState.Loading)
    init {
        viewModelScope.launch {
            repo.stream().collect { _state.value = FeedState.Ready(it) } // BAD
        }
    }
}

class ProfileViewModel(repo: Repo) : ViewModel() {
    private val _state = MutableStateFlow(ProfileState())
    init {
        viewModelScope.launch {
            repo.user().collectLatest { u -> _state.update { it.copy(user = u) } } // BAD
        }
    }
}
