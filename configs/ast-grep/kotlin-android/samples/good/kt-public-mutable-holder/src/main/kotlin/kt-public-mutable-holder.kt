class EventViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow() // GOOD
}

// 容易誤報:LiveData 對外只給唯讀型別;Channel 收進 private,對外是 receiveAsFlow
class LegacyViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user // GOOD
    private val _toasts = Channel<String>(Channel.BUFFERED)
    val toasts = _toasts.receiveAsFlow() // GOOD
}
// 容易誤報:建好立刻轉成唯讀流
class Legit {
    val flowLegit = MutableSharedFlow<Int>().asSharedFlow()
}
