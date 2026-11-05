class A {
    private fun a() {
        scope.launch { // GOOD
            try { mayThrow() } catch (e: Exception) { log(e) }
        }
    }
    suspend fun b() {
        try { // GOOD
            coroutineScope { launch { work() } }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) { }
    }
    suspend fun c() {
        try { withContext(io) { load() } } catch (e: IOException) { } // GOOD
    }
    fun d() {
        try { prepare() } finally { scope.launch { cleanup() } } // GOOD
    }
}

// 容易誤報:launch 寫在 catch 區塊裡(錯誤發生後才開協程回報),不是被 try 包住
fun CoroutineScope.parseOrReport(raw: String) {
    try {
        parse(raw)
    } catch (e: Exception) {
        launch { report(e) } // GOOD
    }
}
