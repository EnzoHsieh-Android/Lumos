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
// 容易誤報:SupervisorJob 先存進變數再組 scope
class Holder {
    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.Main + job) // GOOD
}
// 容易誤報(代碼審 r3 規則席 Finding 3):SupervisorJob 屬性用加法接在 CoroutineScope(…) 後面
class Holder2 {
    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.Main) + job // GOOD
}
