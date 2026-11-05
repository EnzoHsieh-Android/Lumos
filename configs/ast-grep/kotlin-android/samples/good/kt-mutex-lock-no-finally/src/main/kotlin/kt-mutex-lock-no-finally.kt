suspend fun a() {
    mutex.lock() // GOOD
    try { work() } finally { mutex.unlock() }
}
suspend fun b() {
    mutex.withLock { work() } // GOOD
}
suspend fun c() {
    try {
        mutex.lock() // GOOD
        work()
    } finally { mutex.unlock() }
}
