class Inbox {
    private val _events = Channel<Event>()
    val events = _events.receiveAsFlow() // GOOD
    suspend fun drain() {
        _events.consumeAsFlow().collect { handle(it) } // GOOD
    }
}

// 容易誤報:consumeAsFlow 是函式裡的區域變數,只收一次,不是類別屬性
suspend fun drainAll(channel: ReceiveChannel<Event>) {
    val flow = channel.consumeAsFlow() // GOOD
    flow.collect { handle(it) }
}
