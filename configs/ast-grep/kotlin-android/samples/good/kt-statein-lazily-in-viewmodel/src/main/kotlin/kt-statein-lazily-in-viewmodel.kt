class Vm(repo: Repo) : ViewModel() {
    val a = repo.items.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList()) // GOOD
}
object Settings {
    val prefs = store.data.stateIn(appScope, SharingStarted.Lazily, null) // GOOD
}
class Vm2 : ViewModel() {
    val heavy by lazy { compute() } // GOOD
}
// 去重:SharingStarted.Lazily 歸 kt-statein-lazily-or-no-timeout 報,這條不重複
class Vm3(repo: Repo) : ViewModel() {
    val c = repo.items.stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}
