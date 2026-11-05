package good

// case: private-suspend
class M3ViewModel(private val repo: Repo) : ViewModel() {
    fun save() { viewModelScope.launch { doSave() } }
    private suspend fun doSave() { repo.save() }
}
// case: repository-suspend
class SaveRepository { suspend fun save() { } }
// case: suspend-lambda-param
class M4ViewModel : ViewModel() {
    fun run(block: suspend () -> Unit) { viewModelScope.launch { block() } }
}
