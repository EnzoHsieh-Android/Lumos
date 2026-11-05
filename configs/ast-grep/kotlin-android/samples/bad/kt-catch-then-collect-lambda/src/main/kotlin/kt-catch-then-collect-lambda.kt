suspend fun a() {
    flow.catch { log(it) }.collect { v -> parse(v) } // BAD
    repo.items().catch { emit(emptyList()) }.collectLatest { render(it) } // BAD
}
