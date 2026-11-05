package good

// case: cancelled-in-onCleared
class N4ViewModel : ViewModel() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    override fun onCleared() { scope.cancel() }
}
// case: closeable-ctor
class N5ViewModel(private val scope: CoroutineScope = CoroutineScope(Dispatchers.Main)) : ViewModel(scope as AutoCloseable)
// case: child-of-viewModelScope
class N6ViewModel : ViewModel() {
    private val io = CoroutineScope(viewModelScope.coroutineContext + Dispatchers.IO)
}
// case: repository-own-scope
class SyncRepository { private val scope = CoroutineScope(SupervisorJob()) }
