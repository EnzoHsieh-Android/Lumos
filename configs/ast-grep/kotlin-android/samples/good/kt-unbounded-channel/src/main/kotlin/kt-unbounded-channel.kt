val a = Channel<Event>(64, BufferOverflow.DROP_OLDEST) // GOOD
val b = Channel<Int>(Channel.BUFFERED) // GOOD
fun c() = sensor.readings().buffer(64, BufferOverflow.DROP_OLDEST) // GOOD
val d = listOf(Channel.UNLIMITED) // GOOD
