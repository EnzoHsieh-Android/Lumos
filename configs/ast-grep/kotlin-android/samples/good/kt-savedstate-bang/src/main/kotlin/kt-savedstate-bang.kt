package good

// case: toRoute
class U3ViewModel(savedStateHandle: SavedStateHandle) : ViewModel() {
    private val route = savedStateHandle.toRoute<DetailIdRoute>()
}
// case: default-value
class U4ViewModel(savedStateHandle: SavedStateHandle) : ViewModel() {
    private val id = savedStateHandle.get<String>(ARG_ID) ?: ""
}
// case: plain-map-bang
fun lookup(map: Map<String, Int>) = map["x"]!!
