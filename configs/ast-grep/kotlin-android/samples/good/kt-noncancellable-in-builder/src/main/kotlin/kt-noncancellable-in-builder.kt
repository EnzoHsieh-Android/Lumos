suspend fun a() {
    try { work() } finally {
        withContext(NonCancellable) { cleanup() } // GOOD
    }
    appScope.launch { save() } // GOOD
    scope.launch(Dispatchers.IO) { save() } // GOOD
}

// 容易誤報:NonCancellable 出現在 launch 裡面的 withContext,不是傳給 launch
fun Repo.closeAsync(appScope: CoroutineScope) {
    appScope.launch {
        withContext(NonCancellable) { flush() } // GOOD
    }
}
