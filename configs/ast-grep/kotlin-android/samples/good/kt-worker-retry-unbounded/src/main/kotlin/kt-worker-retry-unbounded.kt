class W(c: Context, p: WorkerParameters) : CoroutineWorker(c, p) {
    override suspend fun doWork(): Result = try {
        upload(); Result.success()
    } catch (e: IOException) {
        if (runAttemptCount < 3) Result.retry() else Result.failure() // GOOD
    }
    fun other(): Result = when {
        runAttemptCount >= MAX -> Result.failure()
        else -> Result.retry() // GOOD
    }
}

// 容易誤報:retry 寫在依錯誤類型分流的 when 裡,同一個 when 有 runAttemptCount 上限
class UploadWorker(c: Context, p: WorkerParameters) : CoroutineWorker(c, p) {
    override suspend fun doWork(): Result = try {
        upload()
        Result.success()
    } catch (e: HttpException) {
        when {
            e.code() in 400..499 -> Result.failure()
            runAttemptCount < MAX_ATTEMPTS -> Result.retry() // GOOD
            else -> Result.failure()
        }
    }
}

// 容易誤報:先用 runAttemptCount 早退,後面的 retry 已經有上限
class EarlyExitWorker(c: Context, p: WorkerParameters) : CoroutineWorker(c, p) {
    override suspend fun doWork(): Result {
        if (runAttemptCount >= 3) return Result.failure()
        return try { sync(); Result.success() } catch (e: IOException) { Result.retry() } // GOOD
    }
}
