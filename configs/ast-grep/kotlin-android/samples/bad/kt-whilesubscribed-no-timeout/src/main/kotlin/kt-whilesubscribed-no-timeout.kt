val a = flow.stateIn(viewModelScope, SharingStarted.WhileSubscribed(), 0) // BAD
val b = flow.shareIn(viewModelScope, WhileSubscribed()) // BAD
val c = flow.stateIn(viewModelScope, SharingStarted.WhileSubscribed(replayExpirationMillis = 0), 0) // BAD
