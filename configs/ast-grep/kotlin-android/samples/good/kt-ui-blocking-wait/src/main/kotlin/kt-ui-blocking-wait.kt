package good

class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val view = viewRef.get()
        lifecycleScope.launch {
            val r = deferred.await()
            job.join()
        }
        executor.execute { latch.await(5, TimeUnit.SECONDS) }
        thread { worker.join() }
    }

    private suspend fun load() {
        loader.await()
    }
}

class Repo {
    fun blocking() = future.get()
}
