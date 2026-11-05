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
// 容易誤報:ViewModel 裡拿 Channel 當工作佇列,不是一次性事件
class B3ViewModel : ViewModel() {
    private val work = Channel<Int>(Channel.UNLIMITED)
    private val jobs = work.receiveAsFlow()
}
// 容易誤報:聊天訊息是資料流,不是一次性事件
class B4ViewModel : ViewModel() {
    private val incoming = MutableSharedFlow<ChatMessage>(replay = 50)
    private val pending: Channel<Upload> = Channel()
}
