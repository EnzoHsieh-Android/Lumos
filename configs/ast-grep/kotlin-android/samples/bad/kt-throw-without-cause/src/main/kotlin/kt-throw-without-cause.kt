fun a() {
    try { load() } catch (e: IOException) { throw MyError("load failed") } // BAD
}
fun b() {
    try { load() } catch (e: Exception) {
        throw IllegalStateException("bad: ${e.message}") // BAD
    }
}
