suspend fun a() {
    mutex.withLock { // BAD
        mutex.withLock { work() }
    }
}
suspend fun b() {
    lock.withLock { // BAD
        if (ready) { lock.lock() }
    }
}
