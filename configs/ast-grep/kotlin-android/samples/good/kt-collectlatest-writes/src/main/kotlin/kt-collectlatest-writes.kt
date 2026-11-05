suspend fun a() {
    events.collect { db.insert(it) } // GOOD
}
suspend fun b() {
    query.collectLatest { q -> _state.value = search(q) } // GOOD
}
suspend fun c() {
    events.collectLatest { withContext(NonCancellable) { db.insert(it) } } // GOOD
}
suspend fun d() {
    data.collectLatest { _state.update { s -> s.copy(v = it) } } // GOOD
}
