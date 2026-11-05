class W(c: Context, p: WorkerParameters) : CoroutineWorker(c, p) {
    override suspend fun doWork(): Result = try {
        upload(); Result.success()
    } catch (e: Exception) {
        Result.retry() // BAD
    }
    fun other(): ListenableWorker.Result = ListenableWorker.Result.retry() // BAD
}

// 代碼審 r2(規則B Finding 3):讀了 runAttemptCount 卻沒拿來判斷,永遠重試
class LogOnlyWorker(c: Context, p: WorkerParameters) : Worker(c, p) {
    override fun doWork(): Result {
        val n = runAttemptCount
        Log.d("w", "attempt=$runAttemptCount")
        return Result.retry() // BAD
    }
}
