class Up(ctx: Context, p: WorkerParameters) : CoroutineWorker(ctx, p) {
    override suspend fun doWork(): Result {
        setForeground(info()) // BAD
        return Result.success()
    }
}
class Up2(ctx: Context, p: WorkerParameters) : Worker(ctx, p) {
    override fun doWork(): Result { setForegroundAsync(info()).get(); return Result.success() } // BAD
}
