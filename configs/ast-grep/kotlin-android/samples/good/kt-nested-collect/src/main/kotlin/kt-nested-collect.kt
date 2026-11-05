class ProfileViewModel(user: Flow<User>, prefs: Flow<Prefs>) : ViewModel() {
    val state = combine(user, prefs) { u, p -> UiState(u, p) } // GOOD
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState.Loading)
}

// 容易誤報:兩條 collect 是並排的兩個協程,不是一條收另一條
fun CoroutineScope.watch(user: Flow<User>, prefs: Flow<Prefs>) {
    launch { user.collect { showUser(it) } }
    launch { prefs.collect { applyPrefs(it) } }
}

// 容易誤報:內層在新協程裡收,不卡外層
fun CoroutineScope.fanOut(outer: Flow<Int>) = launch {
    outer.collect { id -> launch { inner(id).collect { show(it) } } }
}
