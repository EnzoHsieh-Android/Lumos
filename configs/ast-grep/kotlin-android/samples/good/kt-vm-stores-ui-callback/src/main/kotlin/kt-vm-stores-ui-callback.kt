package good

// case: lambda-param-not-stored
class G4ViewModel : ViewModel() {
    fun load(onDone: () -> Unit) { viewModelScope.launch { onDone() } }
}
// case: exception-handler-property
class G5ViewModel : ViewModel() {
    private val handler = CoroutineExceptionHandler { _, e -> log(e) }
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}
// case: non-vm-holds-listener
class Presenter {
    private var listener: OnDoneListener? = null
}
