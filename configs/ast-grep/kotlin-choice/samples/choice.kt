// 選擇點規則樣本:行尾 `// HIT <列號…>` = 那條規則有節點從這一行開始;`// MISS <列號…>` = 沒有節點從這一行開始。
// 型錄〈選擇點表〉每一列至少一個 HIT;configs/ast-grep/kotlin-android/check.py 的 choice_sample_problems 用真的 ast-grep 核對。
package sample

fun relational(count: Int, limit: Int, enabled: Boolean, a: Int, b: Int) {
    if (count > limit && enabled) save(count) // HIT C-1 C-9 C-17
    if (a < b) save(a) // HIT C-2
    if (a >= b || enabled) save(b) // HIT C-3 C-10 C-17
    if (a <= b) save(a) // HIT C-4
    if (a == b) save(a) // HIT C-5
    if (a != b) save(b) // HIT C-6
    if (a === b) save(a) // HIT C-7
    if (a !== b) save(b) // HIT C-8
}

fun arithmetic(x: Int, a: Int, b: Int): Int {
    val s = x + a // HIT C-11
    val d = x - a // HIT C-12
    val m = x * a // HIT C-13
    val q = x / a // HIT C-14
    val r = x % a // HIT C-15
    return s + d + m + q + r
}

fun unary(done: Boolean, state: State) {
    while (!done) step() // HIT C-16
    if (state.isLoading) return // HIT C-17
    if (isReady()) go() // HIT C-17
    val label = "a < b" // MISS C-2
    // flatMapLatest here
    val ok = done // MISS C-17
}

fun statements(x: Int) {
    save(x) // HIT C-18
    notify() // HIT C-18
}

fun only(x: Int) {
    save(x) // MISS C-18
}

fun lambdas(list: List<Int>) {
    list.map { x -> // HIT C-18
        transform(x) // MISS C-18
    }
    val v = if (list.isEmpty()) {
        compute() // MISS C-18
    } else 0
    list.forEach { y ->
        log2(y) // HIT C-18
        keep(y) // MISS C-18
    }
}

fun api(xs: List<Int>, flow: Flow<Int>) {
    xs.filter { it > 0 } // HIT C-19 C-1
    xs.filterNot { it > 0 } // HIT C-20 C-1
    xs.any { it > 0 } // HIT C-21 C-1
    xs.all { it > 0 } // HIT C-22 C-1
    xs.none { it > 0 } // HIT C-23 C-1
    xs.sortedBy { it } // HIT C-24
    xs.sortedByDescending { it } // HIT C-25
    xs.minByOrNull { it } // HIT C-26
    xs.maxByOrNull { it } // HIT C-27
    flow.flatMapLatest { repo.search(it) } // HIT C-28
    flow.flatMapConcat { repo.search(it) } // HIT C-29
    flow.flatMapMerge { repo.search(it) } // HIT C-30
    flow.distinctUntilChanged().collect { show(it) } // HIT C-31
    val f = xs.filter // MISS C-19
}
