package good

// case: channel-in-repository
class DownloadRepository {
    private val queue = Channel<Job>(capacity = 64)
    val jobs = queue.receiveAsFlow()
}
// case: state-field-instead
class B1ViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState = _uiState.asStateFlow()
    fun userMessageShown() { _uiState.update { it.copy(userMessage = null) } }
}
// case: sharedflow-unit-trigger
class B2ViewModel : ViewModel() {
    private val refresh = MutableSharedFlow<Unit>(replay = 1)
}
