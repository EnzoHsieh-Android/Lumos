// 語意覆核級已知誤報(代碼審 r2 規則B Finding 3):runAttemptCount 先存變數再判上限,形狀上看不到它在條件裡
class VarWorker(c: Context, p: WorkerParameters) : Worker(c, p) {
    override fun doWork(): Result {
        val attempts = runAttemptCount
        if (attempts >= 3) return Result.failure()
        return Result.retry()
    }
}
