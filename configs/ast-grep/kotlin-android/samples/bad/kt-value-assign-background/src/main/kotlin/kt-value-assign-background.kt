package bad

// case: withContext-io-assign
suspend fun Q1ViewModel.load() { withContext(Dispatchers.IO) { live.value = repo.get() } }
// case: thread-assign
fun Q2ViewModel.load() { thread { live.value = 1 } }
