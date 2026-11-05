fun a() {
    val d = newSingleThreadContext("x") // BAD
    scope.launch(d) { work() }
}
fun b() {
    val pool = Executors.newFixedThreadPool(4).asCoroutineDispatcher() // BAD
    runWith(pool)
}
class Worker {
    private val single = newSingleThreadContext("worker") // BAD
}

// 代碼審 r2(規則B Finding 5):先把執行緒池存進變數再轉派發器
class S1 {
    private val e = Executors.newFixedThreadPool(2)
    val d = e.asCoroutineDispatcher() // BAD
}
fun f2() {
    val ex = Executors.newSingleThreadExecutor()
    val d = ex.asCoroutineDispatcher() // BAD
    scope.launch(d) { work() }
}
