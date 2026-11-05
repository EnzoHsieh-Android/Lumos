suspend fun a() {
    job.cancelAndJoin() // GOOD
    startNew()
}
suspend fun b() {
    job.cancel() // GOOD
    job.join()
}
fun c() {
    searchJob?.cancel() // GOOD
    searchJob = scope.launch { search() }
}
override fun onDestroy() {
    super.onDestroy()
    job.cancel() // GOOD
}
fun d() {
    scope.cancel() // GOOD
    other()
}
