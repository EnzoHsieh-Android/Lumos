class W(c: Context, p: WorkerParameters) : Worker(c, p) {
    override fun doWork(): Result {
        scope.launch { upload() } // BAD
        thread { upload() } // BAD
        GlobalScope.launch(Dispatchers.IO) { upload() } // BAD
        return Result.success()
    }
}
