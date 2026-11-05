class ProfileViewModel(user: Flow<User>, prefs: Flow<Prefs>) : ViewModel() {
    val state = combine(user, prefs) { u, p -> UiState(u, p) } // GOOD
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState.Loading)
}

// 容易誤報:兩條 collect 是並排的兩個協程,不是一條收另一條
fun CoroutineScope.watch(user: Flow<User>, prefs: Flow<Prefs>) {
    launch { user.collect { showUser(it) } }
    launch { prefs.collect { applyPrefs(it) } }
}
