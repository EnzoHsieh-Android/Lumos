fun a() = channelFlow {
    launch { send(1) } // GOOD
}
private fun b() {
    scope.launch {
        flow { emit(1) }.collect { show(it) } // GOOD
    }
}
fun c() = flow { emit(load()) } // GOOD
