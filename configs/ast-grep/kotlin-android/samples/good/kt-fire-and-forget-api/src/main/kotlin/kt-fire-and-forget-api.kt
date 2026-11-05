class Repo(private val scope: CoroutineScope) {
    suspend fun initialize() { warmUp() } // GOOD
    fun refresh(): Job = scope.launch { sync() } // GOOD
    private fun bg() { // GOOD
        scope.launch { sync() }
    }
}
class Vm : ViewModel() {
    fun onClick() { // GOOD
        viewModelScope.launch { save() }
    }
}
