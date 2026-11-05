suspend fun a() = withContext(Dispatchers.Default) {
    file.readText() // BAD
}
fun b() {
    scope.launch(Dispatchers.Default) {
        val r = client.newCall(req).execute() // BAD
        val s = FileInputStream(path) // BAD
    }
}
