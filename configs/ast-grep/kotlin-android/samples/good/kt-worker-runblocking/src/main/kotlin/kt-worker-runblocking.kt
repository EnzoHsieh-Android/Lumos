class W(c: Context, p: WorkerParameters) : CoroutineWorker(c, p) {
    override suspend fun doWork(): Result { upload(); return Result.success() } // GOOD
}
fun main() = runBlocking { app() } // GOOD 不在 doWork
