class Repo(private val scope: CoroutineScope) {
    fun initialize() { // BAD
        scope.launch { warmUp() }
    }
    fun refresh(force: Boolean) { // BAD
        appScope.launch(Dispatchers.IO) { sync(force) }
    }
}
