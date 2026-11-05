class Counter {
    @Volatile var n = 0
    @Volatile private var total: Long = 0
    suspend fun hit(x: Long) {
        n++ // BAD
        total += x // BAD
        n = n + 1 // BAD
    }
}
