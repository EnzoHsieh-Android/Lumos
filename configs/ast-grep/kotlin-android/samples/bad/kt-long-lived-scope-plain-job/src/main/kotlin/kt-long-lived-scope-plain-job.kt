class Repo {
    private val scope = CoroutineScope(Job() + Dispatchers.IO) // BAD
}
class Sync {
    val scope = CoroutineScope(Dispatchers.IO) // BAD
}
class Uploader(private val io: CoroutineDispatcher) {
    private val scope: CoroutineScope = CoroutineScope(io + Job()) // BAD
}
// 代碼審 r2(規則B Finding 8):類別裡有 SupervisorJob,但這個 scope 沒用它
class S {
    private val job = SupervisorJob()
    val scope = CoroutineScope(Dispatchers.IO) // BAD
}
// 代碼審 r3(規則席 Finding 3 的反向對照):加法接的是普通 Job 屬性,不是 SupervisorJob 那個
class S2 {
    private val job = SupervisorJob()
    private val other = Job()
    private val scope = CoroutineScope(Dispatchers.Main) + other // BAD
}

// 括號裡的加法接的是普通 Job,照樣報
class S3 {
    private val other = Job()
    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.Main) + (CoroutineName("s3") + other)
}
