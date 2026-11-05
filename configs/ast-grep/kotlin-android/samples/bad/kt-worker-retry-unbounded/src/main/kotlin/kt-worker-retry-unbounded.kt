class W(c: Context, p: WorkerParameters) : CoroutineWorker(c, p) {
    override suspend fun doWork(): Result = try {
        upload(); Result.success()
    } catch (e: Exception) {
        Result.retry() // BAD
    }
    fun other(): ListenableWorker.Result = ListenableWorker.Result.retry() // BAD
}
