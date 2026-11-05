package bad

// case: io-scope-property
class N1ViewModel : ViewModel() {
    private val scope = CoroutineScope(Dispatchers.IO)
    fun go() { scope.launch { } }
}
// case: mainscope
class N2ViewModel : ViewModel() {
    private val ui = MainScope()
}
// case: supervisor-scope-android-vm
class N3ViewModel(app: Application) : AndroidViewModel(app) {
    private val bg = CoroutineScope(SupervisorJob() + Dispatchers.Default)
}
