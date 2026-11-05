class W(c: Context, p: WorkerParameters) : CoroutineWorker(c, p) {
    override suspend fun doWork(): Result {
        try { upload() } catch (e: Exception) { } // BAD
        return Result.success()
    }
}
class W2(c: Context, p: WorkerParameters) : Worker(c, p) {
    override fun doWork(): Result {
        try {
            upload()
        } catch (t: Throwable) { // BAD
            Log.e("t", "fail", t)
        }
        return Result.success()
    }
}
