val a = Channel<Event>(Channel.UNLIMITED) // BAD
val b = Channel<Int>(capacity = Channel.UNLIMITED) // BAD
fun c() = sensor.readings().buffer(UNLIMITED) // BAD
