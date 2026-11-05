class Vm(repo: Repo) : ViewModel() {
    val a = repo.items.stateIn(viewModelScope, SharingStarted.Lazily, emptyList()) // BAD
    val b = repo.events.shareIn(
        viewModelScope,
        started = SharingStarted.Lazily, // BAD
    )
}
