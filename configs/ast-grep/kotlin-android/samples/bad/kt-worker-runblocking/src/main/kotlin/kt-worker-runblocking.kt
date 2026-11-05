class W(c: Context, p: WorkerParameters) : Worker(c, p) {
    override fun doWork(): Result {
        runBlocking { upload() } // BAD
        return runBlocking(Dispatchers.IO) { // BAD
            Result.success()
        }
    }
}
