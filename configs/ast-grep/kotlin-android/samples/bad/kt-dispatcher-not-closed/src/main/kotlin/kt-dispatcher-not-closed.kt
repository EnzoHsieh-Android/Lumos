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
