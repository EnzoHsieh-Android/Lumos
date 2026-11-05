fun a() = flow { emit(load()) }.catch { emit(fallback) } // GOOD
fun b() = flow {
    val v = try { load() } catch (e: IOException) { null } // GOOD
    emit(v)
}
fun c() = flow {
    try { emit(load()) } catch (e: IOException) { throw e } // GOOD
}
fun d() = flow {
    try { emit(load()) } finally { close() } // GOOD
}
