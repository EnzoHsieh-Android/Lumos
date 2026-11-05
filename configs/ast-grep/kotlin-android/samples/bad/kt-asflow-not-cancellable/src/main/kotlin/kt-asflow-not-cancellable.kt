suspend fun a() {
    (1..1_000_000).asFlow().collect { heavy(it) } // BAD
    items.asFlow().map { convert(it) }.collect() // BAD
}
