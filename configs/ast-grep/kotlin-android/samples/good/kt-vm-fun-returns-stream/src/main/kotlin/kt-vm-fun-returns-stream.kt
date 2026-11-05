package good

// case: derived-property
class I4ViewModel(private val repository: Repo) : ViewModel() {
    private val addressInput = MutableStateFlow("")
    val postalCode: StateFlow<String> = addressInput.flatMapLatest { repository.getPostCode(it) }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "")
    fun setInput(address: String) { addressInput.value = address }
}
// case: private-helper-returns-flow
class I5ViewModel(private val repo: Repo) : ViewModel() {
    private fun source(id: String): Flow<User> = repo.user(id)
}
// case: repository-returns-flow
class UserStore { fun observeUser(): Flow<User> = flowOf() }
