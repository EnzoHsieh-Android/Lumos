package good

// case: postValue
fun P4ViewModel.load() { thread { live.postValue(repo.get()) } }
// case: back-to-main
suspend fun P5ViewModel.load() { withContext(Dispatchers.IO) { val x = repo.get(); withContext(Dispatchers.Main) { live.setValue(x) } } }
// case: main-thread-setValue
fun P6ViewModel.load() { viewModelScope.launch { live.setValue(1) } }
