class A {
    fun a() {
        try {
            scope.launch { mayThrow() } // BAD
        } catch (e: Exception) { log(e) }
    }
    fun b() {
        try {
            viewModelScope.launch(Dispatchers.IO) { load() } // BAD
        } catch (e: IOException) { }
    }
    suspend fun c() = coroutineScope {
        try {
            val job = launch { work() } // BAD
        } catch (e: Exception) { }
    }
}
