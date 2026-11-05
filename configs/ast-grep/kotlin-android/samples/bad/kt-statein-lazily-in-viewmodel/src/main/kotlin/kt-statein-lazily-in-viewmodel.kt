// 只管 import 後直接寫 Lazily 的長相;SharingStarted.Lazily 歸 kt-statein-lazily-or-no-timeout
class Vm(repo: Repo) : ViewModel() {
    val a = repo.items.stateIn(viewModelScope, Lazily, emptyList()) // BAD
    val b = repo.events.shareIn(
        viewModelScope,
        started = Lazily, // BAD
    )
}
