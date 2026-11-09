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

// 括號裡再包一層加法:SupervisorJob 屬性是內層加法的直接運算元(代碼審 r4 通才席 Finding 2)
class Holder3 {
    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.Main) + (CoroutineName("h3") + job)
}

// 容易誤報:括號包住 SupervisorJob 屬性再加上去,要認得是同一個屬性
class Holder4 {
    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.Main) + (job) // GOOD
}

// 容易誤報:兩層括號的加法,屬性在最裡層
class Holder5 {
    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.Main) + (CoroutineName("h5") + (job)) // GOOD
}
