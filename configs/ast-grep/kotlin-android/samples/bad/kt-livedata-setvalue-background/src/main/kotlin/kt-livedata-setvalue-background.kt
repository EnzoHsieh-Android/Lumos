package bad

// case: withContext-io
suspend fun P1ViewModel.load() { withContext(Dispatchers.IO) { live.setValue(repo.get()) } }
// case: thread
fun P2ViewModel.load() { thread { live.setValue(repo.get()) } }
// case: launch-io
fun P3ViewModel.load() { viewModelScope.launch(Dispatchers.IO) { live.setValue(1) } }
// case: outer-main-inner-io(外層 Main、內層又切 IO)
suspend fun P7ViewModel.load() { withContext(Dispatchers.Main) { withContext(Dispatchers.IO) { live.setValue(repo.get()) } } }
