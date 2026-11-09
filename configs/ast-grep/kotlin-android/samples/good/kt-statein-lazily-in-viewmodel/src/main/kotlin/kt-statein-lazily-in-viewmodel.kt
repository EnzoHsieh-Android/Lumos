class Vm(repo: Repo) : ViewModel() {
    val a = repo.items.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList()) // GOOD
}
object Settings {
    val prefs = store.data.stateIn(appScope, SharingStarted.Lazily, null) // GOOD
}
class Vm2 : ViewModel() {
    val heavy by lazy { compute() } // GOOD
}
