class Repo {
    private val scope = CoroutineScope(Job() + Dispatchers.IO) // BAD
}
class Sync {
    val scope = CoroutineScope(Dispatchers.IO) // BAD
}
class Uploader(private val io: CoroutineDispatcher) {
    private val scope: CoroutineScope = CoroutineScope(io + Job()) // BAD
}
