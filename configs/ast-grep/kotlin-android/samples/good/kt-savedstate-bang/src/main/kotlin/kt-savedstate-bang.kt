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
// 容易誤報:名字含 handle/savedState 但不是 SavedStateHandle
fun pick(handlers: Map<Type, Handler>, type: Type) = handlers[type]!!
fun err(errorHandler: Registry, k: String) = errorHandler.get(k)!!
fun st(savedStates: Map<Int, Bundle>, id: Int) = savedStates[id]!!
fun reg(owner: SavedStateRegistryOwner) = owner.savedStateRegistry.get("x")!!
