package good

// case: postValue
fun Q3ViewModel.load() { thread { live.postValue(1) } }
// case: main-assign
fun Q4ViewModel.load() { viewModelScope.launch { live.value = 1 } }
// case: known-fp-stateflow-from-io
suspend fun Q5ViewModel.load() { withContext(Dispatchers.IO) { _stateFlow.value = repo.get() } }
