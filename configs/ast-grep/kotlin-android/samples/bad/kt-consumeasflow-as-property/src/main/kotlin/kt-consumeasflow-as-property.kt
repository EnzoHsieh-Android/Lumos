class Vm : ViewModel() {
    private val _events = Channel<Event>()
    val events = _events.consumeAsFlow() // BAD
    val other: Flow<Int> = channel.consumeAsFlow().map { it * 2 } // BAD
}
