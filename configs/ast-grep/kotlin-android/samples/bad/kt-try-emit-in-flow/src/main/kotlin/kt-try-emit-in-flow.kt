fun a() = flow {
    try { // BAD
        emit(load())
    } catch (e: Exception) {
        emit(fallback)
    }
}
fun b() = flow<Int> {
    upstream.collect { v ->
        try { emit(v) } catch (e: IOException) { log(e) } // BAD
    }
}
