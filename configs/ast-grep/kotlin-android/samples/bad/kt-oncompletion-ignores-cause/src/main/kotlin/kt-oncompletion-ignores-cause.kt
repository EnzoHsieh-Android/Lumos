fun a() {
    flow.onCompletion { showDone() }.launchIn(scope) // BAD
    // BAD-NEXT
    repo.sync()
        .onCompletion { _state.value = Done }
        .collect()
}
