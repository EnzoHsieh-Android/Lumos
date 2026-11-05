fun a() {
    flow.catch { log(it) }.map { mayThrow(it) }.collect() // BAD
    flow.catch { emit(0) }.filter { check(it) }.launchIn(scope) // BAD
    flow.catch { }.mapNotNull(::parse).collect() // BAD
}
