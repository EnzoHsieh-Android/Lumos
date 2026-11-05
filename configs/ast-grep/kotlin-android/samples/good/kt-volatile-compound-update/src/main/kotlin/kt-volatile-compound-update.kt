class Counter {
    private val n = AtomicInteger(0)
    @Volatile var flag = false
    var plain = 0
    fun hit() {
        n.incrementAndGet() // GOOD
        flag = true // GOOD
        plain++ // GOOD
    }
}

// 容易誤報:@Volatile 欄位只整個換值;計數交給 AtomicLong;區域變數 ++ 沒有共享
class Stats {
    @Volatile private var snapshot = Snapshot(0)
    private val hits = AtomicLong()
    fun hit() {
        snapshot = Snapshot(hits.incrementAndGet()) // GOOD
    }
    fun countEven(xs: List<Int>): Int {
        var n = 0
        for (x in xs) if (x % 2 == 0) n++ // GOOD
        return n
    }
}

// 容易誤報:++ 放在鎖裡,讀改寫已經互斥
class Guarded(private val lock: Any, private val mutex: Mutex) {
    @Volatile var n = 0
    @Volatile var m = 0
    fun hit() {
        synchronized(lock) { n++ } // GOOD
    }
    suspend fun hit2() {
        mutex.withLock { m += 1 } // GOOD
    }
}
