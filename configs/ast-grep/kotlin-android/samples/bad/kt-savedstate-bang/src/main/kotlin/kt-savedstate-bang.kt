package bad

// case: get-generic-bang
class U1ViewModel(savedStateHandle: SavedStateHandle) : ViewModel() {
    private val id = savedStateHandle.get<String>("id")!!
}
// case: index-bang
class U2ViewModel(private val handle: SavedStateHandle) : ViewModel() {
    private val id: String = handle["userId"]!!
}
