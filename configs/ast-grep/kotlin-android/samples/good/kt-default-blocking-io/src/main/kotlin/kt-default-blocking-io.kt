suspend fun a() = withContext(Dispatchers.IO) {
    file.readText() // GOOD
}
suspend fun b() = withContext(Dispatchers.Default) {
    items.sortedBy { it.score } // GOOD
}
suspend fun c() = withContext(Dispatchers.Default) {
    val text = withContext(Dispatchers.IO) { file.readText() } // GOOD
    parse(text)
}
