fun a() {
    uiState.map { it.title }.distinctUntilChanged().collect() // GOOD
    events.conflate().collect() // GOOD
}
val s = upstream.flowOn(Dispatchers.IO).stateIn(scope, SharingStarted.WhileSubscribed(5_000), 0) // GOOD
