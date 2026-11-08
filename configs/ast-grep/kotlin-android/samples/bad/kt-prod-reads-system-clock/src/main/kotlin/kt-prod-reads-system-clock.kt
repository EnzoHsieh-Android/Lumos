package bad

class SessionManager(private val store: Store) {
    fun stamp() = Order(createdAt = Instant.now()) // BAD

    fun stampKt() = kotlin.time.Clock.System.now() // BAD

    fun today() = LocalDate.now() // BAD
}
