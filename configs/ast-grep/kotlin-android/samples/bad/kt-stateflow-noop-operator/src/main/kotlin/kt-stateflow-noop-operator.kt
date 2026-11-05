fun a() {
    uiState.distinctUntilChanged().collect() // BAD
    _state.flowOn(Dispatchers.IO).launchIn(scope) // BAD
    viewModel.state.conflate().collect() // BAD
    repo.data.stateIn(scope, SharingStarted.Lazily, 0).cancellable() // BAD
}
