class Up(ctx: Context, p: WorkerParameters) : CoroutineWorker(ctx, p) {
    override suspend fun doWork(): Result {
        try {
            setForeground(info()) // GOOD
        } catch (e: IllegalStateException) {
            Log.w("t", "fg not allowed", e)
        }
        try { setForegroundAsync(info()).get() } catch (e: IllegalStateException) { Log.w("t", "fg", e) } // GOOD
        startForeground(1, n) // GOOD 不同 API
        return Result.success()
    }
}

// 容易誤報:setForeground 包在 runCatching 裡,失敗退回一般工作
class SyncWorker(ctx: Context, p: WorkerParameters) : CoroutineWorker(ctx, p) {
    override suspend fun doWork(): Result {
        runCatching { setForeground(info()) }.onFailure { Log.w("sync", "fg not allowed", it) } // GOOD
        sync()
        return Result.success()
    }
}
