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
