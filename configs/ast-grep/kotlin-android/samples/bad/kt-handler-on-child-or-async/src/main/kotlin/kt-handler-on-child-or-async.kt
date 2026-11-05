class A {
    fun a() {
        scope.launch {
            launch(handler) { work() } // BAD
        }
    }
    fun b() {
        val d = scope.async(exceptionHandler) { load() } // BAD
    }
    fun c() {
        viewModelScope.launch {
            scope.launch(Dispatchers.IO + errorHandler) { x() } // BAD
        }
    }
}
