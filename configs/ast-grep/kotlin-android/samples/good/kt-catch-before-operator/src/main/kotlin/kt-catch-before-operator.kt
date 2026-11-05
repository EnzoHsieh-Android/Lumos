fun a() {
    flow.map { mayThrow(it) }.catch { log(it) }.collect() // GOOD
    flow.catch { log(it) }.collect { } // GOOD
}
val s = flow.catch { log(it) }.stateIn(scope, SharingStarted.WhileSubscribed(5_000), 0) // GOOD
