class A {
    fun a() {
        scope.launch(handler) { work() } // GOOD
    }
    private fun b() {
        scope.launch {
            launch(Dispatchers.IO) { work() } // GOOD
        }
    }
    private fun c() {
        scope.launch {
            supervisorScope { launch(handler) { work() } } // GOOD
        }
    }
    fun d() {
        val d = scope.async(Dispatchers.IO) { load() } // GOOD
    }
}

// 容易誤報:handler 裝在根協程,裡面的子協程不帶 handler
class SyncRunner(private val scope: CoroutineScope) {
    private val handler = CoroutineExceptionHandler { _, e -> log(e) }
    fun start() = scope.launch(handler) {
        launch { syncUsers() } // GOOD
        launch { syncOrders() } // GOOD
    }
}
