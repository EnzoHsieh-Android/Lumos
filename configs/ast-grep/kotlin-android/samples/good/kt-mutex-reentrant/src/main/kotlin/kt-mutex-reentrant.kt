suspend fun a() {
    mutexA.withLock { // GOOD
        mutexB.withLock { work() }
    }
}
suspend fun b() {
    mutex.withLock { step1() } // GOOD
    mutex.withLock { step2() } // GOOD
}
