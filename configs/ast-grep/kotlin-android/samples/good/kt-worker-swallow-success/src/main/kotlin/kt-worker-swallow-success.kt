class W(c: Context, p: WorkerParameters) : Worker(c, p) {
    override fun doWork(): Result {
        try { upload() } catch (e: Exception) { return if (runAttemptCount < 3) Result.retry() else Result.failure() } // GOOD
        try { upload() } catch (e: Throwable) { return Result.failure() } // GOOD
        try { setForegroundAsync(info()).get() } catch (e: IllegalStateException) { Log.w("t", "fg", e) } // GOOD 刻意吞掉非致命錯誤
        try { upload() } catch (e: CancellationException) { throw e } // GOOD
        return Result.success()
    }
    fun helper() = try { 1 } catch (e: Exception) { 0 } // GOOD 不在 doWork
}

// 容易誤報:catch 接 Exception,但包成自己的例外往外拋,沒有吞掉
class SyncWorker(c: Context, p: WorkerParameters) : CoroutineWorker(c, p) {
    override suspend fun doWork(): Result {
        try {
            sync()
        } catch (e: Exception) {
            throw SyncFailed(e) // GOOD
        }
        return Result.success()
    }
}
