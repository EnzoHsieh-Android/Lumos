package bad

class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val r = loadFuture.get() // BAD
        latch.await(5, TimeUnit.SECONDS) // BAD
        worker.join() // BAD
        val t = Tasks.await(task) // BAD
    }
}
