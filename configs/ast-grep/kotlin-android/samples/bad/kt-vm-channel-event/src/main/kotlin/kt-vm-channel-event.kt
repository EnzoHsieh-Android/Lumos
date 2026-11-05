package bad

// case: channel-receiveAsFlow
class A1ViewModel : ViewModel() {
    private val _events = Channel<UiEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()
}
// case: sharedflow-navigation
class A2ViewModel @Inject constructor(private val repo: Repo) : ViewModel() {
    private val _nav = MutableSharedFlow<NavigationEvent>(extraBufferCapacity = 1)
    val nav = _nav.asSharedFlow()
}
// case: consumeAsFlow
class A3ViewModel : ViewModel() {
    private val ch = Channel<String>()
    val toasts = ch.consumeAsFlow()
}
// case: untyped-channel-named-event
class A4ViewModel : ViewModel() {
    private val _effects: Channel<UiEffect> = Channel()
}
