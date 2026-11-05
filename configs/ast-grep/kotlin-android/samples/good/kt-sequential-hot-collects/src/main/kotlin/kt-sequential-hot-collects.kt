class MainActivity : AppCompatActivity() {
    fun a() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch { viewModel.uiState.collect { render(it) } } // GOOD
                launch { viewModel.events.collect { handle(it) } } // GOOD
            }
        }
    }
}
suspend fun b() {
    repo.loadPage(1).collect { add(it) } // GOOD
    repo.loadPage(2).collect { add(it) } // GOOD
}
