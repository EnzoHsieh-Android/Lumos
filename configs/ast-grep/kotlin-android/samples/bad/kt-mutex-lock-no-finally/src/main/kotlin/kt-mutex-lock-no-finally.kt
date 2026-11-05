suspend fun a() {
    mutex.lock() // BAD
    work()
    mutex.unlock()
}
suspend fun b() {
    mutex.lock(owner) // BAD
    val r = compute()
    mutex.unlock(owner)
}
