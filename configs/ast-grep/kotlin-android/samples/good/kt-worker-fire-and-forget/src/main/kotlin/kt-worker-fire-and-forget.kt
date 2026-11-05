class W(c: Context, p: WorkerParameters) : CoroutineWorker(c, p) {
    override suspend fun doWork(): Result {
        upload() // GOOD 直接 suspend
        coroutineScope { launch { a() }; launch { b() } } // GOOD 結構化,會等完
        return Result.success()
    }
}
class VM : ViewModel() { fun x() = viewModelScope.launch { } } // GOOD 不在 doWork
