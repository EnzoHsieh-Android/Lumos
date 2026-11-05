class EventViewModel : ViewModel() {
    val events = MutableSharedFlow<Event>() // BAD
    val items = mutableStateListOf<Item>() // BAD
}

class LegacyViewModel : ViewModel() {
    val user = MutableLiveData<User>() // BAD
}
