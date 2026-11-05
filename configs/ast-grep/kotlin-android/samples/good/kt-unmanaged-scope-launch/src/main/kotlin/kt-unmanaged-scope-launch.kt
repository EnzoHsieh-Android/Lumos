class Sync(private val applicationScope: CoroutineScope, private val api: Api) {
    fun a() = applicationScope.launch { api.sync() } // GOOD 注入的 scope
}
class VM : ViewModel() {
    fun b() = viewModelScope.launch { } // GOOD
}
suspend fun c() = coroutineScope { launch { } } // GOOD 結構化
