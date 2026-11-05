fun a() {
    lifecycleScope.launch {
        viewModel.uiState.collect { render(it) }
        viewModel.events.collect { handle(it) } // BAD
    }
}
fun b() {
    scope.launch {
        _state.collectLatest { draw(it) }
        effects.collect() // BAD
    }
}
