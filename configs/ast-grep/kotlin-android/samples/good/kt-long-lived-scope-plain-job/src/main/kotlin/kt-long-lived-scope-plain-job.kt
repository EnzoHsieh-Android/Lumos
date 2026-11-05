class Repo {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO) // GOOD
}
class Sync(parent: Job) {
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob(parent)) // GOOD
}
class Once {
    fun run() {
        val local = CoroutineScope(Job()) // GOOD
        local.cancel()
    }
}
class Ui {
    private val scope = MainScope() // GOOD
}
