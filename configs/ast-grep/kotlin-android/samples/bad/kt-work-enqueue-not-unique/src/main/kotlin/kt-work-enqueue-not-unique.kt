fun a(ctx: Context) {
    WorkManager.getInstance(ctx).enqueue(OneTimeWorkRequestBuilder<SyncWorker>().build()) // BAD
}
class Sched(private val workManager: WorkManager) {
    fun b() = workManager.enqueue(OneTimeWorkRequest.from(SyncWorker::class.java)) // BAD
}
