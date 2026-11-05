val a = flow.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0) // GOOD
val b = flow.stateIn(viewModelScope, SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000), 0) // GOOD
val c = flow.stateIn(viewModelScope, SharingStarted.WhileSubscribed(STOP_TIMEOUT), 0) // GOOD
