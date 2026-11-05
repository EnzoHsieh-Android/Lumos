fun a() = flow {
    coroutineScope {
        launch { emit(1) } // BAD
    }
}
fun b() = flow<Int> {
    val d = scope.async { emit(load()) } // BAD
}
