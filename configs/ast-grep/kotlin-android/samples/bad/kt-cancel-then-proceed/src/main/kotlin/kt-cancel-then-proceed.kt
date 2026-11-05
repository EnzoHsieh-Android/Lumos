fun a() {
    job.cancel() // BAD
    startNew()
}
fun b() {
    searchJob?.cancel() // BAD
    resetResults()
}
