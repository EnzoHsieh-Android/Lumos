// 跨規則邊界案例(檔名以 cross- 開頭):ViewModel 裡的 SharingStarted.Lazily 歸 kt-statein-lazily-or-no-timeout(STATE-4)報,
// 放在這裡是證明 kt-statein-lazily-in-viewmodel 不重複報;好例的跨規則檢查略過這種檔
class Vm3(repo: Repo) : ViewModel() {
    val c = repo.items.stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}
