package bad

// case: get-generic-bang
class U1ViewModel(savedStateHandle: SavedStateHandle) : ViewModel() {
    private val id = savedStateHandle.get<String>("id")!!
}
// case: index-bang
class U2ViewModel(private val handle: SavedStateHandle) : ViewModel() {
    private val id: String = handle["userId"]!!
}
// case: private-underscore-handle
class U5ViewModel(private val _savedStateHandle: SavedStateHandle) : ViewModel() {
    private val tab: Int = _savedStateHandle["tab"]!!
}
// case: savedState-name(代碼審 r2 規則B Finding 6:官方範例慣用名;泛用名 state 代碼審 r3 拿掉)
class S1ViewModel(private val savedState: SavedStateHandle) : ViewModel() {
    val a = savedState.get<String>("id")!!
    val b = savedState["id"]!!
}
