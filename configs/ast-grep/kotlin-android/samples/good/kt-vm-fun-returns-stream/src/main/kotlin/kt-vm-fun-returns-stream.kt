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
// 容易誤報:getter 式函式回傳既有流的唯讀視圖,不重打資料層
class I6ViewModel : ViewModel() {
    private val _state = MutableStateFlow(S())
    private val _ticks = Channel<Tick>()
    fun getState(): StateFlow<S> = _state.asStateFlow()
    fun ticks(): Flow<Tick> = _ticks.receiveAsFlow()
}
