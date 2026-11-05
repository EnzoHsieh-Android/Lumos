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
